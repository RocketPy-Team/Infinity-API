import gzip
import io
import logging
import json

from typing import NoReturn

from views.environment import EnvironmentSimulation
from views.flight import FlightSimulation
from views.motor import MotorSimulation
from views.rocket import RocketSimulation

from rocketpy._encoders import RocketPyEncoder
from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger(__name__)


def rocketpy_encoder(obj):
    """
    Encode a RocketPy object using official RocketPy encoders.

    This function uses RocketPy's official RocketPyEncoder for complete
    object serialization.

    Args:
        obj: RocketPy object (Environment, Motor, Rocket, Flight)

    Returns:
        Dictionary of encoded attributes
    """

    json_str = json.dumps(
        obj,
        cls=RocketPyEncoder,
        include_outputs=True,
        include_function_data=True,
        discretize=True,
        allow_pickle=False,
    )
    return json.loads(json_str)


def collect_attributes(obj, attribute_classes=None):
    """
    Collect attributes from various simulation classes and populate them from the flight object.
    
    Args:
        obj: RocketPy Flight object
        attribute_classes: List of attribute classes to collect from

    Returns:
        Dictionary with all collected attributes
    """
    if attribute_classes is None:
        attribute_classes = []

    attributes = rocketpy_encoder(obj)

    for attribute_class in attribute_classes:
        if issubclass(attribute_class, FlightSimulation):
            flight_attributes_list = [
                attr for attr in attribute_class.__annotations__.keys() 
                if attr not in ['message', 'rocket', 'env']
            ]
            try:
                for key in flight_attributes_list:
                    if key not in attributes:
                        try:
                            value = getattr(obj, key)
                            attributes[key] = value
                        except AttributeError:
                            pass
                        except Exception:
                            pass
            except Exception:
                pass
                
        elif issubclass(attribute_class, RocketSimulation):
            rocket_attributes_list = [
                attr for attr in attribute_class.__annotations__.keys() 
                if attr not in ['message', 'motor']
            ]
            try:
                for key in rocket_attributes_list:
                    if key not in attributes.get("rocket", {}):
                        try:
                            value = getattr(obj.rocket, key)
                            if "rocket" not in attributes:
                                attributes["rocket"] = {}
                            attributes["rocket"][key] = value
                        except AttributeError:
                            pass
                        except Exception:
                            pass
            except Exception:
                pass
                
        elif issubclass(attribute_class, MotorSimulation):
            motor_attributes_list = [
                attr for attr in attribute_class.__annotations__.keys() 
                if attr not in ['message']
            ]
            try:
                for key in motor_attributes_list:
                    if key not in attributes.get("rocket", {}).get("motor", {}):
                        try:
                            value = getattr(obj.rocket.motor, key)
                            if "rocket" not in attributes:
                                attributes["rocket"] = {}
                            if "motor" not in attributes["rocket"]:
                                attributes["rocket"]["motor"] = {}
                            attributes["rocket"]["motor"][key] = value
                        except AttributeError:
                            pass
                        except Exception:
                            pass
            except Exception:
                pass
                
        elif issubclass(attribute_class, EnvironmentSimulation):
            environment_attributes_list = [
                attr for attr in attribute_class.__annotations__.keys()
                if attr not in ['message']
            ]
            try:
                for key in environment_attributes_list:
                    if key not in attributes.get("env", {}):
                        try:
                            value = getattr(obj.env, key)
                            if "env" not in attributes:
                                attributes["env"] = {}
                            attributes["env"][key] = value
                        except AttributeError:
                            pass
                        except Exception:
                            pass
            except Exception:
                pass
        else:
            continue

    return rocketpy_encoder(attributes)

class RocketPyGZipMiddleware:
    def __init__(
        self, app: ASGIApp, minimum_size: int = 500, compresslevel: int = 9
    ) -> None:
        self.app = app
        self.minimum_size = minimum_size
        self.compresslevel = compresslevel

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        if scope["type"] == "http":
            headers = Headers(scope=scope)
            if "gzip" in headers.get("Accept-Encoding", ""):
                responder = GZipResponder(
                    self.app,
                    self.minimum_size,
                    compresslevel=self.compresslevel,
                )
                await responder(scope, receive, send)
                return
        await self.app(scope, receive, send)


class GZipResponder:
    # fork of https://github.com/encode/starlette/blob/master/starlette/middleware/gzip.py
    def __init__(
        self, app: ASGIApp, minimum_size: int, compresslevel: int = 9
    ) -> None:
        self.app = app
        self.minimum_size = minimum_size
        self.send: Send = unattached_send
        self.initial_message: Message = {}
        self.started = False
        self.content_encoding_set = False
        self.gzip_buffer = io.BytesIO()
        self.gzip_file = gzip.GzipFile(
            mode="wb", fileobj=self.gzip_buffer, compresslevel=compresslevel
        )

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        self.send = send
        with self.gzip_buffer, self.gzip_file:
            await self.app(scope, receive, self.send_with_gzip)

    async def send_with_gzip(self, message: Message) -> None:
        message_type = message["type"]
        if message_type == "http.response.start":
            # Don't send the initial message until we've determined how to
            # modify the outgoing headers correctly.
            self.initial_message = message
            headers = Headers(raw=self.initial_message["headers"])
            self.content_encoding_set = "content-encoding" in headers
        elif (
            message_type == "http.response.body" and self.content_encoding_set
        ):
            if not self.started:
                self.started = True
                await self.send(self.initial_message)
            await self.send(message)
        elif message_type == "http.response.body" and not self.started:
            self.started = True
            body = message.get("body", b"")
            more_body = message.get("more_body", False)
            if ((len(body) < self.minimum_size) and not more_body) or any(
                value == b'application/octet-stream'
                for header, value in self.initial_message["headers"]
            ):
                # Don't apply GZip to small outgoing responses or octet-streams.
                await self.send(self.initial_message)
                await self.send(message)  # pylint: disable=unreachable
            elif not more_body:
                # Standard GZip response.
                self.gzip_file.write(body)
                self.gzip_file.close()
                body = self.gzip_buffer.getvalue()

                headers = MutableHeaders(raw=self.initial_message["headers"])
                headers["Content-Encoding"] = "gzip"
                headers["Content-Length"] = str(len(body))
                headers.add_vary_header("Accept-Encoding")
                message["body"] = body

                await self.send(self.initial_message)
                await self.send(message)  # pylint: disable=unreachable
            else:
                # Initial body in streaming GZip response.
                headers = MutableHeaders(raw=self.initial_message["headers"])
                headers["Content-Encoding"] = "gzip"
                headers.add_vary_header("Accept-Encoding")
                del headers["Content-Length"]

                self.gzip_file.write(body)
                message["body"] = self.gzip_buffer.getvalue()
                self.gzip_buffer.seek(0)
                self.gzip_buffer.truncate()

                await self.send(self.initial_message)
                await self.send(message)  # pylint: disable=unreachable

        elif message_type == "http.response.body":
            # Remaining body in streaming GZip response.
            body = message.get("body", b"")
            more_body = message.get("more_body", False)

            self.gzip_file.write(body)
            if not more_body:
                self.gzip_file.close()

            message["body"] = self.gzip_buffer.getvalue()
            self.gzip_buffer.seek(0)
            self.gzip_buffer.truncate()

            await self.send(message)


async def unattached_send(message: Message) -> NoReturn:
    raise RuntimeError("send awaitable not set")  # pragma: no cover

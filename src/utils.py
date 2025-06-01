# fork of https://github.com/encode/starlette/blob/master/starlette/middleware/gzip.py
import gzip
import io
import logging
import json

from typing import NoReturn, Tuple

from rocketpy import Function
from rocketpy._encoders import RocketPyEncoder
from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger(__name__)


class DiscretizeConfig:
    """
    Configuration class for RocketPy function discretization.

    This class allows easy configuration of discretization parameters
    for different types of RocketPy objects and their callable attributes.
    """

    def __init__(
        self, bounds: Tuple[float, float] = (0, 10), samples: int = 200
    ):
        self.bounds = bounds
        self.samples = samples

    @classmethod
    def for_environment(cls) -> 'DiscretizeConfig':
        return cls(bounds=(0, 50000), samples=100)

    @classmethod
    def for_motor(cls) -> 'DiscretizeConfig':
        return cls(bounds=(0, 10), samples=150)

    @classmethod
    def for_rocket(cls) -> 'DiscretizeConfig':
        return cls(bounds=(0, 1), samples=100)

    @classmethod
    def for_flight(cls) -> 'DiscretizeConfig':
        return cls(bounds=(0, 30), samples=200)


def rocketpy_encoder(obj, config: DiscretizeConfig = DiscretizeConfig()):
    """
    Encode a RocketPy object using official RocketPy encoders.

    This function discretizes callable Function attributes and then uses
    RocketPy's official RocketPyEncoder for complete object serialization.

    Args:
        obj: RocketPy object (Environment, Motor, Rocket, Flight)
        config: DiscretizeConfig object with discretization parameters (optional)

    Returns:
        Dictionary of encoded attributes
    """

    for attr_name in dir(obj):
        if attr_name.startswith('_'):
            continue

        try:
            attr_value = getattr(obj, attr_name)
        except Exception:
            continue

        if callable(attr_value) and isinstance(attr_value, Function):
            try:
                # Create a new Function from the source to avoid mutating the original object.
                # This is important because:
                # 1. The original RocketPy object should remain unchanged for reusability
                # 2. Multiple simulations might need different discretization parameters
                # 3. Other parts of the system might depend on the original continuous function
                discretized_func = Function(attr_value.source)
                discretized_func.set_discrete(
                    lower=config.bounds[0],
                    upper=config.bounds[1],
                    samples=config.samples,
                    mutate_self=True,
                )

                setattr(obj, attr_name, discretized_func)

            except Exception as e:
                logger.warning(f"Failed to discretize {attr_name}: {e}")

    try:
        json_str = json.dumps(
            obj,
            cls=RocketPyEncoder,
            include_outputs=True,
            include_function_data=True,
        )
        return json.loads(json_str)
    except Exception as e:
        logger.warning(f"Failed to encode with RocketPyEncoder: {e}")
        attributes = {}
        for attr_name in dir(obj):
            if not attr_name.startswith('_'):
                try:
                    attr_value = getattr(obj, attr_name)
                    if not callable(attr_value):
                        attributes[attr_name] = str(attr_value)
                except Exception:
                    continue
        return attributes


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

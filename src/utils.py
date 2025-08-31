import gzip
import io
import logging
import json
from datetime import datetime
from typing import NoReturn, Tuple

import numpy as np
from scipy.interpolate import interp1d

from rocketpy import Function, Flight
from rocketpy._encoders import RocketPyEncoder

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from src.views.environment import EnvironmentSimulation
from src.views.flight import FlightSimulation
from src.views.motor import MotorSimulation
from src.views.rocket import RocketSimulation

logger = logging.getLogger(__name__)


class DiscretizeConfig:
    """
    Configuration class for RocketPy function discretization.
    """

    def __init__(
        self, bounds: Tuple[float, float] = (0, 10), samples: int = 200
    ):
        self.bounds = bounds
        self.samples = samples

    @classmethod
    def for_environment(cls) -> "DiscretizeConfig":
        return cls(bounds=(0, 50000), samples=100)

    @classmethod
    def for_motor(cls) -> "DiscretizeConfig":
        return cls(bounds=(0, 10), samples=150)

    @classmethod
    def for_rocket(cls) -> "DiscretizeConfig":
        return cls(bounds=(0, 1), samples=100)

    @classmethod
    def for_flight(cls) -> "DiscretizeConfig":
        return cls(bounds=(0, 30), samples=200)


class InfinityEncoder(RocketPyEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def default(self, obj):
        if (
            isinstance(obj, Function)
            and not callable(obj.source)
            and obj.__dom_dim__ == 1
        ):
            size = len(obj._domain)
            reduction_factor = 1
            if size > 25:
                reduction_factor = size // 25
            if reduction_factor > 1:
                obj = obj.set_discrete(
                    obj.x_array[0],
                    obj.x_array[-1],
                    size // reduction_factor,
                    mutate_self=False,
                )
        if isinstance(obj, Flight):
            obj._Flight__evaluate_post_process
            solution = np.array(obj.solution)
            size = len(solution)
            if size > 25:
                reduction_factor = size // 25
                reduced_solution = np.zeros(
                    (size // reduction_factor, solution.shape[1])
                )
                reduced_scale = np.linspace(
                    solution[0, 0], solution[-1, 0], size // reduction_factor
                )
                for i, col in enumerate(solution.T):
                    reduced_solution[:, i] = interp1d(
                        solution[:, 0], col, assume_sorted=True
                    )(reduced_scale)
                obj.solution = reduced_solution.tolist()

            obj.flight_phases = None
            obj.function_evaluations = None

        return super().default(obj)


def rocketpy_encoder(obj):
    """
    Encode a RocketPy object using official RocketPy encoders.

    Uses InfinityEncoder for serialization and reduction.
    """
    json_str = json.dumps(
        obj,
        cls=InfinityEncoder,
        include_outputs=True,
        include_function_data=True,
        discretize=True,
        allow_pickle=False,
    )
    encoded_result = json.loads(json_str)
    return _fix_datetime_fields(encoded_result)


def collect_attributes(obj, attribute_classes=None):
    """
    Collect attributes from various simulation classes and populate them from the flight object.
    """
    if attribute_classes is None:
        attribute_classes = []

    attributes = rocketpy_encoder(obj)

    for attribute_class in attribute_classes:
        if issubclass(attribute_class, FlightSimulation):
            flight_attributes_list = [
                attr
                for attr in attribute_class.__annotations__.keys()
                if attr not in ["message", "rocket", "env"]
            ]
            try:
                for key in flight_attributes_list:
                    if key not in attributes:
                        try:
                            value = getattr(obj, key)
                            attributes[key] = value
                        except Exception:
                            pass
            except Exception:
                pass

        elif issubclass(attribute_class, RocketSimulation):
            rocket_attributes_list = [
                attr
                for attr in attribute_class.__annotations__.keys()
                if attr not in ["message", "motor"]
            ]
            try:
                for key in rocket_attributes_list:
                    if key not in attributes.get("rocket", {}):
                        try:
                            value = getattr(obj.rocket, key)
                            attributes.setdefault("rocket", {})[key] = value
                        except Exception:
                            pass
            except Exception:
                pass

        elif issubclass(attribute_class, MotorSimulation):
            motor_attributes_list = [
                attr
                for attr in attribute_class.__annotations__.keys()
                if attr not in ["message"]
            ]
            try:
                for key in motor_attributes_list:
                    if key not in attributes.get("rocket", {}).get(
                        "motor", {}
                    ):
                        try:
                            value = getattr(obj.rocket.motor, key)
                            attributes.setdefault("rocket", {}).setdefault(
                                "motor", {}
                            )[key] = value
                        except Exception:
                            pass
            except Exception:
                pass

        elif issubclass(attribute_class, EnvironmentSimulation):
            environment_attributes_list = [
                attr
                for attr in attribute_class.__annotations__.keys()
                if attr not in ["message"]
            ]
            try:
                for key in environment_attributes_list:
                    if key not in attributes.get("env", {}):
                        try:
                            value = getattr(obj.env, key)
                            attributes.setdefault("env", {})[key] = value
                        except Exception:
                            pass
            except Exception:
                pass
        else:
            continue

    return rocketpy_encoder(attributes)


def _fix_datetime_fields(data):
    """
    Fix datetime fields that RocketPyEncoder converted to lists.
    """
    if isinstance(data, dict):
        fixed = {}
        for key, value in data.items():
            if (
                key in ["date", "local_date", "datetime_date"]
                and isinstance(value, list)
                and len(value) >= 3
            ):
                try:
                    year, month, day = value[0:3]
                    hour = value[3] if len(value) > 3 else 0
                    minute = value[4] if len(value) > 4 else 0
                    second = value[5] if len(value) > 5 else 0
                    microsecond = value[6] if len(value) > 6 else 0

                    fixed[key] = datetime(
                        year, month, day, hour, minute, second, microsecond
                    )
                except Exception:
                    fixed[key] = value
            else:
                fixed[key] = _fix_datetime_fields(value)
        return fixed
    if isinstance(data, (list, tuple)):
        return [_fix_datetime_fields(item) for item in data]
    return data


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
                value == b"application/octet-stream"
                for header, value in self.initial_message["headers"]
            ):
                await self.send(self.initial_message)
                await self.send(message)
            elif not more_body:
                self.gzip_file.write(body)
                self.gzip_file.close()
                body = self.gzip_buffer.getvalue()

                headers = MutableHeaders(raw=self.initial_message["headers"])
                headers["Content-Encoding"] = "gzip"
                headers["Content-Length"] = str(len(body))
                headers.add_vary_header("Accept-Encoding")
                message["body"] = body

                await self.send(self.initial_message)
                await self.send(message)
            else:
                headers = MutableHeaders(raw=self.initial_message["headers"])
                headers["Content-Encoding"] = "gzip"
                headers.add_vary_header("Accept-Encoding")
                del headers["Content-Length"]

                self.gzip_file.write(body)
                message["body"] = self.gzip_buffer.getvalue()
                self.gzip_buffer.seek(0)
                self.gzip_buffer.truncate()

                await self.send(self.initial_message)
                await self.send(message)

        elif message_type == "http.response.body":
            body = message.get("body", b"")
            more_body = message.get("more_body", False)

            self.gzip_file.write(body)
            if not more_body:
                self.gzip_file.close()

            message["body"] = self.gzip_buffer.getvalue()
            self.gzip_buffer.seek(0)
            self.gzip_buffer.truncate()

            await self.send(message)
        else:
            if not self.started:
                self.started = True
                await self.send(self.initial_message)
            await self.send(message)


async def unattached_send(message: Message) -> NoReturn:
    raise RuntimeError("send awaitable not set")

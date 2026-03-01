import json
from typing import Self, Tuple

import numpy as np

from rocketpy.simulation.flight import Flight as RocketPyFlight
from rocketpy._encoders import RocketPyEncoder, RocketPyDecoder
from rocketpy.mathutils.function import Function
from rocketpy.motors.solid_motor import SolidMotor
from rocketpy.motors.liquid_motor import LiquidMotor
from rocketpy.motors.hybrid_motor import HybridMotor
from rocketpy import (
    LevelBasedTank,
    MassBasedTank,
    UllageBasedTank,
)
from rocketpy.rocket.aero_surface import (
    NoseCone as RocketPyNoseCone,
    TrapezoidalFins as RocketPyTrapezoidalFins,
    EllipticalFins as RocketPyEllipticalFins,
    Tail as RocketPyTail,
)

from src.services.environment import EnvironmentService
from src.services.rocket import RocketService
from src.models.environment import EnvironmentModel
from src.models.motor import MotorModel, MotorKinds
from src.models.rocket import RocketModel
from src.models.flight import FlightModel
from src.models.sub.aerosurfaces import (
    NoseCone,
    Fins,
    Tail,
    Parachute,
)
from src.models.sub.tanks import MotorTank, TankFluids, TankKinds
from src.views.flight import FlightSimulation
from src.views.rocket import RocketSimulation
from src.views.motor import MotorSimulation
from src.views.environment import EnvironmentSimulation
from src.utils import collect_attributes


class FlightService:
    _flight: RocketPyFlight

    def __init__(self, flight: RocketPyFlight = None):
        self._flight = flight

    @classmethod
    def from_flight_model(cls, flight: FlightModel) -> Self:
        """
        Get the rocketpy flight object.

        Returns:
            FlightService containing the rocketpy flight object.
        """
        rocketpy_env = EnvironmentService.from_env_model(
            flight.environment
        ).environment
        rocketpy_rocket = RocketService.from_rocket_model(flight.rocket).rocket
        rocketpy_flight = RocketPyFlight(
            rocket=rocketpy_rocket,
            environment=rocketpy_env,
            rail_length=flight.rail_length,
            terminate_on_apogee=flight.terminate_on_apogee,
            time_overshoot=flight.time_overshoot,
            equations_of_motion=flight.equations_of_motion,
            **flight.get_additional_parameters(),
        )
        return cls(flight=rocketpy_flight)

    @classmethod
    def from_rpy(cls, content: bytes) -> Self:
        """
        Deserialize a JSON-based ``.rpy`` file into a FlightService.

        The ``.rpy`` format is RocketPy's native portable
        serialization (plain JSON via ``RocketPyEncoder`` /
        ``RocketPyDecoder``).  It is architecture-, OS-, and
        Python-version-agnostic.

        Args:
            content: raw bytes of a ``.rpy`` JSON file.

        Returns:
            FlightService wrapping the deserialized flight.

        Raises:
            ValueError: If the payload is not valid ``.rpy`` JSON
                        or does not contain a Flight.
        """
        data = json.loads(content)
        simulation = data.get("simulation", data)
        flight = json.loads(
            json.dumps(simulation),
            cls=RocketPyDecoder,
            resimulate=False,
        )
        if not isinstance(flight, RocketPyFlight):
            raise ValueError("File does not contain a RocketPy Flight object")
        return cls(flight=flight)

    @property
    def flight(self) -> RocketPyFlight:
        return self._flight

    @flight.setter
    def flight(self, flight: RocketPyFlight):
        self._flight = flight

    def extract_models(
        self,
    ) -> Tuple[EnvironmentModel, MotorModel, RocketModel, FlightModel]:
        """
        Decompose a live RocketPy Flight into the API model
        hierarchy: Environment, Motor, Rocket, Flight.

        Returns:
            (EnvironmentModel, MotorModel, RocketModel, FlightModel)
        """
        env_model = self._extract_environment(self.flight.env)
        motor_model = self._extract_motor(self.flight.rocket.motor)
        rocket_model = self._extract_rocket(self.flight.rocket, motor_model)
        flight_model = self._extract_flight(
            self.flight, env_model, rocket_model
        )
        return env_model, motor_model, rocket_model, flight_model

    # ------------------------------------------------------------------
    # Private extraction helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_environment(env) -> EnvironmentModel:
        return EnvironmentModel(
            latitude=env.latitude,
            longitude=env.longitude,
            elevation=env.elevation,
            atmospheric_model_type=env.atmospheric_model_type,
            date=env.date,
        )

    @staticmethod
    def _extract_motor(motor) -> MotorModel:
        match motor:
            case SolidMotor():
                kind = MotorKinds.SOLID
            case HybridMotor():
                kind = MotorKinds.HYBRID
            case LiquidMotor():
                kind = MotorKinds.LIQUID
            case _:
                kind = MotorKinds.GENERIC

        thrust = motor.thrust_source
        match thrust:
            case np.ndarray():
                thrust = thrust.tolist()

        data = {
            "thrust_source": thrust,
            "burn_time": motor.burn_duration,
            "nozzle_radius": motor.nozzle_radius,
            "dry_mass": motor.dry_mass,
            "dry_inertia": (
                motor.dry_I_11,
                motor.dry_I_22,
                motor.dry_I_33,
            ),
            "center_of_dry_mass_position": (motor.center_of_dry_mass_position),
            "motor_kind": kind,
            "interpolation_method": motor.interpolate,
            "coordinate_system_orientation": (
                motor.coordinate_system_orientation
            ),
        }

        grain_fields = {
            "grain_number": motor.grain_number,
            "grain_density": motor.grain_density,
            "grain_outer_radius": motor.grain_outer_radius,
            "grain_initial_inner_radius": (motor.grain_initial_inner_radius),
            "grain_initial_height": motor.grain_initial_height,
            "grain_separation": motor.grain_separation,
            "grains_center_of_mass_position": (
                motor.grains_center_of_mass_position
            ),
            "throat_radius": motor.throat_radius,
        }

        match kind:
            case MotorKinds.SOLID:
                data |= grain_fields
            case MotorKinds.HYBRID:
                data |= grain_fields
                data["tanks"] = FlightService._extract_tanks(motor)
            case MotorKinds.LIQUID:
                data["tanks"] = FlightService._extract_tanks(motor)
            case MotorKinds.GENERIC:
                data |= {
                    "chamber_radius": getattr(motor, "chamber_radius", None),
                    "chamber_height": getattr(motor, "chamber_height", None),
                    "chamber_position": getattr(
                        motor, "chamber_position", None
                    ),
                    "propellant_initial_mass": getattr(
                        motor,
                        "propellant_initial_mass",
                        None,
                    ),
                    "nozzle_position": getattr(motor, "nozzle_position", None),
                }

        return MotorModel(**data)

    @staticmethod
    def _to_float(value) -> float:
        """Extract a plain float from a RocketPy Function or scalar."""
        match value:
            case Function():
                return float(value(0))
            case _:
                return float(value)

    @staticmethod
    def _extract_tanks(motor) -> list[MotorTank]:
        tanks: list[MotorTank] = []
        for entry in motor.positioned_tanks:
            tank, position = entry["tank"], entry["position"]

            match tank:
                case LevelBasedTank():
                    tank_kind = TankKinds.LEVEL
                case MassBasedTank():
                    tank_kind = TankKinds.MASS
                case UllageBasedTank():
                    tank_kind = TankKinds.ULLAGE
                case _:
                    tank_kind = TankKinds.MASS_FLOW

            geometry = [
                (bounds, float(func(0)))
                for bounds, func in tank.geometry.geometry.items()
            ]

            data: dict = {
                "geometry": geometry,
                "gas": TankFluids(
                    name=tank.gas.name,
                    density=tank.gas.density,
                ),
                "liquid": TankFluids(
                    name=tank.liquid.name,
                    density=tank.liquid.density,
                ),
                "flux_time": tank.flux_time,
                "position": position,
                "discretize": tank.discretize,
                "tank_kind": tank_kind,
                "name": tank.name,
            }

            _f = FlightService._to_float
            match tank_kind:
                case TankKinds.LEVEL:
                    data["liquid_height"] = _f(tank.liquid_height)
                case TankKinds.MASS:
                    data["liquid_mass"] = _f(tank.liquid_mass)
                    data["gas_mass"] = _f(tank.gas_mass)
                case TankKinds.MASS_FLOW:
                    data |= {
                        "gas_mass_flow_rate_in": _f(
                            tank.gas_mass_flow_rate_in
                        ),
                        "gas_mass_flow_rate_out": _f(
                            tank.gas_mass_flow_rate_out
                        ),
                        "liquid_mass_flow_rate_in": _f(
                            tank.liquid_mass_flow_rate_in
                        ),
                        "liquid_mass_flow_rate_out": _f(
                            tank.liquid_mass_flow_rate_out
                        ),
                        "initial_liquid_mass": (tank.initial_liquid_mass),
                        "initial_gas_mass": (tank.initial_gas_mass),
                    }
                case TankKinds.ULLAGE:
                    data["ullage"] = _f(tank.ullage)

            tanks.append(MotorTank(**data))
        return tanks

    @staticmethod
    def _drag_to_list(fn) -> list:
        match getattr(fn, "source", None):
            case np.ndarray() as arr:
                return arr.tolist()
            case _:
                return [(0, 0)]

    @staticmethod
    def _extract_rocket(rocket, motor_model: MotorModel) -> RocketModel:
        nose = None
        fins_list: list[Fins] = []
        tail = None

        for surface, position in rocket.aerodynamic_surfaces:
            match position:
                case (_, _, z):
                    pos_z = z
                case [_, _, z]:
                    pos_z = z
                case _:
                    pos_z = position

            match surface:
                case RocketPyNoseCone():
                    nose = NoseCone(
                        name=surface.name,
                        length=surface.length,
                        kind=surface.kind,
                        position=pos_z,
                        base_radius=surface.base_radius,
                        rocket_radius=surface.rocket_radius,
                    )
                case RocketPyTrapezoidalFins():
                    fins_list.append(
                        Fins(
                            fins_kind="trapezoidal",
                            name=surface.name,
                            n=surface.n,
                            root_chord=surface.root_chord,
                            span=surface.span,
                            position=pos_z,
                            tip_chord=getattr(surface, "tip_chord", None),
                            cant_angle=getattr(surface, "cant_angle", None),
                            rocket_radius=surface.rocket_radius,
                        )
                    )
                case RocketPyEllipticalFins():
                    fins_list.append(
                        Fins(
                            fins_kind="elliptical",
                            name=surface.name,
                            n=surface.n,
                            root_chord=surface.root_chord,
                            span=surface.span,
                            position=pos_z,
                            rocket_radius=surface.rocket_radius,
                        )
                    )
                case RocketPyTail():
                    tail = Tail(
                        name=surface.name,
                        top_radius=surface.top_radius,
                        bottom_radius=surface.bottom_radius,
                        length=surface.length,
                        position=pos_z,
                        radius=surface.rocket_radius,
                    )

        parachutes = (
            [
                Parachute(
                    name=p.name,
                    cd_s=p.cd_s,
                    trigger=p.trigger,
                    sampling_rate=p.sampling_rate,
                    lag=p.lag,
                    noise=p.noise,
                )
                for p in rocket.parachutes
            ]
            if rocket.parachutes
            else None
        )

        inertia = (
            rocket.I_11_without_motor,
            rocket.I_22_without_motor,
            rocket.I_33_without_motor,
        )

        # Schema requires at least one Fins entry; n=0 means
        # no physical fins (safe for downstream aero calculations).
        default_fins = [
            Fins(
                fins_kind="trapezoidal",
                name="default",
                n=0,
                root_chord=0,
                span=0,
                position=0,
            )
        ]

        return RocketModel(
            motor=motor_model,
            radius=rocket.radius,
            mass=rocket.mass,
            motor_position=rocket.motor_position,
            center_of_mass_without_motor=(rocket.center_of_mass_without_motor),
            inertia=inertia,
            power_off_drag=FlightService._drag_to_list(rocket.power_off_drag),
            power_on_drag=FlightService._drag_to_list(rocket.power_on_drag),
            coordinate_system_orientation=(
                rocket.coordinate_system_orientation
            ),
            nose=nose,
            fins=fins_list or default_fins,
            tail=tail,
            parachutes=parachutes,
        )

    @staticmethod
    def _extract_flight(
        flight,
        env: EnvironmentModel,
        rocket: RocketModel,
    ) -> FlightModel:
        match getattr(flight, "equations_of_motion", "standard"):
            case str() as eom:
                pass
            case _:
                eom = "standard"

        optional = {
            attr: val
            for attr in (
                "max_time",
                "max_time_step",
                "min_time_step",
                "rtol",
                "atol",
            )
            if (val := getattr(flight, attr, None)) is not None
        }

        return FlightModel(
            environment=env,
            rocket=rocket,
            rail_length=flight.rail_length,
            time_overshoot=flight.time_overshoot,
            terminate_on_apogee=flight.terminate_on_apogee,
            equations_of_motion=eom,
            inclination=flight.inclination,
            heading=flight.heading,
            **optional,
        )

    # ------------------------------------------------------------------
    # Simulation & export
    # ------------------------------------------------------------------

    def get_flight_simulation(self) -> FlightSimulation:
        """
        Get the simulation of the flight.

        Returns:
            FlightSimulation
        """
        encoded_attributes = collect_attributes(
            self.flight,
            [
                FlightSimulation,
                RocketSimulation,
                MotorSimulation,
                EnvironmentSimulation,
            ],
        )
        flight_simulation = FlightSimulation(**encoded_attributes)
        return flight_simulation

    def get_flight_rpy(self) -> bytes:
        """
        Get the portable JSON ``.rpy`` representation of the flight.

        Returns:
            bytes (UTF-8 encoded JSON)
        """
        return json.dumps(
            {"simulation": self.flight},
            cls=RocketPyEncoder,
            indent=2,
            include_outputs=False,
        ).encode()

    @staticmethod
    def generate_notebook(flight_id: str) -> dict:
        """
        Generate a Jupyter notebook dict for a given flight.

        The notebook loads the flight's ``.rpy`` file and calls
        ``flight.all_info()``, giving power users a quick
        playground.

        Args:
            flight_id: Persisted flight identifier.

        Returns:
            dict representing a valid .ipynb (nbformat 4).
        """
        rpy_filename = f"rocketpy_flight_{flight_id}.rpy"
        cells = [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# RocketPy Flight Analysis\n",
                    "\n",
                    "This notebook was auto-generated by "
                    "**Infinity API**.\n",
                    "\n",
                    "It loads a serialised RocketPy `Flight` "
                    "object so you can inspect and extend the "
                    "analysis interactively.",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "from rocketpy.utilities import load_from_rpy\n",
                    "import matplotlib\n",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "flight = load_from_rpy("
                    f'"{rpy_filename}", '
                    "resimulate=False)\n",
                    "\n",
                    "flight.all_info()",
                ],
            },
        ]
        notebook = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3",
                },
                "language_info": {
                    "name": "python",
                    "version": "3.12.0",
                },
            },
            "cells": cells,
        }
        return notebook

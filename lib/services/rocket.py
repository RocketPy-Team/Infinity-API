from typing import Self, List

import dill

from rocketpy.rocket.rocket import Rocket as RocketPyRocket
from rocketpy.rocket.parachute import Parachute as RocketPyParachute
from rocketpy.rocket.aero_surface import (
    TrapezoidalFins as RocketPyTrapezoidalFins,
    EllipticalFins as RocketPyEllipticalFins,
    NoseCone as RocketPyNoseCone,
    Fins as RocketPyFins,
    Tail as RocketPyTail,
)
from rocketpy.utilities import get_instance_attributes

from lib import logger
from lib.models.rocket import Rocket, Parachute
from lib.models.aerosurfaces import NoseCone, Tail, Fins
from lib.services.motor import MotorService
from lib.views.rocket import RocketSummary


class RocketService:
    _rocket: RocketPyRocket

    def __init__(self, rocket: RocketPyRocket = None):
        self._rocket = rocket

    @classmethod
    def from_rocket_model(cls, rocket: Rocket) -> Self:
        """
        Get the rocketpy rocket object.

        Returns:
            RocketService containing the rocketpy rocket object.
        """

        # Core
        rocketpy_rocket = RocketPyRocket(
            radius=rocket.radius,
            mass=rocket.mass,
            inertia=rocket.inertia,
            power_off_drag=rocket.power_off_drag,
            power_on_drag=rocket.power_on_drag,
            center_of_mass_without_motor=rocket.center_of_mass_without_motor,
            coordinate_system_orientation=rocket.coordinate_system_orientation.value.lower(),
        )

        # RailButtons
        rocketpy_rocket.set_rail_buttons(
            upper_button_position=rocket.rail_buttons.upper_button_position,
            lower_button_position=rocket.rail_buttons.lower_button_position,
            angular_position=rocket.rail_buttons.angular_position,
        )
        rocketpy_rocket.add_motor(
            MotorService.from_motor_model(rocket.motor).motor,
            rocket.motor_position,
        )

        # NoseCone
        nose = cls.get_rocketpy_nose(rocket.nose)
        rocketpy_rocket.aerodynamic_surfaces.add(nose, nose.position)
        rocketpy_rocket.evaluate_static_margin()

        # FinSet
        rocketpy_finset_list = cls.get_rocketpy_finset_list_from_fins_list(
            rocket.fins
        )
        for finset in rocketpy_finset_list:
            rocketpy_rocket.aerodynamic_surfaces.add(finset, finset.position)
        rocketpy_rocket.evaluate_static_margin()

        # Tail
        tail = cls.get_rocketpy_tail(rocket.tail)
        rocketpy_rocket.aerodynamic_surfaces.add(tail, tail.position)
        rocketpy_rocket.evaluate_static_margin()

        # Air Brakes

        # Parachutes
        for parachute in rocket.parachutes:
            if cls.check_parachute_trigger(parachute.trigger):
                rocketpy_parachute = cls.get_rocketpy_parachute(parachute)
                rocketpy_rocket.parachutes.append(rocketpy_parachute)
            else:
                logger.warning(
                    "Parachute trigger not valid. Skipping parachute."
                )
                continue

        return cls(rocket=rocketpy_rocket)

    @property
    def rocket(self) -> RocketPyRocket:
        return self._rocket

    @rocket.setter
    def rocket(self, rocket: RocketPyRocket):
        self._rocket = rocket

    def get_rocket_summary(self) -> RocketSummary:
        """
        Get the summary of the rocket.

        Returns:
            RocketSummary
        """
        attributes = get_instance_attributes(self.rocket)
        rocket_summary = RocketSummary(**attributes)
        return rocket_summary

    def get_rocket_binary(self) -> bytes:
        """
        Get the binary representation of the rocket.

        Returns:
            bytes
        """
        return dill.dumps(self.rocket)

    @staticmethod
    def get_rocketpy_nose(nose: NoseCone) -> RocketPyNoseCone:
        """
        Get a rocketpy nose cone object.

        Returns:
            RocketPyNoseCone
        """

        rocketpy_nose = RocketPyNoseCone(
            name=nose.name,
            length=nose.length,
            kind=nose.kind,
            base_radius=nose.base_radius,
            rocket_radius=nose.rocket_radius,
        )
        rocketpy_nose.position = nose.position
        return rocketpy_nose

    @classmethod
    def get_rocketpy_finset_list_from_fins_list(
        cls, fins_list: List[Fins]
    ) -> List[RocketPyFins]:
        return [
            cls.get_rocketpy_finset(fins, fins.fins_kind) for fins in fins_list
        ]

    @staticmethod
    def get_rocketpy_finset(fins: Fins, kind: str) -> RocketPyFins:
        """
        Get a rocketpy finset object.

        Returns one of:
            RocketPyTrapezoidalFins
            RocketPyEllipticalFins
        """
        match kind:
            case "TRAPEZOIDAL":
                rocketpy_finset = RocketPyTrapezoidalFins(
                    n=fins.n,
                    name=fins.name,
                    root_chord=fins.root_chord,
                    tip_chord=fins.tip_chord,
                    span=fins.span,
                    cant_angle=fins.cant_angle,
                    rocket_radius=fins.radius,
                    airfoil=fins.airfoil,
                )
            case "ELLIPTICAL":
                rocketpy_finset = RocketPyEllipticalFins(
                    n=fins.n,
                    name=fins.name,
                    root_chord=fins.root_chord,
                    span=fins.span,
                    cant_angle=fins.cant_angle,
                    rocket_radius=fins.radius,
                    airfoil=fins.airfoil,
                )
            case _:
                raise ValueError(f"Invalid fins kind: {kind}")
        rocketpy_finset.position = fins.position
        return rocketpy_finset

    @staticmethod
    def get_rocketpy_tail(tail: Tail) -> RocketPyTail:
        """
        Get a rocketpy tail object.

        Returns:
            RocketPyTail
        """
        rocketpy_tail = RocketPyTail(
            name=tail.name,
            top_radius=tail.top_radius,
            bottom_radius=tail.bottom_radius,
            length=tail.length,
            rocket_radius=tail.radius,
        )
        rocketpy_tail.position = tail.position
        return rocketpy_tail

    @staticmethod
    def get_rocketpy_parachute(parachute: Parachute) -> RocketPyParachute:
        """
        Get a rocketpy parachute object.

        Returns:
            RocketPyParachute
        """
        rocketpy_parachute = RocketPyParachute(
            name=parachute.name,
            cd_s=parachute.cd_s,
            trigger=parachute.trigger,
            sampling_rate=parachute.sampling_rate,
            lag=parachute.lag,
            noise=parachute.noise,
        )
        return rocketpy_parachute

    @staticmethod
    def check_parachute_trigger(trigger) -> bool:
        """
        Check if the trigger expression is valid.

        Args:
            trigger: str | float

        Returns:
            bool: True if the expression is valid, False otherwise.
        """

        if trigger == "apogee":
            return True
        if isinstance(trigger, (int, float)):
            return True
        return False

import ast
from typing import Self

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
            power_off_drag=(
                rocket.power_off_drag if rocket.power_off_drag else None
            ),
            power_on_drag=(
                rocket.power_on_drag if rocket.power_on_drag else None
            ),
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
        finset = cls.get_rocketpy_finset(rocket.fins, rocket.fins.fins_kind)
        rocketpy_rocket.aerodynamic_surfaces.add(finset, finset.position)
        rocketpy_rocket.evaluate_static_margin()

        # Tail
        tail = cls.get_rocketpy_tail(rocket.tail)
        rocketpy_rocket.aerodynamic_surfaces.add(tail, tail.position)
        rocketpy_rocket.evaluate_static_margin()

        # Air Brakes

        # Parachutes
        for parachute in rocket.parachutes:
            if cls.check_parachute_trigger(
                trigger_expression := parachute.trigger
            ):
                parachute.trigger = eval(  # pylint: disable=eval-used
                    trigger_expression, {"__builtins__": None}, {}
                )
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
    def check_parachute_trigger(expression: str) -> bool:
        """
        Check if the trigger expression is valid.

        Args:
            expression: str

        Returns:
            bool: True if the expression is valid, False otherwise.
        """

        class InvalidParachuteTrigger(Exception):
            pass

        # Parsing the expression into an AST
        try:
            parsed_expression = ast.parse(expression, mode="eval")
        except SyntaxError as e:
            raise InvalidParachuteTrigger(
                f"Invalid expression syntax: {str(e)}"
            ) from None

        # Constant case (supported after beta v1)
        if isinstance(parsed_expression.body, ast.Constant):
            return True
        # Name case (supported after beta v1)
        if (
            isinstance(parsed_expression.body, ast.Name)
            and parsed_expression.body.id == "apogee"
        ):
            return True

        # Validating the expression structure
        if not isinstance(parsed_expression.body, ast.Lambda):
            raise InvalidParachuteTrigger(
                "Invalid expression structure: not a lambda."
            ) from None

        lambda_node = parsed_expression.body
        if len(lambda_node.args.args) != 3:
            raise InvalidParachuteTrigger(
                "Invalid expression structure: lambda should have 3 arguments."
            ) from None

        if not isinstance(lambda_node.body, ast.Compare):
            try:
                for operand in lambda_node.body.values:
                    if not isinstance(operand, ast.Compare):
                        raise InvalidParachuteTrigger(
                            "Invalid expression structure: not a Compare."
                        ) from None
            except AttributeError:
                raise InvalidParachuteTrigger(
                    "Invalid expression structure: not a Compare."
                ) from None

        # Restricting access to functions or attributes
        for node in ast.walk(lambda_node):
            if isinstance(node, ast.Call):
                raise InvalidParachuteTrigger(
                    "Calling functions is not allowed in the expression."
                ) from None
            if isinstance(node, ast.Attribute):
                raise InvalidParachuteTrigger(
                    "Accessing attributes is not allowed in the expression."
                ) from None
        return True

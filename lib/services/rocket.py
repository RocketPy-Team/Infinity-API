import ast
from typing import Self
from rocketpy.rocket.rocket import Rocket as RocketPyRocket
from rocketpy.rocket.parachute import Parachute as RocketPyParachute
from rocketpy.rocket.aero_surface import NoseCone as RocketPyNoseCone
from rocketpy.rocket.aero_surface import (
    TrapezoidalFins as RocketPyTrapezoidalFins,
)
from rocketpy.rocket.aero_surface import Tail as RocketPyTail
from rocketpy.utilities import get_instance_attributes

from lib.models.rocket import Rocket
from lib.models.aerosurfaces import NoseCone, TrapezoidalFins, Tail
from lib.models.parachute import Parachute
from lib.services.motor import MotorService
from lib.views.rocket import RocketSummary


class RocketService(RocketPyRocket):

    @classmethod
    def from_rocket_model(cls, rocket: Rocket) -> Self:
        """
        Get the rocketpy rocket object.

        Returns:
            RocketPyRocket
        """

        rocketpy_rocket = RocketPyRocket(
            radius=rocket.radius,
            mass=rocket.mass,
            inertia=rocket.inertia,
            power_off_drag=rocket.power_off_drag,
            power_on_drag=rocket.power_on_drag,
            center_of_mass_without_motor=rocket.center_of_mass_without_motor,
            coordinate_system_orientation=rocket.coordinate_system_orientation,
        )

        # RailButtons
        rocketpy_rocket.set_rail_buttons(
            upper_button_position=rocket.rail_buttons.upper_button_position,
            lower_button_position=rocket.rail_buttons.lower_button_position,
            angular_position=rocket.rail_buttons.angular_position,
        )
        rocketpy_rocket.add_motor(
            MotorService.from_motor_model(rocket.motor),
            rocket.motor_position,
        )

        # NoseCone
        nose = cls.get_rocketpy_nose(rocket.nose)
        rocketpy_rocket.aerodynamic_surfaces.add(nose, nose.position)
        rocketpy_rocket.evaluate_static_margin()

        # FinSet
        # TODO: re-write this to match overall fins not only TrapezoidalFins
        # Maybe a strategy with different factory methods?
        finset = cls.get_rocketpy_finset(rocket.fins)
        rocketpy_rocket.aerodynamic_surfaces.add(finset, finset.position)
        rocketpy_rocket.evaluate_static_margin()

        # Tail
        tail = cls.get_rocketpy_tail(rocket.tail)
        rocketpy_rocket.aerodynamic_surfaces.add(tail, tail.position)
        rocketpy_rocket.evaluate_static_margin()

        # Parachutes
        for p, _ in enumerate(rocket.parachutes):
            parachute_trigger = rocket.parachutes[p].triggers[0]
            if cls.check_parachute_trigger(parachute_trigger):
                rocket.parachutes[p].triggers[0] = compile(
                    parachute_trigger, "<string>", "eval"
                )
                parachute = cls.get_rocketpy_parachute(rocket.parachutes, p)
                rocketpy_rocket.parachutes.append(parachute)
            else:
                print("Parachute trigger not valid. Skipping parachute.")
                continue

        return rocketpy_rocket

    def get_rocket_summary(self) -> RocketSummary:
        """
        Get the summary of the rocket.

        Returns:
            RocketSummary
        """
        attributes = get_instance_attributes(self)
        rocket_summary = RocketSummary(**attributes)
        return rocket_summary

    @staticmethod
    def get_rocketpy_nose(nose: NoseCone) -> RocketPyNoseCone:
        """
        Get a rocketpy nose cone object.

        Returns:
            RocketPyNoseCone
        """

        rocketpy_nose = RocketPyNoseCone(
            length=nose.length,
            kind=nose.kind,
            base_radius=nose.base_radius,
            rocket_radius=nose.rocket_radius,
        )
        rocketpy_nose.position = nose.position
        return rocketpy_nose

    @staticmethod
    def get_rocketpy_finset(
        trapezoidal_fins: TrapezoidalFins,
    ) -> RocketPyTrapezoidalFins:
        """
        Get a rocketpy finset object.

        Returns:
            RocketPyTrapezoidalFins
        """
        rocketpy_finset = RocketPyTrapezoidalFins(
            n=trapezoidal_fins.n,
            root_chord=trapezoidal_fins.root_chord,
            tip_chord=trapezoidal_fins.tip_chord,
            span=trapezoidal_fins.span,
            cant_angle=trapezoidal_fins.cant_angle,
            rocket_radius=trapezoidal_fins.radius,
            airfoil=trapezoidal_fins.airfoil,
        )
        rocketpy_finset.position = trapezoidal_fins.position
        return rocketpy_finset

    @staticmethod
    def get_rocketpy_tail(tail: Tail) -> RocketPyTail:
        """
        Get a rocketpy tail object.

        Returns:
            RocketPyTail
        """
        rocketpy_tail = RocketPyTail(
            top_radius=tail.top_radius,
            bottom_radius=tail.bottom_radius,
            length=tail.length,
            rocket_radius=tail.radius,
        )
        rocketpy_tail.position = tail.position
        return rocketpy_tail

    @staticmethod
    def get_rocketpy_parachute(
        parachute: Parachute, p: int
    ) -> RocketPyParachute:
        """
        Get a rocketpy parachute object.

        Returns:
            RocketPyParachute
        """
        rocketpy_parachute = RocketPyParachute(
            name=parachute[p].name[0],
            cd_s=parachute[p].cd_s[0],
            trigger=eval(parachute[p].triggers[0]),
            sampling_rate=parachute[p].sampling_rate[0],
            lag=parachute[p].lag[0],
            noise=parachute[p].noise[0],
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

        # Parsing the expression into an AST
        try:
            parsed_expression = ast.parse(expression, mode="eval")
        except SyntaxError:
            print("Invalid syntax.")
            return False

        # Constant case (supported after beta v1)
        if isinstance(parsed_expression.body, ast.Constant):
            return True
        # Name case (supported after beta v1)
        if (
            isinstance(parsed_expression.body, ast.Name)
            and parsed_expression.body.id == "apogee"
        ):
            global apogee
            apogee = "apogee"
            return True

        # Validating the expression structure
        if not isinstance(parsed_expression.body, ast.Lambda):
            print("Invalid expression structure (not a Lambda).")
            return False

        lambda_node = parsed_expression.body
        if len(lambda_node.args.args) != 3:
            print("Invalid expression structure (invalid arity).")
            return False

        if not isinstance(lambda_node.body, ast.Compare):
            try:
                for operand in lambda_node.body.values:
                    if not isinstance(operand, ast.Compare):
                        print("Invalid expression structure (not a Compare).")
                        return False
            except AttributeError:
                print("Invalid expression structure (not a Compare).")
                return False

        # Restricting access to functions or attributes
        for node in ast.walk(lambda_node):
            if isinstance(node, ast.Call):
                print("Calling functions is not allowed in the expression.")
                return False
            if isinstance(node, ast.Attribute):
                print("Accessing attributes is not allowed in the expression.")
                return False
        return True

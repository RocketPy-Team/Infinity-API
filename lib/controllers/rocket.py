from typing import Union
import ast
import jsonpickle

from fastapi import HTTPException, status

# from inspect import getsourcelines

from rocketpy.rocket.parachute import Parachute as RocketpyParachute
from rocketpy.rocket.rocket import Rocket as RocketpyRocket
from rocketpy.rocket.aero_surface import NoseCone as RocketpyNoseCone
from rocketpy.rocket.aero_surface import TrapezoidalFins as RocketpyTrapezoidalFins
from rocketpy.rocket.aero_surface import Tail as RocketpyTail

from lib.controllers.motor import MotorController
from lib.models.rocket import Rocket, RocketOptions
from lib.models.motor import MotorKinds
from lib.models.aerosurfaces import NoseCone, TrapezoidalFins, Tail
from lib.models.parachute import Parachute
from lib.repositories.rocket import RocketRepository
from lib.views.rocket import (
    InertiaDetails,
    RocketGeometricalParameters,
    RocketAerodynamicsQuantities,
    ParachuteData,
    RocketData,
    RocketSummary,
    RocketCreated,
    RocketUpdated,
    RocketDeleted,
    RocketPickle,
)


class RocketController:
    """
    Controller for the Rocket model.

    Init Attributes:
        rocket (models.Rocket): Rocket model object.

    Enables:
       create a RocketpyRocket object from a Rocket model object.
    """

    def __init__(self, rocket: Rocket, rocket_option, motor_kind):
        rocketpy_rocket = RocketpyRocket(
            radius=rocket.radius,
            mass=rocket.mass,
            inertia=rocket.inertia,
            power_off_drag=f"lib/data/{rocket_option.value.lower()}/powerOffDragCurve.csv",
            power_on_drag=f"lib/data/{rocket_option.value.lower()}/powerOnDragCurve.csv",
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
            MotorController(rocket.motor, motor_kind).rocketpy_motor,
            rocket.motor_position,
        )

        # NoseCone
        nose = self.NoseConeController(rocket.nose).rocketpy_nose
        rocketpy_rocket.aerodynamic_surfaces.add(nose, nose.position)
        rocketpy_rocket.evaluate_static_margin()

        # FinSet
        # TODO: re-write this to match overall fins not only TrapezoidalFins
        finset = self.TrapezoidalFinsController(rocket.fins).rocketpy_finset
        rocketpy_rocket.aerodynamic_surfaces.add(finset, finset.position)
        rocketpy_rocket.evaluate_static_margin()

        # Tail
        tail = self.TailController(rocket.tail).rocketpy_tail
        rocketpy_rocket.aerodynamic_surfaces.add(tail, tail.position)
        rocketpy_rocket.evaluate_static_margin()

        # Parachutes
        for p in range(len(rocket.parachutes)):
            parachute_trigger = rocket.parachutes[p].triggers[0]
            if self.ParachuteController.check_trigger(parachute_trigger):
                rocket.parachutes[p].triggers[0] = compile(
                    parachute_trigger, "<string>", "eval"
                )
                parachute = self.ParachuteController(
                    rocket.parachutes, p
                ).rocketpy_parachute
                rocketpy_rocket.parachutes.append(parachute)
            else:
                print("Parachute trigger not valid. Skipping parachute.")
                continue

        self.rocket_option = rocket_option  # tracks rocket option state
        self.rocketpy_rocket = rocketpy_rocket
        self.rocket = rocket

    class NoseConeController:
        """
        Controller for the NoseCone model.

        Init Attributes:
            nose (models.NoseCone): NoseCone model object.

        Enables:
            - Create a rocketpy.AeroSurface.NoseCone object from a NoseCone model object.
        """

        def __init__(self, nose: NoseCone):
            rocketpy_nose = RocketpyNoseCone(
                length=nose.length,
                kind=nose.kind,
                base_radius=nose.base_radius,
                rocket_radius=nose.rocket_radius,
            )
            rocketpy_nose.position = nose.position
            self.rocketpy_nose = rocketpy_nose
            self.nose = nose

    class TrapezoidalFinsController:
        """
        Controller for the TrapezoidalFins model.

        Init Attributes:
            trapezoidal_fins (models.TrapezoidalFins): TrapezoidalFins model object.

        Enables:
            - Create a rocketpy.AeroSurface.TrapezoidalFins object from a TrapezoidalFins model object.
        """

        def __init__(self, trapezoidal_fins: TrapezoidalFins):
            rocketpy_finset = RocketpyTrapezoidalFins(
                n=trapezoidal_fins.n,
                root_chord=trapezoidal_fins.root_chord,
                tip_chord=trapezoidal_fins.tip_chord,
                span=trapezoidal_fins.span,
                cant_angle=trapezoidal_fins.cant_angle,
                rocket_radius=trapezoidal_fins.radius,
                airfoil=trapezoidal_fins.airfoil,
            )
            rocketpy_finset.position = trapezoidal_fins.position
            self.rocketpy_finset = rocketpy_finset
            self.trapezoidal_fins = trapezoidal_fins

    class TailController:
        """
        Controller for the Tail model.

        Init Attributes:
            tail (models.Tail): Tail model object.

        Enables:
            - Create a rocketpy.AeroSurface.Tail object from a Tail model object.
        """

        def __init__(self, tail: Tail):
            rocketpy_tail = RocketpyTail(
                top_radius=tail.top_radius,
                bottom_radius=tail.bottom_radius,
                length=tail.length,
                rocket_radius=tail.radius,
            )
            rocketpy_tail.position = tail.position
            self.rocketpy_tail = rocketpy_tail
            self.tail = tail

    class ParachuteController:
        """
        Controller for the Parachute model.

        Init Attributes:
            parachute (models.Parachute): Parachute model object.

        Enables:
            - Create a RocketpyParachute.Parachute object from a Parachute model object.
        """

        def __init__(self, parachute: Parachute, p: int):
            rocketpy_parachute = RocketpyParachute(
                name=parachute[p].name[0],
                cd_s=parachute[p].cd_s[0],
                trigger=eval(parachute[p].triggers[0]),
                sampling_rate=parachute[p].sampling_rate[0],
                lag=parachute[p].lag[0],
                noise=parachute[p].noise[0],
            )
            self.rocketpy_parachute = rocketpy_parachute
            self.parachute = parachute

        @staticmethod
        def check_trigger(expression: str) -> bool:
            """
            Check if the trigger expression is valid.

            Args:
                expression (str): Trigger expression.

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

    async def create_rocket(self) -> "Union[RocketCreated, HTTPException]":
        """
        Create a rocket in the database.

        Returns:
            RocketCreated: Rocket id.
        """
        rocket = RocketRepository(rocket=self.rocket)
        successfully_created_rocket = await rocket.create_rocket(
            rocket_option=self.rocket_option
        )
        if not successfully_created_rocket:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create rocket.",
            )

        return RocketCreated(rocket_id=str(rocket.rocket_id))

    @staticmethod
    async def get_rocket(rocket_id: int) -> "Union[Rocket, HTTPException]":
        """
        Get a rocket from the database.

        Args:
            rocket_id (int): Rocket id.

        Returns:
            rocket model object

        Raises:
            HTTP 404 Not Found: If the rocket is not found in the database.
        """
        successfully_read_rocket = await RocketRepository(
            rocket_id=rocket_id
        ).get_rocket()
        if not successfully_read_rocket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rocket not found."
            )

        return successfully_read_rocket

    @staticmethod
    async def get_rocketpy_rocket(
        rocket_id: int,
    ) -> "Union[RocketPickle, HTTPException]":
        """
        Get a rocketpy rocket object encoded as jsonpickle string from the database.

        Args:
            rocket_id (int): rocket id.

        Returns:
            str: jsonpickle string of the rocketpy rocket.

        Raises:
            HTTP 404 Not Found: If the rocket is not found in the database.
        """
        successfully_read_rocket = await RocketRepository(
            rocket_id=rocket_id
        ).get_rocket()
        if not successfully_read_rocket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rocket not found."
            )

        successfully_read_rocketpy_rocket = RocketController(
            rocket=successfully_read_rocket,
            rocket_option=RocketOptions(successfully_read_rocket._rocket_option),
            motor_kind=MotorKinds(successfully_read_rocket.motor._motor_kind),
        ).rocketpy_rocket

        return RocketPickle(
            jsonpickle_rocketpy_rocket=jsonpickle.encode(
                successfully_read_rocketpy_rocket
            )
        )

    async def update_rocket(
        self, rocket_id: int
    ) -> "Union[RocketUpdated, HTTPException]":
        """
        Update a rocket in the database.

        Args:
            rocket_id (int): rocket id.

        Returns:
            RocketUpdated: rocket id and message.

        Raises:
            HTTP 404 Not Found: If the rocket is not found in the database.
        """
        successfully_read_rocket = await RocketRepository(
            rocket_id=rocket_id
        ).get_rocket()
        if not successfully_read_rocket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rocket not found."
            )

        successfully_updated_rocket = await RocketRepository(
            rocket=self.rocket, rocket_id=rocket_id
        ).update_rocket(rocket_option=self.rocket_option)
        if not successfully_updated_rocket:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update rocket.",
            )

        return RocketUpdated(new_rocket_id=str(successfully_updated_rocket))

    @staticmethod
    async def delete_rocket(rocket_id: int) -> "Union[RocketDeleted, HTTPException]":
        """
        Delete a rocket from the database.

        Args:
            rocket_id (int): Rocket id.

        Returns:
            RocketDeleted: Rocket id and message.

        Raises:
            HTTP 404 Not Found: If the rocket is not found in the database.
        """
        successfully_read_rocket = await RocketRepository(
            rocket_id=rocket_id
        ).get_rocket()
        if not successfully_read_rocket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rocket not found."
            )

        successfully_deleted_rocket = await RocketRepository(
            rocket_id=rocket_id
        ).delete_rocket()
        if not successfully_deleted_rocket:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete rocket.",
            )

        return RocketDeleted(deleted_rocket_id=str(rocket_id))

    @staticmethod
    async def simulate(rocket_id: int) -> "Union[RocketSummary, HTTPException]":
        """
        Simulate a rocket rocket.

        Args:
            rocket_id (int): Rocket id.

        Returns:
            Rocket summary view.

        Raises:
            HTTP 404 Not Found: If the rocket does not exist in the database.
        """
        successfully_read_rocket = await RocketRepository(
            rocket_id=rocket_id
        ).get_rocket()
        if not successfully_read_rocket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rocket not found."
            )

        try:
            rocket = RocketController(
                rocket=successfully_read_rocket,
                rocket_option=RocketOptions(successfully_read_rocket._rocket_option),
                motor_kind=MotorKinds(successfully_read_rocket.motor._motor_kind),
            ).rocketpy_rocket

            _inertia_details = InertiaDetails(
                rocket_mass_without_propellant="Rocket Mass: {:.3f} kg (No Propellant)".format(
                    rocket.mass
                ),
                rocket_mass_with_propellant="Rocket Mass: {:.3f} kg (With Propellant)".format(
                    rocket.total_mass(0)
                ),
                rocket_inertia_with_motor_without_propellant=[
                    "Rocket Inertia (with motor, but without propellant) 11: {:.3f} kg*m2".format(
                        rocket.dry_I_11
                    ),
                    "Rocket Inertia (with motor, but without propellant) 22: {:.3f} kg*m2".format(
                        rocket.dry_I_22
                    ),
                    "Rocket Inertia (with motor, but without propellant) 33: {:.3f} kg*m2".format(
                        rocket.dry_I_33
                    ),
                    "Rocket Inertia (with motor, but without propellant) 12: {:.3f} kg*m2".format(
                        rocket.dry_I_12
                    ),
                    "Rocket Inertia (with motor, but without propellant) 13: {:.3f} kg*m2".format(
                        rocket.dry_I_13
                    ),
                    "Rocket Inertia (with motor, but without propellant) 23: {:.3f} kg*m2".format(
                        rocket.dry_I_23
                    ),
                ],
            )

            _rocket_geometrical_parameters = RocketGeometricalParameters(
                rocket_maximum_radius="Rocket Maximum Radius: "
                + str(rocket.radius)
                + " m",
                rocket_frontal_area="Rocket Frontal Area: "
                + "{:.6f}".format(rocket.area)
                + " m2",
                rocket_codm_nozzle_exit_distance="Rocket Center of Dry Mass - Nozzle Exit Distance: "
                + "{:.3f} m".format(
                    abs(rocket.center_of_dry_mass_position - rocket.motor_position)
                ),
                rocket_codm_center_of_propellant_mass="Rocket Center of Dry Mass - Center of Propellant Mass: "
                + "{:.3f} m".format(
                    abs(
                        rocket.center_of_propellant_position(0)
                        - rocket.center_of_dry_mass_position
                    )
                ),
                rocket_codm_loaded_center_of_mass="Rocket Center of Mass - Rocket Loaded Center of Mass: "
                + "{:.3f} m".format(
                    abs(rocket.center_of_mass(0) - rocket.center_of_dry_mass_position)
                ),
            )

            _aerodynamics_lift_coefficient_derivatives = {}
            for surface, _position in rocket.aerodynamic_surfaces:
                name = surface.name
                _aerodynamics_lift_coefficient_derivatives[name] = []
                _aerodynamics_lift_coefficient_derivatives[name].append(
                    name
                    + " Lift Coefficient Derivative: {:.3f}".format(surface.clalpha(0))
                    + "/rad"
                )

            _aerodynamics_center_of_pressure = {}
            for surface, _position in rocket.aerodynamic_surfaces:
                name = surface.name
                cpz = surface.cp[2]
                _aerodynamics_center_of_pressure[name] = []
                _aerodynamics_center_of_pressure[name].append(
                    name + " Center of Pressure to CM: {:.3f}".format(cpz) + " m"
                )

            _rocket_aerodynamics_quantities = RocketAerodynamicsQuantities(
                aerodynamics_lift_coefficient_derivatives=_aerodynamics_lift_coefficient_derivatives,
                aerodynamics_center_of_pressure=_aerodynamics_center_of_pressure,
                distance_cop_to_codm="Distance from Center of Pressure to Center of Dry Mass: "
                + "{:.3f}".format(rocket.center_of_mass(0) - rocket.cp_position)
                + " m",
                initial_static_margin="Initial Static Margin: "
                + "{:.3f}".format(rocket.static_margin(0))
                + " c",
                final_static_margin="Final Static Margin: "
                + "{:.3f}".format(rocket.static_margin(rocket.motor.burn_out_time))
                + " c",
            )

            _parachute_details = {}
            _parachute_ejection_signal_trigger = {}
            _parachute_ejection_system_refresh_rate = {}
            _parachute_lag = {}
            for chute in rocket.parachutes:
                _parachute_details[chute.name] = chute.__str__()

                if chute.trigger.__name__ == "<lambda>":
                    # line = getsourcelines(chute.trigger)[0][0]
                    # _parachute_ejection_signal_trigger[chute.name] = "Ejection signal trigger: " + line.split("lambda ")[1].split(",")[0].split("\n")[0]
                    pass

                else:
                    _parachute_ejection_signal_trigger[chute.name] = (
                        "Ejection signal trigger: " + chute.trigger.__name__
                    )
                    _parachute_ejection_system_refresh_rate[
                        chute.name
                    ] = "Ejection system refresh rate: {chute.sampling_rate:.3f} Hz"
                    _parachute_lag[
                        chute.name
                    ] = "Time between ejection signal is triggered and the parachute is fully opened: {chute.lag:.1f} s\n"

            _parachute_data = ParachuteData(
                parachute_details=_parachute_details,
                # parachute_ejection_signal_trigger = _parachute_ejection_signal_trigger,
                parachute_ejection_system_refresh_rate=_parachute_ejection_system_refresh_rate,
                parachute_lag=_parachute_lag,
            )

            _rocket_data = RocketData(
                inertia_details=_inertia_details,
                rocket_geometrical_parameters=_rocket_geometrical_parameters,
                rocket_aerodynamics_quantities=_rocket_aerodynamics_quantities,
                parachute_data=_parachute_data,
            )

            rocket_summary = RocketSummary(rocket_data=_rocket_data)
            return rocket_summary
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to simulate rocket: {e}",
            ) from e

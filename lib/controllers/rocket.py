from typing import Union
import ast
import jsonpickle

from fastapi import HTTPException, status

# TODO
# from inspect import getsourcelines

from rocketpy.rocket.parachute import Parachute as RocketPyParachute
from rocketpy.rocket.rocket import Rocket as RocketPyRocket
from rocketpy.rocket.aero_surface import NoseCone as RocketPyNoseCone
from rocketpy.rocket.aero_surface import (
    TrapezoidalFins as RocketPyTrapezoidalFins,
)
from rocketpy.rocket.aero_surface import Tail as RocketPyTail

from lib import logging, parse_error
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

logger = logging.getLogger(__name__)


class RocketController:
    """
    Controller for the Rocket model.

    Init Attributes:
        rocket: models.Rocket.

    Enables:
       - CRUD operations over models.Rocket on the database.
    """

    def __init__(self, rocket: Rocket, rocket_option, motor_kind):
        self._rocket = rocket
        self._rocket_option = rocket_option
        self._motor_kind = motor_kind

    @property
    def rocket(self) -> Rocket:
        return self._rocket

    @rocket.setter
    def rocket(self, rocket: Rocket):
        self._rocket = rocket

    @property
    def rocket_option(self) -> RocketOptions:
        return self._rocket_option

    @property
    def motor_kind(self) -> MotorKinds:
        return self._motor_kind

    @classmethod
    def get_rocketpy_rocket(cls, rocket: Rocket) -> RocketPyRocket:
        """
        Get a rocketpy rocket object.

        Returns:
            RocketPyRocket
        """

        rocketpy_rocket = RocketPyRocket(
            radius=rocket.radius,
            mass=rocket.mass,
            inertia=rocket.inertia,
            power_off_drag=f"lib/data/{rocket.rocket_option.value.lower()}/powerOffDragCurve.csv",
            power_on_drag=f"lib/data/{rocket.rocket_option.value.lower()}/powerOnDragCurve.csv",
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
            MotorController.get_rocketpy_motor(rocket.motor),
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
        for p in range(len(rocket.parachutes)):
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

    async def create_rocket(self) -> Union[RocketCreated, HTTPException]:
        """
        Create a rocket in the database.

        Returns:
            views.RocketCreated
        """
        try:
            created_rocket = await RocketRepository(
                rocket=self.rocket
            ).create_rocket(
                rocket_option=self.rocket_option, motor_kind=self.motor_kind
            )
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.rocket.create_rocket: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create rocket: {exc_str}",
            ) from e
        else:
            return RocketCreated(rocket_id=str(created_rocket.rocket_id))
        finally:
            logger.info(
                f"Call to controllers.rocket.create_rocket completed for Rocket {hash(self.rocket)}"
            )

    @staticmethod
    async def get_rocket_by_id(
        rocket_id: str,
    ) -> Union[Rocket, HTTPException]:
        """
        Get a rocket from the database.

        Args:
            rocket_id: str

        Returns:
            models.Rocket

        Raises:
            HTTP 404 Not Found: If the rocket is not found in the database.
        """
        try:
            read_rocket = await RocketRepository(
                rocket_id=rocket_id
            ).get_rocket()
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.rocket.get_rocket_by_id: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read rocket: {e}",
            ) from e
        else:
            if read_rocket:
                return read_rocket
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rocket not found",
            )
        finally:
            logger.info(
                f"Call to controllers.rocket.get_rocket_by_id completed for Rocket {rocket_id}"
            )

    @classmethod
    async def get_rocketpy_rocket_as_jsonpickle(
        cls, rocket_id: str
    ) -> Union[RocketPickle, HTTPException]:
        """
        Get a rocketpy.Rocket object as jsonpickle string.

        Args:
            rocket_id: str

        Returns:
            views.RocketPickle

        Raises:
            HTTP 404 Not Found: If the rocket is not found in the database.
        """
        try:
            read_rocket = await cls.get_rocket_by_id(rocket_id)
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(
                f"controllers.rocket.get_rocketpy_rocket_as_jsonpickle: {exc_str}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read rocket: {e}",
            ) from e
        else:
            rocketpy_rocket = cls.get_rocketpy_rocket(read_rocket)
            return RocketPickle(
                jsonpickle_rocketpy_rocket=jsonpickle.encode(rocketpy_rocket)
            )
        finally:
            logger.info(
                f"Call to controllers.rocket.get_rocketpy_rocket_as_jsonpickle completed for Rocket {rocket_id}"
            )

    async def update_rocket(
        self, rocket_id: str
    ) -> Union[RocketUpdated, HTTPException]:
        """
        Update a rocket in the database.

        Args:
            rocket_id: str

        Returns:
            views.RocketUpdated

        Raises:
            HTTP 404 Not Found: If the rocket is not found in the database.
        """
        try:
            await RocketController.get_rocket_by_id(rocket_id)
            updated_rocket = await RocketRepository(
                rocket=self.rocket, rocket_id=rocket_id
            ).update_rocket(rocket_option=self.rocket_option)
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.rocket.update_rocket: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update rocket: {e}",
            ) from e
        else:
            return RocketUpdated(new_rocket_id=str(updated_rocket.rocket_id))
        finally:
            logger.info(
                f"Call to controllers.rocket.update_rocket completed for Rocket {rocket_id}"
            )

    @staticmethod
    async def delete_rocket(
        rocket_id: str,
    ) -> Union[RocketDeleted, HTTPException]:
        """
        Delete a rocket from the database.

        Args:
            rocket_id: str

        Returns:
            views.RocketDeleted

        Raises:
            HTTP 404 Not Found: If the rocket is not found in the database.
        """
        try:
            await RocketRepository(rocket_id=rocket_id).delete_rocket()
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.rocket.delete_rocket: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete rocket: {e}",
            ) from e
        else:
            return RocketDeleted(deleted_rocket_id=str(rocket_id))
        finally:
            logger.info(
                f"Call to controllers.rocket.delete_rocket completed for Rocket {rocket_id}"
            )

    @classmethod
    async def simulate(
        cls,
        rocket_id: str,
    ) -> Union[RocketSummary, HTTPException]:
        """
        Simulate a rocket rocket.

        Args:
            rocket_id: str

        Returns:
            views.RocketSummary

        Raises:
            HTTP 404 Not Found: If the rocket does not exist in the database.
        """
        try:
            read_rocket = await cls.get_rocket_by_id(rocket_id)
            rocket = await cls.get_rocketpy_rocket(read_rocket)

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
                    abs(
                        rocket.center_of_dry_mass_position
                        - rocket.motor_position
                    )
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
                    abs(
                        rocket.center_of_mass(0)
                        - rocket.center_of_dry_mass_position
                    )
                ),
            )

            _aerodynamics_lift_coefficient_derivatives = {}
            for surface, _position in rocket.aerodynamic_surfaces:
                name = surface.name
                _aerodynamics_lift_coefficient_derivatives[name] = []
                _aerodynamics_lift_coefficient_derivatives[name].append(
                    name
                    + " Lift Coefficient Derivative: {:.3f}".format(
                        surface.clalpha(0)
                    )
                    + "/rad"
                )

            _aerodynamics_center_of_pressure = {}
            for surface, _position in rocket.aerodynamic_surfaces:
                name = surface.name
                cpz = surface.cp[2]
                _aerodynamics_center_of_pressure[name] = []
                _aerodynamics_center_of_pressure[name].append(
                    name
                    + " Center of Pressure to CM: {:.3f}".format(cpz)
                    + " m"
                )

            _rocket_aerodynamics_quantities = RocketAerodynamicsQuantities(
                aerodynamics_lift_coefficient_derivatives=_aerodynamics_lift_coefficient_derivatives,
                aerodynamics_center_of_pressure=_aerodynamics_center_of_pressure,
                distance_cop_to_codm="Distance from Center of Pressure to Center of Dry Mass: "
                + "{:.3f}".format(
                    rocket.center_of_mass(0) - rocket.cp_position
                )
                + " m",
                initial_static_margin="Initial Static Margin: "
                + "{:.3f}".format(rocket.static_margin(0))
                + " c",
                final_static_margin="Final Static Margin: "
                + "{:.3f}".format(
                    rocket.static_margin(rocket.motor.burn_out_time)
                )
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
                    _parachute_ejection_system_refresh_rate[chute.name] = (
                        "Ejection system refresh rate: {chute.sampling_rate:.3f} Hz"
                    )
                    _parachute_lag[chute.name] = (
                        "Time between ejection signal is triggered and the parachute is fully opened: {chute.lag:.1f} s\n"
                    )

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
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.rocket.simulate: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to simulate rocket: {e}",
            ) from e
        else:
            return rocket_summary
        finally:
            logger.info(
                f"Call to controllers.rocket.simulate completed for Rocket {rocket_id}"
            )

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

from typing import Union
from fastapi import HTTPException, status
from rocketpy.motors.solid_motor import SolidMotor
from rocketpy.motors.liquid_motor import LiquidMotor
from rocketpy.motors.hybrid_motor import HybridMotor
import jsonpickle

from lib import logger, parse_error
from lib.models.motor import Motor, MotorKinds
from lib.repositories.motor import MotorRepository
from lib.views.motor import (
    MotorSummary,
    MotorData,
    MotorCreated,
    MotorUpdated,
    MotorDeleted,
    MotorPickle,
)


class MotorController:
    """
    Controller for the motor model.

    Init Attributes:
        motor (models.Motor): Motor model object.

    Enables:
        - Create a rocketpy.Motor object from a Motor model object.
    """

    def __init__(self, *, motor: Motor, motor_kind: MotorKinds):
        self.guard(motor, motor_kind)
        self._motor = motor
        self._motor_kind = motor_kind

    @property
    def motor(self) -> Motor:
        return self._motor

    @motor.setter
    def motor(self, motor: Motor):
        self._motor = motor

    @property
    def motor_kind(self) -> MotorKinds:
        return self._motor_kind

    @staticmethod
    def get_rocketpy_motor(
        motor: Motor,
    ) -> Union[LiquidMotor, HybridMotor, SolidMotor]:
        """
        Get the rocketpy motor object.

        Returns:
            Union[LiquidMotor, HybridMotor, SolidMotor]
        """

        motor_core = {
            "thrust_source": f"lib/data/engines/{motor.thrust_source.value}.eng",
            "burn_time": motor.burn_time,
            "nozzle_radius": motor.nozzle_radius,
            "dry_mass": motor.dry_mass,
            "dry_inertia": motor.dry_inertia,
            "center_of_dry_mass_position": motor.center_of_dry_mass_position,
        }

        match motor.motor_kind:
            case MotorKinds.LIQUID:
                rocketpy_motor = LiquidMotor(**motor_core)
            case MotorKinds.HYBRID:
                rocketpy_motor = HybridMotor(
                    **motor_core,
                    throat_radius=motor.throat_radius,
                    grain_number=motor.grain_number,
                    grain_density=motor.grain_density,
                    grain_outer_radius=motor.grain_outer_radius,
                    grain_initial_inner_radius=motor.grain_initial_inner_radius,
                    grain_initial_height=motor.grain_initial_height,
                    grain_separation=motor.grain_separation,
                    grains_center_of_mass_position=motor.grains_center_of_mass_position,
                )
            case _:
                rocketpy_motor = SolidMotor(
                    **motor_core,
                    grain_number=motor.grain_number,
                    grain_density=motor.grain_density,
                    grain_outer_radius=motor.grain_outer_radius,
                    grain_initial_inner_radius=motor.grain_initial_inner_radius,
                    grain_initial_height=motor.grain_initial_height,
                    grains_center_of_mass_position=motor.grains_center_of_mass_position,
                    grain_separation=motor.grain_separation,
                    throat_radius=motor.throat_radius,
                    interpolation_method=motor.interpolation_method,
                )

        if motor.motor_kind != MotorKinds.SOLID:
            for tank in motor.tanks:
                rocketpy_motor.add_tank(tank.tank, tank.position)

        return rocketpy_motor

    def guard(self, motor: Motor, motor_kind):
        if motor_kind != MotorKinds.SOLID and motor.tanks is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Tanks must be provided for liquid and hybrid motors.",
            )

    async def create_motor(self) -> Union[MotorCreated, HTTPException]:
        """
        Create a models.Motor in the database.

        Returns:
            views.MotorCreated
        """
        try:
            async with MotorRepository() as motor_repo:
                motor_repo.fetch_motor(self.motor)
                await motor_repo.create_motor(motor_kind=self.motor_kind)
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.motor.create_motor: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create motor: {exc_str}",
            ) from e
        else:
            return MotorCreated(motor_id=self.motor.motor_id)
        finally:
            logger.info(
                f"Call to controllers.motor.create_motor completed for Motor {self.motor.motor_id}"
            )

    @staticmethod
    async def get_motor_by_id(motor_id: str) -> Union[Motor, HTTPException]:
        """
        Get a models.Motor from the database.

        Args:
            motor_id: str

        Returns:
            models.Motor

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database.
        """
        try:
            async with MotorRepository() as motor_repo:
                await motor_repo.get_motor_by_id(motor_id)
                read_motor = motor_repo.motor
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.motor.get_motor_by_id: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read motor: {exc_str}",
            ) from e
        else:
            if read_motor:
                return read_motor
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Motor not found",
            )
        finally:
            logger.info(
                f"Call to controllers.motor.get_motor_by_id completed for Motor {motor_id}"
            )

    @classmethod
    async def get_rocketpy_motor_as_jsonpickle(
        cls,
        motor_id: str,
    ) -> Union[MotorPickle, HTTPException]:
        """
        Get a rocketpy.Motor object as a jsonpickle string.

        Args:
            motor_id: str

        Returns:
            views.MotorPickle

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database.
        """
        try:
            read_motor = await cls.get_motor_by_id(motor_id)
            rocketpy_motor = cls.get_rocketpy_motor(read_motor)
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(
                f"controllers.motor.get_rocketpy_motor_as_jsonpickle: {exc_str}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read motor: {exc_str}",
            ) from e
        else:
            return MotorPickle(
                jsonpickle_rocketpy_motor=jsonpickle.encode(rocketpy_motor)
            )
        finally:
            logger.info(
                f"Call to controllers.motor.get_rocketpy_motor_as_jsonpickle completed for Motor {motor_id}"
            )

    async def update_motor_by_id(
        self, motor_id: str
    ) -> Union[MotorUpdated, HTTPException]:
        """
        Update a motor in the database.

        Args:
            motor_id: str

        Returns:
            views.MotorUpdated

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database.
        """
        try:
            async with MotorRepository() as motor_repo:
                motor_repo.fetch_motor(self.motor)
                await motor_repo.create_motor(motor_kind=self.motor_kind)
                await motor_repo.delete_motor_by_id(motor_id)
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.motor.update_motor: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update motor: {exc_str}",
            ) from e
        else:
            return MotorUpdated(new_motor_id=self.motor.motor_id)
        finally:
            logger.info(
                f"Call to controllers.motor.update_motor completed for Motor {motor_id}"
            )

    @staticmethod
    async def delete_motor_by_id(
        motor_id: str,
    ) -> Union[MotorDeleted, HTTPException]:
        """
        Delete a models.Motor from the database.

        Args:
            motor_id: str

        Returns:
            views.MotorDeleted

        Raises:
            HTTP 404 Not Found: If the motor is not found in the database.
        """
        try:
            async with MotorRepository() as motor_repo:
                await motor_repo.delete_motor_by_id(motor_id)
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.motor.delete_motor: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete motor: {exc_str}",
            ) from e
        else:
            return MotorDeleted(deleted_motor_id=motor_id)
        finally:
            logger.info(
                f"Call to controllers.motor.delete_motor completed for Motor {motor_id}"
            )

    @classmethod
    async def simulate_motor(
        cls, motor_id: str
    ) -> Union[MotorSummary, HTTPException]:
        """
        Simulate a rocketpy motor.

        Args:
            motor_id: str

        Returns:
            views.MotorSummary

        Raises:
            HTTP 404 Not Found: If the motor does not exist in the database.
        """
        try:
            read_motor = await cls.get_motor_by_id(motor_id)
            motor = cls.get_rocketpy_motor(read_motor)

            motor_simulation_numbers = MotorData(
                total_burning_time="Total Burning Time: "
                + str(motor.burn_out_time)
                + " s",
                total_propellant_mass="Total Propellant Mass: "
                + "{:.3f}".format(motor.propellant_initial_mass)
                + " kg",
                average_propellant_exhaust_velocity="Average Propellant Exhaust Velocity: "
                + "{:.3f}".format(
                    motor.exhaust_velocity.average(*motor.burn_time)
                )
                + " m/s",
                average_thrust="Average Thrust: "
                + "{:.3f}".format(motor.average_thrust)
                + " N",
                maximum_thrust="Maximum Thrust: "
                + str(motor.max_thrust)
                + " N at "
                + str(motor.max_thrust_time)
                + " s after ignition.",
                total_impulse="Total Impulse: "
                + "{:.3f}".format(motor.total_impulse)
                + " Ns\n",
            )
            # motor_simulation_plots = MotorPlots(
            #    motor.thrust.plot(lower=lower_limit, upper=upper_limit)
            # )
            motor_summary = MotorSummary(
                motor_data=motor_simulation_numbers
            )  # , plots=motor_simulation_plots )
        except HTTPException as e:
            raise e from e
        except Exception as e:
            exc_str = parse_error(e)
            logger.error(f"controllers.motor.simulate_motor: {exc_str}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to simulate motor: {exc_str}",
            ) from e
        else:
            return motor_summary
        finally:
            logger.info(
                f"Call to controllers.motor.simulate_motor completed for Motor {motor_id}"
            )

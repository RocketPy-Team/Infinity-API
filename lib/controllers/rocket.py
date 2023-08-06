from lib.controllers.motor import MotorController
from lib.models.rocket import Rocket
from lib.models.aerosurfaces import NoseCone, TrapezoidalFins, Tail, RailButtons
from lib.models.parachute import Parachute
from lib.repositories.rocket import RocketRepository

from rocketpy.AeroSurface import NoseCone as rocketpy_NoseCone
from rocketpy.AeroSurface import TrapezoidalFins as rocketpy_TrapezoidalFins
from rocketpy.AeroSurface import Tail as rocketpy_Tail

from fastapi import Response, status
from typing import Dict, Any, Union

import rocketpy.Parachute
import rocketpy.Rocket
import jsonpickle
import ast

class RocketController():
    """
    Controller for the Rocket model.

    Init Attributes:
        rocket (models.Rocket): Rocket model object.

    Enables:
       create a rocketpy.Rocket object from a Rocket model object.
    """
    def __init__(self, rocket: Rocket):
        rocketpy_rocket = rocketpy.Rocket(
                radius=rocket.radius,
                mass=rocket.mass,
                inertiaI=rocket.inertiaI,
                inertiaZ=rocket.inertiaZ,
                powerOffDrag=rocket.powerOffDrag,
                powerOnDrag=rocket.powerOnDrag,
                centerOfDryMassPosition=rocket.centerOfDryMassPosition,
                coordinateSystemOrientation=rocket.coordinateSystemOrientation
        )

        #RailButtons
        rocketpy_rocket.setRailButtons(upper_button_position=rocket.railButtons.upper_button_position,
                                       lower_button_position=rocket.railButtons.lower_button_position,
                                       angular_position=rocket.railButtons.angularPosition)
        rocketpy_rocket.addMotor(MotorController(rocket.motor).rocketpy_motor,
                                 rocket.motorPosition)

        #NoseCone
        nose = self.NoseConeController(rocket.nose).rocketpy_nose
        rocketpy_rocket.aerodynamicSurfaces.add(nose, nose.position)
        rocketpy_rocket.evaluateStaticMargin()

        #FinSet
        #TBD: re-write this to match overall fins not only TrapezoidalFins
        finset = self.TrapezoidalFinsController(rocket.fins).rocketpy_finset
        rocketpy_rocket.aerodynamicSurfaces.add(finset, finset.position)
        rocketpy_rocket.evaluateStaticMargin()

        #Tail
        tail = self.TailController(rocket.tail).rocketpy_tail 
        rocketpy_rocket.aerodynamicSurfaces.add(tail, tail.position)
        rocketpy_rocket.evaluateStaticMargin()

        #Parachutes
        for p in range(len(rocket.parachutes)):
            parachute_trigger = rocket.parachutes[p].triggers[0]
            if self.ParachuteController.check_trigger(parachute_trigger):
                rocket.parachutes[p].triggers[0] = compile(parachute_trigger, '<string>', 'eval')
                parachute = self.ParachuteController(rocket.parachutes, p).rocketpy_parachute
                rocketpy_rocket.parachutes.append(parachute)
            else:
                print("Parachute trigger not valid. Skipping parachute.")
                continue
            
        self.rocketpy_rocket = rocketpy_rocket 
        self.rocket = rocket

    class NoseConeController():
        """
        Controller for the NoseCone model.

        Init Attributes:
            nose (models.NoseCone): NoseCone model object.

        Enables:
            - Create a rocketpy.AeroSurface.NoseCone object from a NoseCone model object.
        """
        def __init__(self, nose: NoseCone):
            rocketpy_nose = rocketpy_NoseCone(
                    length=nose.length,
                    kind=nose.kind,
                    baseRadius=nose.baseRadius,
                    rocketRadius=nose.rocketRadius
            )
            rocketpy_nose.position = nose.position
            self.rocketpy_nose = rocketpy_nose
            self.nose = nose

    class TrapezoidalFinsController():
        """
        Controller for the TrapezoidalFins model.

        Init Attributes:
            trapezoidalFins (models.TrapezoidalFins): TrapezoidalFins model object.

        Enables:
            - Create a rocketpy.AeroSurface.TrapezoidalFins object from a TrapezoidalFins model object.
        """
        def __init__(self, trapezoidalFins: TrapezoidalFins):
            rocketpy_finset = rocketpy_TrapezoidalFins(
                    n=trapezoidalFins.n,
                    rootChord=trapezoidalFins.rootChord,
                    tipChord=trapezoidalFins.tipChord,
                    span=trapezoidalFins.span,
                    cantAngle=trapezoidalFins.cantAngle,
                    rocketRadius=trapezoidalFins.radius,
                    airfoil=trapezoidalFins.airfoil
            )
            rocketpy_finset.position = trapezoidalFins.position
            self.rocketpy_finset = rocketpy_finset
            self.trapezoidalFins = trapezoidalFins

    class TailController():
        """
        Controller for the Tail model.

        Init Attributes:
            tail (models.Tail): Tail model object.

        Enables:
            - Create a rocketpy.AeroSurface.Tail object from a Tail model object.
        """
        def __init__(self, tail: Tail):
            rocketpy_tail = rocketpy_Tail(
                    topRadius=tail.topRadius,
                    bottomRadius=tail.bottomRadius,
                    length=tail.length,
                    rocketRadius=tail.radius
            )
            rocketpy_tail.position = tail.position
            self.rocketpy_tail = rocketpy_tail
            self.tail = tail

    class ParachuteController():
        """
        Controller for the Parachute model.

        Init Attributes:
            parachute (models.Parachute): Parachute model object.

        Enables:
            - Create a rocketpy.Parachute.Parachute object from a Parachute model object.
        """
        def __init__(self, parachute: Parachute, p: int):
            rocketpy_parachute = rocketpy.Parachute.Parachute(
                    name=parachute[p].name[0],
                    CdS=parachute[p].CdS[0],
                    trigger=eval(parachute[p].triggers[0]),
                    samplingRate=parachute[p].samplingRate[0],
                    lag=parachute[p].lag[0],
                    noise=parachute[p].noise[0]
            )
            self.rocketpy_parachute = rocketpy_parachute
            self.parachute = parachute

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
                parsed_expression = ast.parse(expression, mode='eval')
            except SyntaxError:
                print("Invalid syntax.")
                return False

            # Constant case (supported after beta v1) 
            if isinstance(parsed_expression.body, ast.Constant):
                return True
            # Name case (supported after beta v1)
            elif isinstance(parsed_expression.body, ast.Name) \
            and parsed_expression.body.id == "apogee":
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
                elif isinstance(node, ast.Attribute):
                    print("Accessing attributes is not allowed in the expression.")
                    return False
            return True 

    def create_rocket(self) -> "Dict[str, str]":
        """
        Create a rocket in the database.

        Returns:
            Dict[str, str]: Rocket id.
        """
        rocket = RocketRepository(rocket=self.rocket)
        successfully_created_rocket = rocket.create_rocket()
        if successfully_created_rocket: 
            return { "message": "rocket created", "rocket_id": rocket.rocket_id }
        else:
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_rocket(rocket_id: int) -> "Union[Rocket, Response]":
        """
        Get a rocket from the database.

        Args:
            rocket_id (int): Rocket id.

        Returns:
            rocket model object

        Raises:
            HTTP 404 Not Found: If the rocket is not found in the database. 
        """
        successfully_read_rocket = RocketRepository(rocket_id=rocket_id).get_rocket()
        if not successfully_read_rocket:
            return Response(status_code=status.HTTP_404_NOT_FOUND)
        return successfully_read_rocket

    def get_rocketpy_rocket(rocket_id: int) -> "Union[Dict[str, Any], Response]":
        """
        Get a rocketpy rocket object encoded as jsonpickle string from the database.

        Args:
            rocket_id (int): rocket id.

        Returns:
            str: jsonpickle string of the rocketpy rocket.

        Raises:
            HTTP 404 Not Found: If the rocket is not found in the database.
        """
        successfully_read_rocket = RocketRepository(rocket_id=rocket_id).get_rocket()
        if not successfully_read_rocket:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        successfully_read_rocketpy_rocket  = RocketController( successfully_read_rocket ).rocketpy_rocket

        return { "jsonpickle_rocketpy_rocket": jsonpickle.encode(successfully_read_rocketpy_rocket) }

           
    def update_rocket(self, rocket_id: int) -> "Union[Dict[str, Any], Response]":
        """
        Update a rocket in the database.

        Args:
            rocket_id (int): rocket id.

        Returns:
            Dict[str, Any]: rocket id and message.

        Raises:
            HTTP 404 Not Found: If the rocket is not found in the database.
        """
        successfully_read_rocket = RocketRepository(rocket_id=rocket_id).get_rocket()
        if not successfully_read_rocket:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        successfully_updated_rocket = \
                RocketRepository(rocket=self.rocket, rocket_id=rocket_id).update_rocket()

        if successfully_updated_rocket:
            return { 
                    "message": "rocket updated successfully", 
                    "new_rocket_id": successfully_updated_rocket
            }
        else:
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete_rocket(rocket_id: int) -> "Union[Dict[str, str], Response]":
        """
        Delete a rocket from the database.

        Args:
            rocket_id (int): Rocket id.

        Returns:
            Dict[str, str]: Rocket id and message.

        Raises:
            HTTP 404 Not Found: If the rocket is not found in the database.
        """
        successfully_read_rocket = RocketRepository(rocket_id=rocket_id).get_rocket()
        if not successfully_read_rocket:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        successfully_deleted_rocket = RocketRepository(rocket_id=rocket_id).delete_rocket()
        if successfully_deleted_rocket: 
            return {"rocket_id": rocket_id, "message": "rocket deleted successfully"}
        else:
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def simulate(rocket_id: int) -> "Union[RocketSummary, Response]":
        """
        Simulate a rocket rocket.

        Args:
            rocket_id (int): Rocket id.

        Returns:
            Rocket summary view.

        Raises:
            HTTP 404 Not Found: If the rocket does not exist in the database.
        """
        successfully_read_rocket = RocketRepository(rocket_id=rocket_id).get_rocket()
        if not successfully_read_rocket:
            return Response(status_code=status.HTTP_404_NOT_FOUND)

        #rocket = RocketController(successfully_read_rocket).rocketpy_rocket
        #rocket_simulation_numbers = RocketData.parse_obj(rocket.allInfoReturned())
        #rocket_simulation_plots = RocketPlots.parse_obj(rocket.allPlotInfoReturned())

        #rocket_summary = RocketSummary( data=rocket_simulation_numbers, plots=rocket_simulation_plots )

        #return rocket_summary
        pass


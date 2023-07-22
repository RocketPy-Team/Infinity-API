from lib.controllers.motor import MotorController

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

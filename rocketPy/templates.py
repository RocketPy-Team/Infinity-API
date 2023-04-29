from rocketpy import Environment, Rocket, SolidMotor, Flight

def flight_summary(Flight):
    summary = {
        "Flight Simulation Summary": 
        {
            "Surface Wind Conditions": 
            { 
                "Frontal Surface Wind Speed": "{:.2f} m/s".format(Flight.frontalSurfaceWind), 
                "Lateral Surface Wind Speed": "{:.2f} m/s".format(Flight.lateralSurfaceWind)
            },

            "Rail Departure State":
            {
                "Rail Departure Time": "{:.3f} s".format(Flight.outOfRailTime),
                "Rail Departure Velocity": "{:.3f} m/s".format(Flight.outOfRailVelocity),
                "Rail Departure Static Margin": "{:.3f} c".format(Flight.rocket.staticMargin(Flight.outOfRailTime)),
                "Rail Departure Angle of Attack": "{:.3f}°".format(Flight.angleOfAttack(Flight.outOfRailTime)),
                "Rail Departure Thrust-Weight Ratio": "{:.3f}".format(Flight.rocket.thrustToWeight(Flight.outOfRailTime)),
                "Rail Departure Reynolds Number": "{:.3e}".format(Flight.ReynoldsNumber(Flight.outOfRailTime))
            }, 

            "BurnOut State":
            {
                "BurnOut time": "{:.3f} s".format(Flight.rocket.motor.burnOutTime),
#                "Altitude at burnOut": "{:.3f} m/s".format(Flight.speed(Flight.rocket.motor.burnOutTime)),
                "Rocket velocity at burnOut": "{:.3f} m/s".format(Flight.speed(Flight.rocket.motor.burnOutTime)),
                "Freestream velocity at burnOut": "{:.3f} m/s".format((
                    Flight.streamVelocityX(Flight.rocket.motor.burnOutTime) ** 2
                    + Flight.streamVelocityY(Flight.rocket.motor.burnOutTime) ** 2
                    + Flight.streamVelocityZ(Flight.rocket.motor.burnOutTime) ** 2
                )
                ** 0.5),
                "Mach Number at burnOut": "{:.3f}".format(Flight.MachNumber(Flight.rocket.motor.burnOutTime)),
                "Kinetic energy at burnOut": "{:.3e}".format(Flight.kineticEnergy(Flight.rocket.motor.burnOutTime))
            }, 

            "Apogee":
            {
                "Apogee Altitude": "{:.3f} m (ASL) | {:.3f} m (AGL)".format(Flight.apogee, Flight.apogee - Flight.env.elevation),
                "Apogee Time": "{:.3f} s".format(Flight.apogeeTime),
                "Apogee Freestream Speed": "{:.3f} m/s".format(Flight.apogeeFreestreamSpeed) 
            },

            "Maximum Values":
            { 
                "Maximum Speed": "{:.3f} m/s at {:.2f} s".format(Flight.maxSpeed, Flight.maxSpeedTime),
                "Maximum Mach Number": "{:.3f} Mach at {:.2f} s".format(Flight.maxMachNumber, Flight.maxMachNumberTime),
                "Maximum Reynolds Number": "{:.3e} at {:.2f} s".format(Flight.maxReynoldsNumber, Flight.maxReynoldsNumberTime),
                "Maximum Dynamic Pressure": "{:.3e} Pa at {:.2f} s".format(Flight.maxDynamicPressure, Flight.maxDynamicPressureTime),
                "Maximum Acceleration": "{:.3f} m/s² at {:.2f} s".format(Flight.maxAcceleration, Flight.maxAccelerationTime),
                "Maximum Gs": "{:.3f} g at {:.2f} s".format(Flight.maxAcceleration / Flight.env.g, Flight.maxAccelerationTime),
                "Maximum Upper Rail Button Normal Force": "{:.3f} N".format(Flight.maxRailButton1NormalForce),
                "Maximum Upper Rail Button Shear Force": "{:.3f} N".format(Flight.maxRailButton1ShearForce),
                "Maximum Lower Rail Button Normal Force": "{:.3f} N".format(Flight.maxRailButton2NormalForce),
                "Maximum Lower Rail Button Shear Force": "{:.3f} N".format(Flight.maxRailButton2ShearForce) 
            } 
        } 
    } 

    return summary 

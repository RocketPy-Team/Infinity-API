def full_flight_summary(Flight):
    summary = {
        "flight_simulation_summary": 
        {
            "surface_wind_conditions": 
            { 
                "frontal_surface_wind_speed": "{:.2f} m/s".format(Flight.frontalSurfaceWind), 
                "lateral_surface_wind_speed": "{:.2f} m/s".format(Flight.lateralSurfaceWind)
            },

            "rail_departure_state":
            {
                "rail_departure_time": "{:.3f} s".format(Flight.outOfRailTime),
                "rail_departure_velocity": "{:.3f} m/s".format(Flight.outOfRailVelocity),
                "rail_departure_static_margin": "{:.3f} c".format(Flight.rocket.staticMargin(Flight.outOfRailTime)),
                "rail_departure_angle_of_attack": "{:.3f}°".format(Flight.angleOfAttack(Flight.outOfRailTime)),
                "rail_departure_thrust_weight_ratio": "{:.3f}".format(Flight.rocket.thrustToWeight(Flight.outOfRailTime)),
                "rail_departure_reynolds_number": "{:.3e}".format(Flight.ReynoldsNumber(Flight.outOfRailTime))
            }, 

            "burnout_state":
            {
                "burnout_time": "{:.3f} s".format(Flight.rocket.motor.burnOutTime),
#                "Altitude at burnOut": "{:.3f} m/s".format(Flight.speed(Flight.rocket.motor.burnOutTime)),
                "rocket_velocity_at_burnout": "{:.3f} m/s".format(Flight.speed(Flight.rocket.motor.burnOutTime)),
                "freestream_velocity_at_burnout": "{:.3f} m/s".format((
                    Flight.streamVelocityX(Flight.rocket.motor.burnOutTime) ** 2
                    + Flight.streamVelocityY(Flight.rocket.motor.burnOutTime) ** 2
                    + Flight.streamVelocityZ(Flight.rocket.motor.burnOutTime) ** 2
                )
                ** 0.5),
                "mach_number_at_burnout": "{:.3f}".format(Flight.MachNumber(Flight.rocket.motor.burnOutTime)),
                "kinetic_energy_at_burnout": "{:.3e}".format(Flight.kineticEnergy(Flight.rocket.motor.burnOutTime))
            }, 

            "apogee":
            {
                "apogee_altitude": "{:.3f} m (ASL) | {:.3f} m (AGL)".format(Flight.apogee, Flight.apogee - Flight.env.elevation),
                "apogee_time": "{:.3f} s".format(Flight.apogeeTime),
                "apogee_freestream_speed": "{:.3f} m/s".format(Flight.apogeeFreestreamSpeed) 
            },

            "maximum_values":
            { 
                "maximum_speed": "{:.3f} m/s at {:.2f} s".format(Flight.maxSpeed, Flight.maxSpeedTime),
                "maximum_mach_number": "{:.3f} Mach at {:.2f} s".format(Flight.maxMachNumber, Flight.maxMachNumberTime),
                "maximum_reynolds_number": "{:.3e} at {:.2f} s".format(Flight.maxReynoldsNumber, Flight.maxReynoldsNumberTime),
                "maximum_dynamic_pressure": "{:.3e} Pa at {:.2f} s".format(Flight.maxDynamicPressure, Flight.maxDynamicPressureTime),
                "maximum_acceleration": "{:.3f} m/s² at {:.2f} s".format(Flight.maxAcceleration, Flight.maxAccelerationTime),
                "maximum_gs": "{:.3f} g at {:.2f} s".format(Flight.maxAcceleration / Flight.env.g, Flight.maxAccelerationTime),
                "maximum_upper_rail_button_normal_force": "{:.3f} N".format(Flight.maxRailButton1NormalForce),
                "maximum_upper_rail_button_shear_force": "{:.3f} N".format(Flight.maxRailButton1ShearForce),
                "maximum_lower_rail_button_normal_force": "{:.3f} N".format(Flight.maxRailButton2NormalForce),
                "maximum_lower_rail_button_shear_force": "{:.3f} N".format(Flight.maxRailButton2ShearForce) 
            } 
        } 
    } 

    return summary 

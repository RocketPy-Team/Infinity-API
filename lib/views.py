from rocketpy import Environment, Flight

class EnvView():
    def __init__(self, env: Environment):
        self.obj = env 

class FlightView():
    def __init__(self, flight: Flight):
        self.obj = flight

    def full_flight_summary(self):
        summary = {
            "flight_simulation_summary": 
            {
                "surface_wind_conditions": 
                { 
                    "frontal_surface_wind_speed": "{:.2f} m/s".format(self.obj.frontalSurfaceWind), 
                    "lateral_surface_wind_speed": "{:.2f} m/s".format(self.obj.lateralSurfaceWind)
                },

                "rail_departure_state":
                {
                    "rail_departure_time": "{:.3f} s".format(self.obj.outOfRailTime),
                    "rail_departure_velocity": "{:.3f} m/s".format(self.obj.outOfRailVelocity),
                    "rail_departure_static_margin": "{:.3f} c".format(self.obj.rocket.staticMargin(self.obj.outOfRailTime)),
                    "rail_departure_angle_of_attack": "{:.3f}°".format(self.obj.angleOfAttack(self.obj.outOfRailTime)),
                    "rail_departure_thrust_weight_ratio": "{:.3f}".format(self.obj.rocket.thrustToWeight(self.obj.outOfRailTime)),
                    "rail_departure_reynolds_number": "{:.3e}".format(self.obj.ReynoldsNumber(self.obj.outOfRailTime))
                }, 

                "burnout_state":
                {
                    "burnout_time": "{:.3f} s".format(self.obj.rocket.motor.burnOutTime),
    #                "Altitude at burnOut": "{:.3f} m/s".format(self.obj.speed(self.obj.rocket.motor.burnOutTime)),
                    "rocket_velocity_at_burnout": "{:.3f} m/s".format(self.obj.speed(self.obj.rocket.motor.burnOutTime)),
                    "freestream_velocity_at_burnout": "{:.3f} m/s".format((
                        self.obj.streamVelocityX(self.obj.rocket.motor.burnOutTime) ** 2
                        + self.obj.streamVelocityY(self.obj.rocket.motor.burnOutTime) ** 2
                        + self.obj.streamVelocityZ(self.obj.rocket.motor.burnOutTime) ** 2
                    )
                    ** 0.5),
                    "mach_number_at_burnout": "{:.3f}".format(self.obj.MachNumber(self.obj.rocket.motor.burnOutTime)),
                    "kinetic_energy_at_burnout": "{:.3e}".format(self.obj.kineticEnergy(self.obj.rocket.motor.burnOutTime))
                }, 

                "apogee":
                {
                    "apogee_altitude": "{:.3f} m (ASL) | {:.3f} m (AGL)".format(self.obj.apogee, self.obj.apogee - self.obj.env.elevation),
                    "apogee_time": "{:.3f} s".format(self.obj.apogeeTime),
                    "apogee_freestream_speed": "{:.3f} m/s".format(self.obj.apogeeFreestreamSpeed) 
                },

                "maximum_values":
                { 
                    "maximum_speed": "{:.3f} m/s at {:.2f} s".format(self.obj.maxSpeed, self.obj.maxSpeedTime),
                    "maximum_mach_number": "{:.3f} Mach at {:.2f} s".format(self.obj.maxMachNumber, self.obj.maxMachNumberTime),
                    "maximum_reynolds_number": "{:.3e} at {:.2f} s".format(self.obj.maxReynoldsNumber, self.obj.maxReynoldsNumberTime),
                    "maximum_dynamic_pressure": "{:.3e} Pa at {:.2f} s".format(self.obj.maxDynamicPressure, self.obj.maxDynamicPressureTime),
                    "maximum_acceleration": "{:.3f} m/s² at {:.2f} s".format(self.obj.maxAcceleration, self.obj.maxAccelerationTime),
                    "maximum_gs": "{:.3f} g at {:.2f} s".format(self.obj.maxAcceleration / self.obj.env.g, self.obj.maxAccelerationTime),
                    "maximum_upper_rail_button_normal_force": "{:.3f} N".format(self.obj.maxRailButton1NormalForce),
                    "maximum_upper_rail_button_shear_force": "{:.3f} N".format(self.obj.maxRailButton1ShearForce),
                    "maximum_lower_rail_button_normal_force": "{:.3f} N".format(self.obj.maxRailButton2NormalForce),
                    "maximum_lower_rail_button_shear_force": "{:.3f} N".format(self.obj.maxRailButton2ShearForce) 
                } 
            } 
        } 

        return summary 

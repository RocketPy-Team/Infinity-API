from typing import List, Any, Optional
from pydantic import BaseModel

class InertiaDetails(BaseModel):
    rocket_mass_without_propellant: str
    rocket_mass_with_propellant: str
    rocket_inertia_with_motor_without_propellant: "List[str]"

class RocketGeometricalParameters(BaseModel):
    rocket_maximum_radius: str
    rocket_frontal_area: str
    rocket_codm_nozzle_exit_distance: str 
    rocket_codm_center_of_propellant_mass: str
    rocket_codm_loaded_center_of_mass: str

class RocketAerodynamicsQuantities(BaseModel):
    aerodynamics_lift_coefficient_derivatives: "Any"
    aerodynamics_center_of_pressure: "Any"
    distance_cop_to_codm: str
    initial_static_margin: str
    final_static_margin: str

class ParachuteData(BaseModel):
    parachute_details: "Any"
    # parachute_ejection_signal_trigger: "Any"
    parachute_ejection_system_refresh_rate: "Optional[Any]"
    parachute_lag: "Any" 

class RocketData(BaseModel):
    inertia_details: InertiaDetails 
    rocket_geometrical_parameters: RocketGeometricalParameters
    rocket_aerodynamics_quantities: RocketAerodynamicsQuantities
    parachute_data: ParachuteData 

class RocketPlots(BaseModel):
    pass

class RocketSummary(BaseModel):
    rocket_data: RocketData
    #rocket_plots: RocketPlots


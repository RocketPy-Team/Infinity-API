import json
import pytest

from src.models.rocket import RocketModel
from src.models.sub.tanks import MotorTank, TankFluids, TankKinds
from src.models.motor import MotorModel
from src.models.environment import EnvironmentModel
from src.models.sub.aerosurfaces import Fins, NoseCone


@pytest.fixture
def stub_environment_dump():
    env = EnvironmentModel(latitude=0, longitude=0)
    env_json = env.model_dump_json()
    return json.loads(env_json)


@pytest.fixture
def stub_motor_dump():
    # Non-zero dry_inertia so tests that override motor_kind to SOLID/LIQUID/HYBRID
    # pass the validate_dry_inertia_for_kind guard. GENERIC still accepts (0, 0, 0)
    # at the model level, but we use a non-default value here to keep the stub
    # compatible with every motor_kind.
    motor = MotorModel(
        thrust_source=[[0, 0]],
        burn_time=0,
        nozzle_radius=0,
        dry_mass=0,
        dry_inertia=[0.1, 0.1, 0.1],
        center_of_dry_mass_position=0,
        motor_kind='GENERIC',
    )
    motor_json = motor.model_dump_json()
    return json.loads(motor_json)


@pytest.fixture
def stub_tank_dump():
    # Base fixture defaults to MASS_FLOW (matches MotorTank's own default)
    # so the tank validates standalone. Sub-variant fixtures below switch
    # tank_kind and populate only the fields that variant requires.
    tank = MotorTank(
        geometry={
            'geometry_kind': 'custom',
            'geometry': [[(0, 0), 0]],
        },
        gas=TankFluids(name='gas', density=0),
        liquid=TankFluids(name='liquid', density=0),
        flux_time=(0, 0),
        position=0,
        discretize=0,
        name='tank',
        gas_mass_flow_rate_in=0,
        gas_mass_flow_rate_out=0,
        liquid_mass_flow_rate_in=0,
        liquid_mass_flow_rate_out=0,
        initial_liquid_mass=0,
        initial_gas_mass=0,
    )
    tank_json = tank.model_dump_json()
    return json.loads(tank_json)


@pytest.fixture
def stub_cylindrical_tank_dump(stub_tank_dump):
    stub_tank_dump['geometry'] = {
        'geometry_kind': 'cylindrical',
        'radius': 0.1,
        'height': 0.5,
        'spherical_caps': False,
    }
    return stub_tank_dump


@pytest.fixture
def stub_spherical_tank_dump(stub_tank_dump):
    stub_tank_dump['geometry'] = {
        'geometry_kind': 'spherical',
        'radius': 0.2,
    }
    return stub_tank_dump


@pytest.fixture
def stub_tank_with_sampled_density_dump(stub_tank_dump):
    stub_tank_dump['liquid'] = {
        'name': 'LOX',
        'density': [[90.0, 1141.0], [120.0, 1091.0], [150.0, 1021.0]],
    }
    return stub_tank_dump


@pytest.fixture
def stub_level_tank_dump(stub_tank_dump):
    # Switch out of the MASS_FLOW defaults into LEVEL, clearing the
    # unused MASS_FLOW fields so the kind-specific validator passes.
    stub_tank_dump.update(
        {
            'tank_kind': TankKinds.LEVEL,
            'liquid_height': 0,
            'gas_mass_flow_rate_in': None,
            'gas_mass_flow_rate_out': None,
            'liquid_mass_flow_rate_in': None,
            'liquid_mass_flow_rate_out': None,
            'initial_liquid_mass': None,
            'initial_gas_mass': None,
        }
    )
    return stub_tank_dump


@pytest.fixture
def stub_mass_flow_tank_dump(stub_tank_dump):
    # stub_tank_dump already includes all MASS_FLOW fields.
    stub_tank_dump['tank_kind'] = TankKinds.MASS_FLOW
    return stub_tank_dump


@pytest.fixture
def stub_ullage_tank_dump(stub_tank_dump):
    stub_tank_dump.update(
        {
            'tank_kind': TankKinds.ULLAGE,
            'ullage': 0,
            'gas_mass_flow_rate_in': None,
            'gas_mass_flow_rate_out': None,
            'liquid_mass_flow_rate_in': None,
            'liquid_mass_flow_rate_out': None,
            'initial_liquid_mass': None,
            'initial_gas_mass': None,
        }
    )
    return stub_tank_dump


@pytest.fixture
def stub_mass_tank_dump(stub_tank_dump):
    stub_tank_dump.update(
        {
            'tank_kind': TankKinds.MASS,
            'liquid_mass': 0,
            'gas_mass': 0,
            'gas_mass_flow_rate_in': None,
            'gas_mass_flow_rate_out': None,
            'liquid_mass_flow_rate_in': None,
            'liquid_mass_flow_rate_out': None,
            'initial_liquid_mass': None,
            'initial_gas_mass': None,
        }
    )
    return stub_tank_dump


@pytest.fixture
def stub_nose_cone_dump():
    nose_cone = NoseCone(
        name='nose',
        length=0,
        kind='kind',
        position=0,
        base_radius=0,
        rocket_radius=0,
    )
    nose_cone_json = nose_cone.model_dump_json()
    return json.loads(nose_cone_json)


@pytest.fixture
def stub_fins_dump():
    fins = Fins(
        fins_kind='trapezoidal',
        name='fins',
        n=0,
        root_chord=0,
        span=0,
        position=0,
    )
    fins_json = fins.model_dump_json()
    return json.loads(fins_json)


@pytest.fixture
def stub_rocket_dump(stub_motor_dump, stub_nose_cone_dump, stub_fins_dump):
    rocket = RocketModel(
        motor=stub_motor_dump,
        radius=0,
        mass=0,
        motor_position=0,
        center_of_mass_without_motor=0,
        inertia=[0, 0, 0],
        power_off_drag=[(0, 0)],
        power_on_drag=[(0, 0)],
        nose=stub_nose_cone_dump,
        fins=[stub_fins_dump],
        coordinate_system_orientation='tail_to_nose',
    )
    rocket_json = rocket.model_dump_json()
    return json.loads(rocket_json)

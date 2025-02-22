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
    motor = MotorModel(
        thrust_source=[[0, 0]],
        burn_time=0,
        nozzle_radius=0,
        dry_mass=0,
        dry_inertia=[0, 0, 0],
        center_of_dry_mass_position=0,
        motor_kind='GENERIC',
    )
    motor_json = motor.model_dump_json()
    return json.loads(motor_json)


@pytest.fixture
def stub_tank_dump():
    tank = MotorTank(
        geometry=[[(0, 0), 0]],
        gas=TankFluids(name='gas', density=0),
        liquid=TankFluids(name='liquid', density=0),
        flux_time=(0, 0),
        position=0,
        discretize=0,
        name='tank',
    )
    tank_json = tank.model_dump_json()
    return json.loads(tank_json)


@pytest.fixture
def stub_level_tank_dump(stub_tank_dump):
    stub_tank_dump.update({'tank_kind': TankKinds.LEVEL, 'liquid_height': 0})
    return stub_tank_dump


@pytest.fixture
def stub_mass_flow_tank_dump(stub_tank_dump):
    stub_tank_dump.update(
        {
            'tank_kind': TankKinds.MASS_FLOW,
            'gas_mass_flow_rate_in': 0,
            'gas_mass_flow_rate_out': 0,
            'liquid_mass_flow_rate_in': 0,
            'liquid_mass_flow_rate_out': 0,
            'initial_liquid_mass': 0,
            'initial_gas_mass': 0,
        }
    )
    return stub_tank_dump


@pytest.fixture
def stub_ullage_tank_dump(stub_tank_dump):
    stub_tank_dump.update({'tank_kind': TankKinds.ULLAGE, 'ullage': 0})
    return stub_tank_dump


@pytest.fixture
def stub_mass_tank_dump(stub_tank_dump):
    stub_tank_dump.update(
        {'tank_kind': TankKinds.MASS, 'liquid_mass': 0, 'gas_mass': 0}
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

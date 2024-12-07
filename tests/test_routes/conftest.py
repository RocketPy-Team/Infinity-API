import json
import pytest

from lib.models.rocket import Rocket
from lib.models.motor import Motor, MotorTank, TankFluids, TankKinds
from lib.models.environment import Env


@pytest.fixture
def stub_env():
    env = Env(latitude=0, longitude=0)
    env_json = env.model_dump_json()
    return json.loads(env_json)


@pytest.fixture
def stub_motor():
    motor = Motor(
        thrust_source=[[0, 0]],
        burn_time=0,
        nozzle_radius=0,
        dry_mass=0,
        dry_inertia=[0, 0, 0],
        center_of_dry_mass_position=0,
    )
    motor_json = motor.model_dump_json()
    return json.loads(motor_json)


@pytest.fixture
def stub_tank():
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
def stub_level_tank(stub_tank):
    stub_tank.update({'tank_kind': TankKinds.LEVEL, 'liquid_height': 0})
    return stub_tank


@pytest.fixture
def stub_mass_flow_tank(stub_tank):
    stub_tank.update(
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
    return stub_tank


@pytest.fixture
def stub_ullage_tank(stub_tank):
    stub_tank.update({'tank_kind': TankKinds.ULLAGE, 'ullage': 0})
    return stub_tank


@pytest.fixture
def stub_mass_tank(stub_tank):
    stub_tank.update(
        {'tank_kind': TankKinds.MASS, 'liquid_mass': 0, 'gas_mass': 0}
    )
    return stub_tank


@pytest.fixture
def stub_rocket(stub_motor):
    rocket = Rocket(
        motor=stub_motor,
        radius=0,
        mass=0,
        motor_position=0,
        center_of_mass_without_motor=0,
        inertia=[0, 0, 0],
        power_off_drag=[(0, 0)],
        power_on_drag=[(0, 0)],
        coordinate_system_orientation='TAIL_TO_NOSE',
    )
    rocket_json = rocket.model_dump_json()
    return json.loads(rocket_json)

from src.models.environment import EnvironmentModel
from src.services.environment import EnvironmentService


def test_from_env_model_custom_atmosphere_default_wind_none():
    env_model = EnvironmentModel(
        latitude=0.0,
        longitude=0.0,
        elevation=0.0,
        atmospheric_model_type='custom_atmosphere',
        pressure=101325.0,
        temperature=288.15,
        wind_u=None,
        wind_v=None,
    )
    service = EnvironmentService.from_env_model(env_model)
    assert service.environment.wind_velocity_x(0) == 0.0
    assert service.environment.wind_velocity_y(0) == 0.0


def test_from_env_model_custom_atmosphere_one_wind_component_none():
    env_model_u_set = EnvironmentModel(
        latitude=0.0,
        longitude=0.0,
        elevation=0.0,
        atmospheric_model_type='custom_atmosphere',
        pressure=101325.0,
        temperature=288.15,
        wind_u=5.0,
        wind_v=None,
    )
    service_u = EnvironmentService.from_env_model(env_model_u_set)
    assert service_u.environment.wind_velocity_x(0) == 5.0
    assert service_u.environment.wind_velocity_y(0) == 0.0

    env_model_v_set = EnvironmentModel(
        latitude=0.0,
        longitude=0.0,
        elevation=0.0,
        atmospheric_model_type='custom_atmosphere',
        pressure=101325.0,
        temperature=288.15,
        wind_u=None,
        wind_v=3.0,
    )
    service_v = EnvironmentService.from_env_model(env_model_v_set)
    assert service_v.environment.wind_velocity_x(0) == 0.0
    assert service_v.environment.wind_velocity_y(0) == 3.0


def test_from_env_model_custom_atmosphere_explicit_zero_wind():
    env_model = EnvironmentModel(
        latitude=0.0,
        longitude=0.0,
        elevation=0.0,
        atmospheric_model_type='custom_atmosphere',
        pressure=101325.0,
        temperature=288.15,
        wind_u=0.0,
        wind_v=0.0,
    )
    service = EnvironmentService.from_env_model(env_model)
    assert service.environment.wind_velocity_x(0) == 0.0
    assert service.environment.wind_velocity_y(0) == 0.0


def test_from_env_model_custom_atmosphere_wind_profile_list():
    wind_u_profile = [(0.0, 2.0), (1000.0, 10.0)]
    wind_v_profile = [(0.0, 1.0), (1000.0, 5.0)]
    env_model = EnvironmentModel(
        latitude=0.0,
        longitude=0.0,
        elevation=0.0,
        atmospheric_model_type='custom_atmosphere',
        pressure=101325.0,
        temperature=288.15,
        wind_u=wind_u_profile,
        wind_v=wind_v_profile,
    )
    service = EnvironmentService.from_env_model(env_model)
    assert service.environment.wind_velocity_x(0) == 2.0
    assert service.environment.wind_velocity_x(1000) == 10.0
    assert service.environment.wind_velocity_y(0) == 1.0
    assert service.environment.wind_velocity_y(1000) == 5.0


def test_from_env_model_standard_atmosphere():
    env_model = EnvironmentModel(
        latitude=0.0,
        longitude=0.0,
        elevation=0.0,
        atmospheric_model_type='standard_atmosphere',
    )
    service = EnvironmentService.from_env_model(env_model)
    assert service.environment is not None

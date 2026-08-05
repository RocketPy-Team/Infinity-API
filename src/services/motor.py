from typing import Self

import dill
import numpy as np

from rocketpy.motors.motor import Motor as RocketPyMotor
from rocketpy.motors.solid_motor import SolidMotor
from rocketpy.motors.liquid_motor import LiquidMotor
from rocketpy.motors.hybrid_motor import HybridMotor
from rocketpy import (
    CylindricalTank,
    Fluid,
    Function,
    SphericalTank,
    TankGeometry,
)
from rocketpy.motors import (
    EmptyMotor,
    GenericMotor,
    LevelBasedTank,
    MassBasedTank,
    MassFlowRateBasedTank,
    UllageBasedTank,
)

from fastapi import HTTPException, status

from src import logger
from src.models.sub.tanks import (
    CustomTankGeometry,
    CylindricalTankGeometry,
    SphericalTankGeometry,
    TankFluids,
    TankKinds,
)
from src.models.motor import MotorKinds, MotorModel
from src.views.motor import MotorSimulation, MotorDrawingGeometryView
from src.views.drawing import (
    DrawingBounds,
    MotorDrawingGeometry,
    MotorPatch,
)
from src.utils import collect_attributes


def _build_rocketpy_tank_geometry(geometry):
    """Convert an API geometry model into a rocketpy geometry object.

    Dispatch mirrors the discriminated union in
    ``src.models.sub.tanks.TankGeometryInput``.
    """
    if isinstance(geometry, CylindricalTankGeometry):
        return CylindricalTank(
            radius=geometry.radius,
            height=geometry.height,
            spherical_caps=geometry.spherical_caps,
        )
    if isinstance(geometry, SphericalTankGeometry):
        return SphericalTank(radius=geometry.radius)
    if isinstance(geometry, CustomTankGeometry):
        return TankGeometry(geometry_dict=dict(geometry.geometry))
    raise ValueError(
        f"Unsupported tank geometry kind: {type(geometry).__name__}"
    )


def _build_rocketpy_fluid(fluids: TankFluids) -> Fluid:
    """Convert an API TankFluids into a rocketpy Fluid.

    Scalar density is passed through (Fluid stores it as a constant).
    Sampled density is converted to a 1D Temperature → Density Function
    and wrapped in a ``(T, P)`` callable because rocketpy's Fluid expects
    density to be a function of both temperature and pressure. Pressure
    is ignored here intentionally; only temperature-dependent density
    is supported in this iteration.
    """
    density = fluids.density
    if isinstance(density, list):
        temperature_to_density = Function(
            source=density,
            interpolation='linear',
            extrapolation='natural',
            inputs=['Temperature (K)'],
            outputs='Density (kg/m^3)',
        )

        def density_callable(temperature, pressure):  # noqa: ARG001
            # pylint: disable=unused-argument
            # Rocketpy's Fluid wraps this into a 2-input Function of
            # (T, P); pressure is accepted for signature compatibility
            # but intentionally ignored in this iteration.
            return temperature_to_density.get_value(temperature)

        return Fluid(name=fluids.name, density=density_callable)
    return Fluid(name=fluids.name, density=density)


# ---------------------------------------------------------------------------
# Drawing-geometry helpers (module-level, shared by the motor and rocket
# drawing paths). Kept private with the `_` prefix; consumers should go
# through `MotorService.get_drawing_geometry` for the motor-only response
# or through `RocketService.get_drawing_geometry` for the composed rocket
# view (which delegates motor assembly here).
# ---------------------------------------------------------------------------
def _polygon_xy(patch) -> dict:
    """Extract (x, y) coordinate lists from a matplotlib Polygon patch.

    Rocketpy's `_MotorPlots` generator helpers return matplotlib `Polygon`
    objects; we only ever read `patch.xy` (an Nx2 numpy array) as a data
    carrier, never for rendering.
    """
    xy = np.asarray(patch.xy)
    return {"x": xy[:, 0].tolist(), "y": xy[:, 1].tolist()}


def _rebuild_polygon(x: list[float], y: list[float]):
    """Rebuild a matplotlib `Polygon` from coordinate lists.

    Used only so `_MotorPlots._generate_motor_region` can read `patch.xy`
    bounds when we assemble the motor outline.
    """
    from matplotlib.patches import (
        Polygon,
    )  # local import keeps service cold-start lean

    return Polygon(np.column_stack([np.asarray(x), np.asarray(y)]))


def _build_generic_chamber_patch(
    center_x: float, chamber_height: float, chamber_radius: float
):
    """Build a rectangular combustion-chamber polygon for a GenericMotor.

    Mirrors the vertex order of
    `rocketpy.plots.motor_plots._generate_combustion_chamber` so the patch
    can flow through `_generate_motor_region` for outline computation
    identically to a SolidMotor chamber.
    """
    from matplotlib.patches import (
        Polygon,
    )  # local import keeps service cold-start lean

    half_len = chamber_height / 2.0
    x = np.array([-half_len, half_len, half_len, -half_len])
    y = np.array(
        [chamber_radius, chamber_radius, -chamber_radius, -chamber_radius]
    )
    x = x + center_x
    return Polygon(np.column_stack([x, y]))


class MotorService:
    _motor: RocketPyMotor

    def __init__(self, motor: RocketPyMotor = None):
        self._motor = motor

    @classmethod
    def from_motor_model(cls, motor: MotorModel) -> Self:
        """
        Get the rocketpy motor object.

        Returns:
            MotorService containing the rocketpy motor object.
        """

        reshape_thrust_curve = motor.reshape_thrust_curve
        if isinstance(reshape_thrust_curve, bool):
            reshape_thrust_curve = False
        elif isinstance(reshape_thrust_curve, list):
            reshape_thrust_curve = tuple(reshape_thrust_curve)

        motor_core = {
            "thrust_source": motor.thrust_source,
            "nozzle_radius": motor.nozzle_radius,
            "dry_mass": motor.dry_mass,
            "dry_inertia": motor.dry_inertia,
            "center_of_dry_mass_position": motor.center_of_dry_mass_position,
            "coordinate_system_orientation": motor.coordinate_system_orientation,
            "interpolation_method": motor.interpolation_method,
            "reshape_thrust_curve": reshape_thrust_curve,
        }
        # Only forward optional rocketpy args when the client supplied them.
        # Leaving them out lets rocketpy pick its own default (burn_time
        # auto-detected from thrust_source span; nozzle_position = 0).
        if motor.burn_time is not None:
            motor_core["burn_time"] = motor.burn_time
        if motor.nozzle_position is not None:
            motor_core["nozzle_position"] = motor.nozzle_position

        match MotorKinds(motor.motor_kind):
            case MotorKinds.LIQUID:
                rocketpy_motor = LiquidMotor(**motor_core)
            case MotorKinds.HYBRID:
                rocketpy_motor = HybridMotor(
                    **motor_core,
                    throat_radius=motor.throat_radius,
                    grain_number=motor.grain_number,
                    grain_density=motor.grain_density,
                    grain_outer_radius=motor.grain_outer_radius,
                    grain_initial_inner_radius=motor.grain_initial_inner_radius,
                    grain_initial_height=motor.grain_initial_height,
                    grain_separation=motor.grain_separation,
                    grains_center_of_mass_position=motor.grains_center_of_mass_position,
                )
            case MotorKinds.SOLID:
                grain_params = {
                    'grain_number': motor.grain_number,
                    'grain_density': motor.grain_density,
                    'grain_outer_radius': motor.grain_outer_radius,
                    'grain_initial_inner_radius': motor.grain_initial_inner_radius,
                    'grain_initial_height': motor.grain_initial_height,
                    'grain_separation': motor.grain_separation,
                    'grains_center_of_mass_position': motor.grains_center_of_mass_position,
                }

                missing = [
                    key for key, value in grain_params.items() if value is None
                ]
                if missing:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=(
                            "Solid motor requires grain configuration: missing "
                            + ', '.join(missing)
                        ),
                    )

                optional_params = {}
                if motor.throat_radius is not None:
                    optional_params['throat_radius'] = motor.throat_radius

                rocketpy_motor = SolidMotor(
                    **motor_core,
                    **grain_params,
                    **optional_params,
                )
            case _:
                # GenericMotor requires burn_time even though it's optional
                # for the other motor kinds — surface the constraint at the
                # API boundary instead of letting rocketpy raise a
                # confusing stack trace deeper in construction.
                if motor.burn_time is None:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="burn_time is required for generic motors.",
                    )
                # nozzle_position is already forwarded via motor_core when
                # the client supplied it; GenericMotor's own default (0)
                # applies otherwise.
                rocketpy_motor = GenericMotor(
                    **motor_core,
                    chamber_radius=motor.chamber_radius,
                    chamber_height=motor.chamber_height,
                    chamber_position=motor.chamber_position,
                    propellant_initial_mass=motor.propellant_initial_mass,
                )

        if motor.motor_kind not in (MotorKinds.SOLID, MotorKinds.GENERIC):
            for tank in motor.tanks or []:
                tank_core = {
                    "name": tank.name,
                    "geometry": _build_rocketpy_tank_geometry(tank.geometry),
                    "flux_time": tank.flux_time,
                    "gas": _build_rocketpy_fluid(tank.gas),
                    "liquid": _build_rocketpy_fluid(tank.liquid),
                    "discretize": tank.discretize,
                }

                match tank.tank_kind:
                    case TankKinds.LEVEL:
                        rocketpy_tank = LevelBasedTank(
                            **tank_core, liquid_height=tank.liquid_height
                        )
                    case TankKinds.MASS:
                        rocketpy_tank = MassBasedTank(
                            **tank_core,
                            liquid_mass=tank.liquid_mass,
                            gas_mass=tank.gas_mass,
                        )
                    case TankKinds.MASS_FLOW:
                        rocketpy_tank = MassFlowRateBasedTank(
                            **tank_core,
                            gas_mass_flow_rate_in=tank.gas_mass_flow_rate_in,
                            gas_mass_flow_rate_out=tank.gas_mass_flow_rate_out,
                            liquid_mass_flow_rate_in=tank.liquid_mass_flow_rate_in,
                            liquid_mass_flow_rate_out=tank.liquid_mass_flow_rate_out,
                            initial_liquid_mass=tank.initial_liquid_mass,
                            initial_gas_mass=tank.initial_gas_mass,
                        )
                    case TankKinds.ULLAGE:
                        rocketpy_tank = UllageBasedTank(
                            **tank_core, ullage=tank.ullage
                        )
                rocketpy_motor.add_tank(rocketpy_tank, tank.position)

        return cls(motor=rocketpy_motor)

    @property
    def motor(self) -> RocketPyMotor:
        return self._motor

    @motor.setter
    def motor(self, motor: RocketPyMotor):
        self._motor = motor

    def get_motor_simulation(self) -> MotorSimulation:
        """
        Get the simulation of the motor.

        Returns:
            MotorSimulation
        """
        encoded_attributes = collect_attributes(
            self.motor,
            [MotorSimulation],
        )
        motor_simulation = MotorSimulation(**encoded_attributes)
        return motor_simulation

    def get_motor_binary(self) -> bytes:
        """
        Get the binary representation of the motor.

        Returns:
            bytes
        """
        return dill.dumps(self.motor)

    # --------------------------------------------------------------------
    # Drawing geometry
    # --------------------------------------------------------------------
    def get_drawing_geometry(
        self,
        motor_position: float = 0.0,
        parent_csys: int = 1,
    ) -> MotorDrawingGeometryView:
        """Build a motor-only drawing-geometry response.

        Defaults render the motor at its own coordinate origin
        (`motor_position=0`, `parent_csys=1`) so the payload can be used
        standalone in the playground's "motor-only" view. Callers that
        embed the motor into a rocket (see ``RocketService``) pass the
        rocket-level position + csys to align the motor inside the rocket
        frame.

        Raises:
            HTTPException 422 if the motor has no drawable patches.
        """
        motor_geometry, _nozzle_position = self.build_drawing_geometry(
            motor_position=motor_position, parent_csys=parent_csys
        )
        if motor_geometry is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Motor has no drawable geometry.",
            )
        # Fall back to the nozzle radius when the motor has no drawable
        # patches (e.g. EmptyMotor) so the bounds aren't a zero-height
        # line. Every real rocketpy motor class exposes nozzle_radius.
        fallback_radius = float(
            getattr(self._motor, "nozzle_radius", 0.0) or 0.0
        )
        return MotorDrawingGeometryView(
            motor=motor_geometry,
            coordinate_system_orientation=str(
                self._motor.coordinate_system_orientation
            ),
            bounds=_compute_motor_bounds(motor_geometry, fallback_radius),
        )

    def build_drawing_geometry(
        self,
        motor_position: float,
        parent_csys: int,
    ) -> tuple[MotorDrawingGeometry | None, float]:
        """Construct motor patches + the absolute nozzle x-position.

        Returned as a tuple so the rocket service can use the nozzle
        position when extending body tubes to meet the motor. Standalone
        motor rendering can discard the second element.
        """
        motor = self._motor
        total_csys = parent_csys * motor._csys
        nozzle_position = motor_position + motor.nozzle_position * total_csys

        if isinstance(motor, EmptyMotor):
            return (
                MotorDrawingGeometry(
                    type="empty",
                    position=float(motor_position),
                    nozzle_position=float(nozzle_position),
                    patches=[],
                ),
                float(nozzle_position),
            )

        patches: list[MotorPatch] = []
        grains_cm_position: float | None = None
        motor_type = "generic"

        if isinstance(motor, SolidMotor):
            motor_type = "solid"
            grains_cm_position = (
                motor_position
                + motor.grains_center_of_mass_position * total_csys
            )
            chamber = motor.plots._generate_combustion_chamber(
                translate=(grains_cm_position, 0), label=None
            )
            patches.append(MotorPatch(role="chamber", **_polygon_xy(chamber)))
            for grain in motor.plots._generate_grains(
                translate=(grains_cm_position, 0)
            ):
                patches.append(MotorPatch(role="grain", **_polygon_xy(grain)))
        elif isinstance(motor, HybridMotor):
            motor_type = "hybrid"
            grains_cm_position = (
                motor_position
                + motor.grains_center_of_mass_position * total_csys
            )
            chamber = motor.plots._generate_combustion_chamber(
                translate=(grains_cm_position, 0), label=None
            )
            patches.append(MotorPatch(role="chamber", **_polygon_xy(chamber)))
            for grain in motor.plots._generate_grains(
                translate=(grains_cm_position, 0)
            ):
                patches.append(MotorPatch(role="grain", **_polygon_xy(grain)))
            for tank, _center in motor.plots._generate_positioned_tanks(
                translate=(motor_position, 0), csys=total_csys
            ):
                patches.append(MotorPatch(role="tank", **_polygon_xy(tank)))
        elif isinstance(motor, LiquidMotor):
            motor_type = "liquid"
            for tank, _center in motor.plots._generate_positioned_tanks(
                translate=(motor_position, 0), csys=total_csys
            ):
                patches.append(MotorPatch(role="tank", **_polygon_xy(tank)))
        elif isinstance(motor, GenericMotor):
            # RocketPy's Rocket.draw() does not render a chamber for
            # GenericMotor — `_generate_combustion_chamber` depends on
            # grain fields GenericMotor lacks. We build an equivalent
            # rectangular chamber from the GenericMotor fields so users
            # see their chamber geometry in the playground.
            motor_type = "generic"
            chamber_center_x = (
                motor_position + motor.chamber_position * total_csys
            )
            chamber_patch = _build_generic_chamber_patch(
                center_x=chamber_center_x,
                chamber_height=motor.chamber_height,
                chamber_radius=motor.chamber_radius,
            )
            patches.append(
                MotorPatch(role="chamber", **_polygon_xy(chamber_patch))
            )

        # Nozzle is always appended after the body so the motor-region
        # outline encompasses it, matching rocketpy.
        nozzle_patch = motor.plots._generate_nozzle(
            translate=(nozzle_position, 0), csys=parent_csys
        )
        patches.append(MotorPatch(role="nozzle", **_polygon_xy(nozzle_patch)))

        # Motor-region outline. `_generate_motor_region` reads patch.xy
        # arrays, so we rebuild matplotlib Polygons once from our
        # coordinate copies. Any failure here is logged and dropped; the
        # outline is advisory, not load-bearing.
        try:
            mpl_patches = [_rebuild_polygon(p.x, p.y) for p in patches]
            outline_patch = motor.plots._generate_motor_region(
                list_of_patches=mpl_patches
            )
            patches.insert(
                0, MotorPatch(role="outline", **_polygon_xy(outline_patch))
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to generate motor outline patch: %s", exc)

        return (
            MotorDrawingGeometry(
                type=motor_type,
                position=float(motor_position),
                nozzle_position=float(nozzle_position),
                grains_center_of_mass_position=(
                    float(grains_cm_position)
                    if grains_cm_position is not None
                    else None
                ),
                patches=patches,
            ),
            float(nozzle_position),
        )


def _compute_motor_bounds(
    motor: MotorDrawingGeometry, radius: float
) -> DrawingBounds:
    """Compute a tight bounding box for a motor-only drawing payload.

    Mirrors the rocket-side bounds helper but limited to motor patches —
    callers who want rocket-wide bounds use the rocket service's own
    computation.
    """
    xs: list[float] = []
    ys: list[float] = []
    for patch in motor.patches:
        xs += patch.x
        ys += patch.y
    if not xs:
        xs = [float(motor.position)]
    if not ys:
        ys = [-float(radius), float(radius)]
    return DrawingBounds(
        x_min=float(min(xs)),
        x_max=float(max(xs)),
        y_min=float(min(ys)),
        y_max=float(max(ys)),
    )

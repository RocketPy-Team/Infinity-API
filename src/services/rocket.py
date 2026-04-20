from typing import Self, List

import dill
import numpy as np

from rocketpy.motors import EmptyMotor, HybridMotor, LiquidMotor, SolidMotor
from rocketpy.rocket.rocket import Rocket as RocketPyRocket
from rocketpy.rocket.parachute import Parachute as RocketPyParachute
from rocketpy.rocket.aero_surface import (
    TrapezoidalFins as RocketPyTrapezoidalFins,
    EllipticalFins as RocketPyEllipticalFins,
    NoseCone as RocketPyNoseCone,
    Fins as RocketPyFins,
    Tail as RocketPyTail,
)
from rocketpy.rocket.aero_surface.generic_surface import GenericSurface

from fastapi import HTTPException, status

from src import logger
from src.models.rocket import RocketModel, Parachute
from src.models.sub.aerosurfaces import NoseCone, Tail, Fins
from src.services.motor import MotorService
from src.views.rocket import (
    RocketSimulation,
    RocketDrawingGeometry,
    NoseConeGeometry,
    TailGeometry,
    FinsGeometry,
    FinOutline,
    TubeGeometry,
    MotorDrawingGeometry,
    MotorPatch,
    RailButtonsGeometry,
    SensorGeometry,
    DrawingBounds,
)
from src.views.motor import MotorSimulation
from src.utils import collect_attributes


class RocketService:
    _rocket: RocketPyRocket

    def __init__(self, rocket: RocketPyRocket = None):
        self._rocket = rocket

    @classmethod
    def from_rocket_model(cls, rocket: RocketModel) -> Self:
        """
        Get the rocketpy rocket object.

        Returns:
            RocketService containing the rocketpy rocket object.
        """

        # Core
        rocketpy_rocket = RocketPyRocket(
            radius=rocket.radius,
            mass=rocket.mass,
            inertia=rocket.inertia,
            power_off_drag=rocket.power_off_drag,
            power_on_drag=rocket.power_on_drag,
            center_of_mass_without_motor=rocket.center_of_mass_without_motor,
            coordinate_system_orientation=rocket.coordinate_system_orientation,
        )
        rocketpy_rocket.add_motor(
            MotorService.from_motor_model(rocket.motor).motor,
            rocket.motor_position,
        )

        # RailButtons
        if rocket.rail_buttons:
            rocketpy_rocket.set_rail_buttons(
                upper_button_position=rocket.rail_buttons.upper_button_position,
                lower_button_position=rocket.rail_buttons.lower_button_position,
                angular_position=rocket.rail_buttons.angular_position,
            )

        # NoseCone
        if rocket.nose:
            nose = cls.get_rocketpy_nose(rocket.nose)
            rocketpy_rocket.add_surfaces(nose, nose.position)

        # FinSet
        if rocket.fins:
            rocketpy_finset_list = cls.get_rocketpy_finset_list_from_fins_list(
                rocket.fins
            )
            for finset in rocketpy_finset_list:
                rocketpy_rocket.add_surfaces(finset, finset.position)

        # Tail
        if rocket.tail:
            tail = cls.get_rocketpy_tail(rocket.tail)
            rocketpy_rocket.add_surfaces(tail, tail.position)

        # Air Brakes

        # Parachutes
        if rocket.parachutes:
            for parachute in rocket.parachutes:
                if cls.check_parachute_trigger(parachute.trigger):
                    rocketpy_parachute = cls.get_rocketpy_parachute(parachute)
                    rocketpy_rocket.parachutes.append(rocketpy_parachute)
                else:
                    logger.warning(
                        "Parachute trigger not valid. Skipping parachute."
                    )
                    continue

        return cls(rocket=rocketpy_rocket)

    @property
    def rocket(self) -> RocketPyRocket:
        return self._rocket

    @rocket.setter
    def rocket(self, rocket: RocketPyRocket):
        self._rocket = rocket

    def get_rocket_simulation(self) -> RocketSimulation:
        """
        Get the simulation of the rocket.

        Returns:
            RocketSimulation
        """
        encoded_attributes = collect_attributes(
            self.rocket, [RocketSimulation, MotorSimulation]
        )
        rocket_simulation = RocketSimulation(**encoded_attributes)
        return rocket_simulation

    def get_rocket_binary(self) -> bytes:
        """
        Get the binary representation of the rocket.

        Returns:
            bytes
        """
        return dill.dumps(self.rocket)

    def get_drawing_geometry(self) -> RocketDrawingGeometry:
        """
        Build the drawing-geometry payload that mirrors rocketpy.Rocket.draw().

        Coordinates are emitted in the draw frame used by _RocketPlots: the
        axial axis is x (applying rocket._csys), the radial axis is y with the
        caller expected to mirror (x, y) and (x, -y) for the two halves of
        nose/tail/body, and each fin outline is a closed polyline in that
        same frame.

        Returns:
            RocketDrawingGeometry

        Raises:
            HTTP 422: if the rocket has no aerodynamic surfaces to draw.
        """
        rocket = self._rocket

        if not rocket.aerodynamic_surfaces:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Rocket must have at least one aerodynamic surface "
                    "before a drawing can be produced."
                ),
            )

        csys = rocket._csys
        rocket.aerodynamic_surfaces.sort_by_position(reverse=(csys == 1))

        nose_cones: list[NoseConeGeometry] = []
        tails: list[TailGeometry] = []
        fins: list[FinsGeometry] = []
        # drawn_surfaces mirrors the tuples that _RocketPlots._draw_tubes
        # consumes: (surface, reference_x, radius_at_end, last_x).
        drawn_surfaces: list[tuple] = []

        for surface, position in rocket.aerodynamic_surfaces:
            position_z = position.z
            if isinstance(surface, RocketPyNoseCone):
                x_vals = (-csys * np.asarray(surface.shape_vec[0]) + position_z)
                y_vals = np.asarray(surface.shape_vec[1])
                nose_cones.append(
                    NoseConeGeometry(
                        name=getattr(surface, "name", None),
                        kind=getattr(surface, "kind", None),
                        position=float(position_z),
                        x=x_vals.tolist(),
                        y=y_vals.tolist(),
                    )
                )
                drawn_surfaces.append(
                    (surface, float(x_vals[-1]), float(surface.rocket_radius), float(x_vals[-1]))
                )
            elif isinstance(surface, RocketPyTail):
                x_vals = (-csys * np.asarray(surface.shape_vec[0]) + position_z)
                y_vals = np.asarray(surface.shape_vec[1])
                tails.append(
                    TailGeometry(
                        name=getattr(surface, "name", None),
                        position=float(position_z),
                        x=x_vals.tolist(),
                        y=y_vals.tolist(),
                    )
                )
                drawn_surfaces.append(
                    (
                        surface,
                        float(position_z),
                        float(surface.bottom_radius),
                        float(x_vals[-1]),
                    )
                )
            elif isinstance(surface, RocketPyFins):
                num_fins = surface.n
                x_fin = -csys * np.asarray(surface.shape_vec[0]) + position_z
                y_fin = np.asarray(surface.shape_vec[1]) + surface.rocket_radius
                outlines: list[FinOutline] = []
                last_x_rotated = float(x_fin[-1])
                for i in range(num_fins):
                    angle = 2 * np.pi * i / num_fins
                    rotation_matrix = np.array(
                        [[1, 0], [0, np.cos(angle)]]
                    )
                    rotated = rotation_matrix @ np.vstack((x_fin, y_fin))
                    outlines.append(
                        FinOutline(
                            x=rotated[0].tolist(),
                            y=rotated[1].tolist(),
                        )
                    )
                    last_x_rotated = float(rotated[0][-1])
                kind = (
                    "trapezoidal"
                    if isinstance(surface, RocketPyTrapezoidalFins)
                    else "elliptical"
                    if isinstance(surface, RocketPyEllipticalFins)
                    else "free_form"
                )
                fins.append(
                    FinsGeometry(
                        name=getattr(surface, "name", None),
                        kind=kind,
                        n=int(num_fins),
                        cant_angle_deg=float(getattr(surface, "cant_angle", 0.0) or 0.0),
                        position=float(position_z),
                        outlines=outlines,
                    )
                )
                drawn_surfaces.append(
                    (
                        surface,
                        float(position_z),
                        float(surface.rocket_radius),
                        last_x_rotated,
                    )
                )
            elif isinstance(surface, GenericSurface):
                # Generic surfaces aren't part of the rendered rocket shell;
                # they contribute a reference point for tube continuity.
                drawn_surfaces.append(
                    (
                        surface,
                        float(position_z),
                        float(rocket.radius),
                        float(position_z),
                    )
                )

        tubes = self._build_tubes(drawn_surfaces)
        motor_geometry, nozzle_position = self._build_motor_geometry(csys)
        tubes += self._build_nozzle_tube(tubes, drawn_surfaces, nozzle_position, csys)
        rail_buttons = self._build_rail_buttons(csys)
        sensors = self._build_sensors()

        try:
            center_of_mass = float(rocket.center_of_mass(0))
        except Exception:  # pragma: no cover - defensive; rocket may not be fully built
            center_of_mass = None
        try:
            cp_position = float(rocket.cp_position(0))
        except Exception:  # pragma: no cover
            cp_position = None

        bounds = self._compute_bounds(
            nose_cones, tails, fins, tubes, motor_geometry, rocket.radius
        )

        return RocketDrawingGeometry(
            radius=float(rocket.radius),
            csys=int(csys),
            coordinate_system_orientation=str(rocket.coordinate_system_orientation),
            nose_cones=nose_cones,
            tails=tails,
            fins=fins,
            tubes=tubes,
            motor=motor_geometry,
            rail_buttons=rail_buttons,
            center_of_mass=center_of_mass,
            cp_position=cp_position,
            sensors=sensors,
            bounds=bounds,
        )

    @staticmethod
    def _build_tubes(drawn_surfaces: list) -> list[TubeGeometry]:
        tubes: list[TubeGeometry] = []
        for i, d_surface in enumerate(drawn_surfaces):
            surface, position, radius, last_x = d_surface
            if i == len(drawn_surfaces) - 1:
                if isinstance(surface, RocketPyTail):
                    continue
                x_start, x_end = position, last_x
            else:
                next_position = drawn_surfaces[i + 1][1]
                x_start, x_end = last_x, next_position
            tubes.append(
                TubeGeometry(
                    x_start=float(x_start),
                    x_end=float(x_end),
                    radius=float(radius),
                )
            )
        return tubes

    def _build_motor_geometry(
        self, csys: int
    ) -> tuple[MotorDrawingGeometry | None, float]:
        rocket = self._rocket
        motor = rocket.motor
        total_csys = csys * motor._csys
        nozzle_position = (
            rocket.motor_position + motor.nozzle_position * total_csys
        )

        if isinstance(motor, EmptyMotor):
            return (
                MotorDrawingGeometry(
                    type="empty",
                    position=float(rocket.motor_position),
                    nozzle_position=float(nozzle_position),
                    patches=[],
                ),
                float(nozzle_position),
            )

        patches: list[MotorPatch] = []
        grains_cm_position: float | None = None

        if isinstance(motor, SolidMotor):
            motor_type = "solid"
            grains_cm_position = (
                rocket.motor_position
                + motor.grains_center_of_mass_position * total_csys
            )
            chamber = motor.plots._generate_combustion_chamber(
                translate=(grains_cm_position, 0), label=None
            )
            patches.append(
                MotorPatch(role="chamber", **_polygon_xy(chamber))
            )
            for grain in motor.plots._generate_grains(
                translate=(grains_cm_position, 0)
            ):
                patches.append(
                    MotorPatch(role="grain", **_polygon_xy(grain))
                )
        elif isinstance(motor, HybridMotor):
            motor_type = "hybrid"
            grains_cm_position = (
                rocket.motor_position
                + motor.grains_center_of_mass_position * total_csys
            )
            chamber = motor.plots._generate_combustion_chamber(
                translate=(grains_cm_position, 0), label=None
            )
            patches.append(
                MotorPatch(role="chamber", **_polygon_xy(chamber))
            )
            for grain in motor.plots._generate_grains(
                translate=(grains_cm_position, 0)
            ):
                patches.append(
                    MotorPatch(role="grain", **_polygon_xy(grain))
                )
            for tank, _center in motor.plots._generate_positioned_tanks(
                translate=(rocket.motor_position, 0), csys=total_csys
            ):
                patches.append(
                    MotorPatch(role="tank", **_polygon_xy(tank))
                )
        elif isinstance(motor, LiquidMotor):
            motor_type = "liquid"
            for tank, _center in motor.plots._generate_positioned_tanks(
                translate=(rocket.motor_position, 0), csys=total_csys
            ):
                patches.append(
                    MotorPatch(role="tank", **_polygon_xy(tank))
                )
        else:
            motor_type = "generic"

        # Nozzle (added after so the outline encompasses it, matching rocketpy)
        nozzle_patch = motor.plots._generate_nozzle(
            translate=(nozzle_position, 0), csys=csys
        )
        patches.append(MotorPatch(role="nozzle", **_polygon_xy(nozzle_patch)))

        # Motor region outline. _generate_motor_region reads patch.xy arrays
        # so we need matplotlib Polygon objects; rebuild them once from our
        # coordinate copies.
        try:
            mpl_patches = [
                _rebuild_polygon(p.x, p.y) for p in patches
            ]
            outline_patch = motor.plots._generate_motor_region(
                list_of_patches=mpl_patches
            )
            patches.insert(
                0, MotorPatch(role="outline", **_polygon_xy(outline_patch))
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning(
                "Failed to generate motor outline patch: %s", exc
            )

        return (
            MotorDrawingGeometry(
                type=motor_type,
                position=float(rocket.motor_position),
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

    def _build_nozzle_tube(
        self,
        existing_tubes: list[TubeGeometry],
        drawn_surfaces: list,
        nozzle_position: float,
        csys: int,
    ) -> list[TubeGeometry]:
        if not drawn_surfaces:
            return []
        last_surface, _, last_radius, last_x = drawn_surfaces[-1]
        if isinstance(last_surface, RocketPyTail):
            return []
        if csys == 1 and nozzle_position < last_x:
            extra_x = nozzle_position
        elif csys == -1 and nozzle_position > last_x:
            extra_x = nozzle_position
        else:
            return []
        return [
            TubeGeometry(
                x_start=float(last_x),
                x_end=float(extra_x),
                radius=float(last_radius),
            )
        ]

    def _build_rail_buttons(self, csys: int) -> RailButtonsGeometry | None:
        rocket = self._rocket
        try:
            buttons, pos = rocket.rail_buttons[0]
        except IndexError:
            return None
        lower = float(pos.z)
        upper = lower + float(buttons.buttons_distance) * csys
        return RailButtonsGeometry(
            lower_x=lower,
            upper_x=upper,
            y=-float(rocket.radius),
            angular_position_deg=float(
                getattr(buttons, "angular_position", 0.0) or 0.0
            ),
        )

    def _build_sensors(self) -> list[SensorGeometry]:
        rocket = self._rocket
        sensors: list[SensorGeometry] = []
        for sensor_pos in getattr(rocket, "sensors", []) or []:
            sensor = sensor_pos[0]
            pos = sensor_pos[1]
            normal = getattr(sensor, "normal_vector", None)
            normal_tuple = (
                (float(normal.x), float(normal.y), float(normal.z))
                if normal is not None
                else (0.0, 0.0, 0.0)
            )
            sensors.append(
                SensorGeometry(
                    name=getattr(sensor, "name", None),
                    position=(float(pos[0]), float(pos[1]), float(pos[2])),
                    normal=normal_tuple,
                )
            )
        return sensors

    @staticmethod
    def _compute_bounds(
        nose_cones: list[NoseConeGeometry],
        tails: list[TailGeometry],
        fins: list[FinsGeometry],
        tubes: list[TubeGeometry],
        motor: MotorDrawingGeometry | None,
        radius: float,
    ) -> DrawingBounds:
        xs: list[float] = []
        ys: list[float] = []
        for nc in nose_cones:
            xs += nc.x
            ys += nc.y
            ys += [-v for v in nc.y]
        for tail in tails:
            xs += tail.x
            ys += tail.y
            ys += [-v for v in tail.y]
        for finset in fins:
            for outline in finset.outlines:
                xs += outline.x
                ys += outline.y
        for tube in tubes:
            xs += [tube.x_start, tube.x_end]
            ys += [tube.radius, -tube.radius]
        if motor is not None:
            for patch in motor.patches:
                xs += patch.x
                ys += patch.y
        if not xs:
            xs = [0.0]
        if not ys:
            ys = [-float(radius), float(radius)]
        return DrawingBounds(
            x_min=float(min(xs)),
            x_max=float(max(xs)),
            y_min=float(min(ys)),
            y_max=float(max(ys)),
        )

    @staticmethod
    def get_rocketpy_nose(nose: NoseCone) -> RocketPyNoseCone:
        """
        Get a rocketpy nose cone object.

        Returns:
            RocketPyNoseCone
        """

        try:
            rocketpy_nose = RocketPyNoseCone(
                name=nose.name,
                length=nose.length,
                kind=nose.kind,
                base_radius=nose.base_radius,
                rocket_radius=nose.rocket_radius,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc

        rocketpy_nose.position = nose.position
        return rocketpy_nose

    @classmethod
    def get_rocketpy_finset_list_from_fins_list(
        cls, fins_list: List[Fins]
    ) -> List[RocketPyFins]:
        return [
            cls.get_rocketpy_finset(fins, fins.fins_kind) for fins in fins_list
        ]

    @staticmethod
    def get_rocketpy_finset(fins: Fins, kind: str) -> RocketPyFins:
        """
        Get a rocketpy finset object.

        Returns one of:
            RocketPyTrapezoidalFins
            RocketPyEllipticalFins
        """

        if fins.rocket_radius is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Fin definition missing required field 'rocket_radius'",
            )

        base_kwargs = {
            'n': fins.n,
            'name': fins.name,
            'root_chord': fins.root_chord,
            'span': fins.span,
            'rocket_radius': fins.rocket_radius,
        }

        extra_kwargs = {
            key: value
            for key, value in fins.get_additional_parameters().items()
            if key not in base_kwargs
        }
        
        match kind:
            case "trapezoidal":
                factory = RocketPyTrapezoidalFins
            case "elliptical":
                factory = RocketPyEllipticalFins
            case _:
                raise ValueError(f"Invalid fins kind: {kind}")

        try:
            rocketpy_finset = factory(
                **base_kwargs,
                **extra_kwargs,
            )
        except (TypeError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc

        rocketpy_finset.position = fins.position
        return rocketpy_finset

    @staticmethod
    def get_rocketpy_tail(tail: Tail) -> RocketPyTail:
        """
        Get a rocketpy tail object.

        Returns:
            RocketPyTail
        """
        rocketpy_tail = RocketPyTail(
            name=tail.name,
            top_radius=tail.top_radius,
            bottom_radius=tail.bottom_radius,
            length=tail.length,
            rocket_radius=tail.radius,
        )
        rocketpy_tail.position = tail.position
        return rocketpy_tail

    @staticmethod
    def get_rocketpy_parachute(parachute: Parachute) -> RocketPyParachute:
        """
        Get a rocketpy parachute object.

        Returns:
            RocketPyParachute
        """
        rocketpy_parachute = RocketPyParachute(
            name=parachute.name,
            cd_s=parachute.cd_s,
            trigger=parachute.trigger,
            sampling_rate=parachute.sampling_rate,
            lag=parachute.lag,
            noise=parachute.noise,
        )
        return rocketpy_parachute

    @staticmethod
    def check_parachute_trigger(trigger) -> bool:
        """
        Check if the trigger expression is valid.

        Args:
            trigger: str | float

        Returns:
            bool: True if the expression is valid, False otherwise.
        """

        if trigger == "apogee":
            return True
        if isinstance(trigger, (int, float)):
            return True
        return False


def _polygon_xy(patch) -> dict:
    """Extract (x, y) coordinate lists from a matplotlib Polygon patch.

    The generator helpers on rocketpy's _MotorPlots return matplotlib
    Polygon objects; we only ever use them as a data carrier (patch.xy
    is an Nx2 numpy array), never for rendering.
    """
    xy = np.asarray(patch.xy)
    return {"x": xy[:, 0].tolist(), "y": xy[:, 1].tolist()}


def _rebuild_polygon(x: list[float], y: list[float]):
    """Rebuild a matplotlib Polygon from coordinate lists.

    Used only so _MotorPlots._generate_motor_region can read patch.xy
    bounds when we assemble the motor outline.
    """
    from matplotlib.patches import Polygon  # local import keeps service cold-start lean
    return Polygon(np.column_stack([np.asarray(x), np.asarray(y)]))

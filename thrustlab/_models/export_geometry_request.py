from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.export_geometry_request_format import ExportGeometryRequestFormat
from thrustlab._models.export_geometry_request_rotation_type_0 import ExportGeometryRequestRotationType0
from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="ExportGeometryRequest")


@_attrs_define
class ExportGeometryRequest:
    """Export the editor's working geometry (or a saved prop) to CAD bytes.

    Exactly ONE of (``section_coords`` inline | ``component_id`` saved-prop) is
    required (mutually exclusive — the ``@model_validator``). The inline path is
    the primary one: the editor always holds ``section_coords`` from
    ``/v1/geometry/generate``, so the route skips the DB entirely. The
    ``component_id`` path re-runs the deterministic geometry generator
    from the saved ``spec_json`` (caller-scoped, IDOR-safe at the route).

    Strictness (the geometry house style):

    * ``extra="forbid"`` — a stray field (e.g. a motor_id) is rejected.
    * every numeric field carries a bound; the geometry arrays are capped at 200
     stations and ``num_blades`` at 16 (the warm-set max) — the DoS guard, enforced BEFORE any loft.
    * when ``section_coords`` is present, every station must share the same point
     count (a well-posed loft requires it) — the ``@model_validator``.

        Attributes:
            chord (list[float] | None | Unset):
            component_id (None | str | Unset):
            diameter (float | None | Unset): Diameter in inches
            format_ (ExportGeometryRequestFormat | Unset):  Default: ExportGeometryRequestFormat.STEP.
            hub_radius (float | None | Unset):
            include_hub (bool | None | Unset):
            name (None | str | Unset):
            num_blades (int | Unset):  Default: 2.
            radius (list[float] | None | Unset): Absolute radii in meters
            rotation (ExportGeometryRequestRotationType0 | None | Unset):
            section_coords (list[Any] | None | Unset):
            sweep (list[float] | None | Unset):
            twist (list[float] | None | Unset): Twist in degrees
    """

    chord: list[float] | None | Unset = UNSET
    component_id: None | str | Unset = UNSET
    diameter: float | None | Unset = UNSET
    format_: ExportGeometryRequestFormat | Unset = ExportGeometryRequestFormat.STEP
    hub_radius: float | None | Unset = UNSET
    include_hub: bool | None | Unset = UNSET
    name: None | str | Unset = UNSET
    num_blades: int | Unset = 2
    radius: list[float] | None | Unset = UNSET
    rotation: ExportGeometryRequestRotationType0 | None | Unset = UNSET
    section_coords: list[Any] | None | Unset = UNSET
    sweep: list[float] | None | Unset = UNSET
    twist: list[float] | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        chord: list[float] | None | Unset
        if isinstance(self.chord, Unset):
            chord = UNSET
        elif isinstance(self.chord, list):
            chord = self.chord

        else:
            chord = self.chord

        component_id: None | str | Unset
        if isinstance(self.component_id, Unset):
            component_id = UNSET
        else:
            component_id = self.component_id

        diameter: float | None | Unset
        if isinstance(self.diameter, Unset):
            diameter = UNSET
        else:
            diameter = self.diameter

        format_: str | Unset = UNSET
        if not isinstance(self.format_, Unset):
            format_ = self.format_.value

        hub_radius: float | None | Unset
        if isinstance(self.hub_radius, Unset):
            hub_radius = UNSET
        else:
            hub_radius = self.hub_radius

        include_hub: bool | None | Unset
        if isinstance(self.include_hub, Unset):
            include_hub = UNSET
        else:
            include_hub = self.include_hub

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        num_blades = self.num_blades

        radius: list[float] | None | Unset
        if isinstance(self.radius, Unset):
            radius = UNSET
        elif isinstance(self.radius, list):
            radius = self.radius

        else:
            radius = self.radius

        rotation: None | str | Unset
        if isinstance(self.rotation, Unset):
            rotation = UNSET
        elif isinstance(self.rotation, ExportGeometryRequestRotationType0):
            rotation = self.rotation.value
        else:
            rotation = self.rotation

        section_coords: list[Any] | None | Unset
        if isinstance(self.section_coords, Unset):
            section_coords = UNSET
        elif isinstance(self.section_coords, list):
            section_coords = self.section_coords

        else:
            section_coords = self.section_coords

        sweep: list[float] | None | Unset
        if isinstance(self.sweep, Unset):
            sweep = UNSET
        elif isinstance(self.sweep, list):
            sweep = self.sweep

        else:
            sweep = self.sweep

        twist: list[float] | None | Unset
        if isinstance(self.twist, Unset):
            twist = UNSET
        elif isinstance(self.twist, list):
            twist = self.twist

        else:
            twist = self.twist

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if chord is not UNSET:
            field_dict["chord"] = chord
        if component_id is not UNSET:
            field_dict["component_id"] = component_id
        if diameter is not UNSET:
            field_dict["diameter"] = diameter
        if format_ is not UNSET:
            field_dict["format"] = format_
        if hub_radius is not UNSET:
            field_dict["hub_radius"] = hub_radius
        if include_hub is not UNSET:
            field_dict["include_hub"] = include_hub
        if name is not UNSET:
            field_dict["name"] = name
        if num_blades is not UNSET:
            field_dict["num_blades"] = num_blades
        if radius is not UNSET:
            field_dict["radius"] = radius
        if rotation is not UNSET:
            field_dict["rotation"] = rotation
        if section_coords is not UNSET:
            field_dict["section_coords"] = section_coords
        if sweep is not UNSET:
            field_dict["sweep"] = sweep
        if twist is not UNSET:
            field_dict["twist"] = twist

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_chord(data: object) -> list[float] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                chord_type_0 = cast(list[float], data)

                return chord_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[float] | None | Unset, data)

        chord = _parse_chord(d.pop("chord", UNSET))

        def _parse_component_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        component_id = _parse_component_id(d.pop("component_id", UNSET))

        def _parse_diameter(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        diameter = _parse_diameter(d.pop("diameter", UNSET))

        _format_ = d.pop("format", UNSET)
        format_: ExportGeometryRequestFormat | Unset
        if isinstance(_format_, Unset):
            format_ = UNSET
        else:
            format_ = ExportGeometryRequestFormat(_format_)

        def _parse_hub_radius(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        hub_radius = _parse_hub_radius(d.pop("hub_radius", UNSET))

        def _parse_include_hub(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        include_hub = _parse_include_hub(d.pop("include_hub", UNSET))

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        num_blades = d.pop("num_blades", UNSET)

        def _parse_radius(data: object) -> list[float] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                radius_type_0 = cast(list[float], data)

                return radius_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[float] | None | Unset, data)

        radius = _parse_radius(d.pop("radius", UNSET))

        def _parse_rotation(data: object) -> ExportGeometryRequestRotationType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                rotation_type_0 = ExportGeometryRequestRotationType0(data)

                return rotation_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ExportGeometryRequestRotationType0 | None | Unset, data)

        rotation = _parse_rotation(d.pop("rotation", UNSET))

        def _parse_section_coords(data: object) -> list[Any] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                section_coords_type_0 = cast(list[Any], data)

                return section_coords_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[Any] | None | Unset, data)

        section_coords = _parse_section_coords(d.pop("section_coords", UNSET))

        def _parse_sweep(data: object) -> list[float] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                sweep_type_0 = cast(list[float], data)

                return sweep_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[float] | None | Unset, data)

        sweep = _parse_sweep(d.pop("sweep", UNSET))

        def _parse_twist(data: object) -> list[float] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                twist_type_0 = cast(list[float], data)

                return twist_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[float] | None | Unset, data)

        twist = _parse_twist(d.pop("twist", UNSET))

        export_geometry_request = cls(
            chord=chord,
            component_id=component_id,
            diameter=diameter,
            format_=format_,
            hub_radius=hub_radius,
            include_hub=include_hub,
            name=name,
            num_blades=num_blades,
            radius=radius,
            rotation=rotation,
            section_coords=section_coords,
            sweep=sweep,
            twist=twist,
        )

        return export_geometry_request

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.v1_custom_component_override_spec_json import V1CustomComponentOverrideSpecJson


T = TypeVar("T", bound="V1CustomComponentOverride")


@_attrs_define
class V1CustomComponentOverride:
    """Per-request component override for custom-mode submissions.

    Mirrors :class:`app.schemas.simulation.CustomComponentOverride` but accepts
    a string base_component_id (raw UUID or ``comp_<ksuid>`` prefix) so callers
    can use whichever identifier form they hold. Resolved to a UUID in the v1
    POST handlers before handoff to the service layer.

        Attributes:
            name (str):
            spec_json (V1CustomComponentOverrideSpecJson):
            base_component_id (None | str | Unset):
    """

    name: str
    spec_json: V1CustomComponentOverrideSpecJson
    base_component_id: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        spec_json = self.spec_json.to_dict()

        base_component_id: None | str | Unset
        if isinstance(self.base_component_id, Unset):
            base_component_id = UNSET
        else:
            base_component_id = self.base_component_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
                "spec_json": spec_json,
            }
        )
        if base_component_id is not UNSET:
            field_dict["base_component_id"] = base_component_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.v1_custom_component_override_spec_json import V1CustomComponentOverrideSpecJson

        d = dict(src_dict)
        name = d.pop("name")

        spec_json = V1CustomComponentOverrideSpecJson.from_dict(d.pop("spec_json"))

        def _parse_base_component_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        base_component_id = _parse_base_component_id(d.pop("base_component_id", UNSET))

        v1_custom_component_override = cls(
            name=name,
            spec_json=spec_json,
            base_component_id=base_component_id,
        )

        return v1_custom_component_override

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.sweep_patch_plot_config_json_type_0_item import SweepPatchPlotConfigJsonType0Item


T = TypeVar("T", bound="SweepPatch")


@_attrs_define
class SweepPatch:
    """
    Attributes:
        is_starred (bool | None | Unset):
        name (None | str | Unset):
        plot_config_json (list[SweepPatchPlotConfigJsonType0Item] | None | Unset):
    """

    is_starred: bool | None | Unset = UNSET
    name: None | str | Unset = UNSET
    plot_config_json: list[SweepPatchPlotConfigJsonType0Item] | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        is_starred: bool | None | Unset
        if isinstance(self.is_starred, Unset):
            is_starred = UNSET
        else:
            is_starred = self.is_starred

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        plot_config_json: list[dict[str, Any]] | None | Unset
        if isinstance(self.plot_config_json, Unset):
            plot_config_json = UNSET
        elif isinstance(self.plot_config_json, list):
            plot_config_json = []
            for plot_config_json_type_0_item_data in self.plot_config_json:
                plot_config_json_type_0_item = plot_config_json_type_0_item_data.to_dict()
                plot_config_json.append(plot_config_json_type_0_item)

        else:
            plot_config_json = self.plot_config_json

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if is_starred is not UNSET:
            field_dict["is_starred"] = is_starred
        if name is not UNSET:
            field_dict["name"] = name
        if plot_config_json is not UNSET:
            field_dict["plot_config_json"] = plot_config_json

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.sweep_patch_plot_config_json_type_0_item import SweepPatchPlotConfigJsonType0Item

        d = dict(src_dict)

        def _parse_is_starred(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_starred = _parse_is_starred(d.pop("is_starred", UNSET))

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_plot_config_json(data: object) -> list[SweepPatchPlotConfigJsonType0Item] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                plot_config_json_type_0 = []
                _plot_config_json_type_0 = data
                for plot_config_json_type_0_item_data in _plot_config_json_type_0:
                    plot_config_json_type_0_item = SweepPatchPlotConfigJsonType0Item.from_dict(
                        plot_config_json_type_0_item_data
                    )

                    plot_config_json_type_0.append(plot_config_json_type_0_item)

                return plot_config_json_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[SweepPatchPlotConfigJsonType0Item] | None | Unset, data)

        plot_config_json = _parse_plot_config_json(d.pop("plot_config_json", UNSET))

        sweep_patch = cls(
            is_starred=is_starred,
            name=name,
            plot_config_json=plot_config_json,
        )

        return sweep_patch

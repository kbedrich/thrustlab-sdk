from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.pack_leaf_in import PackLeafIn
    from thrustlab._models.pack_parallel_in import PackParallelIn
    from thrustlab._models.pack_series_in import PackSeriesIn


T = TypeVar("T", bound="PackTopologyIn")


@_attrs_define
class PackTopologyIn:
    """
    Attributes:
        root (PackLeafIn | PackParallelIn | PackSeriesIn):
        bus_wire_resistance_mohm (float | Unset):  Default: 0.0.
        cross_charge_warning_acknowledged (bool | Unset):  Default: False.
        schema (Literal[1] | Unset):  Default: 1.
    """

    root: PackLeafIn | PackParallelIn | PackSeriesIn
    bus_wire_resistance_mohm: float | Unset = 0.0
    cross_charge_warning_acknowledged: bool | Unset = False
    schema: Literal[1] | Unset = 1

    def to_dict(self) -> dict[str, Any]:
        from thrustlab._models.pack_leaf_in import PackLeafIn
        from thrustlab._models.pack_series_in import PackSeriesIn

        root: dict[str, Any]
        if isinstance(self.root, PackLeafIn):
            root = self.root.to_dict()
        elif isinstance(self.root, PackSeriesIn):
            root = self.root.to_dict()
        else:
            root = self.root.to_dict()

        bus_wire_resistance_mohm = self.bus_wire_resistance_mohm

        cross_charge_warning_acknowledged = self.cross_charge_warning_acknowledged

        schema = self.schema

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "root": root,
            }
        )
        if bus_wire_resistance_mohm is not UNSET:
            field_dict["bus_wire_resistance_mohm"] = bus_wire_resistance_mohm
        if cross_charge_warning_acknowledged is not UNSET:
            field_dict["cross_charge_warning_acknowledged"] = cross_charge_warning_acknowledged
        if schema is not UNSET:
            field_dict["schema"] = schema

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.pack_leaf_in import PackLeafIn
        from thrustlab._models.pack_parallel_in import PackParallelIn
        from thrustlab._models.pack_series_in import PackSeriesIn

        d = dict(src_dict)

        def _parse_root(data: object) -> PackLeafIn | PackParallelIn | PackSeriesIn:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                root_type_0 = PackLeafIn.from_dict(data)

                return root_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                root_type_1 = PackSeriesIn.from_dict(data)

                return root_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            root_type_2 = PackParallelIn.from_dict(data)

            return root_type_2

        root = _parse_root(d.pop("root"))

        bus_wire_resistance_mohm = d.pop("bus_wire_resistance_mohm", UNSET)

        cross_charge_warning_acknowledged = d.pop("cross_charge_warning_acknowledged", UNSET)

        schema = cast(Literal[1] | Unset, d.pop("schema", UNSET))
        if schema != 1 and not isinstance(schema, Unset):
            raise ValueError(f"schema must match const 1, got '{schema}'")

        pack_topology_in = cls(
            root=root,
            bus_wire_resistance_mohm=bus_wire_resistance_mohm,
            cross_charge_warning_acknowledged=cross_charge_warning_acknowledged,
            schema=schema,
        )

        return pack_topology_in

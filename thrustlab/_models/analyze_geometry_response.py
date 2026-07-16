from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.analyze_station_row import AnalyzeStationRow


T = TypeVar("T", bound="AnalyzeGeometryResponse")


@_attrs_define
class AnalyzeGeometryResponse:
    """Bounded aero-only union response for all three modes.

    Every field is optional so a single shape carries a point, a sweep, OR a
    non-converged solve (``converged: false`` + ``reason``). NO motor/battery
    field anywhere.

        Attributes:
            mode (str):
            cp (float | None | Unset):
            ct (float | None | Unset):
            j (float | None | Unset):
            converged (bool | None | Unset):
            efficiency (float | None | Unset):
            object_ (str | Unset):  Default: 'geometry_analysis'.
            power (float | None | Unset):
            reason (None | str | Unset):
            rpm (float | None | Unset):
            stations (list[AnalyzeStationRow] | Unset):
            sweep_cp (list[float] | Unset):
            sweep_ct (list[float] | Unset):
            sweep_j (list[float] | Unset):
            sweep_eta (list[float | None] | Unset):
            thrust (float | None | Unset):
    """

    mode: str
    cp: float | None | Unset = UNSET
    ct: float | None | Unset = UNSET
    j: float | None | Unset = UNSET
    converged: bool | None | Unset = UNSET
    efficiency: float | None | Unset = UNSET
    object_: str | Unset = "geometry_analysis"
    power: float | None | Unset = UNSET
    reason: None | str | Unset = UNSET
    rpm: float | None | Unset = UNSET
    stations: list[AnalyzeStationRow] | Unset = UNSET
    sweep_cp: list[float] | Unset = UNSET
    sweep_ct: list[float] | Unset = UNSET
    sweep_j: list[float] | Unset = UNSET
    sweep_eta: list[float | None] | Unset = UNSET
    thrust: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        mode = self.mode

        cp: float | None | Unset
        if isinstance(self.cp, Unset):
            cp = UNSET
        else:
            cp = self.cp

        ct: float | None | Unset
        if isinstance(self.ct, Unset):
            ct = UNSET
        else:
            ct = self.ct

        j: float | None | Unset
        if isinstance(self.j, Unset):
            j = UNSET
        else:
            j = self.j

        converged: bool | None | Unset
        if isinstance(self.converged, Unset):
            converged = UNSET
        else:
            converged = self.converged

        efficiency: float | None | Unset
        if isinstance(self.efficiency, Unset):
            efficiency = UNSET
        else:
            efficiency = self.efficiency

        object_ = self.object_

        power: float | None | Unset
        if isinstance(self.power, Unset):
            power = UNSET
        else:
            power = self.power

        reason: None | str | Unset
        if isinstance(self.reason, Unset):
            reason = UNSET
        else:
            reason = self.reason

        rpm: float | None | Unset
        if isinstance(self.rpm, Unset):
            rpm = UNSET
        else:
            rpm = self.rpm

        stations: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.stations, Unset):
            stations = []
            for stations_item_data in self.stations:
                stations_item = stations_item_data.to_dict()
                stations.append(stations_item)

        sweep_cp: list[float] | Unset = UNSET
        if not isinstance(self.sweep_cp, Unset):
            sweep_cp = self.sweep_cp

        sweep_ct: list[float] | Unset = UNSET
        if not isinstance(self.sweep_ct, Unset):
            sweep_ct = self.sweep_ct

        sweep_j: list[float] | Unset = UNSET
        if not isinstance(self.sweep_j, Unset):
            sweep_j = self.sweep_j

        sweep_eta: list[float | None] | Unset = UNSET
        if not isinstance(self.sweep_eta, Unset):
            sweep_eta = []
            for sweep_eta_item_data in self.sweep_eta:
                sweep_eta_item: float | None
                sweep_eta_item = sweep_eta_item_data
                sweep_eta.append(sweep_eta_item)

        thrust: float | None | Unset
        if isinstance(self.thrust, Unset):
            thrust = UNSET
        else:
            thrust = self.thrust

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "mode": mode,
            }
        )
        if cp is not UNSET:
            field_dict["Cp"] = cp
        if ct is not UNSET:
            field_dict["Ct"] = ct
        if j is not UNSET:
            field_dict["J"] = j
        if converged is not UNSET:
            field_dict["converged"] = converged
        if efficiency is not UNSET:
            field_dict["efficiency"] = efficiency
        if object_ is not UNSET:
            field_dict["object"] = object_
        if power is not UNSET:
            field_dict["power"] = power
        if reason is not UNSET:
            field_dict["reason"] = reason
        if rpm is not UNSET:
            field_dict["rpm"] = rpm
        if stations is not UNSET:
            field_dict["stations"] = stations
        if sweep_cp is not UNSET:
            field_dict["sweep_Cp"] = sweep_cp
        if sweep_ct is not UNSET:
            field_dict["sweep_Ct"] = sweep_ct
        if sweep_j is not UNSET:
            field_dict["sweep_J"] = sweep_j
        if sweep_eta is not UNSET:
            field_dict["sweep_eta"] = sweep_eta
        if thrust is not UNSET:
            field_dict["thrust"] = thrust

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.analyze_station_row import AnalyzeStationRow

        d = dict(src_dict)
        mode = d.pop("mode")

        def _parse_cp(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        cp = _parse_cp(d.pop("Cp", UNSET))

        def _parse_ct(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        ct = _parse_ct(d.pop("Ct", UNSET))

        def _parse_j(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        j = _parse_j(d.pop("J", UNSET))

        def _parse_converged(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        converged = _parse_converged(d.pop("converged", UNSET))

        def _parse_efficiency(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        efficiency = _parse_efficiency(d.pop("efficiency", UNSET))

        object_ = d.pop("object", UNSET)

        def _parse_power(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        power = _parse_power(d.pop("power", UNSET))

        def _parse_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reason = _parse_reason(d.pop("reason", UNSET))

        def _parse_rpm(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        rpm = _parse_rpm(d.pop("rpm", UNSET))

        _stations = d.pop("stations", UNSET)
        stations: list[AnalyzeStationRow] | Unset = UNSET
        if _stations is not UNSET:
            stations = []
            for stations_item_data in _stations:
                stations_item = AnalyzeStationRow.from_dict(stations_item_data)

                stations.append(stations_item)

        sweep_cp = cast(list[float], d.pop("sweep_Cp", UNSET))

        sweep_ct = cast(list[float], d.pop("sweep_Ct", UNSET))

        sweep_j = cast(list[float], d.pop("sweep_J", UNSET))

        _sweep_eta = d.pop("sweep_eta", UNSET)
        sweep_eta: list[float | None] | Unset = UNSET
        if _sweep_eta is not UNSET:
            sweep_eta = []
            for sweep_eta_item_data in _sweep_eta:

                def _parse_sweep_eta_item(data: object) -> float | None:
                    if data is None:
                        return data
                    return cast(float | None, data)

                sweep_eta_item = _parse_sweep_eta_item(sweep_eta_item_data)

                sweep_eta.append(sweep_eta_item)

        def _parse_thrust(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        thrust = _parse_thrust(d.pop("thrust", UNSET))

        analyze_geometry_response = cls(
            mode=mode,
            cp=cp,
            ct=ct,
            j=j,
            converged=converged,
            efficiency=efficiency,
            object_=object_,
            power=power,
            reason=reason,
            rpm=rpm,
            stations=stations,
            sweep_cp=sweep_cp,
            sweep_ct=sweep_ct,
            sweep_j=sweep_j,
            sweep_eta=sweep_eta,
            thrust=thrust,
        )

        analyze_geometry_response.additional_properties = d
        return analyze_geometry_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

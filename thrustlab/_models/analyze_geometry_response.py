from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.analyze_geometry_response_envelope_limiting_factor_type_0 import (
    AnalyzeGeometryResponseEnvelopeLimitingFactorType0,
)
from thrustlab._models.analyze_geometry_response_envelope_status_type_0 import AnalyzeGeometryResponseEnvelopeStatusType0
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
            cp_raw (float | None | Unset): Power coefficient from the raw blade-element solve, before the empirical
                correction.
            ct (float | None | Unset):
            ct_raw (float | None | Unset): Thrust coefficient from the raw blade-element solve, before the empirical
                correction. The `stations` table integrates to this.
            j (float | None | Unset):
            converged (bool | None | Unset):
            efficiency (float | None | Unset):
            envelope_limiting_factor (AnalyzeGeometryResponseEnvelopeLimitingFactorType0 | None | Unset): Which dimension
                takes this solve outside the validation envelope. Absent when `envelope_status` is `validated` or absent.
            envelope_status (AnalyzeGeometryResponseEnvelopeStatusType0 | None | Unset): Where this solve sits relative to
                the published validation envelope (17 two-bladed APC Thin-Electric propellers, in diameter, advance ratio J <=
                0.95, tip Mach <= 0.43). `validated` = operating point and propeller both inside it. `partial` = outside in one
                dimension but still carrying most of the validated model — the common case, and not an error. `outside` = far
                enough out that the answer is the underlying physics model's own prediction. Absent when the envelope could not
                be established for this solve.
            object_ (str | Unset):  Default: 'geometry_analysis'.
            power (float | None | Unset):
            power_raw (float | None | Unset): Shaft power in W from the raw blade-element solve.
            reason (None | str | Unset):
            rpm (float | None | Unset):
            stations (list[AnalyzeStationRow] | Unset):
            sweep_cp (list[float] | Unset):
            sweep_ct (list[float] | Unset):
            sweep_j (list[float] | Unset):
            sweep_eta (list[float | None] | Unset):
            thrust (float | None | Unset):
            thrust_raw (float | None | Unset): Thrust in N from the raw blade-element solve. sum(dT_dr * dr) over `stations`
                equals THIS, not `thrust`.
            torque_raw (float | None | Unset): Torque in N·m from the raw blade-element solve. sum(dQ_dr * dr) over
                `stations` equals THIS.
    """

    mode: str
    cp: float | None | Unset = UNSET
    cp_raw: float | None | Unset = UNSET
    ct: float | None | Unset = UNSET
    ct_raw: float | None | Unset = UNSET
    j: float | None | Unset = UNSET
    converged: bool | None | Unset = UNSET
    efficiency: float | None | Unset = UNSET
    envelope_limiting_factor: AnalyzeGeometryResponseEnvelopeLimitingFactorType0 | None | Unset = UNSET
    envelope_status: AnalyzeGeometryResponseEnvelopeStatusType0 | None | Unset = UNSET
    object_: str | Unset = "geometry_analysis"
    power: float | None | Unset = UNSET
    power_raw: float | None | Unset = UNSET
    reason: None | str | Unset = UNSET
    rpm: float | None | Unset = UNSET
    stations: list[AnalyzeStationRow] | Unset = UNSET
    sweep_cp: list[float] | Unset = UNSET
    sweep_ct: list[float] | Unset = UNSET
    sweep_j: list[float] | Unset = UNSET
    sweep_eta: list[float | None] | Unset = UNSET
    thrust: float | None | Unset = UNSET
    thrust_raw: float | None | Unset = UNSET
    torque_raw: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        mode = self.mode

        cp: float | None | Unset
        if isinstance(self.cp, Unset):
            cp = UNSET
        else:
            cp = self.cp

        cp_raw: float | None | Unset
        if isinstance(self.cp_raw, Unset):
            cp_raw = UNSET
        else:
            cp_raw = self.cp_raw

        ct: float | None | Unset
        if isinstance(self.ct, Unset):
            ct = UNSET
        else:
            ct = self.ct

        ct_raw: float | None | Unset
        if isinstance(self.ct_raw, Unset):
            ct_raw = UNSET
        else:
            ct_raw = self.ct_raw

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

        envelope_limiting_factor: None | str | Unset
        if isinstance(self.envelope_limiting_factor, Unset):
            envelope_limiting_factor = UNSET
        elif isinstance(self.envelope_limiting_factor, AnalyzeGeometryResponseEnvelopeLimitingFactorType0):
            envelope_limiting_factor = self.envelope_limiting_factor.value
        else:
            envelope_limiting_factor = self.envelope_limiting_factor

        envelope_status: None | str | Unset
        if isinstance(self.envelope_status, Unset):
            envelope_status = UNSET
        elif isinstance(self.envelope_status, AnalyzeGeometryResponseEnvelopeStatusType0):
            envelope_status = self.envelope_status.value
        else:
            envelope_status = self.envelope_status

        object_ = self.object_

        power: float | None | Unset
        if isinstance(self.power, Unset):
            power = UNSET
        else:
            power = self.power

        power_raw: float | None | Unset
        if isinstance(self.power_raw, Unset):
            power_raw = UNSET
        else:
            power_raw = self.power_raw

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

        thrust_raw: float | None | Unset
        if isinstance(self.thrust_raw, Unset):
            thrust_raw = UNSET
        else:
            thrust_raw = self.thrust_raw

        torque_raw: float | None | Unset
        if isinstance(self.torque_raw, Unset):
            torque_raw = UNSET
        else:
            torque_raw = self.torque_raw

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "mode": mode,
            }
        )
        if cp is not UNSET:
            field_dict["Cp"] = cp
        if cp_raw is not UNSET:
            field_dict["Cp_raw"] = cp_raw
        if ct is not UNSET:
            field_dict["Ct"] = ct
        if ct_raw is not UNSET:
            field_dict["Ct_raw"] = ct_raw
        if j is not UNSET:
            field_dict["J"] = j
        if converged is not UNSET:
            field_dict["converged"] = converged
        if efficiency is not UNSET:
            field_dict["efficiency"] = efficiency
        if envelope_limiting_factor is not UNSET:
            field_dict["envelope_limiting_factor"] = envelope_limiting_factor
        if envelope_status is not UNSET:
            field_dict["envelope_status"] = envelope_status
        if object_ is not UNSET:
            field_dict["object"] = object_
        if power is not UNSET:
            field_dict["power"] = power
        if power_raw is not UNSET:
            field_dict["power_raw"] = power_raw
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
        if thrust_raw is not UNSET:
            field_dict["thrust_raw"] = thrust_raw
        if torque_raw is not UNSET:
            field_dict["torque_raw"] = torque_raw

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

        def _parse_cp_raw(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        cp_raw = _parse_cp_raw(d.pop("Cp_raw", UNSET))

        def _parse_ct(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        ct = _parse_ct(d.pop("Ct", UNSET))

        def _parse_ct_raw(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        ct_raw = _parse_ct_raw(d.pop("Ct_raw", UNSET))

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

        def _parse_envelope_limiting_factor(
            data: object,
        ) -> AnalyzeGeometryResponseEnvelopeLimitingFactorType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                envelope_limiting_factor_type_0 = AnalyzeGeometryResponseEnvelopeLimitingFactorType0(data)

                return envelope_limiting_factor_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AnalyzeGeometryResponseEnvelopeLimitingFactorType0 | None | Unset, data)

        envelope_limiting_factor = _parse_envelope_limiting_factor(d.pop("envelope_limiting_factor", UNSET))

        def _parse_envelope_status(data: object) -> AnalyzeGeometryResponseEnvelopeStatusType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                envelope_status_type_0 = AnalyzeGeometryResponseEnvelopeStatusType0(data)

                return envelope_status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AnalyzeGeometryResponseEnvelopeStatusType0 | None | Unset, data)

        envelope_status = _parse_envelope_status(d.pop("envelope_status", UNSET))

        object_ = d.pop("object", UNSET)

        def _parse_power(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        power = _parse_power(d.pop("power", UNSET))

        def _parse_power_raw(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        power_raw = _parse_power_raw(d.pop("power_raw", UNSET))

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

        def _parse_thrust_raw(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        thrust_raw = _parse_thrust_raw(d.pop("thrust_raw", UNSET))

        def _parse_torque_raw(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        torque_raw = _parse_torque_raw(d.pop("torque_raw", UNSET))

        analyze_geometry_response = cls(
            mode=mode,
            cp=cp,
            cp_raw=cp_raw,
            ct=ct,
            ct_raw=ct_raw,
            j=j,
            converged=converged,
            efficiency=efficiency,
            envelope_limiting_factor=envelope_limiting_factor,
            envelope_status=envelope_status,
            object_=object_,
            power=power,
            power_raw=power_raw,
            reason=reason,
            rpm=rpm,
            stations=stations,
            sweep_cp=sweep_cp,
            sweep_ct=sweep_ct,
            sweep_j=sweep_j,
            sweep_eta=sweep_eta,
            thrust=thrust,
            thrust_raw=thrust_raw,
            torque_raw=torque_raw,
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

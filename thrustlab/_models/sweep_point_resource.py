from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from thrustlab._models.sweep_point_inputs import SweepPointInputs
    from thrustlab._models.sweep_point_resource_rotors_type_0 import SweepPointResourceRotorsType0


T = TypeVar("T", bound="SweepPointResource")


@_attrs_define
class SweepPointResource:
    """A single sweep grid point.

    ``rotors`` is the full per-point solver result dict — keyed per-rotor
    ("1", "2"...) plus the "All"/"Battery" aggregates — mirroring
    ``SimulationResource.result``. Each per-rotor entry follows the canonical
    snake_case ``SimulationResultV1`` shape (wired at read time in a later
    wave); the schema below references that shape so an SDK/consumer sees the
    canonical per-rotor keys.

    NON-coercing rationale: the runtime type stays a raw
    ``dict[str, dict[str, Any]]`` — NOT a coercing per-rotor ``SimulationResultV1``
    model. Coercing every rotor value through that model would re-introduce the
    2026-06-02 aggregate-drop regression on sweep points, silently dropping the
    "All"/"Battery" aggregate-only fields (Max T_core, Cell voltages...). See
    the matching note on ``SimulationResource.result`` (serializers_simulations.py).
    The per-rotor snake shape is documented via the schema reference only; the
    values are never re-validated through a model.

        Attributes:
            failed (bool):
            index (int):
            inputs (SweepPointInputs): ESC-13 item 4 — the operating condition this grid point was solved at.

                Previously typed ``dict[str, Any]``, which is the wire equivalent of saying
                nothing: an SDK user got an untyped bag and had to learn the key set by
                running a sweep and reading one. ESC-13 already made the RUNTIME blob
                self-describing (it is built from the point rather than from a hardcoded
                five-key literal, so a new axis appears the day it lands); this makes the
                CONTRACT say so too.

                ``extra="allow"`` is load-bearing, not laziness. Two families of key are
                generated per-sweep and cannot be enumerated in a static model:

                  * ``tilt_<group_index>`` — group-targeted tilt is one grid dimension per
                    MASKED rotor group, so the key set depends on the mask.
                  * ``component_<axis>_<slots>`` — a component axis contributes its selected
                    index under a name encoding the slots it spans (``component_motor_0``,
                    or ``component_motor_0-2`` when synced).

                Declaring those away would be worse than leaving the model untyped, because
                a strict model would DROP them at serialization — the same failure mode as
                the 2026-06-02 aggregate-drop that ``rotors`` is deliberately non-coercing to
                avoid. Every declared field is optional and permissively typed for the same
                reason: this model documents the shape, it does not police it.
            is_starred (bool):
            object_ (Literal['sweep_point']):
            rotors (None | SweepPointResourceRotorsType0): Per-point rotor results, keyed per-rotor ("1", "2", ...) plus the
                "All"/"Battery" aggregates. Each per-rotor entry follows the canonical snake_case SimulationResultV1 shape; NON-
                coercing at runtime so aggregate-only fields are never dropped.
    """

    failed: bool
    index: int
    inputs: SweepPointInputs
    is_starred: bool
    object_: Literal["sweep_point"]
    rotors: None | SweepPointResourceRotorsType0

    def to_dict(self) -> dict[str, Any]:
        from thrustlab._models.sweep_point_resource_rotors_type_0 import SweepPointResourceRotorsType0

        failed = self.failed

        index = self.index

        inputs = self.inputs.to_dict()

        is_starred = self.is_starred

        object_ = self.object_

        rotors: dict[str, Any] | None
        if isinstance(self.rotors, SweepPointResourceRotorsType0):
            rotors = self.rotors.to_dict()
        else:
            rotors = self.rotors

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "failed": failed,
                "index": index,
                "inputs": inputs,
                "is_starred": is_starred,
                "object": object_,
                "rotors": rotors,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.sweep_point_inputs import SweepPointInputs
        from thrustlab._models.sweep_point_resource_rotors_type_0 import SweepPointResourceRotorsType0

        d = dict(src_dict)
        failed = d.pop("failed")

        index = d.pop("index")

        inputs = SweepPointInputs.from_dict(d.pop("inputs"))

        is_starred = d.pop("is_starred")

        object_ = cast(Literal["sweep_point"], d.pop("object"))
        if object_ != "sweep_point":
            raise ValueError(f"object must match const 'sweep_point', got '{object_}'")

        def _parse_rotors(data: object) -> None | SweepPointResourceRotorsType0:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                rotors_type_0 = SweepPointResourceRotorsType0.from_dict(data)

                return rotors_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SweepPointResourceRotorsType0, data)

        rotors = _parse_rotors(d.pop("rotors"))

        sweep_point_resource = cls(
            failed=failed,
            index=index,
            inputs=inputs,
            is_starred=is_starred,
            object_=object_,
            rotors=rotors,
        )

        return sweep_point_resource

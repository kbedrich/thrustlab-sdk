"""FMU export: run a simulation -> export -> wait (with progress) -> download.

Run it:
    export THRUSTLAB_API_KEY=key_...        # never hard-code the key
    python examples/fmu/export_and_download.py

Requires the `fmi_export` capability (Pro tier) on the calling account.
Exports the verification combo (BadAss 2826-820Kv + 10.5x4.5 + Liperior
4S 5000 mAh @ 70% throttle, static) as an FMI 3.0 Co-Simulation FMU. Swap in
your own component IDs, or resolve them by name with
client.components.find(...).
"""

from thrustlab import Client

client = Client()  # reads $THRUSTLAB_API_KEY from the environment

project = client.projects.create(name="sdk fmu export example")

motor = client.components.find(name="BadAss 2826-820Kv")
prop = client.components.find(name="10.5x4.5")
battery = client.components.find(
    name="Liperior 5000mAh 4S 35C 14.8V Lipo Battery With XT90 Plug"
)

# The FMU export source must be a COMPLETED single-point simulation: no
# multi-pack battery topology, no coaxial stack (heterogeneous rotor groups
# ARE supported).
sim = client.simulations.create(
    project_id=project["id"],
    battery_component_id=battery["id"],
    airspeed_m_s=0.0,
    density_kg_m3=1.225,
    battery_charge_pct=100,
    rotor_groups=[
        {
            "label": "main",
            "count": 4,
            "motor_component_id": motor["id"],
            "propeller_component_id": prop["id"],
            "throttle_pct": 70,
        }
    ],
)
sim = client.simulations.wait(sim["id"], timeout=300)
if sim["status"] != "completed":
    raise SystemExit(f"source simulation did not complete: {sim['status']}")
print(f"source simulation {sim['id']} completed")

# export() queues the job and returns immediately (202 + job id).
job = client.fmu.export(sim["id"])
print(f"export job {job['id']} queued")


def on_progress(status: dict) -> None:
    # `chunks_done`/`chunks_total` are always present while solving; treat any
    # other key (`progress`, `eta_s`, `phase`, ...) as optional — the status
    # contract is additive across releases.
    chunks = ""
    if status.get("chunks_total"):
        chunks = f" ({status.get('chunks_done', 0)}/{status['chunks_total']})"
    print(f"  status: {status['status']}{chunks}")


# No default timeout on fmu.wait() — a lane-table/aero-table build can run
# well past the 600 s used elsewhere in the SDK. Pass timeout=... to cap it.
result = client.fmu.wait(job["id"], on_progress=on_progress, poll_interval=2.0)

if result["status"] != "completed":
    # wait() never raises on a failed job — check status() and error yourself,
    # same as every other resource's wait().
    error = result.get("error") or {}
    raise SystemExit(
        f"export {job['id']} did not complete: {result['status']} "
        f"({error.get('error_code')}: {error.get('message')})"
    )

dest = f"{result.get('filename', 'powertrain.fmu')}"
out_path = client.fmu.download(job["id"], dest)
print(f"downloaded {out_path} ({result.get('bytes', '?')} bytes)")

# thrustlab — official Python SDK for the ThrustLab API

[![PyPI](https://img.shields.io/pypi/v/thrustlab.svg)](https://pypi.org/project/thrustlab/)
[![Python](https://img.shields.io/pypi/pyversions/thrustlab.svg)](https://pypi.org/project/thrustlab/)
[![License](https://img.shields.io/pypi/l/thrustlab.svg)](https://github.com/kbedrich/thrustlab-sdk/blob/main/LICENSE)

## Install

```bash
pip install thrustlab
```

Requires Python 3.10+.

## Quickstart

```python
from thrustlab import Client

client = Client()  # reads $THRUSTLAB_API_KEY (never hard-code the key)

# Create a project
project = client.projects.create(name="my project")

# Run a single-point simulation and wait for the result.
# A rotor group carries the motor + propeller + throttle (0–100); the battery
# and flight condition are top-level. Resolve component IDs from the catalog
# (client.components.find(name=...)) or paste them directly.
sim = client.simulations.create(
    project_id=project["id"],
    battery_component_id="comp_batt_xxx",
    airspeed_m_s=0.0,
    density_kg_m3=1.225,
    battery_charge_pct=100,
    rotor_groups=[
        {
            "label": "main",
            "count": 4,
            "motor_component_id": "comp_motor_xxx",
            "propeller_component_id": "comp_prop_xxx",
            "throttle_pct": 70,
        }
    ],
)
result = client.simulations.wait(sim["id"], timeout=300)

# Canonical snake_case result: per-rotor group under "1"/"2"/…, roll-ups
# under "All" (a sibling `display_labels` map carries the human labels).
print(result["result"]["1"]["thrust_n"], result["result"]["All"]["total_thrust_n"])
```

Runnable end-to-end examples for every simulation type live in
[`examples/`](./examples): [`simulations/run_sync.py`](./examples/simulations/run_sync.py),
[`sweeps/run_and_poll.py`](./examples/sweeps/run_and_poll.py), and
[`dynamic/run_and_poll.py`](./examples/dynamic/run_and_poll.py).

## Why the SDK (and not `urllib` / `wget`)?

Use this SDK — or, if you hand-roll a client, an HTTP library that is **not**
stdlib `urllib`. Requests from Python's `urllib.request` (and `wget`) are
**blocked at the Cloudflare edge** by a managed WAF rule matching the literal
`Python-urllib/*` User-Agent. The block is terminated at the edge: the request
**never reaches the ThrustLab API**, so you get an opaque HTML *error 1010*
challenge page — **not** a JSON error envelope. The API cannot return a
structured error for a request it never sees.

This SDK is built on [`httpx`](https://www.python-httpx.org/) and sends its own
`thrustlab-python/<version>` User-Agent, so it is **unaffected**. If you must
hand-roll a client, set an explicit non-`urllib` `User-Agent` header (e.g.
`requests`, `httpx`, or `curl`) and you will reach the API normally.

## Configuration

| Setting      | Constructor arg  | Env var               | Default                  |
|--------------|------------------|-----------------------|--------------------------|
| API key      | `api_key=`       | `THRUSTLAB_API_KEY`   | (required)               |
| Base URL     | `base_url=`      | `THRUSTLAB_BASE_URL`  | `https://thrustlab.com`  |
| Timeout      | `timeout=`       | —                     | `30` (seconds)           |
| Max retries  | `max_retries=`   | —                     | `3`                      |

## Resources

Every `/v1/` route family is exposed as an attribute on the client:

```python
client.users
client.projects
client.simulations
client.sweeps
client.dynamic_simulations
client.components
client.submissions
client.starred_components
client.compute_units
client.webhook_endpoints
```

## Error handling

```python
from thrustlab import Client
from thrustlab.exceptions import (
    AuthenticationError,
    ValidationError,
    RateLimitError,
    NotFoundError,
)

client = Client()
try:
    client.simulations.create(project_id="proj_xxx", rotor_groups=[...], ...)
except ValidationError as exc:
    print(f"bad request: {exc.code} ({exc.param}): {exc.message}")
except RateLimitError as exc:
    print(f"rate limited; retry after {exc.retry_after}s")
except NotFoundError as exc:
    print(f"not found: {exc.message}")
except AuthenticationError as exc:
    print(f"auth failed: {exc.message}")
```

Every error carries `.code`, `.type`, `.request_id`, `.http_status`, and
`.message`. `ValidationError` additionally exposes `.param`. See
[thrustlab.com/docs/guides/errors](https://thrustlab.com/docs/guides/errors)
for the full code reference.

## Pagination

List endpoints return a `CursorPager` — a lazy iterator that fetches the
next page only when needed:

```python
# Iterate all pages automatically
for project in client.projects.list():
    print(project["id"])

# Materialise the first page only
first_page = list(client.projects.list(limit=20))
```

## Async polling

`simulations.wait()`, `sweeps.wait()`, and `dynamic_simulations.wait()` block
until the resource reaches a terminal state (`completed`, `failed`, or
`canceled` — one 'l' on the wire) or the timeout fires. On timeout the returned
dict carries the SDK-side sentinel `status="timed_out"` (never a server state):

```python
sweep = client.sweeps.create(...)
result = client.sweeps.wait(sweep["id"], timeout=600, poll_interval=2.0)
if result["status"] == "completed":
    for point in client.sweeps.list_points(sweep["id"]):
        print(point["rotors"]["1"]["thrust_n"])
```

## Webhooks

```python
from thrustlab import Webhook
from thrustlab.exceptions import SignatureVerificationError

WEBHOOK_SECRET = "whsec_..."

@app.post("/webhooks/thrustlab")
async def handle(request):
    payload = await request.body()
    sig    = request.headers["Thrustlab-Signature"]
    try:
        event = Webhook.verify(payload, sig, WEBHOOK_SECRET)
    except SignatureVerificationError:
        return Response(status_code=400)
    if event.type == "simulation.succeeded":
        print(event.data)
```

## Retries

The client automatically retries on 429 (rate limit) and 5xx responses using
exponential backoff with jitter. Set `max_retries=0` to disable:

```python
client = Client(max_retries=0)
```

## Links

- Documentation: https://thrustlab.com/docs
- API reference: https://thrustlab.com/docs/reference
- SDK guide: https://thrustlab.com/docs/sdk/python
- Changelog: https://thrustlab.com/docs/changelog
- Issue tracker: https://github.com/kbedrich/thrustlab-sdk/issues

## License

Apache-2.0. See [`LICENSE`](./LICENSE) and [`NOTICE`](./NOTICE).

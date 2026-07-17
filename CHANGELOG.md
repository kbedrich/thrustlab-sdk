# Changelog

All notable changes to the `thrustlab` Python SDK are documented here. The
project follows [semantic versioning](https://semver.org/) independent of the
ThrustLab API version (which is permanently `/v1/`).

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.3.2] - 2026-07-16

Bug-fix release: a docs-vs-code audit found several SDK surfaces that
silently did nothing (the server ignores unknown query params) or targeted
endpoints that don't exist. No new API surface beyond the fixes below.

### Fixed

- **`list(project_id=...)` on `simulations`, `sweeps`, and
  `dynamic_simulations` now actually filters.** The SDK sent a `project_id`
  query key but the endpoints read `project` — the filter was silently
  ignored and every listing returned ALL of the caller's runs. The kwarg
  name is unchanged; the SDK now sends the right param.
- **`projects.list`, `submissions.list`, `webhook_endpoints.list`,
  `list_events`, and `list_deliveries` pagination kwarg renamed
  `starting_after=` → `cursor=`.** The endpoints read `cursor`;
  `starting_after` was silently ignored (same defect the 0.3.0 changelog
  fixed for sims/sweeps — these five were missed).
- **BREAKING — `client.starred_components` rewritten against the real API.**
  The previous resource targeted `GET/POST /v1/projects/{pid}/starred-components`,
  which does not exist under `/v1/` — every call 404'd. Stars are flat,
  first-class resources:
  - `list(project_id=..., component_type=..., cursor=...)` →
    `GET /v1/starred_components`;
  - `add(project_id=..., component_id=..., component_type=...)` →
    `POST /v1/starred_components` (component_type is required; duplicate
    star raises `ConflictError` 409 `already_starred`);
  - `remove(star_id)` → `DELETE /v1/starred_components/{star_id}` — keys on
    the star's own `star_<ksuid>` id (from `list()`/`add()`), not the
    component id.
- **`APIError.request_id` is now populated.** It is read from the error
  envelope's `request_id` (with the `X-Request-ID` response header as a
  fallback); previously the SDK only read the header, which the server did
  not send, so `request_id` was always `None`.

### Added

- `simulations.list(status=...)` — filter by `queued` / `running` /
  `completed` / `failed` / `canceled`.
- `submissions.list(status=...)` — filter by moderation status.
- `submissions.update(id, ...)` / `submissions.withdraw(id)` — edit or
  withdraw a submission while it is still `submitted`.
- `webhook_endpoints.list_deliveries(..., event_type=..., created_at_gte=...)`
  — the endpoint's remaining filters, previously unreachable from the SDK.

## [0.3.1] - 2026-07-16

Packaging-metadata fix, no code changes:

- The `Repository` project URL shipped in 0.3.0 carried a literal
  `<owner>` placeholder; it now points to the public SDK repo,
  `https://github.com/kbedrich/thrustlab-sdk`.
- README links corrected to the same repo.

## [0.3.0] - 2026-07-15

The ThrustLab public API was refocused to a **product-only** surface: account,
billing, subscription, API-key and geometry-calibration management are no
longer part of the public `/v1/` contract. This SDK release realigns the
client to that surface.

> **0.2.0 was built but never published to PyPI.** 0.3.0 is the first release
> after 0.1.2, and it **consolidates the unpublished 0.2.0 changes** (canonical
> `snake_case` result keys, the `dynamic_simulations` resource, the sims/sweeps
> `cursor` fix) together with the API-refocus breaking changes below. If you are
> upgrading from `0.1.x`, read this whole entry — it is the full delta.

### Removed

- **BREAKING — `client.subscriptions` and `client.api_keys` resources are gone.**
  Subscription/billing-portal and API-key management are not part of the public
  product SDK. `client.subscriptions` / `client.api_keys` now raise
  `AttributeError`. (Create and manage API keys from the ThrustLab dashboard.)

### Changed

- **BREAKING — `client.credits` renamed to `client.compute_units`.** The public
  credits surface was renamed to *compute units*:
  - accessor `client.credits` → `client.compute_units`;
  - method `usage(...)` → `transactions(...)`;
  - endpoints `/v1/credits/balance` → `/v1/compute-units/balance` and
    `/v1/credits/usage` → `/v1/compute-units/transactions`;
  - the pager keyword `starting_after=` → `cursor=` (the endpoint reads `cursor`;
    this matches the 0.2.0 sims/sweeps fix — a `starting_after=` kwarg was
    silently ignored). The `credit_type=` filter keyword is unchanged.
- **BREAKING (from the unpublished 0.2.0) — result payloads are canonical
  `snake_case` across single-point, sweep, AND dynamic endpoints**, each with a
  sibling `display_labels` map (`{snake_key: "Human Label"}`). Consumers that
  parsed the old display-label result keys on sweep points (`"Thrust (N)"`,
  `"RPM"`, …) must read the snake keys (`thrust_n`, `rpm`, …) and use
  `display_labels` to recover a human string.
- **BREAKING — simulation / sweep / dynamic create bodies drop the first-party
  fields `solver`, `input_snapshot`, and `design_cl`.** These were never part of
  the public product contract; passing them is no longer accepted. (They remain
  present in *response* payloads where the server legitimately echoes them.)
- **BREAKING — rotor-group count is capped at 16 total rotors (Σ ≤ 16)** across
  all groups on a create request; larger configurations are rejected by the API.

### Added

- **`client.components.create(...)`** — create a private custom component
  (`POST /v1/components`) without dropping to the raw transport. Takes
  `type`, `name`, `spec_json`, and an optional `idempotency_key`.
- Component create/update responses may carry a non-blocking `warnings` list
  (`code` / `param` / `message`) when a spec value looks physically
  implausible — e.g. a motor `R` far outside the expected range for its `kv`
  and `weight` (milliohm/ohm mix-up, or a per-phase value where phase-to-phase
  is expected). The write always succeeds.
- **`client.compute_units.summary()`** — usage-meter read for the current
  metering window (`GET /v1/compute-units/summary`).
- **`client.dynamic_simulations` resource** (`create` / `retrieve` / `wait` /
  `list` / `cancel` / `estimate`) mirroring `client.sweeps`, plus a runnable
  dynamic example (`examples/dynamic/run_and_poll.py`).
- Runnable end-to-end examples for all three simulation types
  (single-point / sweep / dynamic) reading canonical `snake_case` result keys,
  and a corrected README quickstart using the real create body
  (`rotor_groups=[…]` + `battery_component_id`).

### Fixed

- **`cursor` pagination** — an explicit `starting_after=` kwarg on
  `simulations.list`, `sweeps.list`, and `sweeps.list_points` was silently
  ignored (the backend reads `cursor`). The keyword argument is now `cursor=`.
  Automatic multi-page iteration was unaffected.

### Migration from 0.1.x / 0.2.0

```python
# --- credits -> compute_units ---------------------------------------------
# before (<= 0.2.0)
balance = client.credits.balance()
for ev in client.credits.usage(credit_type="simulation", starting_after=cur):
    ...

# after (0.3.0)
balance = client.compute_units.balance()
for ev in client.compute_units.transactions(credit_type="simulation", cursor=cur):
    ...

# --- removed resources ----------------------------------------------------
# client.subscriptions.* and client.api_keys.* no longer exist — manage
# subscriptions and API keys from the ThrustLab dashboard.

# --- sweep result keys are snake_case (from 0.2.0) ------------------------
# before: point["rotors"]["1"]["Thrust (N)"]
# after:  point["rotors"]["1"]["thrust_n"]   # display_labels["thrust_n"] -> "Thrust (N)"
```

## [0.2.0] - 2026-07-09

### Changed

- **BREAKING — result payloads are now canonical `snake_case` across
  single-point, sweep, AND dynamic endpoints, each with a sibling
  `display_labels` map (`{snake_key: "Human Label"}`).** Single-point results
  were already snake_case; this release aligns **sweep points** and **dynamic
  samples** to the same contract. Consumers that parsed the old display-label
  result keys on sweep points (`"Thrust (N)"`, `"RPM"`, `"Current (A)"`, …)
  must now read the snake keys (`thrust_n`, `rpm`, `current_a`, …). Use the
  sibling `display_labels` map to recover a human string for any key.

  Migration:

  ```python
  # before (0.1.x) — sweep point rotor keys were display labels
  thrust = point["rotors"]["1"]["Thrust (N)"]

  # after (0.2.0) — canonical snake_case, with display_labels for UI
  thrust = point["rotors"]["1"]["thrust_n"]
  label  = sweep["display_labels"]["thrust_n"]   # -> "Thrust (N)"
  ```

### Added

- **`client.dynamic_simulations` resource** (`create` / `retrieve` / `wait` /
  `list` / `cancel` / `estimate`) mirroring `client.sweeps`, plus a runnable
  dynamic example (`examples/dynamic/run_and_poll.py`).
- Runnable end-to-end examples for all three simulation types
  (single-point / sweep / dynamic) reading canonical snake_case result keys,
  and a corrected README quickstart that uses the real create body
  (`rotor_groups=[…]` + `battery_component_id`, not the phantom
  `motor=/propeller=/battery=/throttle=` kwargs).

### Fixed

- **`cursor` pagination** — an explicit `starting_after=` kwarg on
  `simulations.list`, `sweeps.list`, and `sweeps.list_points` was silently
  ignored (the backend reads `cursor`). The keyword argument is now `cursor=`.
  Automatic multi-page iteration was unaffected.

### Corrected (documentation record)

- The 0.1.0 changelog listed a `geometry` resource module and terminal states
  `succeeded`/`cancelled` that never matched the shipped library. The SDK has
  **no** `geometry` resource, and the canonical terminal states are
  `completed` / `failed` / `canceled` (one-L wire spelling), with a
  `timed_out` client-side sentinel from `wait()`.

## [0.1.2] - 2026-07-08

### Fixed

- **`wait()` now recognizes the canonical terminal states
  `completed`/`failed`/`canceled`** (one-L `canceled` wire spelling). The
  previous set omitted `canceled`, so `wait()` polled forever on a canceled
  run until it hit the timeout sentinel.

## [0.1.1] - 2026-04-28

### Changed

- **License relicensed from MIT to Apache-2.0.** The Apache-2.0 license
  includes an explicit patent grant scoped to the SDK plus a defensive
  termination clause (anyone who sues ThrustLab for patent infringement
  loses the patent grant). MIT had no explicit patent terms. ThrustLab
  reserves all rights to the underlying simulation methodology that this
  SDK calls; the license here applies only to this client library.
- Added `NOTICE` file alongside `LICENSE` per Apache convention.

### Migration from 0.1.0

If you pinned `thrustlab==0.1.0`, upgrade to `thrustlab==0.1.1`. No code
changes — only the license text differs. Version 0.1.0 has been yanked
from PyPI.

## [0.1.0] - 2026-04-27

Initial public beta release of the official ThrustLab Python SDK.

### Added

- Full coverage of the `/v1/` API surface across **12 resource modules**:
  `api_keys`, `users`, `projects`, `simulations`, `sweeps`, `components`,
  `submissions`, `starred_components`, `geometry`, `credits`,
  `subscriptions`, `webhook_endpoints`.
- Sync transport (`httpx.Client`) with bearer-token authentication.
- Auto-generated `Idempotency-Key` header on every mutating request (override
  via `idempotency_key=` keyword argument).
- Exponential backoff + jitter retry on 429, 5xx, and transient network
  errors (`max_retries=3` default, configurable per client instance).
- `CursorPager[T]` lazy iterator for cursor-paginated list endpoints;
  transparent multi-page iteration.
- `wait()` helpers on `simulations` and `sweeps` for polling async resources
  to terminal state (`succeeded` / `failed` / `cancelled` / `timed_out`).
- `Webhook.verify()` for HMAC SHA256 webhook signature verification with
  configurable timestamp tolerance (default 300 s).
- Stripe-style typed exception hierarchy:
  `ThrustlabError` → `APIError` → `AuthenticationError`, `PermissionError`,
  `NotFoundError`, `ValidationError`, `ConflictError`, `RateLimitError`,
  `APIServerError`; plus `NetworkError`, `SignatureVerificationError`,
  `ConfigurationError`.
- Pydantic v2 models generated from `openapi.json` via
  `openapi-python-client`; used internally for request/response shaping.
- Configuration via constructor kwargs (`api_key`, `base_url`, `timeout`,
  `max_retries`) or env vars (`THRUSTLAB_API_KEY`, `THRUSTLAB_BASE_URL`).
- 103 unit + integration tests (pytest).

### Out of scope (deferred)

- Async transport (`httpx.AsyncClient`). Planned for v0.2.
- Streaming response support.
- Python 3.9 compatibility.
- CLI tool (`thrustlab` command).
- SDKs in other languages.

## Pre-release rehearsal procedure

Before tagging v0.1.0, rehearse with:

1. Create a short-lived release-rehearsal branch from master.
2. Tag `sdk-py-v0.0.1-rc1` and push it.
3. The CI workflow runs build + TestPyPI publish only (gate step enforces
   ancestry before either publish step fires).
4. Delete the rehearsal tag + branch after validation.
5. Tag `sdk-py-v0.1.0` from the actual master-merge commit for production publish.

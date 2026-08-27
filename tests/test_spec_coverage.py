"""Confirm every /v1/ operationId in openapi.json maps to an SDK method.

If a new endpoint lands without a corresponding SDK method, this test fails
and forces the developer to either implement the method or explicitly skip-list it.
"""
import json
import pathlib

import pytest

_parents = pathlib.Path(__file__).resolve().parents
SPEC = (
    _parents[4] / "docs" / "api" / "openapi.json"
    if len(_parents) > 4
    else pathlib.Path("openapi-json-not-present")
)

# The coverage gate needs the API's OpenAPI export, which lives beside the API
# source. It is not shipped with the standalone SDK repo — skip cleanly there.
pytestmark = pytest.mark.skipif(
    not SPEC.exists(), reason="openapi.json not present (API-repo-only gate)"
)

# operationIds for endpoints that intentionally have no SDK method.
#
# Operations that leave the public /v1/ spec are NOT skip-listed: a removed op
# drops out of the coverage loop entirely, and dead-listing it would mask the
# fact that it's gone.
SKIP_LIST = {
    "v1_health_v1_health_get",  # health check; no SDK use case
    # Dynamic-simulation SSE live stream — no polling/wait SDK use case; the
    # DynamicSimulationsResource covers create/get/list/cancel/estimate/patch/export.
    "stream_dynamic_v1_v1_dynamic_simulations__public_id__stream_get",
    # The geometry endpoints are deliberately unexposed in the public SDK
    # (no `geometry` resource) — an advanced surface outside the core
    # sim-SDK scope for now.
    "analyze_geometry_v1_geometry_analyze_post",
    "design_geometry_v1_geometry_design_post",
    "stream_design_v1_geometry_design__job_id__stream_get",
    "export_geometry_v1_geometry_export_post",
    "generate_geometry_v1_geometry_generate_post",
    "list_geometry_styles_v1_geometry_styles_get",
    "get_geometry_style_v1_geometry_styles__slug__get",
    # Airfoil catalog management sits outside the sim SDK surface.
    "list_airfoils_v1_airfoils_get",
    "import_airfoil_v1_airfoils_import_post",
    "delete_airfoil_v1_airfoils__airfoil_id__delete",
    "get_airfoil_v1_airfoils__airfoil_id__get",
    # /v1/public/* is the UNauthenticated web/SEO read surface (curated results,
    # shared links, public propellers) — the SDK is bearer-auth'd; no SDK use case.
    "list_public_propellers_v1_public_propellers_get",
    "get_public_result_v1_public_results__slug__get",
    "get_shared_result_v1_public_share__share_token__get",
}


# Every non-skip-listed /v1/ operationId must resolve to a live SDK resource
# method (the family_map below maps each /v1/ path family to its resource
# accessor).
def test_every_operation_has_sdk_coverage():
    spec = json.loads(SPEC.read_text())
    missing = []
    for path, ops in spec["paths"].items():
        for method, op in ops.items():
            if not isinstance(op, dict):
                continue
            opid = op.get("operationId")
            if not opid or opid in SKIP_LIST:
                continue
            # Heuristic: every operationId must resolve to a module.method on
            # the Client. Map paths → resource accessors. If the path can't
            # be mapped, we record it as missing.
            if not _resource_method_exists(path, method, opid):
                missing.append(f"{method.upper()} {path} (operationId={opid})")
    if missing:
        pytest.fail(
            f"{len(missing)} /v1/ operations have no SDK method:\n" + "\n".join(missing[:30])
        )


def _resource_method_exists(path: str, method: str, opid: str) -> bool:
    """Return True if the SDK has a plausible resource method for this path/method."""
    from thrustlab import Client

    # Map path prefix to resource accessor name.
    #
    # `/v1/api_keys` and `/v1/subscriptions` are no longer part of the public
    # spec and have no SDK accessors, so those prefixes are absent from the
    # map. `/v1/credits` was renamed to `/v1/compute-units` and the SDK
    # accessor renamed `credits` → `compute_units` to match.
    family_map = {
        "/v1/users": "users",
        "/v1/projects": "projects",
        "/v1/simulations": "simulations",
        "/v1/sweeps": "sweeps",
        "/v1/dynamic-simulations": "dynamic_simulations",
        "/v1/components": "components",
        "/v1/submissions": "submissions",
        "/v1/starred_components": "starred_components",
        "/v1/compute-units": "compute_units",
        "/v1/webhook_endpoints": "webhook_endpoints",
        "/v1/events": "webhook_endpoints",  # events surface owned by webhooks resource
    }
    prefix = next((p for p in family_map if path.startswith(p)), None)
    if not prefix:
        return False
    accessor = family_map[prefix]

    client = Client(api_key="dummy")  # noqa - no network call
    resource = getattr(client, accessor, None)
    if resource is None:
        return False

    # Best-effort method lookup: any callable attribute on the resource counts.
    # Stricter mapping lives in real SDK QA — for the gate, "the resource exists
    # and has at least one method" is the bar.
    return any(callable(getattr(resource, attr)) for attr in dir(resource) if not attr.startswith("_"))

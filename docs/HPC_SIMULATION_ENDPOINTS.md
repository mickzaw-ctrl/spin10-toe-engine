# HPC Simulation Endpoints

**Status:** Integration pending end-to-end validation
**Last reviewed:** 2026-07-31

## Purpose

This document separates the Base44 control plane from the Spin(10) HPC simulation data plane and records the endpoint behavior verified during deployment of the `executeSimulationEndpoint` backend function.

## Endpoint map

| Component | Method and route | Purpose | Status |
|---|---|---|---|
| Base44 backend function | Managed `executeSimulationEndpoint` function URL | Authenticates the caller, validates the simulation type, supports `dry_run`, and forwards approved jobs | Deployed; validation tested |
| Spin(10) Quantum Core | `POST https://<HPC_HOST>/api/v1/simulate` | Submits a simulation to the FastAPI/Ray orchestrator | Route confirmed in engine source; production host still requires a successful smoke test |
| Spin(10) health check | `GET https://<HPC_HOST>/health` | Reports gateway and Ray initialization status | Route confirmed in engine source |
| Base44 conversations API | `https://app.base44.com/api/agents/<agent_id>/conversations` | Manages Superagent conversations | **Not an HPC simulation endpoint** |

`SPIN10_HPC_ENDPOINT` must contain the complete HTTPS URL, including the simulation route. A bare hostname, a URL containing whitespace, or the Base44 conversations URL is invalid for HPC dispatch.

## Backend function contract

The Base44 backend function accepts authenticated `POST` requests with this shape:

```json
{
  "simulation_type": "rge",
  "parameters": {
    "loops": 2,
    "validation_only": true
  },
  "dry_run": true
}
```

Allowed simulation types:

- `rge`
- `mukhanov_sasaki`
- `bayesian_mcmc`
- `spectral_dimension`
- `mera`
- `tokenizer_eval`
- `pretraining_stage`
- `regression_eval`

When `dry_run` is `true`, the request is validated but is not sent to the HPC service. Production dispatch requires both encrypted secrets:

- `SPIN10_HPC_ENDPOINT`
- `SPIN10_HPC_TOKEN`

Never commit either secret or print its value in logs.

## Current Quantum Core route contract

At engine commit `75a53d68f7f50ecd8ae20686e83774c64f995545`, `src/quantum_core/spin10_gateway.py` defines:

```http
POST /api/v1/simulate?priority=3&batch_size=1000
GET  /health
```

The current FastAPI handler receives `priority` and `batch_size` as query parameters. The deployed Base44 function forwards a JSON body containing `request_id`, `simulation_type`, `parameters`, `requested_by`, and `requested_at`.

This is a known interface mismatch. Before declaring production integration complete, either:

1. update the Base44 adapter to map approved parameters to the FastAPI query contract; or
2. update the FastAPI route to accept a versioned JSON request model that preserves `simulation_type` and audit metadata.

The second option is preferred for a multi-simulation production API because it provides explicit schema validation and versioning.

## Verified deployment observations

Tests performed on 2026-07-31:

| Test | Result | Interpretation |
|---|---|---|
| Authenticated `dry_run` for `rge` | HTTP 200, `validated_not_dispatched` | Base44 authentication and input validation are operational |
| Dispatch with malformed endpoint value | HTTP 500, `invalid_hpc_endpoint_configuration` | Endpoint validation correctly rejects non-URL values |
| Dispatch to a reachable host with an incorrect route | Upstream HTTP 404, surfaced as gateway HTTP 502 | HTTPS connectivity works, but the configured POST path does not exist |
| Production simulation execution | Not validated | No successful upstream acceptance has been recorded |

A 404 response must not be reported as a successful HPC deployment. It confirms network reachability only.

## Recommended smoke-test sequence

1. Verify the endpoint format without exposing it: HTTPS scheme, hostname present, no whitespace.
2. Call `GET /health` on the HPC host and require a healthy response.
3. Run the Base44 function with `dry_run: true`.
4. Submit a minimal `validation_only` job to the exact `POST /api/v1/simulate` route.
5. Require an upstream success response and record the request ID.
6. Inspect backend and HPC logs for the same request ID.
7. Only then mark the deployment as production-ready.

## Expected error mapping

| Backend status | Error | Meaning |
|---|---|---|
| 400 | `invalid_json`, `unsupported_simulation_type`, or invalid parameters | Caller input failed validation |
| 401 | `authentication_required` | Base44 caller is not authenticated |
| 413 | `payload_too_large` | Request exceeded the gateway limit |
| 500 | Invalid endpoint configuration or non-HTTPS endpoint | Deployment configuration error |
| 502 | `hpc_dispatch_failed` or `hpc_unavailable` | Upstream rejected the request or could not be reached |
| 504 | `hpc_timeout` | Upstream exceeded the configured timeout |

## Provenance

- Repository: `mickzaw-ctrl/spin10-toe-engine`
- Pinned engine commit: `75a53d68f7f50ecd8ae20686e83774c64f995545`
- FastAPI simulation route: `src/quantum_core/spin10_gateway.py`, lines 40–61
- FastAPI health route: `src/quantum_core/spin10_gateway.py`, lines 63–66
- REST client example: `README.md`, lines 390–399 at the pinned commit
- Base44 gateway source: `functions/executeSimulationEndpoint.ts`, deployment revision `2026-07-31-production-endpoint-bound`

## Scientific impact

None. This documentation update changes deployment guidance only; it does not modify equations, physical assumptions, numerical solvers, datasets, or scientific claims.

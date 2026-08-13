"""FastAPI application for the Spin(10) Research Lab."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from lab import services

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="Spin(10) Research Lab",
    version="16.1.0",
    description="Fail-closed workbench and internally closed Spin(10) specification.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RGERequest(BaseModel):
    m_susy: float = Field(5000.0, ge=200.0, le=1.0e7)
    loops: Literal[1, 2] = 2
    n_points: int = Field(240, ge=40, le=800)


class SpectralRequest(BaseModel):
    graph: Literal["cycle", "torus", "random"] = "torus"
    size: int = Field(24, ge=8, le=400)
    walkers: int = Field(4000, ge=200, le=20000)
    steps: int = Field(80, ge=20, le=250)
    seed: int = Field(42, ge=0, le=1_000_000_000)


class TCDRequest(BaseModel):
    points: int = Field(80, ge=20, le=200)


class LQCRequest(BaseModel):
    gamma: float = Field(0.2375, ge=0.05, le=1.5)
    spin: float = Field(0.5, ge=0.5, le=20.0)
    punctures: int = Field(100, ge=1, le=10_000)


class InflationRequest(BaseModel):
    alpha: float = Field(3.75, ge=0.1, le=20.0)
    n_efolds: float = Field(60.0, ge=40.0, le=80.0)


class GaugeRequest(BaseModel):
    n_nodes: int = Field(24, ge=12, le=40)
    seed: int = Field(7, ge=0, le=1_000_000_000)


class TheoryRequest(BaseModel):
    fast: bool = True


class JacobsonRequest(BaseModel):
    n_nodes: int = Field(1_000_000, ge=100, le=10**10)
    omega: float = Field(0.0, ge=0.0, le=1.0e5)
    points: int = Field(80, ge=20, le=200)


class ConfrontationRequest(BaseModel):
    alpha: float = Field(3.75, ge=0.1, le=20.0)
    n_efolds: float = Field(60.0, ge=40.0, le=80.0)
    m_susy: float = Field(5000.0, ge=200.0, le=1.0e7)
    alpha_h_gev3: float = Field(0.015, ge=0.001, le=0.05)


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def _call(fn, **kwargs):
    try:
        return _jsonable(fn(**kwargs))
    except (ValueError, services.TCDInputError, services.ClosureInputError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "service": "spin10-research-lab", "version": "16.1.0"}


@app.get("/api/status")
def status() -> dict:
    return services.lab_status()


@app.post("/api/rge")
def rge(body: RGERequest) -> dict:
    return _call(services.run_rge, m_susy=body.m_susy, loops=body.loops, n_points=body.n_points)


@app.post("/api/spectral")
def spectral(body: SpectralRequest) -> dict:
    return _call(
        services.run_spectral,
        graph=body.graph,
        size=body.size,
        walkers=body.walkers,
        steps=body.steps,
        seed=body.seed,
    )


@app.post("/api/tcd")
def tcd(body: TCDRequest) -> dict:
    return _call(services.run_tcd_sweep, points=body.points)


@app.post("/api/lqc")
def lqc(body: LQCRequest) -> dict:
    return _call(services.run_lqc, gamma=body.gamma, spin=body.spin, punctures=body.punctures)


@app.post("/api/inflation")
def inflation(body: InflationRequest) -> dict:
    return _call(services.run_inflation, alpha=body.alpha, n_efolds=body.n_efolds)


@app.get("/api/ledger")
def ledger() -> dict:
    return services.run_ledger()


@app.post("/api/theory")
def theory(body: TheoryRequest) -> dict:
    return _call(services.run_theory, fast=body.fast)


@app.post("/api/jacobson")
def jacobson(body: JacobsonRequest) -> dict:
    return _call(
        services.run_jacobson,
        n_nodes=body.n_nodes,
        omega=body.omega,
        points=body.points,
    )


@app.post("/api/confrontation")
def confrontation(body: ConfrontationRequest) -> dict:
    return _call(
        services.run_confrontation,
        alpha=body.alpha,
        n_efolds=body.n_efolds,
        m_susy=body.m_susy,
        alpha_h_gev3=body.alpha_h_gev3,
    )


@app.post("/api/gauge")
def gauge(body: GaugeRequest) -> dict:
    return _call(services.run_gauge_snapshot, n_nodes=body.n_nodes, seed=body.seed)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount(
    "/www",
    StaticFiles(directory=Path(__file__).resolve().parents[1] / "docs", html=True),
    name="www",
)

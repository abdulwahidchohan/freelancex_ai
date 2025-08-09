#!/usr/bin/env python3
"""
Minimal FastAPI API Gateway for FreelanceX.AI
- /health: health check
- /v1/agents/run: run the orchestrator
"""

import asyncio
import logging
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel

from config.settings import get_config
from fx_agents.orchestrator import run_orchestration
from fx_agents.api_switcher import get_status as api_status, switch_provider as api_switch
from fx_agents.mcp import get_mcp

# Prometheus metrics
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

logger = logging.getLogger(__name__)

app = FastAPI(title="FreelanceX.AI API Gateway", version="0.1.0")

LLM_REQUESTS = Counter("llm_requests_total", "Total LLM requests", ["provider"]) 
RUN_LATENCY = Histogram("orchestration_seconds", "Duration of orchestrations")
CACHE_HITS = Counter("llm_cache_hits_total", "Total cache hits")

try:
    # Optional OpenTelemetry auto-instrumentation + OTLP exporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    import os

    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://127.0.0.1:4317")
    provider = TracerProvider(resource=Resource.create({"service.name": "freelancex_api"}))
    span_exporter = OTLPSpanExporter(endpoint=endpoint)
    provider.add_span_processor(BatchSpanProcessor(span_exporter))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)
except Exception:
    pass


class RunRequest(BaseModel):
    user_id: str = "default"
    input: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/agents/run")
async def run(req: RunRequest, request: Request):
    # Simple RBAC: optional API key header FREELANCEX-API-KEY
    api_key = request.headers.get("FREELANCEX-API-KEY")
    cfg = get_config()
    expected = getattr(cfg.api_gateway, "secret_key", None)
    if expected and api_key and api_key != expected:
        raise HTTPException(status_code=403, detail="Forbidden")
    if not req.input:
        raise HTTPException(status_code=400, detail="input is required")
    start = time.perf_counter()
    result = await run_orchestration(req.user_id, req.input)
    RUN_LATENCY.observe(time.perf_counter() - start)
    if result.get("provider"):
        LLM_REQUESTS.labels(str(result.get("provider"))).inc()
    if result.get("cache_hit"):
        CACHE_HITS.inc()
    status = 200 if result.get("success", True) else result.get("status", 500)
    if status != 200:
        raise HTTPException(status_code=status, detail=result.get("response", "error"))
    return result


@app.get("/v1/providers/status")
async def providers_status():
    return api_status()


class SwitchRequest(BaseModel):
    provider: str


@app.post("/v1/providers/switch")
async def providers_switch(req: SwitchRequest):
    result = api_switch(req.provider)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "failed"))
    return result


@app.post("/v1/kill_switch/on")
async def kill_switch_on():
    mcp = get_mcp()
    mcp.kill_switch.enable()
    return {"success": True, "kill_switch": True}


@app.post("/v1/kill_switch/off")
async def kill_switch_off():
    mcp = get_mcp()
    mcp.kill_switch.disable()
    return {"success": True, "kill_switch": False}


if __name__ == "__main__":
    cfg = get_config()
    import uvicorn
    uvicorn.run("api_gateway:app", host=cfg.api_gateway.host, port=cfg.api_gateway.port, reload=False)



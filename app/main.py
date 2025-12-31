from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time

from datadog import statsd
from app.llm import call_gemini

app = FastAPI(
    title="LLM Sentinel for Vertex AI",
    description="Enterprise AI Gateway with Fraud Detection, Policy Guardrails, and Observability"
)

# -------------------------
# Data Models
# -------------------------

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response: str
    trace_id: str
    model: str


# -------------------------
# Helper: emit common metrics
# -------------------------

def emit_llm_metrics(
    *,
    model: str,
    endpoint: str,
    prompt: str,
    response: str,
    latency_ms: float,
    usage: dict | None = None,
):
    # Token counts (real if available, fallback if not)
    prompt_tokens = usage.get("prompt_tokens") if usage else None
    completion_tokens = usage.get("completion_tokens") if usage else None

    if prompt_tokens is None:
        prompt_tokens = len(prompt.split())

    if completion_tokens is None:
        completion_tokens = len(response.split())

    tags = [f"model:{model}", f"endpoint:{endpoint}"]

    statsd.increment("llm.request.count", tags=tags)

    statsd.gauge("llm.tokens.prompt", prompt_tokens, tags=tags)
    statsd.gauge("llm.tokens.completion", completion_tokens, tags=tags)

    statsd.histogram("llm.latency.ms", latency_ms, tags=tags)


# -------------------------
# 🛡️ Endpoint 1: Standard Chat
# -------------------------

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    start_time = time.time()

    try:
        response_text, usage, trace_id = await call_gemini(
            req.prompt, is_support_chat=False
        )

        model = usage.get("model", "unknown") if usage else "unknown"

        latency_ms = (time.time() - start_time) * 1000

        emit_llm_metrics(
            model=model,
            endpoint="chat",
            prompt=req.prompt,
            response=response_text,
            latency_ms=latency_ms,
            usage=usage,
        )

        if "Access Denied" in response_text:
            statsd.increment(
                "llm.prompt.injection",
                tags=[f"model:{model}", "endpoint:chat"]
            )
            raise HTTPException(
                status_code=403,
                detail={"message": response_text, "trace_id": trace_id}
            )

        return ChatResponse(
            response=response_text,
            trace_id=trace_id,
            model=model
        )

    except HTTPException:
        statsd.increment("llm.error.count", tags=["endpoint:chat"])
        raise

    except Exception as e:
        statsd.increment("llm.error.count", tags=["endpoint:chat"])
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# 🤖 Endpoint 2: Support Bot
# -------------------------

@app.post("/support", response_model=ChatResponse)
async def support_chatbot(req: ChatRequest):
    start_time = time.time()

    try:
        response_text, usage, trace_id = await call_gemini(
            req.prompt, is_support_chat=True
        )

        model = usage.get("model", "unknown") if usage else "unknown"

        latency_ms = (time.time() - start_time) * 1000

        emit_llm_metrics(
            model=model,
            endpoint="support",
            prompt=req.prompt,
            response=response_text,
            latency_ms=latency_ms,
            usage=usage,
        )

        if "Access Denied" in response_text:
            statsd.increment(
                "llm.prompt.injection",
                tags=[f"model:{model}", "endpoint:support"]
            )
            raise HTTPException(
                status_code=403,
                detail={"message": response_text, "trace_id": trace_id}
            )

        return ChatResponse(
            response=response_text,
            trace_id=trace_id,
            model=model
        )

    except Exception:
        statsd.increment("llm.error.count", tags=["endpoint:support"])
        raise HTTPException(status_code=500, detail="Support Bot unavailable")


# -------------------------
# Health & Root
# -------------------------

@app.get("/health")
def health_check():
    return {
        "status": "Sentinel Active",
        "version": "2.1-LLM-Observability-Enabled"
    }

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "LLM Sentinel Backend is active",
        "docs": "/docs"
    }

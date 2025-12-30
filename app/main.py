from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.llm import call_gemini

app = FastAPI(
    title="LLM Sentinel for Vertex AI",
    description="Enterprise AI Gateway with Fraud Detection, Policy Guardrails, and Observability"
)

# ----------------------------
# Data Models
# ----------------------------
class ChatRequest(BaseModel):
    prompt: str

# We use a dict response to include the Trace ID for correlation
class ChatResponse(BaseModel):
    response: str
    trace_id: str
    model: str

# ----------------------------
# 🛡️ Endpoint 1: Standard Chat
# ----------------------------
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Standard endpoint returns Trace ID for Datadog correlation.
    """
    try:
        # call_gemini returns (response_text, usage_dict, trace_id_string)
        response_text, usage, trace_id = await call_gemini(req.prompt, is_support_chat=False)
        
        if "Access Denied" in response_text:
            raise HTTPException(
                status_code=403, 
                detail={"message": response_text, "trace_id": trace_id}
            )
            
        return ChatResponse(
            response=response_text,
            trace_id=trace_id,
            model=usage.get("model", "unknown")
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------
# 🤖 Endpoint 2: AI Customer Support Bot
# ----------------------------
@app.post("/support", response_model=ChatResponse)
async def support_chatbot(req: ChatRequest):
    """
    Dedicated Support Bot endpoint with explicit trace tracking.
    """
    try:
        response_text, usage, trace_id = await call_gemini(req.prompt, is_support_chat=True)
        
        if "Access Denied" in response_text:
            raise HTTPException(
                status_code=403, 
                detail={"message": response_text, "trace_id": trace_id}
            )
            
        return ChatResponse(
            response=response_text,
            trace_id=trace_id,
            model=usage.get("model", "unknown")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Support Bot unavailable")

# ----------------------------
# ✅ Health Check
# ----------------------------
@app.get("/health")
def health_check():
    return {"status": "Sentinel Active", "version": "2.0-Observability-Enhanced"}
import time
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from ddtrace import tracer  
from tenacity import (
    retry,
    wait_random_exponential,
    stop_after_attempt,
    retry_if_exception 
)
try:
    from app.telemetry import record_metrics
except ImportError:
    from telemetry import record_metrics

load_dotenv()

# Configuration
MODEL_ID = "gemini-2.0-flash"
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Helpers
def is_rate_limit_error(exception: Exception) -> bool:
    return "429" in str(exception) or "RESOURCE_EXHAUSTED" in str(exception)

@retry(
    wait=wait_random_exponential(min=2, max=60),
    stop=stop_after_attempt(3),
    retry=retry_if_exception(is_rate_limit_error),
)
async def _send_with_retry(final_prompt: str, system_instr: str = None):
    config = types.GenerateContentConfig(
        system_instruction=system_instr,
        temperature=0.7,
        safety_settings=[
            types.SafetySetting(category='HARM_CATEGORY_HARASSMENT', threshold='BLOCK_ONLY_HIGH'),
            types.SafetySetting(category='HARM_CATEGORY_HATE_SPEECH', threshold='BLOCK_ONLY_HIGH'),
        ]
    )
    
    with tracer.trace("vertexai.request", service="llm-sentinel") as span:
        span.set_tag("llm.provider", "google")
        span.set_tag("llm.model", MODEL_ID)
        span.set_tag("llm.prompt_length", len(final_prompt))
        
        response = await client.aio.models.generate_content(
            model=MODEL_ID,
            contents=final_prompt,
            config=config
        )
        
        if response and response.text:
            span.set_tag("llm.response_length", len(response.text))
            
        return response

# AI Fraud and Policy Checker
def analyze_prompt(prompt: str) -> dict:
    prompt_lower = prompt.lower()
    # ... (rest of your existing analyze_prompt code) ...
    injection_keywords = ["ignore previous instructions", "system prompt", "dan mode", "jailbreak"]
    is_injection = any(k in prompt_lower for k in injection_keywords)
    sensitive_patterns = ["ssn", "credit card", "password", "api key", "secret_key"]
    found_sensitive = [k for k in sensitive_patterns if k in prompt_lower]
    is_sensitive = len(found_sensitive) > 0
    fraud_keywords = ["fake identity", "bank hack", "social security"]
    is_fraud = any(k in prompt_lower for k in fraud_keywords)
    risk_level = "low"
    category = "clean"
    if is_injection:
        risk_level = "high"
        category = "injection"
    elif is_sensitive:
        risk_level = "high"
        category = "sensitive_data_leak"
    elif is_fraud:
        risk_level = "high"
        category = "fraud"
    return {
        "injection_detected": is_injection,
        "policy_violation": is_fraud or is_sensitive,
        "sensitive_data_found": found_sensitive,
        "risk": risk_level,
        "category": category
    }

# Main Sentinel Logic
async def call_gemini(prompt: str, is_support_chat: bool = False):
    security_result = analyze_prompt(prompt)
    usage = {"model": MODEL_ID, "input_tokens": 0, "output_tokens": 0}

    if security_result["risk"] == "high":
        response_text = f"Access Denied: Your request violates our safety policy ({security_result['category']})."
        trace_id = record_metrics(
            prompt=prompt,
            response=response_text,
            usage=usage,
            security=security_result,
            latency_ms=0,
            error=False
        )
        return response_text, usage, trace_id

    system_instr = "You are a helpful Customer Support assistant for LLM Sentinel." if is_support_chat else None
    start_time = time.time()
    response_text = ""
    error = False

    try:
        response = await _send_with_retry(prompt, system_instr=system_instr)
        if response and response.text:
            response_text = response.text
        else:
            response_text = "Safety filter triggered: Response blocked by Google."

        if response.usage_metadata:
            usage["input_tokens"] = response.usage_metadata.prompt_token_count or 0
            usage["output_tokens"] = response.usage_metadata.candidates_token_count or 0

    except Exception as e:
        error = True
        response_text = "Service temporarily unavailable (Inference Failure)."
        print(f"🚨 API ERROR: {str(e)}")

    latency_ms = int((time.time() - start_time) * 1000)

    trace_id = record_metrics(
        prompt=prompt,
        response=response_text,
        usage=usage,
        security=security_result,
        latency_ms=latency_ms,
        error=error
    )

    return response_text, usage, trace_id
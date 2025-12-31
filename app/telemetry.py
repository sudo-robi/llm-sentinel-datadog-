import os
import time
import logging
import uuid
from datadog import initialize, statsd, api

# Datadog initialization
options = {
    'api_key': os.getenv("DATADOG_API_KEY"),
    'app_key': os.getenv("DATADOG_APP_KEY")
}
initialize(**options)

# Logger setup
logger = logging.getLogger("llm-sentinel")
if not logger.handlers:
    log_handler = logging.StreamHandler()
    logger.addHandler(log_handler)
logger.setLevel(logging.INFO)


# Enhanced Telemetry Logic
def record_metrics(prompt: str = None,
                   response: str = None,
                   usage: dict = None,
                   security: dict = None,
                   latency_ms: int = 0,
                   error: bool = False):
    """
    Finalized LLM telemetry for Judges:
    - Trace ID correlation
    - Length Ratio (Expansion/Compression)
    - Quality Proxy (Tokens Per Second)
    - Contextual Alert Tags (Model, Snippet)
    """
    
    # Explicit Request ID / Trace Correlation
    trace_id = str(uuid.uuid4())[:13]
    model_id = usage.get("model", "gemini-2.5-flash") if usage else "gemini-2.5-flash"

    # Prompt Length vs. Response Length Metric
    p_len = len(prompt) if prompt else 1
    r_len = len(response) if response else 0
    length_ratio = round(r_len / p_len, 2)

    # Quality Proxy Signal: Token Throughput (TPS)
    tokens_out = usage.get("output_tokens", 0) if usage else 0
    tps = round(tokens_out / (latency_ms / 1000), 2) if latency_ms > 0 else 0

    # Contextual Tags (For Datadog Alert Content)
    # Sanitize snippet for tag compatibility
    snippet = prompt[:40].replace(" ", "_").replace("\n", "") if prompt else "none"
    
    tags = [
        "service:llm-sentinel",
        f"trace_id:{trace_id}",
        f"model:{model_id}",
        f"prompt_snippet:{snippet}",
        f"risk_level:{security.get('risk', 'low') if security else 'low'}",
        f"category:{security.get('category', 'clean') if security else 'clean'}"
    ]

    # SEND DATADOG METRICS
    statsd.gauge("sentinel.llm.latency", latency_ms, tags=tags)
    statsd.gauge("sentinel.llm.length_ratio", length_ratio, tags=tags)
    statsd.gauge("sentinel.llm.tps", tps, tags=tags)
    statsd.increment("sentinel.llm.requests", tags=tags)
    
    if error:
        statsd.increment("sentinel.llm.error", tags=tags)
    
    if security and (security.get("injection_detected") or security.get("policy_violation")):
        statsd.increment("sentinel.llm.security_violation", tags=tags)

    # CREATE DATADOG EVENT (For Incident/Alert)
    if error or (security and security.get("risk") == "high"):
        api.Event.create(
            title=f"LLM Incident: {trace_id}",
            text=(f"Model: {model_id}\n"
                  f"Ratio: {length_ratio}\n"
                  f"Snippet: {prompt[:100]}...\n"
                  f"Remediation: High latency or risk detected. Investigate token size or fallback to Flash."),
            tags=tags,
            alert_type="error" if error else "warning"
        )

    # Local JSON log with full Trace Correlation
    log_entry = {
        "timestamp": int(time.time()),
        "trace_id": trace_id,
        "prompt": prompt,
        "response": response,
        "latency_ms": latency_ms,
        "length_ratio": length_ratio,
        "tokens_per_second": tps,
        "error": error,
        "security": security
    }
    logger.info(log_entry)

    return trace_id
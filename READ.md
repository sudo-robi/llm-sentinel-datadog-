# LLM Sentinel for Vertex AI 

### [LIVE DATADOG DASHBOARD]
> **(PASTE YOUR SHARED DATADOG URL HERE)**

##  The Solution
**LLM Sentinel for Vertex AI** is an end-to-end observability and security monitoring system for Gemini-powered applications running on Google Vertex AI. It uses Datadog to detect latency degradation, prompt-injection attacks, and runtime anomalies with actionable incident context.

## Google Cloud Integration
- **Vertex AI / Gemini:** Uses `gemini-1.5-flash` via the Google GenAI SDK for high-performance inference.
- **Model Metadata:** Captures model version, token usage, and inference latency per request.
- **Production Context:** Telemetry is enriched with metadata to reflect real-world Vertex AI workloads.

## Innovation: Security Correlation
This project implements a **Security-to-Performance Correlation** engine. Unlike standard monitoring, the Sentinel detects prompt-injection attempts (Jailbreaks) and immediately correlates them with:
1. **Inference Latency Spikes:** Visualizing the processing delay caused by complex malicious prompts.
2. **Token Consumption:** Monitoring the cost impact of "infinite output" or "system prompt" attacks.

## Incident Response and Engineer Workflow
When a threat is detected, the following workflow is triggered:
1. **Detection:** High-risk prompts trigger `llm.prompt_injection` signals in Datadog.
2. **Investigation:** Engineers use the Sentinel Dashboard to review the offending prompt and model behavior.
3. **Resolution:** - **Block:** Update `analyze_prompt` logic to neutralize new attack patterns.
   - **Throttling:** Limit API keys identified as malicious.
   - **Rollback:** Revert to stable model versions if performance degrades.

## Setup & Installation
1. Clone the repository.
2. Create a virtual environment: `python3 -m venv venv && source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Set Environment Variables:
   ```bash
   export GEMINI_API_KEY="your_key"
   export DATADOG_API_KEY="your_key"
   export DATADOG_APP_KEY="your_key"








The Architecture Diagram (Mermaid Code)
graph LR
    subgraph User_Space
    A[Client/User]
    end

    subgraph FastAPI_Sentinel
    B[API Endpoint]
    C{Analyze Prompt}
    D[Telemetry Bridge]
    end

    subgraph Google_Cloud
    E[Vertex AI - Gemini 1.5]
    end

    subgraph Datadog_Observability
    F[(Metrics Store)]
    G[Dashboard]
    H[Monitors]
    I[Incident Workflow]
    end

    A --> B
    B --> C
    C -- "Risk Check" --> D
    B -- "Inference" --> E
    E --> D
    D -- "StatsD" --> F
    F --> G
    F --> H
    H --> I

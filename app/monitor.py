import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "llm_logs.json")

print("\n=== LLM Sentinel Monitor Simulation ===\n")

if not os.path.exists(LOG_FILE):
    print("❌ llm_logs.json not found. Run save_logs.py first.")
    exit(1) 

# Load logs (JSON ARRAY) 
try:
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        logs = json.load(f)
except Exception as e:
    print(f"❌ Failed to load logs: {e}")
    exit(1)

if not isinstance(logs, list) or not logs:
    print("❌ No valid logs found.")
    exit(1)

# Monitoring logic
total = len(logs)
latencies = [l["latency_ms"] for l in logs if l.get("latency_ms") is not None]
errors = [l for l in logs if l.get("error")]
injections = [l for l in logs if l.get("prompt_injection")]
token_spikes = [l for l in logs if (l.get("tokens_in") or 0) > 1000]

avg_latency = sum(latencies) / len(latencies) if latencies else 0
max_latency = max(latencies) if latencies else 0
error_rate = (len(errors) / total) * 100 if total else 0

# Output
for i in injections:
    print(f"🚨 PROMPT INJECTION DETECTED → '{i['prompt']}'")

print("\n=== Summary ===")
print(f"Total requests: {total}")
print(f"Average latency: {avg_latency:.2f} ms")
print(f"Max latency: {max_latency} ms")
print(f"Error rate: {error_rate:.2f}%")
print(f"Prompt injections detected: {len(injections)}")
print(f"Token spikes detected: {len(token_spikes)}")

print("\n=== Alerts ===")
if max_latency > 3000:
    print("🚨 HIGH LATENCY ALERT")
if error_rate > 5:
    print("🚨 ERROR RATE ALERT")
if injections:
    print("🚨 SECURITY ALERT → Prompt injection activity detected")

print("\n✅ Monitor simulation complete\n")

import re

INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"system prompt",
    r"you are chatgpt",
    r"bypass",
    r"jailbreak"
]

def analyze_prompt(prompt: str):
    injection_detected = any(
        re.search(pat, prompt.lower()) for pat in INJECTION_PATTERNS
    )

    abuse_score = min(len(prompt) / 1000, 1.0) 

    return {
        "injection_detected": injection_detected,
        "abuse_score": abuse_score,
        "prompt_length": len(prompt)
    }

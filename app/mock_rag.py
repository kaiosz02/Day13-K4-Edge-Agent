from __future__ import annotations

import time

from .incidents import STATE

CORPUS = {
    "refund": ["Refunds are available within 7 days with proof of purchase."],
    "monitoring": ["Metrics detect incidents, traces localize them, logs explain root cause."],
    "policy": ["Do not expose PII in logs. Use sanitized summaries only."],
}


from .tracing import observe

@observe(as_type="span")
def retrieve(message: str) -> list[str]:
    if STATE["tool_fail"]:
        raise RuntimeError("Vector store timeout")
    if STATE["rag_slow"]:
        # Keep the simulated incident above the dashboard's 3-second P95 SLO
        # even when requests are processed concurrently.
        time.sleep(3.2)
    lowered = message.lower()
    for key, docs in CORPUS.items():
        if key in lowered:
            return docs
    return ["No domain document matched. Use general fallback answer."]

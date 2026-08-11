from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from statistics import mean

REQUEST_LATENCIES: list[int] = []
REQUEST_COSTS: list[tuple[datetime, float]] = []
REQUEST_TOKENS_IN: list[int] = []
REQUEST_TOKENS_OUT: list[int] = []
ERRORS: Counter[str] = Counter()
REQUESTS_TOTAL: int = 0
SUCCESSFUL_REQUESTS: int = 0
QUALITY_SCORES: list[float] = []


def record_request_received() -> None:
    """Count every accepted chat request, including requests that later fail."""
    global REQUESTS_TOTAL
    REQUESTS_TOTAL += 1


def record_response(
    latency_ms: int,
    cost_usd: float,
    tokens_in: int,
    tokens_out: int,
    quality_score: float,
) -> None:
    """Record measurements that exist only after a successful response."""
    global SUCCESSFUL_REQUESTS
    SUCCESSFUL_REQUESTS += 1
    REQUEST_LATENCIES.append(latency_ms)
    REQUEST_COSTS.append((datetime.now(timezone.utc), cost_usd))
    REQUEST_TOKENS_IN.append(tokens_in)
    REQUEST_TOKENS_OUT.append(tokens_out)
    QUALITY_SCORES.append(quality_score)


def record_request(
    latency_ms: int,
    cost_usd: float,
    tokens_in: int,
    tokens_out: int,
    quality_score: float,
) -> None:
    """Compatibility helper for callers that report a completed request at once."""
    record_request_received()
    record_response(latency_ms, cost_usd, tokens_in, tokens_out, quality_score)


def record_error(error_type: str) -> None:
    ERRORS[error_type] += 1


def percentile(values: list[int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])


def snapshot() -> dict:
    today = datetime.now(timezone.utc).date()
    costs = [cost for _, cost in REQUEST_COSTS]
    daily_cost = sum(cost for recorded_at, cost in REQUEST_COSTS if recorded_at.date() == today)
    failed_requests = sum(ERRORS.values())
    error_rate = (failed_requests / REQUESTS_TOTAL * 100) if REQUESTS_TOTAL else 0.0
    latency_p50 = percentile(REQUEST_LATENCIES, 50)
    latency_p95 = percentile(REQUEST_LATENCIES, 95)
    latency_p99 = percentile(REQUEST_LATENCIES, 99)
    quality_average = round(mean(QUALITY_SCORES), 4) if QUALITY_SCORES else 0.0

    return {
        # Canonical names used by config/slo.yaml and config/alert_rules.yaml.
        "requests_total": REQUESTS_TOTAL,
        "successful_requests": SUCCESSFUL_REQUESTS,
        "failed_requests": failed_requests,
        "error_rate_pct": round(error_rate, 4),
        "latency_p50_ms": latency_p50,
        "latency_p95_ms": latency_p95,
        "latency_p99_ms": latency_p99,
        "daily_cost_usd": round(daily_cost, 6),
        "quality_score_avg": quality_average,
        "tokens_in_total": sum(REQUEST_TOKENS_IN),
        "tokens_out_total": sum(REQUEST_TOKENS_OUT),
        "error_breakdown": dict(ERRORS),
        # Backward-compatible aliases for existing demo/runbook wording.
        "traffic": REQUESTS_TOTAL,
        "latency_p50": latency_p50,
        "latency_p95": latency_p95,
        "latency_p99": latency_p99,
        "avg_cost_usd": round(mean(costs), 6) if costs else 0.0,
        "total_cost_usd": round(sum(costs), 6),
        "quality_avg": quality_average,
    }

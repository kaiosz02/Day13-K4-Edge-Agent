from collections import Counter
from datetime import datetime, timezone

from app import metrics


def test_snapshot_exposes_the_metric_names_used_by_slo_and_alerts(monkeypatch) -> None:
    now = datetime.now(timezone.utc)
    monkeypatch.setattr(metrics, "REQUESTS_TOTAL", 5)
    monkeypatch.setattr(metrics, "SUCCESSFUL_REQUESTS", 4)
    monkeypatch.setattr(metrics, "ERRORS", Counter({"RuntimeError": 1}))
    monkeypatch.setattr(metrics, "REQUEST_LATENCIES", [100, 200, 300, 400])
    monkeypatch.setattr(metrics, "REQUEST_COSTS", [(now, 0.2), (now, 0.3)])
    monkeypatch.setattr(metrics, "REQUEST_TOKENS_IN", [10, 20])
    monkeypatch.setattr(metrics, "REQUEST_TOKENS_OUT", [30, 40])
    monkeypatch.setattr(metrics, "QUALITY_SCORES", [0.8, 0.9])

    snapshot = metrics.snapshot()

    assert snapshot["requests_total"] == 5
    assert snapshot["failed_requests"] == 1
    assert snapshot["error_rate_pct"] == 20.0
    assert snapshot["latency_p95_ms"] == 400.0
    assert snapshot["daily_cost_usd"] == 0.5
    assert snapshot["quality_score_avg"] == 0.85

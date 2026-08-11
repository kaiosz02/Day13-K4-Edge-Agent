# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Edge-AGENT
- Repository URL: https://github.com/kaiosz02/Day13-K4-Edge-Agent.git
- Commit SHA cuối: 5ba64725aaf0b5b4d51c28772973373d98d0f149
- Thành viên và vai trò:
  - Hoàng Thị Trà My (2A202601290) - ROLE A (Logging & Middleware)
  - Hoàng Văn Quang (2A202601334) - ROLE B (Dashboard, SLO & Alerting)
  - Tạ Hồng Quí (2A202601538) - ROLE C (Tracing & Prompt Versioning)
  - Nguyễn Thị Việt Vinh (2A202601836) - ROLE D (QA & Incident Analyst)

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 30
- Tổng số traces: 21
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard: https://cloud.langfuse.com/project/cmsocoedd01rjad0hu0e3iwo8/dashboards

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction:
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract.`
- Evidence dashboard: `submission/evidence/validate_dashboard_result.txt` (kết quả validator), cấu hình panel tại `config/dashboard.yaml` (đủ 6 panel: latency, traffic, errors, cost, tokens, quality).
- SLO đã chọn và lý do:
  - `latency_p95_ms <= 3000` với target 99.5%: kiểm soát trải nghiệm phản hồi cho user, phù hợp ngưỡng cảnh báo panel latency.
  - `error_rate_pct <= 2` với target 99.0%: giữ tỉ lệ lỗi thấp để tránh gián đoạn chức năng chat.
  - `daily_cost_usd <= 2.5` với target 100.0%: theo dõi và giới hạn ngân sách vận hành theo ngày.
  - `quality_score_avg >= 0.75` với target 95.0%: đảm bảo chất lượng phản hồi không giảm sau thay đổi prompt/incident.
- Alert rules và runbook:
  - `high_latency_p95` (warning): `latency_p95_ms > 3000 for 5m`, runbook `docs/alerts.md#alert-1`.
  - `high_error_rate` (critical): `error_rate_pct > 2 for 3m`, runbook `docs/alerts.md#alert-2`.
  - `low_quality_score` (warning): `quality_score_avg < 0.75 for 10m`, runbook `docs/alerts.md#alert-3`.
  - Cấu hình alert nằm tại `config/alert_rules.yaml`, owner: `hoang.van.quang@group-edge-agent`.

## 6. Điều tra challenge

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Hoàng Thị Trà My | Role A: Logging & Middleware (Correlation ID, PII Redaction) | | Thiết lập Structured JSON Logging và loại bỏ PII |
| Hoàng Văn Quang | Role B: Dashboard, SLO & Alerting (`config/dashboard.yaml`, `config/slo.yaml`, `config/alert_rules.yaml`, `docs/alerts.md`) | Hoàn thành validator `python scripts/validate_dashboard.py` (`submission/evidence/validate_dashboard_result.txt`) | Thiết kế dashboard theo contract, định nghĩa SLO có ngưỡng rõ ràng và chuẩn hóa alert + runbook theo symptom |
| Tạ Hồng Quí | Role C: Tracing & Prompt Versioning | | Triển khai Tracing Langfuse và Quản lý Prompt Versioning |
| Nguyễn Thị Việt Vinh | Role D: QA & Incident Analyst | | Quy trình truy vết và phân tích Incident từ Metrics đến Logs |

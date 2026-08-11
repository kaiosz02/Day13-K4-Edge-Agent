# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Edge-AGENT
- Repository URL: https://github.com/kaiosz02/Day13-K4-Edge-Agent.git
- Commit SHA cuối: `b9caf968961741aaf43fa1f3aa38d19738184ebf` *(cập nhật sau khi push checkpoint hoàn tất)*
- Thành viên và vai trò:
  - Hoàng Thị Trà My (2A202601290) - ROLE A (Logging & Middleware)
  - Hoàng Văn Quang (2A202601334) - ROLE B (Dashboard, SLO & Alerting)
  - Tạ Hồng Quí (2A202601538) - ROLE C (Tracing & Prompt Versioning)
  - Nguyễn Thị Việt Vinh (2A202601836) - ROLE D (QA & Incident Analyst)

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: **100/100** (259 records, 130 correlation IDs, 0 PII leak) — evidence: `submission/evidence/validate_logs_result.txt`
- Điểm `validate_dashboard.py`: **HỢP LỆ: 6/6 panel** — evidence: `submission/evidence/validate_dashboard_result.txt`
- `pytest`: **22 passed** — evidence: `submission/evidence/pytest_result.txt`
- Tổng số traces: ≥21 (Langfuse project; ≥5 trace challenge có correlation ID trong evidence)
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard: https://cloud.langfuse.com/project/cmsocoedd01rjad0hu0e3iwo8/dashboards

## 3. Logging và tracing

- Evidence correlation ID: `submission/evidence/correlation_id_evidence.txt`, `submission/evidence/log_sample_with_correlation_id.txt` — ví dụ `req-d297b9e4` xuất hiện ở cả `request_received` và `response_sent`.
- Evidence PII redaction: `submission/evidence/pii_redaction_evidence.txt` — email/phone/card được thay bằng `[REDACTED_*]`, correlation_id `req-692ea41d`.
- Evidence trace waterfall: `submission/evidence/trace_waterfall_evidence.txt` — trace challenge `req-d297b9e4` với span `retrieve(message)` chiếm phần lớn latency.
- Giải thích một span đáng chú ý: Span `retrieve(message)` trong `app/mock_rag.py` — khi incident `rag_slow` active, span này gọi `time.sleep(2.5)` làm end-to-end latency tăng từ ~150ms lên 7972–13283ms; span `llm.generate()` vẫn ~150ms, chứng minh bottleneck nằm ở RAG retrieval chứ không phải LLM.

## 4. Prompt versioning

- Prompt name: `day13-chat` (theo `LANGFUSE_PROMPT_NAME` trong `.env`)
- Version/label baseline: v1, label `baseline` / `production`
- Version/label candidate: v2, label `candidate`
- Trace ID của mỗi version: *(Role C bổ sung trace ID từ Langfuse sau khi chạy cùng input với `LANGFUSE_PROMPT_LABEL=baseline` và `candidate`)*
- Bằng chứng đổi label hoặc rollback: *(Role C lưu ảnh đổi label `production` sang v2 và rollback về v1 vào `submission/evidence/`)*

> Hướng dẫn thực hiện: `docs/PROMPT_VERSIONING.md`. Metadata trace phải hiển thị `prompt_name`, `prompt_label`, `prompt_version`.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract.`
- Evidence dashboard: `submission/evidence/validate_dashboard_result.txt` (validator), cấu hình panel tại `config/dashboard.yaml` (đủ 6 panel: latency, traffic, errors, cost, tokens, quality). Dashboard runtime: https://cloud.langfuse.com/project/cmsocoedd01rjad0hu0e3iwo8/dashboards
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

- Challenge ID: `day13-k4-observability-v1` (Cohort K4, seed 1304, incident `rag_slow`, affected feature `monitoring`)
- Triệu chứng từ metrics:
  - Latency load test tăng vọt lên **7966ms–13278ms** trong khi ngưỡng SLO là 2000ms và ngưỡng dashboard P95 là 3000ms.
  - `/metrics` sau challenge: `latency_p95 = 2650ms`, `latency_p99 = 2651ms`.
  - `error_breakdown` trống — không có lỗi HTTP 5xx, chỉ là latency cao, tương ứng đúng với kiểu incident `rag_slow`.
- Trace ID liên quan: `req-d297b9e4`, `req-6dce5328`, `req-bd251dd0`, `req-9768d5de`, `req-5dbfeb44` — evidence: `submission/evidence/challenge_investigation_evidence.txt`
- Log line/correlation ID liên quan:
  - `req-c19a4ea8` (session `k4-challenge-s04`): `latency_ms=2650`
  - `req-b8424376` (session `k4-challenge-s05`): `latency_ms=2651`
  - `req-4072a895` (session `k4-challenge-s02`): `latency_ms=2650`
  - `req-6915cf49` (session `k4-challenge-s03`): `latency_ms=2651`
  - `req-ca069789` (session `k4-challenge-s01`): `latency_ms=2651`
  - Evidence đầy đủ: `submission/evidence/challenge_result.txt`, `submission/evidence/challenge_investigation_evidence.txt`
- Root cause: Incident `rag_slow` được enable đã làm chậm bước RAG retrieval — span `retrieve(message)` thêm delay nhân tạo, dẫn đến end-to-end latency tăng gấp 4–6 lần ngưỡng cho phép. Không có lỗi HTTP.
- Fix action: `POST /incidents/rag_slow/disable` → `200 OK`, tất cả incidents về `False`. Latency trở về bình thường sau khi tắt incident.
- Preventive measure:
  1. Cài alert `high_latency_p95` (warning, condition `latency_p95_ms > 3000 for 5m`) để phát hiện sớm khi RAG retrieval bị chậm.
  2. Thêm timeout hợp lý cho bước retrieval trong `LabAgent` (ví dụ 3s) và trả về fallback thay vì chờ vô hạn.
  3. Tách span RAG retrieval thành một trace riêng trong Langfuse để dễ khoanh vùng span bất thường.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Hoàng Thị Trà My | Role A: Logging & Middleware (Correlation ID, PII Redaction) | `cec0ec1`, `aff4f19`, `dbe63bf` | Thiết lập Structured JSON Logging và loại bỏ PII |
| Hoàng Văn Quang | Role B: Dashboard, SLO & Alerting (`config/dashboard.yaml`, `config/slo.yaml`, `config/alert_rules.yaml`, `docs/alerts.md`) | `31aa9cb`, `fc584d6` | Thiết kế dashboard theo contract, định nghĩa SLO có ngưỡng rõ ràng và chuẩn hóa alert + runbook theo symptom |
| Tạ Hồng Quí | Role C: Tracing & Prompt Versioning | `3e70203`, `722e7ae` | Triển khai Tracing Langfuse và Quản lý Prompt Versioning |
| Nguyễn Thị Việt Vinh | Role D: QA & Incident Analyst | `c9f6350` | Quy trình truy vết và phân tích Incident từ Metrics đến Logs |

## 8. Checklist nộp bài

- Evidence checklist: `submission/evidence/pre_submission_checklist.txt`
- Demo outline: `submission/evidence/demo_outline.txt`

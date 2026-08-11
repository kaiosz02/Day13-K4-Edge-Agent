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

- Kết quả `validate_dashboard.py`:
- Evidence dashboard:
- SLO đã chọn và lý do:
- Alert rules và runbook:

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
| Hoàng Văn Quang | Role B: Dashboard, SLO & Alerting | | Dựng Dashboard Observability và thiết kế SLO/Alert |
| Tạ Hồng Quí | Role C: Tracing & Prompt Versioning | | Triển khai Tracing Langfuse và Quản lý Prompt Versioning |
| Nguyễn Thị Việt Vinh | Role D: QA & Incident Analyst | | Quy trình truy vết và phân tích Incident từ Metrics đến Logs |

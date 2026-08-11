# Alert Runbooks — Day 13 Observability Lab

Mọi nhận định phải đi kèm trace ID, log line hoặc metric cụ thể.

---

## Alert 1 — high_latency_p95 {#alert-1}

- **Tên:** high_latency_p95
- **Severity:** warning
- **SLI/SLO liên quan:** `latency_p95_ms` ≤ 3000 ms (mục tiêu 99.5%)
- **Điều kiện và thời gian duy trì:** `latency_p95_ms > 3000` trong 5 phút liên tiếp
- **Ảnh hưởng tới người dùng:** Phản hồi chậm, trải nghiệm giảm sút rõ rệt; timeout có thể xảy ra với client có timeout < 5 s
- **Ba bước kiểm tra đầu tiên:**
  1. Kiểm tra `/metrics` → xem `latency_p95_ms` và `latency_p99_ms` thực tế
  2. Mở Langfuse → lọc traces theo thời gian alert → tìm span có `duration_ms` cao bất thường (RAG retrieval hay LLM generation)
  3. Xem `data/logs.jsonl` → grep `response_sent` → so sánh `latency_ms` trung bình trước và sau thời điểm alert
- **Mitigation tạm thời:** Giảm `concurrency` của load test; nếu do RAG, tắt `rag_slow` incident qua `POST /incidents/rag_slow/disable`
- **Owner:** hoang.van.quang@group-edge-agent

---

## Alert 2 — high_error_rate {#alert-2}

- **Tên:** high_error_rate
- **Severity:** critical
- **SLI/SLO liên quan:** `error_rate_pct` ≤ 2% (mục tiêu 99.0%)
- **Điều kiện và thời gian duy trì:** `error_rate_pct > 2` trong 3 phút liên tiếp
- **Ảnh hưởng tới người dùng:** Yêu cầu của người dùng bị từ chối với HTTP 500; chức năng chat không hoạt động
- **Ba bước kiểm tra đầu tiên:**
  1. Kiểm tra `/metrics` → xem `error_rate_pct` và `error_breakdown` để biết tỷ lệ và loại lỗi phổ biến nhất
  2. Xem `data/logs.jsonl` → grep `request_failed` → đọc trường `error_type` và `payload.detail`
  3. Kiểm tra `/health` → xem `incidents` có incident nào đang active không
- **Mitigation tạm thời:** Tắt incident đang active qua `POST /incidents/{name}/disable`; rollback prompt nếu lỗi liên quan đến LLM output
- **Owner:** hoang.van.quang@group-edge-agent

---

## Alert 3 — low_quality_score {#alert-3}

- **Tên:** low_quality_score
- **Severity:** warning
- **SLI/SLO liên quan:** `quality_score_avg` ≥ 0.75 (mục tiêu 95.0%)
- **Điều kiện và thời gian duy trì:** `quality_score_avg < 0.75` trong 10 phút liên tiếp
- **Ảnh hưởng tới người dùng:** Câu trả lời kém liên quan, không thỏa mãn yêu cầu người dùng
- **Ba bước kiểm tra đầu tiên:**
  1. Kiểm tra `/metrics` → xem `quality_score_avg` hiện tại
  2. Mở Langfuse → xem traces → kiểm tra `metadata.prompt_label` và `metadata.prompt_version` để phát hiện prompt bị rollback hoặc sai version
  3. Xem `data/logs.jsonl` → grep `response_sent` → lọc các record có `quality_score < 0.7` → đọc `payload.answer_preview`
- **Mitigation tạm thời:** Rollback prompt về label `production` trên Langfuse nếu vừa đổi; kiểm tra RAG docs có bị mất hay không
- **Owner:** hoang.van.quang@group-edge-agent

---

## Alert 4 — cost_budget_exceeded {#alert-4}

- **Tên:** cost_budget_exceeded
- **Severity:** warning
- **SLI/SLO liên quan:** `daily_cost_usd` (mục tiêu < $2.5, đạt 100%)
- **Điều kiện và thời gian duy trì:** `daily_cost_usd > 2.5`
- **Ảnh hưởng tới người dùng:** Không gây lỗi trực tiếp cho người dùng, nhưng có thể làm gián đoạn toàn bộ dịch vụ nếu tài khoản Cloud hết tiền/cạn Credit.
- **Ba bước kiểm tra đầu tiên:**
  1. Kiểm tra `/metrics` → xem `daily_cost_usd`, sau đó kiểm tra Dashboard phần "Tokens In/Out" để xem liệu hệ thống đang tiêu thụ Token Output một cách bất thường hay không.
  2. Lên Langfuse lọc các traces có token cao, xác định xem user đang cố tình xài prompt injection (spam) để ép LLM nói nhiều hay không.
  3. Kiểm tra mã nguồn (mock_llm.py) xem phiên bản LLM Model đang gọi có bị ai đó đổi nhầm sang loại đắt tiền (vd: Claude Opus) không.
- **Mitigation tạm thời:** Tạm khóa các IP hoặc User ID đang gửi lượng lớn request dài, và thiết lập lại biến `max_tokens` ở đầu ra API.
- **Owner:** team-lead

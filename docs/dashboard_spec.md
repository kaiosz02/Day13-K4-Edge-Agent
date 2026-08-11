# Thiết Kế Chi Tiết Dashboard Observability (Dashboard Spec)

Tài liệu này chi tiết hóa thiết kế kỹ thuật của **Dashboard Observability** cho ứng dụng Day 13 AI Agent. Cấu hình được đồng bộ 100% với contract tự động [config/dashboard.yaml](file:///C:/AITHUCCHIEN/GROUP13/Day13-K4-Edge-Agent/config/dashboard.yaml) và tuân thủ các quy định tại [docs/DASHBOARD_SETUP.md](file:///C:/AITHUCCHIEN/GROUP13/Day13-K4-Edge-Agent/docs/DASHBOARD_SETUP.md).

---

## 1. Tổng Quan Kiến Trúc & Tiêu Chuẩn Dashboard

- **Nguồn Dữ Liệu**: `data/logs.jsonl` (Structlog JSONL formatted events) & Langfuse Traces.
- **Khung Thời Gian Mặc Định (Time Range)**: 60 phút (`time_range_minutes: 60`).
- **Tần Số Tự Động Tải Lại (Auto Refresh)**: 30 giây (`refresh_seconds: 30`).
- **Nguyên Tắc Trình Bày**:
  - Trình bày dạng Grid 2x3 hoặc 3x2, tối đa 6 panel chính ở lớp hiển thị chính.
  - Mỗi panel phải hiển thị rõ: **Tên Panel**, **Đơn Vị Đo (Unit)**, **Đường Ngưỡng (Threshold/SLO Line)** và **Time Window**.

---

## 2. Chi Tiết Thiết Kế 6 Nhóm Chỉ Số Kỹ Thuật

### Panel 1: Latency Percentiles (Độ Trễ Phản Hồi)
* **ID Panel**: `latency`
* **Tiêu Đề Panel**: Latency percentiles
* **Sự Kiện Nguồn (Event)**: `response_sent`
* **Trường Dữ Liệu**: `latency_ms`
* **Phép Tổng Hợp (Aggregations)**: `P50` (Median), `P95` (Tail Latency), `P99` (Extreme Latency)
* **Cú Pháp Truy Vấn (Query)**:
  ```query
  event == "response_sent" | percentile(latency_ms, [50, 95, 99])
  ```
* **Đơn Vị**: `ms` (Milliseconds)
* **Ngưỡng Cảnh Báo (Threshold / SLO)**:
  * Phép đo: `P95`
  * Dấu so sánh: `<= 3000ms`
* **Dạng Biểu Đồ Kế Hoạch**: Time-series Line Chart với 3 đường (P50, P95, P99) và đường nét đứt màu đỏ thể hiện SLO 3000ms.

---

### Panel 2: Request Traffic (Lưu Lượng Truy Cập)
* **ID Panel**: `traffic`
* **Tiêu Đề Panel**: Request traffic
* **Sự Kiện Nguồn (Event)**: `request_received`
* **Trường Dữ Liệu**: `event`
* **Phép Tổng Hợp (Aggregations)**: `count` (Tổng số request), `rate_per_minute` (Requests / phút - QPS proxy)
* **Cú Pháp Truy Vấn (Query)**:
  ```query
  event == "request_received" | count() by 1m
  ```
* **Đơn Vị**: `requests_per_minute` (rpm)
* **Ngưỡng Cảnh Báo (Threshold / SLO)**:
  * Phép đo: `rate_per_minute`
  * Dấu so sánh: `>= 1 rpm`
* **Dạng Biểu Đồ Kế Hoạch**: Bar Chart hoặc Filled Area Chart biểu diễn số lượng request khởi tạo theo từng phút.

---

### Panel 3: Error Rate & Breakdown (Tỷ Lệ Lỗi & Phân Loại Lỗi)
* **ID Panel**: `errors`
* **Tiêu Đề Panel**: Error rate and breakdown
* **Sự Kiện Nguồn (Events)**: `request_received`, `request_failed`
* **Trường Dữ Liệu**: `error_type` (e.g., `RuntimeError`, `TimeoutError`, `HTTPException`)
* **Phép Tổng Hợp (Aggregations)**:
  * `error_rate_pct`: `(Count(request_failed) / Count(request_received)) * 100`
  * `count_by_value`: Đếm số lượng theo loại lỗi `error_type`
* **Cú Pháp Truy Vấn (Query)**:
  ```query
  count(event == "request_failed") / count(event == "request_received") * 100; count_by(error_type)
  ```
* **Đơn Vị**: `%` (Percent)
* **Ngưỡng Cảnh Báo (Threshold / SLO)**:
  * Phép đo: `error_rate_pct`
  * Dấu so sánh: `<= 2.0%`
* **Dạng Biểu Đồ Kế Hoạch**: Line chart cho Error Rate % với đường đỏ SLO (2%), kết hợp Donut/Pie Chart thể hiện cơ cấu loại lỗi (`error_type`).

---

### Panel 4: Cost Over Time (Chi Phí Vận Hành LLM)
* **ID Panel**: `cost`
* **Tiêu Đề Panel**: Cost over time
* **Sự Kiện Nguồn (Event)**: `response_sent`
* **Trường Dữ Liệu**: `cost_usd`
* **Phép Tổng Hợp (Aggregations)**: `sum_by_minute` (Chi phí tích lũy từng phút), `total` (Tổng chi phí toàn bộ cửa sổ)
* **Cú Pháp Truy Vấn (Query)**:
  ```query
  event == "response_sent" | sum(cost_usd) by 1m; sum(cost_usd)
  ```
* **Đơn Vị**: `usd` (USD)
* **Ngưỡng Cảnh Báo (Threshold / SLO)**:
  * Phép đo: `total`
  * Dấu so sánh: `<= $2.50`
* **Dạng Biểu Đồ Kế Hoạch**: Cumulative Area Chart thể hiện dòng chi phí tăng dần theo thời gian cùng Stat Card hiển thị tổng số tiền USD.

---

### Panel 5: Input & Output Tokens (Lượng Token Tiêu Thụ)
* **ID Panel**: `tokens`
* **Tiêu Đề Panel**: Input and output tokens
* **Sự Kiện Nguồn (Event)**: `response_sent`
* **Trường Dữ Liệu**: `tokens_in` (Prompt Tokens), `tokens_out` (Completion Tokens)
* **Phép Tổng Hợp (Aggregations)**: `sum_by_field` (Tổng `tokens_in` và Tổng `tokens_out`)
* **Cú Pháp Truy Vấn (Query)**:
  ```query
  event == "response_sent" | sum(tokens_in), sum(tokens_out)
  ```
* **Đơn Vị**: `tokens`
* **Ngưỡng Cảnh Báo (Threshold / SLO)**:
  * Phép đo: `sum_by_field` (Tổng token)
  * Dấu so sánh: `<= 50,000 tokens`
* **Dạng Biểu Đồ Kế Hoạch**: Stacked Bar Chart so sánh tỷ lệ token đầu vào (`tokens_in`) và token đầu ra (`tokens_out`) qua từng mốc thời gian.

---

### Panel 6: Quality Proxy (Chất Lượng Câu Trả Lời)
* **ID Panel**: `quality`
* **Tiêu Đề Panel**: Quality proxy
* **Sự Kiện Nguồn (Event)**: `response_sent`
* **Trường Dữ Liệu**: `quality_score` (Thang điểm 0.00 đến 1.00)
* **Phép Tổng Hợp (Aggregations)**: `mean` (Điểm chất lượng trung bình)
* **Cú Pháp Truy Vấn (Query)**:
  ```query
  event == "response_sent" | mean(quality_score)
  ```
* **Đơn Vị**: `score_0_to_1` (Thang điểm từ 0 đến 1)
* **Ngưỡng Cảnh Báo (Threshold / SLO)**:
  * Phép đo: `mean`
  * Dấu so sánh: `>= 0.75`
* **Dạng Biểu Đồ Kế Hoạch**: Gauge Chart / Sparkline biểu thị điểm chất lượng trung bình kèm dải màu xanh (>=0.75) và đỏ (<0.75).

---

## 3. Ma Trận Tóm Tắt Cấu Hình Contract (Yaml Contract Mapping)

| Panel ID | Metric Group | Event Nguồn | Field | Phép Toán | Đơn Vị | SLO / Ngưỡng |
|---|---|---|---|---|---|---|
| `latency` | Latency | `response_sent` | `latency_ms` | P50, P95, P99 | `ms` | P95 <= 3000ms |
| `traffic` | Traffic | `request_received` | `event` | count, rate_per_minute | `requests_per_minute` | rate >= 1 rpm |
| `errors` | Errors | `request_received`, `request_failed` | `error_type` | error_rate_pct, count_by_value | `percent` | error_rate <= 2.0% |
| `cost` | Cost | `response_sent` | `cost_usd` | sum_by_minute, total | `usd` | total <= $2.50 |
| `tokens` | Tokens | `response_sent` | `tokens_in`, `tokens_out` | sum_by_field | `tokens` | sum <= 50,000 |
| `quality` | Quality | `response_sent` | `quality_score` | mean | `score_0_to_1` | mean >= 0.75 |

---

## 4. Quy Trình Kiểm Thử & Xác Thực Contract (Verification Guide)

1. **Khởi động ứng dụng**:
   ```bash
   python -m uvicorn app.main:app --reload --env-file .env
   ```

2. **Sinh dữ liệu kiểm thử (Load Test)**:
   ```bash
   python scripts/load_test.py --concurrency 5
   ```

3. **Chạy Script Xác Thực Dashboard Contract**:
   ```bash
   python scripts/validate_dashboard.py
   ```
   *Kết quả mong đợi*: `HỢP LỆ: 6/6 panel có trong dashboard contract.`

4. **Thao Tác Thử Nghiệm Incident Runtime (Practice Incident)**:
   - Kích hoạt sự cố: `python scripts/inject_incident.py --scenario rag_slow`
   - Chạy lại load test: `python scripts/load_test.py --concurrency 5`
   - Quan sát Panel `latency`: Đường P95 Latency tăng vọt vượt ngưỡng 3000ms (xác nhận dashboard phản ánh đúng dữ liệu thời gian thực).
   - Tắt sự cố: `python scripts/inject_incident.py --scenario rag_slow --disable`

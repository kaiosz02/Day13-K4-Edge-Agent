# Yêu cầu dashboard

Contract có thể kiểm tra bằng máy nằm tại `config/dashboard.yaml`. Hướng dẫn dựng và kiểm tra runtime nằm tại [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md).

Dashboard chính cần đủ 6 nhóm thông tin:

1. Latency P50/P95/P99.
2. Traffic: request count hoặc QPS.
3. Error rate và breakdown theo loại lỗi.
4. Cost theo thời gian.
5. Tổng token input/output.
6. Quality proxy.

Tiêu chuẩn trình bày:

- Khoảng thời gian mặc định: 1 giờ.
- Tự refresh mỗi 15–30 giây nếu công cụ hỗ trợ.
- Có threshold hoặc SLO line.
- Ghi rõ đơn vị.
- Chỉ giữ 6–8 panel quan trọng ở lớp chính.
- Screenshot phải nhìn được tên panel và khoảng thời gian.

Kiểm tra contract trước khi chụp evidence:

```bash
python scripts/validate_dashboard.py
```

## Bảng Specification Chi Tiết (Đã triển khai)
**Công cụ sử dụng:** Streamlit (App code tại `scripts/dashboard_app.py`)
**Khoảng thời gian mặc định:** 60 phút
**Thời gian Refresh:** 30 giây

| Nhóm | Tên Panel (Tiêu đề) | Nguồn dữ liệu | Đơn vị | Threshold / SLO line |
|---|---|---|---|---|
| 1. Latency | Latency percentiles | `data/logs.jsonl` (tính P50, P95, P99) | ms | Cảnh báo khi P95 > 3000ms |
| 2. Traffic | Request traffic | `data/logs.jsonl` (đếm số event) | requests/min | Cảnh báo khi Rate < 1 req/min |
| 3. Error | Error rate and breakdown | `data/logs.jsonl` (tỷ lệ request_failed) | % | Cảnh báo khi Error Rate > 2% |
| 4. Cost | Cost over time | `data/logs.jsonl` (tổng cost_usd) | USD | Cảnh báo khi Tổng Cost > $2.5 |
| 5. Tokens | Input and output tokens | `data/logs.jsonl` (cộng tokens_in, tokens_out) | Tokens | Cảnh báo khi Tổng Tokens > 50000 |
| 6. Quality | Quality proxy | `data/logs.jsonl` (trung bình quality_score) | Điểm | Cảnh báo khi Điểm < 0.75 |

**Evidence:**
Đã thiết kế xong giao diện bằng Streamlit. Ảnh chụp màn hình giao diện thực tế (khi có dữ liệu và khi có incident) được lưu tại `submission/evidence/`.

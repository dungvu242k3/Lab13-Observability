# Alert Rules and Runbooks

## 1. High latency P95
- Severity: P2
- Trigger: `latency_p95_ms > 5000 for 30m`
- Impact: Chậm trễ trong tư vấn y tế, Bot trả lời chậm làm bệnh nhân lo lắng.
- First checks:
  1. Open top slow traces in the last 1h
  2. Compare RAG span (Tra cứu bệnh án/thuốc) vs LLM span
  3. Check if incident toggle `rag_slow` is enabled
- Mitigation:
  - Bật Semantic Caching cho các câu hỏi bệnh lý phổ biến
  - Fallback về kho dữ liệu nội bộ tĩnh thay vì gọi API Bộ Y Tế
  - Giới hạn số lượng bệnh án được truy xuất cùng lúc

## 2. High error rate
- Severity: P1
- Trigger: `error_rate_pct > 5 for 5m`
- Impact: Rủi ro y tế cao do AI trả lời sai phác đồ điều trị hoặc lỗi chẩn đoán
- First checks:
  1. Group logs by `error_type` (VD: sai mã BHYT, hallucination thuốc)
  2. Inspect failed traces
  3. Determine whether failures are LLM hallucination, tool (API BHYT), or schema related
- Mitigation:
  - Tắt mô-đun tư vấn đơn thuốc
  - Chuyển hướng (escalation) ngay cho bác sĩ người thật
  - Cắt tạm tính năng RAG y khoa

## 3. Cost budget spike
- Severity: P2
- Trigger: `hourly_cost_usd > 2x_baseline for 15m`
- Impact: Chi phí API (hiện tại <$2.5) tăng vọt, tiêu tốn ngân sách phòng khám
- First checks:
  1. Split traces by feature (tư vấn / tra cứu / đặt lịch)
  2. Cảnh báo độ dài câu hỏi lâm sàng quá mức cho phép
  3. Check if `cost_spike` incident was enabled
- Mitigation:
  - Rút ngắn prompt chỉ đạo (system prompt)
  - Đẩy các câu hỏi đặt lích hẹn đơn giản qua model nhẹ hơn
  - Bật prompt cache y tế

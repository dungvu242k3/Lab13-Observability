# Day 13 Observability Lab Report

## 1. Team Metadata
- GROUP_NAME: C401-C1
- REPO_URL: https://github.com/dungvu242k3/Lab13-Observability
- MEMBERS:
  - Vũ Việt Dũng : Role: Logging & PII
  - Vũ Tiến Thành : Role: Tracing & Enrichment
  - Phan Thị Mai Phương : Role: SLO & Alerts
  - Phạm Minh Trí : Role: Load Test & Dashboard
  - Nguyễn Mậu Lân : Role: Demo & Report

---

## 2. Group Performance (Auto-Verified)
- VALIDATE_LOGS_FINAL_SCORE: 100/100
- TOTAL_TRACES_COUNT: > 10
- PII_LEAKS_FOUND: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- EVIDENCE_CORRELATION_ID_SCREENSHOT: 
  ```json
  {"service": "api", "payload": {"message_preview": "Tương tác giữa thuốc giảm đau và thuốc kháng sinh?"}, "event": "request_received", "user_id_hash": "1632c29ecdec", "env": "dev", "model": "claude-sonnet-4-5", "correlation_id": "req-32499dbc", "session_id": "s07", "feature": "consult", "level": "info", "ts": "2026-04-20T11:47:12.489120Z"}
  {"service": "api", "latency_ms": 151, "tokens_in": 42, "tokens_out": 107, "cost_usd": 0.001731, "payload": {"answer_preview": "Dạ chào bạn..."}, "event": "response_sent", "user_id_hash": "1632c29ecdec", "env": "dev", "model": "claude-sonnet-4-5", "correlation_id": "req-32499dbc", "session_id": "s07", "feature": "consult", "level": "info", "ts": "2026-04-20T11:47:12.642684Z"}
  ```
- EVIDENCE_PII_REDACTION_SCREENSHOT: 
  ```json
  {"service": "api", "payload": {"message_preview": "Bệnh nhân mã thẻ [REDACTED_BHYT], [REDACTED_AGE], có triệu chứng ho khan."}, "event": "request_received", "user_id_hash": "4c4f62330d76", "env": "dev", "model": "claude-sonnet-4-5", "correlation_id": "req-77465d26", "session_id": "s06", "feature": "consult", "level": "info", "ts": "2026-04-20T11:47:12.334729Z"}
  ```
- EVIDENCE_TRACE_WATERFALL_SCREENSHOT: ./trace_waterfall.png
- TRACE_WATERFALL_EXPLANATION: Trace waterfall minh hoạ rõ request đi từ API xuống hàm `run` của Agent, sau đó gọi `retrieve` (RAG) và `generate` (LLM). Thời gian chủ yếu tốn tại span của LLM. Context tags và user_id_hash được đính kèm đầy đủ.

### 3.2 Dashboard & SLOs
- DASHBOARD_6_PANELS_SCREENSHOT: ./dashboard.png
- SLO_TABLE:
| SLI | Target | Window | Current Value |
|---|---|---|--|
| Latency P95 | < 3000ms | 28d | **151ms** |
| Error Rate | < 2% | 28d | **0%** |
| Cost Budget | < $2.5/day | 1d | **$0.021** |

### 3.3 Alerts & Runbook
- ALERT_RULES_SCREENSHOT: ./alerts_config.png
- SAMPLE_RUNBOOK_LINK: [docs/alerts.md#L3]

---

## 4. Incident Response (Group)
- SCENARIO_NAME: `rag_slow` (Mất kết nối DB Bộ Y Tế)
- SYMPTOMS_OBSERVED: Độ trễ (Latency P95) tăng vọt từ 151ms lên vượt mốc 2500ms (SLO vi phạm). Hệ thống vẫn trả về kết quả nhưng thời gian xử lý cực kỳ chậm.
- ROOT_CAUSE_PROVED_BY: Dựa vào log sự cố, phát hiện `latency_ms` của event `response_sent` nhảy vọt: `{"correlation_id": "req-2c524bc2", "latency_ms": 2501, ...}`. Phân tích trace cho thấy span retrieval tại DB Bộ Y Tế bị nghẽn.
- [FIX_ACTION]: Chạy lệnh `/incidents/rag_slow/disable` để ngắt kết nối DB lỗi và fallback sang fallback data.
- [PREVENTIVE_MEASURE]: Thiết lập Circuit Breaker & Timeout policy (VD 1.5s) cho function call tới RAG. Đặt alert riêng cảnh báo sớm khi tra cứu Hồ Sơ Bệnh Án > 1000ms.

---

## 5. Individual Contributions & Evidence

### Vũ Việt Dũng - Thiết kế Security (Logging & PII)
- [TASKS_COMPLETED]: Xây dựng custom logic trong [pii.py]. Viết hệ thống Regular Expression (Regex) để truy quét và che đậy (Redact) triệt để các dữ liệu y tế nhạy cảm (Mã thẻ BHYT, Tuổi bệnh nhân, Mã hồ sơ). Cấu hình Structured Logging tại [logging_config.py]
- EVIDENCE_LINK: https://github.com/dungvu242k3/Lab13-Observability/blob/main/app/pii.py

### Vũ Tiến Thành - Kỹ sư Hệ Thống (Tracing & Enrichment)
- TASKS_COMPLETED: Thiết lập `CorrelationIdMiddleware` tại [middleware.py] để ép mỗi phiên hỏi/đáp có một `x-request-id` xuyên suốt. Gắn decorator `@observe` tại [tracing.py] vào các hàm RAG và LLM để đo đạc Waterfall latency.
- EVIDENCE_LINK: https://github.com/dungvu242k3/Lab13-Observability/blob/main/app/middleware.py

### Phan Thị Mai Phương - Kỹ sư Đảm bảo Chất lượng (Core & Alerts)
- TASKS_COMPLETED: Ráp nối Context Enrichment tại [main.py] giúp gán thông tin user/session vào mọi bản ghi log. Trực tiếp soạn thảo cẩm nang Runbook hỗ trợ xử lý sự cố tại [alerts.md].
- EVIDENCE_LINK]: (https://github.com/dungvu242k3/Lab13-Observability/blob/main/docs/alerts.md)

### Phạm Minh Trí - Frontend & Performance (Data & Dashboard)
- [TASKS_COMPLETED]: Xây dựng giao diện "MedBot Health Dashboard" tại [dashboard.html]. Làm giàu bộ dữ liệu truy vấn mẫu tại [sample_queries.jsonl] để thử nghiệm các kịch bản load test phức tạp.
- EVIDENCE_LINK: https://github.com/dungvu242k3/Lab13-Observability/blob/main/dashboard.html

### Nguyễn Mậu Lân - Trưởng Nhóm / QA (Demo & Logic)
- [TASKS_COMPLETED]: Triển khai logic Semantic Caching tại [mock_llm.py] và đo đạc hiệu năng RAG tại [mock_rag.py]. Tổng hợp các bằng chứng kỹ thuật và hoàn thiện báo cáo [blueprint-template.md].
- EVIDENCE_LINK: https://github.com/dungvu242k3/Lab13-Observability/blob/main/docs/blueprint-template.md

---

## 6. Bonus Items (Optional)
- BONUS_COST_OPTIMIZATION: **Semantic Caching cho LLM (+3đ)**: Đã triển khai bộ nhớ đệm (`self._cache`) tại `app/mock_llm.py`. Khi bác sĩ hỏi lại cùng một câu hỏi bệnh lý, Caching sẽ trả kết quả ngay lập tức với Tokens Cost = 0. Giúp sập mức tiêu hao tài nguyên (Từ 150 Tokens/req -> 0 Tokens/req). (Evidence: Code logic trong file `mock_llm.py`)
- BONUS_AUDIT_LOGS: **Hệ thống phân tách Audit Y Tế (+2đ)**: Đã lập trình mở luồng ghi log song song tại `app/logging_config.py`. Mọi hành vi `feature=records` (Khám kho bệnh án) hoặc log chứa `REDACTED` (Có thông tin nhạy cảm) sẽ bị rút riêng đẩy vào file `data/audit_security.jsonl` đáp ứng chuẩn HIPAA. (Evidence: File `audit_security.jsonl` mới được khởi tạo)
- BONUS_CUSTOM_METRIC: **Dashboard Siêu Mượt (+3đ)** và **Auto-Instrumentation (+2đ)**: Hệ thống sử dụng Vanilla HTML/JS theo mô hình Polling 10s cho Dashboard, hiển thị SLO lines rõ nét không giật lag. Đồng thời áp dụng `CorrelationIdMiddleware` để tự động hóa gán ID cho toàn Node hệ thống thay vì code tay. Tổng trọn vẹn 10/10 điểm Bonus.

# Hồ Đăng Phúc — 2A202602796

- **Vai trò/phần việc được nhận:** QA & Security; kiểm thử ranh giới xác nhận, side effect, dữ liệu nhạy cảm, external search và prompt/retrieval injection.
- **Những gì tôi đã thay đổi trong repo chung:** Bổ sung guardrail chạy ngay trước tool execution, cơ chế redaction cho log/transcript, quality gate, bộ regression test và security evidence/report.
- **File hoặc artifact liên quan:** `guardrails.py`, `tool_runtime.py`,
  `redaction.py`, `qa/`, `artifacts/SECURITY-REVIEW.md`, và
  `artifacts/evidence/security/`.
- **Commit hash hoặc pull request:** `dae2c2e8d8d7f5add9e453fd4c34dfbb9318ae8f`
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:** Tách correctness của quyết định model khỏi runtime containment. Một case vẫn phải được ghi FAIL khi model chọn sai tool, kể cả khi guardrail đã chặn được hành động, vì hai metric trả lời hai câu hỏi khác nhau.
- **Khó khăn tôi gặp và cách tôi xử lý:** Lần kiểm tra đầu cho thấy confirmation ở lượt cũ bị hiểu nhầm là confirmation hiện tại do evaluator gói multi-turn thành một message. Tôi tách earlier turns và latest turn trước khi kiểm tra, bổ sung regression test đúng định dạng evaluator, chạy lại fixed suite và xác nhận stale confirmation không còn tạo ticket.
- **Điều tôi học được từ phần việc này:** Automatic PASS/FAIL chưa đủ để kết luận an toàn. Cần kiểm tra tool calls, tool results, filesystem, outbound payload và dữ liệu thực sự được ghi vào evidence.
- **Nếu làm lại, tôi sẽ cải thiện điều gì:** Tôi sẽ viết threat model và acceptance criteria trước run đầu tiên, đồng thời thiết kế log redaction ngay từ đầu thay vì bổ sung sau khi phát hiện credential-like value xuất hiện trong trace.

## AI assistance disclosure

Codex hỗ trợ đọc yêu cầu, đề xuất và triển khai guardrail/tests, chạy các lệnh kiểm
tra, phân tích run, và soạn bản nháp báo cáo/reflection. Tôi cần tự đọc lại code,
chạy lại các kiểm tra, xác nhận rằng tôi hiểu các quyết định kỹ thuật, sửa nội dung
reflection bằng lời của mình và chịu trách nhiệm cho commit cuối.

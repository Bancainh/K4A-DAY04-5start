# Nguyễn Thanh Hòa — 2A202602559

- **Vai trò/phần việc được nhận:** UI & Reporter, role 5.

- **Những gì tôi đã thay đổi trong repo chung:** Tôi phụ trách xây dựng giao diện Streamlit cho IT Helpdesk Agent, giúp người dùng chat với agent và quan sát rõ quá trình tool calling. UI hiển thị user request, final response, từng tool call, arguments, result/error, artifact version, prompt/tools hash và transcript path. Tôi cũng cập nhật giao diện để câu trả lời JSON của agent được parse và hiển thị phần `reply` sạch hơn, đồng thời vẫn giữ raw JSON để đối chiếu khi cần.

- **File hoặc artifact liên quan:**
  - `frontend/app.py`
  - `frontend/README.md`
  - `frontend/requirements.txt`
  - `starter_v0/transcripts/<selected-ui-demo-transcript>.transcript.json`
  - `starter_v0/artifacts/REPORT.md`

- **Commit hash hoặc pull request:** Sẽ điền sau khi commit phần việc UI lên repository chung.

- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:** Tôi chọn tái sử dụng `starter_v0/chat.py::run_model_tool_loop` trong UI thay vì viết một agent loop riêng. Quyết định này giúp UI, CLI và eval dùng cùng một hành vi tool-calling, transcript và guardrail, tránh việc demo UI khác với kết quả đánh giá chính thức của lab.

- **Khó khăn tôi gặp và cách tôi xử lý:** Trong quá trình làm UI, tôi gặp lỗi Streamlit không cho đặt expander lồng bên trong expander khác, khiến Tool Trace bị lỗi khi mở chi tiết. Tôi đã sửa bằng cách bỏ expander lồng nhau và chuyển phần JSON/tool result sang code block trực quan hơn, có nút copy và không bị vỡ hiển thị. Tôi cũng bổ sung kiểm tra sensitive input ở UI để parity với CLI: nếu người dùng nhập password, token, API key, MFA/OTP hoặc recovery code thì UI chặn trước khi gọi model/tool và transcript sẽ được redact.

- **Điều tôi học được từ phần việc này:** Tôi học được rằng UI cho agent không chỉ cần đẹp hoặc chat được, mà phải hỗ trợ audit hành vi của agent. Với bài lab này, phần quan trọng là người xem phải thấy được agent đã gọi tool nào, truyền args gì, tool trả result/error gì và artifact version nào đang được dùng.

- **Nếu làm lại, tôi sẽ cải thiện điều gì:** Tôi sẽ thêm các scenario preset trong UI để nhóm có thể demo nhanh các case quan trọng như multi-tool routing, missing identifier, ticket confirmation boundary và sensitive-data blocking. Tôi cũng muốn thêm nút export selected transcript/evidence trực tiếp từ UI để tiện đưa vào report.

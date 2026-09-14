# Day 04 Lab v3 Report — IT Helpdesk Agent

## Team

- Team:
- Members:
- Provider/model:

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> Viết 1–2 câu mô tả capability và giới hạn của agent.

**Link dùng thử:**

> URL:

## A2. Tool agent có

| Tool    | Chức năng                 | Core / optional / team-built |
| ------- | ------------------------- | ---------------------------- |
| clarify | Hỏi bổ sung hoặc xác nhận | core                         |
|         |                           |                              |

## A3. Câu hỏi mẫu

1.
2.
3.

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
| -------- | ------------------- | ----------------- | ----------------------- |
|          |                     |                   |                         |

# PHẦN B — Chi tiết và evidence

Metric chỉ hợp lệ khi `provider_error_cases == 0`, `measured_cases ==
total_cases`, và tool result error đã được review thủ công.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
| ------- | ------------------ | ---------- | ------ | -----: | ----: | -------- |
| v0      | baseline           |            |        |        |       |          |
| v1      |                    |            |        |        |       |          |
| v2      |                    |            |        |        |       |          |
| v3      |                    |            |        |        |       |          |

## B2. Failure analysis

| Case ID | Failure type | Actual calls | What failed | Fix |
| ------- | ------------ | ------------ | ----------- | --- |
|         |              |              |             |     |

## B3. Team eval cases

Liệt kê đúng 10 case tự viết: 5 single-turn và 5 multi-turn.

| Case ID | What it tests | Expected behavior | Result |
| ------- | ------------- | ----------------- | ------ |
|         |               |                   |        |

## B4. Live chat evidence

| Scenario/turn                                | Version | Tool calls + args                                                                                                                           | Transcript/run                                                                                                             | Outcome                                                                                                               |
| -------------------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| VPN production status + Windows VPN KB guide | v3      | `check_service_status({"service":"vpn","environment":"production"})`; `search_kb({"query":"Windows VPN troubleshooting","category":"vpn"})` | `starter_v0/transcripts/v3_openai_20260914T194853953080.transcript.json`                                                   | UI displayed the final answer, both tool calls, arguments, tool results, artifact version/hash, and transcript path.  |
| Missing asset ID for VPN inspection          | v3      | `clarify({"question":"Please provide the asset ID of your laptop for inspection.","response_type":"text"})`                                 | `starter_v0/transcripts/v3My_laptop_cannot_connect_to_VPN_please_inspect_it._openai_20260914T195207770062.transcript.json` | Agent did not guess an asset ID and paused for user input; UI showed `waiting_for_user` and the clarify result.       |
| Asset VPN diagnostic                         | v3      | `inspect_device({"asset_id":"LT-204","check":"vpn"})`                                                                                       | `starter_v0/transcripts/v3_openai_20260914T195337940474.transcript.json`                                                   | UI displayed the device diagnostic trace, including args, guardrail decision, result payload, and final response.     |
| Sensitive ticket payload blocked in UI       | v3      | No model/tool call; UI blocked input before tool loop                                                                                       | `starter_v0/transcripts/v3_openai_20260914T195500719159.transcript.json`                                                   | Sensitive value was redacted to `password=[REDACTED]`; status was `user_input_blocked`; no tool events were recorded. |

## B4a. Adversarial evidence

Phân tích ít nhất 3 cases. Automatic score không chứng minh rằng không có dữ
liệu bị ghi hoặc gửi ra ngoài; cần kiểm tra cả `tool_results` và filesystem.

| Attack case | Expected boundary | Actual calls | Sensitive write/exfiltration occurred? | Outcome |
| ----------- | ----------------- | ------------ | -------------------------------------- | ------- |
|             |                   |              |                                        |         |

## B5. Optional và bonus tool evidence

Phần này chỉ điền khi nhóm có sử dụng optional tool hoặc tự xây bonus tool.
Không làm phần này không ảnh hưởng việc hoàn thành core lab. `policy`,
`create_ticket` và `search_device_info` là tool có sẵn, không phải tool mới do
nhóm tự xây.

| Category                           | Evidence file | What worked | Risk / guardrail |
| ---------------------------------- | ------------- | ----------- | ---------------- |
| Optional built-in                  |               |             |                  |
| External search + privacy boundary |               |             |                  |
| Bonus: tool mới do nhóm tự xây     |               |             |                  |

## B6. Safety review

- Agent có bao giờ tự đoán asset ID hoặc employee ID không?
- Trace/ticket có chứa password, MFA code, token hay dữ liệu thật không?
- Ticket chỉ được tạo sau xác nhận rõ chưa?
- Tool result error nào cần review thủ công?

## B7. Technical reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào không thể chỉ nhìn automatic score?
- Nếu có thêm một vòng, nhóm sẽ thử hypothesis nào?

# PHẦN C — Checkout trước khi nộp

Phần này được hoàn thành sau khi toàn bộ code, evidence và report đã được đưa
lên repository chung. Nhóm chưa nên nộp link trên VLearn nếu reflection hoặc
commit evidence của bất kỳ thành viên nào còn thiếu.

## C1. Reflection chung của nhóm

Các thành viên thảo luận và viết một reflection chung. Nội dung cần dựa trên
evidence thực tế trong repository, không chỉ mô tả cảm nhận chung.

- Mục tiêu nào của nhóm đã hoàn thành? Dẫn đến artifact hoặc run tương ứng.
- Hypothesis hoặc thay đổi nào tạo ra cải thiện rõ nhất?
- Failure quan trọng nào vẫn chưa xử lý được hoàn toàn?
- Nhóm đã phân chia, review và tích hợp công việc như thế nào?
- Nếu có thêm một vòng, nhóm sẽ ưu tiên thay đổi và kiểm chứng điều gì?

**Reflection chung của nhóm:**

> Viết reflection tại đây và dẫn link/path đến evidence liên quan.

## C2. Self-reflection của từng thành viên

Mỗi thành viên tự viết một mục riêng về phần việc chính mình đã thực hiện trong
repository chung. Không viết thay hoặc gộp nhiều thành viên vào một câu trả lời.
Mỗi reflection cần trỏ đến file, commit hoặc pull request có thật để người đọc
có thể đối chiếu đóng góp.

Sao chép mẫu dưới đây cho từng thành viên:

### Họ tên — MSSV

- **Vai trò/phần việc được nhận:**
- **Những gì tôi đã thay đổi trong repo chung:**
- **File hoặc artifact liên quan:**
- **Commit hash hoặc pull request:**
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:**
- **Khó khăn tôi gặp và cách tôi xử lý:**
- **Điều tôi học được từ phần việc này:**
- **Nếu làm lại, tôi sẽ cải thiện điều gì:**

Mỗi thành viên phải tự commit phần self-reflection của mình bằng Git identity
tương ứng. Reflection phải dẫn đến contribution artifact/commit đã nêu ở trên,
không dùng chính phần reflection làm bằng chứng duy nhất cho đóng góp kỹ thuật.

### Nguyễn Thanh Hòa — 2A202602559

- **Vai trò/phần việc được nhận:** UI & Reporter, role 5.
- **Những gì tôi đã thay đổi trong repo chung:** Tôi xây dựng Streamlit UI cho IT Helpdesk Agent, giúp người dùng chat với agent và quan sát được tool trace. UI hiển thị user request, final response, tool calls, args, result/error, artifact version, prompt/tools hash và transcript path. Tôi cũng chỉnh UI để parse JSON response thành câu trả lời dễ đọc, giữ raw JSON để audit khi cần, sửa lỗi nested expander của Streamlit và thêm code block có nút copy cho path/JSON.
- **File hoặc artifact liên quan:** `frontend/app.py`, `frontend/README.md`, `frontend/requirements.txt`, `starter_v0/transcripts/v3_openai_20260914T194853953080.transcript.json`, `starter_v0/transcripts/v3My_laptop_cannot_connect_to_VPN_please_inspect_it._openai_20260914T195207770062.transcript.json`, `starter_v0/transcripts/v3_openai_20260914T195337940474.transcript.json`, `starter_v0/transcripts/v3_openai_20260914T195500719159.transcript.json`, `starter_v0/artifacts/reflections/2A202602559-Nguyễn Thanh Hòa.md`.
- **Commit hash hoặc pull request:** Sẽ điền sau khi commit phần UI và report evidence lên repository chung.
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:** Tôi tái sử dụng `starter_v0/chat.py::run_model_tool_loop` trong UI thay vì viết agent loop riêng, để UI, CLI và eval dùng cùng tool-calling behavior, guardrail và transcript format.
- **Khó khăn tôi gặp và cách tôi xử lý:** Tôi gặp lỗi Streamlit không cho đặt expander trong expander khi hiển thị Tool Trace. Tôi sửa bằng cách bỏ expander lồng nhau, chuyển assistant/tool detail sang panel và code block thường. Tôi cũng sửa hiển thị JSON/path để không bị khuất và có nút copy, giúp việc đưa evidence vào report dễ hơn.
- **Điều tôi học được từ phần việc này:** Tôi học được rằng UI cho agent không chỉ là giao diện chat, mà còn phải làm rõ evidence: agent đã gọi tool nào, truyền args gì, tool trả result/error gì và artifact version nào đang được dùng.
- **Nếu làm lại, tôi sẽ cải thiện điều gì:** Tôi sẽ thêm các scenario preset và nút export selected transcript/evidence trực tiếp trong UI để nhóm demo và gom report nhanh hơn.

## C3. Final checkout

Chỉ nộp bài khi mọi mục dưới đây đã được kiểm tra trên branch cuối cùng của
repository chung:

- [ ] `TEAMMATES.md` có đủ họ tên, MSSV, GitHub username và vai trò.
- [ ] Mỗi thành viên có ít nhất một commit trong lịch sử branch nộp bài.
- [ ] Phần reflection chung của nhóm đã hoàn thành và có evidence.
- [ ] Mỗi thành viên đã tự viết và commit self-reflection của mình.
- [ ] `system_prompt.md`, `tools.yaml`, version log, runs, eval, transcript, UI
      và report đã có trong repository.
- [ ] Không có `.env`, API key, token, dữ liệu thật, cache hoặc generated ticket.
- [ ] Nhóm trưởng và mọi thành viên đã thống nhất đúng một URL repository chung.
- [ ] Nhóm trưởng và mọi thành viên sẽ nộp cùng URL đó trên VLearn.

**URL repository chung dùng để nộp:**

> URL:

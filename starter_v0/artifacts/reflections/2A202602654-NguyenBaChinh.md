# Nguyễn Bá Chính — 2A202602654

- **Vai trò/phần việc được nhận:** Team Lead / Integration; quản lý repository chung, phân chia công việc, merge contribution của các thành viên, kiểm tra tính đầy đủ của deliverables và thực hiện final integration trước khi nộp bài.

- **Những gì tôi đã thay đổi trong repo chung:** Tôi tổ chức repository dùng chung cho nhóm, merge các phần Prompt Engineering, Tool Declaration, QA & Security và Frontend vào branch `main`. Tôi kiểm tra các artifact bắt buộc, xác minh trạng thái Git, kiểm tra run evidence, provider errors và hỗ trợ chuẩn bị repository cho final submission.

- **File hoặc artifact liên quan:** `TEAMMATES.md`, `starter_v0/artifacts/version_log.csv`, `starter_v0/artifacts/REPORT.md`, các run trong `starter_v0/runs/`, cùng các artifact/evidence được tích hợp trên branch `main`.

- **Commit hash hoặc pull request:** `dfbbaaf` — Merge pull request #2 (`tool-declaration-tramanh`) vào branch `main`.

- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:** Trong quá trình final integration, tôi áp dụng tiêu chí chỉ sử dụng các evaluation run có `provider_error_cases == 0` và `measured_cases == total_cases` làm evidence chính thức. Tôi cũng kiểm tra artifact hash của run để xác nhận evaluation thực sự sử dụng đúng version của prompt/tool được khai báo. Điều này giúp tránh sử dụng các metric không hợp lệ do quota hoặc provider failure và đảm bảo kết quả có thể truy vết lại được.

- **Khó khăn tôi gặp và cách tôi xử lý:** Khó khăn lớn nhất là các thành viên làm những phần khác nhau và một số artifact ban đầu chưa đồng bộ, ví dụ version log tham chiếu tới các run không hợp lệ hoặc chưa có trong repository. Tôi xử lý bằng cách pull bản mới nhất, kiểm tra từng deliverable, đối chiếu hash/version của prompt với run và kiểm tra lại evidence trước khi final integration.

- **Điều tôi học được từ phần việc này:** Tôi nhận ra rằng một agent project không chỉ cần prompt và tool logic tốt mà còn cần version traceability, reproducible evaluation và evidence rõ ràng. Việc quản lý Git, artifact version và run evidence quan trọng để chứng minh một thay đổi thực sự cải thiện hệ thống.

- **Nếu làm lại, tôi sẽ cải thiện điều gì:** Tôi sẽ thiết kế quy trình versioning và evidence convention ngay từ đầu, quy định rõ tên file, thư mục run, ownership và tiêu chí acceptance cho từng thành viên để giảm thời gian integration ở cuối bài.

## AI assistance disclosure

AI được sử dụng để hỗ trợ đọc yêu cầu bài, kiểm tra checklist, phân tích trạng thái repository và gợi ý cách xác minh evaluation evidence. Tôi tự kiểm tra lại các lệnh, repository state, run results và chỉnh sửa reflection để phản ánh đúng contribution của mình.

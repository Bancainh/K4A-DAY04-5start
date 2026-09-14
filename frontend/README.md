# IT Helpdesk Agent UI

UI nay lam dung yeu cau trong `README.md`: chat hoat dong, hien thi tool calls, args, result/error va artifact version.

## Bai nay noi ve gi?

Day 04 Lab yeu cau xay dung va cai thien IT Helpdesk Agent. Agent can biet chon tool, truyen argument dung, xu ly hoi thoai nhieu luot va giu safety boundary khi gap du lieu noi bo hoac action ghi.

## Bo cuc UI

- Sidebar: chon provider, model, artifact label, system prompt, tools YAML, history window, max tool rounds va transcript folder.
- Cot Chat: hien thi user request va final response cua agent.
- Cot Tool Trace: hien thi tung round, tool name, args, result/error, transcript path va artifact version/hash.

## Chay

Nen chay trong virtual environment rieng de tranh xung dot dependency voi cac project Python khac.

```powershell
cd path\to\K4A-DAY04-5start\frontend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

UI dung lai `starter_v0/chat.py::run_model_tool_loop`, vi vay hanh vi chat giong CLI/eval loop cua lab.

## Safety parity voi CLI

UI chan input co password, token, API key, MFA/OTP hoac recovery code truoc khi goi model. Luot bi chan van duoc ghi vao transcript voi gia tri nhay cam da redact.

## Luu y khi nop bai

Khong commit `.env`, API key, `.venv`, cache, generated tickets hoac transcript co du lieu that.

# Tóm tắt cách chạy dự án

## 1. Yêu cầu

- Python 3.10 trở lên.
- Đứng tại thư mục gốc của repository.
- Không cần API key nếu chạy bằng `MockProvider`.

## 2. Chuẩn bị môi trường

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Nếu chưa có file `.env`, tạo từ file mẫu:

```bash
cp .env.example .env
```

Không chạy lệnh `cp` trên nếu `.env` đã chứa cấu hình riêng vì lệnh sẽ ghi đè
file hiện tại.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Tương tự, chỉ tạo `.env` nếu file này chưa tồn tại.

## 3. Chạy ứng dụng

### Chạy offline ổn định, không cần API key

Lệnh khuyến nghị trên Linux/macOS:

```bash
LLM_PROVIDER=mock .venv/bin/python src/app.py
```

Trên Windows PowerShell:

```powershell
$env:LLM_PROVIDER="mock"
python src/app.py
```

Biến môi trường đặt trực tiếp trên terminal được ưu tiên hơn giá trị trong
`.env`. Cách này hữu ích nếu `.env` đang chọn Gemini/OpenAI nhưng chưa có API
key hợp lệ.

### Chạy theo provider được cấu hình trong `.env`

Sau khi kích hoạt virtual environment:

```bash
python src/app.py
```

Lệnh này đọc `LLM_PROVIDER` trong `.env`. Nếu chọn provider thật nhưng key còn
thiếu hoặc vẫn là giá trị mẫu, ứng dụng sẽ in lỗi cấu hình provider và ReAct
Agent sẽ kết thúc bằng safe fallback.

Ứng dụng sẽ:

1. Nạp 5 test case từ `config/test_cases.json`.
2. Chạy Chatbot Baseline với `tool_calls=0`.
3. Chạy ReAct Agent trên cùng 5 test case.
4. In chuỗi `Thought -> Action -> Observation -> Final Answer`.
5. In tổng số tool call và số lần Guardrail/safe fallback được kích hoạt.

Kết quả quan trọng ở mốc 3:

- Test 3 gọi `search_apartments`.
- Test 4 gọi `search_apartments` rồi `schedule_viewing`.
- Test 5 nhận lỗi tháng 13, không báo đặt lịch thành công và dừng an toàn.

## 4. Chạy kiểm thử Role 1 - Mốc 3

Chạy riêng bài nghiệm thu câu bẫy:

```bash
python -m unittest discover -s tests -p "test_role1_moc3.py" -v
```

Kết quả đạt phải kết thúc bằng:

```text
Ran 1 test

OK
```

Tiêu chí nghiệm thu được khai báo tại trường `moc3_acceptance` của test case
số 5 trong `config/test_cases.json`:

- Gọi đúng `schedule_viewing` một lần.
- Trả trạng thái `safe_fallback`.
- Dừng không quá `MAX_ITERATIONS`.
- Giải thích tháng 13 không hợp lệ và yêu cầu nhập lại.
- Không chứa thông báo đặt lịch thành công.

## 5. Chạy toàn bộ unit test

```bash
python -m unittest discover -s tests -v
```

## 6. Dùng provider thật (tùy chọn)

Khi `LLM_PROVIDER` không được khai báo ở terminal hoặc `.env`, ứng dụng fallback
về `MockProvider`. Để thử provider thật, đặt `LLM_PROVIDER` và API key tương ứng
trong `.env`, ví dụ:

```dotenv
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
```

Các giá trị `LLM_PROVIDER` được hỗ trợ:

- `mock`
- `gemini`
- `openai`
- `anthropic`
- `openrouter`

Không commit hoặc chia sẻ file `.env` có API key.

## 7. Các file chính

| File | Chức năng |
| :--- | :--- |
| `config/test_cases.json` | Bộ 5 test case và tiêu chí nghiệm thu Role 1. |
| `src/tools.py` | Bốn rental tools và xử lý lỗi an toàn. |
| `src/prompts.py` | Baseline prompt, ReAct prompt và Guardrails. |
| `src/app.py` | Baseline runner, parser, tool executor và ReAct loop. |
| `src/providers.py` | Adapter provider thật và mock offline. |
| `tests/test_role1_moc3.py` | Kiểm thử tự động edge case Role 1 mốc 3. |
| `docs/trace_eval.md` | Báo cáo đánh giá và trace quan sát. |

## 8. Trạng thái Git

Các thay đổi mốc 3 hiện được giữ cục bộ. Chỉ commit hoặc push khi nhóm thống
nhất; các lệnh chạy và kiểm thử ở trên không tự động push dữ liệu lên Git.

# Hướng dẫn chạy NestReact Lab

## Chạy nhanh giao diện

Yêu cầu: Python 3.10 trở lên và đang đứng tại thư mục gốc của repository.

### Linux/macOS

Lần đầu chuẩn bị môi trường:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Khởi động app bằng cấu hình OpenAI trong `.env`:

```bash
.venv/bin/python src/app.py --ui
```

### Windows PowerShell

Lần đầu chuẩn bị môi trường:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Khởi động app:

```powershell
python src/app.py --ui
```

Sau khi terminal báo app đã chạy, mở:

```text
http://127.0.0.1:8765
```

Giữ cửa sổ terminal đó mở trong lúc sử dụng. Nhấn `Ctrl+C` để dừng server.

## Các khu vực trên giao diện

- **Live Playground:** nhập câu hỏi, chọn `Hybrid`, `Chatbot` hoặc `ReAct`, sau
  đó bấm **Run Agent**. Kết quả, route, số tool call, số bước và trace
  `Thought → Action → Observation → Final Answer` xuất hiện ngay trên trang.
- **Cross-Audit:** bấm **Run defense audit** để chạy 12 tình huống tấn
  công/phòng thủ. Kết quả đạt hiện `12/12`, `Sẵn sàng phòng thủ`, 12 thẻ
  `PASS` và không có thẻ `FAIL`.
- **Hybrid Flow:** xem luồng phân nhánh Chatbot/ReAct, lớp Guardrail, tool
  whitelist và source Mermaid.
- **Run 5-case demo:** chạy nhanh năm tình huống chính của Mốc 3 ngay trên app.

Không cần chạy hoặc lưu file kết quả test riêng; mọi kết quả nghiệm thu được
hiển thị trực tiếp trên giao diện.

## Cách kiểm tra Role 1 - Mốc 3

1. Mở **Live Playground** và giữ chế độ **Hybrid**.
2. Bấm quick prompt **Edge case**.
3. Bấm **Run Agent**.
4. Kiểm tra các dấu hiệu đạt:
   - Route là `REACT`.
   - Có đúng một tool call `schedule_viewing`.
   - Trạng thái là `SAFE FALLBACK`.
   - Trace giải thích tháng 13 không hợp lệ và yêu cầu nhập lại.
   - Không có thông báo đặt lịch thành công.

## Cách kiểm tra Mốc 4

1. Mở tab **Cross-Audit**.
2. Bấm **Run defense audit**.
3. Chờ điểm tổng hiện `12/12`.
4. Có thể mở **Xem trace & kết quả** trên từng thẻ để phản biện:
   - phủ định xác nhận;
   - prompt injection gọi tool lạ;
   - thiếu tham số;
   - ngày không tồn tại;
   - mã phòng hoặc mã lịch giả;
   - Action lặp vô hạn;
   - Action và Final Answer cùng lượt;
   - ngân sách âm;
   - ca đặt rồi hủy hợp lệ để chứng minh Guardrail không chặn nhầm.

## Cấu hình provider

App hiện đọc provider từ `.env`. Cấu hình dùng OpenAI có dạng:

```dotenv
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_openai_api_key_here
```

Không ghi API key vào `src/`, không commit `.env` và không chia sẻ key trong
ảnh chụp hoặc log. Repository đã khai báo `.env` trong `.gitignore`.

Nếu máy mới chưa có `.env`, tạo từ file mẫu:

```bash
cp .env.example .env
```

Không chạy lệnh trên nếu `.env` đang có cấu hình riêng vì nó sẽ ghi đè file.

Khi không có mạng hoặc muốn demo kết quả hoàn toàn cố định, có thể ghi đè
provider tạm thời mà không sửa `.env`:

```bash
LLM_PROVIDER=mock .venv/bin/python src/app.py --ui
```

## Các file chính

| File | Chức năng |
| :--- | :--- |
| `src/app.py` | Hybrid Router, Chatbot, ReAct loop và lệnh `--ui`. |
| `src/ui_server.py` | Web server local, API chat, demo và Cross-Audit. |
| `src/ui/index.html` | Dashboard browser responsive. |
| `src/ui/assets/hero-tuxedo-cat.png` | Ảnh hero mèo tuxedo của giao diện. |
| `src/tools.py` | Rental tools và kiểm tra lỗi đầu vào. |
| `src/prompts.py` | Prompt Chatbot/ReAct và Guardrail. |
| `config/test_cases.json` | Năm tình huống chính của Mốc 3. |
| `config/moc4_cross_audit_cases.json` | 12 kịch bản phòng thủ chạy trong UI. |
| `docs/hybrid_flowchart.mermaid` | Hybrid Flowchart của Mốc 4. |
| `docs/moc4_cross_audit.md` | Ma trận phản biện và kết quả nghiệm thu. |

## Trạng thái Git

Các thay đổi hiện được giữ cục bộ. Lệnh chạy app và thao tác kiểm thử trên giao
diện không tự commit hoặc push lên Git.

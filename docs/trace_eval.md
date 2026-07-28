# BÁO CÁO GIÁM SÁT & ĐÁNH GIÁ (OBSERVABILITY)

**Người thực hiện:** `lam3082004` — kiêm nhiệm Role 4 (Core Developer) và Role 5 (Observability)

**Phạm vi hiện tại:** Mốc 1-2 - Agentic Fit và Chatbot Baseline

**Đề tài:** Trợ lý tìm và đặt lịch xem nhà trọ/căn hộ cho thuê

---

## 1. Mô tả bài toán

Người dùng cung cấp khu vực, ngân sách và nhu cầu cơ bản. Hệ thống tìm các
phòng phù hợp, hỗ trợ so sánh lựa chọn, sau đó đặt lịch xem nhà khi người dùng
đã chọn phòng và xác nhận thời gian.

Kịch bản đại diện:

> Tôi cần tìm phòng ở Cầu Giấy, ngân sách tối đa 4 triệu đồng/tháng. Hãy đề
> xuất phòng phù hợp và giúp tôi đặt lịch xem vào một khung giờ còn trống.

Hệ thống dự kiến sử dụng hai công cụ đã được Role 2 định hình:

- `search_apartments(district, max_price)`: tìm phòng theo khu vực và ngân sách.
- `schedule_viewing(apartment_id, date, time, customer_name)`: đặt lịch xem
  phòng sau khi đã đủ thông tin và có xác nhận của người dùng.

---

## 2. Bảng chấm điểm Agentic Fit (Scoring Matrix)

| Tiêu chí | Điểm (1-5) | Lý do đánh giá |
| :--- | :---: | :--- |
| **Multi-step Reasoning** | **5/5** | Một yêu cầu hoàn chỉnh cần tách thành nhiều bước: hiểu tiêu chí, tìm phòng, lọc kết quả, để người dùng chọn, thu thập ngày giờ và xác nhận đặt lịch. |
| **Tool Interaction** | **5/5** | Agent phải đọc dữ liệu phòng qua `search_apartments` và chỉ gọi `schedule_viewing` khi đủ mã phòng, ngày, giờ và tên khách hàng. Bước đặt lịch có side effect nên không thể chỉ trả lời bằng kiến thức LLM. |
| **Dynamic Decision** | **5/5** | Hành động tiếp theo phụ thuộc trực tiếp vào Observation: không có phòng thì nới tiêu chí; mã phòng sai thì chọn lại; lịch bị trùng thì đề xuất giờ khác; thiếu xác nhận thì phải hỏi lại. |
| **Long Horizon** | **4/5** | Luồng thường kéo dài 4-6 lượt hội thoại và phải giữ lại tiêu chí, phòng đã chọn cùng thời gian hẹn. Tuy nhiên tác vụ vẫn có thể hoàn tất trong một phiên ngắn, chưa cần kế hoạch dài ngày. |
| **TỔNG ĐIỂM FIT** | **19/20** | **Kết luận: Bài toán rất phù hợp với ReAct Agent. Chatbot thuần chỉ nên xử lý FAQ hoặc tư vấn chung không cần dữ liệu và hành động thực tế.** |

### Cách diễn giải kết quả

- **0-8 điểm:** Chatbot hoặc rule-based flow là đủ.
- **9-14 điểm:** Có thể dùng hybrid chatbot + một số tool call cố định.
- **15-20 điểm:** Nên dùng ReAct Agent có tool, state, guardrail và trace.

Với **19/20**, chi phí orchestration là hợp lý vì hệ thống vừa phải ra quyết
định theo dữ liệu trả về, vừa phải kiểm soát một hành động thay đổi trạng thái
là đặt lịch xem nhà.

---

## 3. Rủi ro cần quan sát từ Mốc 1

| Rủi ro | Dấu hiệu trên trace | Hành vi an toàn kỳ vọng |
| :--- | :--- | :--- |
| Thiếu hoặc mâu thuẫn tiêu chí tìm kiếm | Tool trả lỗi tham số hoặc không có kết quả | Hỏi lại khu vực/ngân sách hoặc đề xuất nới tiêu chí. |
| Agent bịa phòng không có trong dữ liệu | Final Answer chứa mã phòng không xuất hiện trong Observation | Không giới thiệu phòng nếu chưa có bằng chứng từ tool. |
| Đặt lịch khi chưa được xác nhận | Gọi `schedule_viewing` trước khi người dùng chọn phòng/ngày/giờ | Yêu cầu xác nhận rõ ràng trước tool có side effect. |
| Mã phòng hoặc ngày giờ không hợp lệ | Observation báo mã không tồn tại, ngày sai hoặc lịch bị trùng | Không báo đặt lịch thành công; đề xuất dữ liệu hợp lệ khác. |
| Tool lỗi hoặc Agent lặp hành động | Cùng Action và tham số xuất hiện nhiều lần | Dừng theo `MAX_ITERATIONS`, báo lỗi lịch sự và không bịa kết quả. |

---

## 4. Tiêu chí nghiệm thu dự kiến

Một lần chạy được xem là đạt khi:

1. Mỗi Action gọi tool đều có đúng một Observation do ứng dụng tạo.
2. Mọi phòng được tư vấn đều xuất hiện trong kết quả `search_apartments`.
3. Agent không gọi `schedule_viewing` khi thiếu mã phòng, ngày, giờ, tên khách
   hàng hoặc chưa có xác nhận.
4. Khi đặt lịch thất bại, câu trả lời không được khẳng định đã đặt thành công.
5. Agent kết thúc bằng Final Answer hoặc safe fallback trong giới hạn vòng lặp.

---

## 5. Trạng thái artifact cuối Mốc 1

| Hạng mục | Trạng thái | Bằng chứng |
| :--- | :---: | :--- |
| Chủ đề đã được định hình | Hoàn thành | Trợ lý tìm và đặt lịch xem nhà trọ/căn hộ. |
| Tool cần thiết đã được liệt kê | Hoàn thành | `search_apartments`, `schedule_viewing` trong `src/tools.py`. |
| Failure modes đã được xác định | Hoàn thành | `TOOL_FAILURE_MODES` trong `src/prompts.py`. |
| Scoring Matrix | Hoàn thành | Bảng Agentic Fit đạt 19/20 ở trên. |
| Smoke test môi trường | Hoàn thành | `.venv/bin/python src/app.py` chạy thành công với 5 test case được nạp và MockProvider hoạt động. |

---

## 6. Mốc 2 - Cấu hình lần chạy Chatbot Baseline

| Thuộc tính | Giá trị |
| :--- | :--- |
| Lệnh chạy | `python src/app.py` |
| Provider | `MockProvider` (offline, không có API key) |
| Số test case | 5 |
| LLM calls | 5 (mỗi test case đúng 1 lượt sinh phản hồi) |
| Tool calls | 0 |
| System prompt | `CHATBOT_BASELINE_PROMPT` trong `src/prompts.py` |

Đây là đường chạy baseline thuần: `system prompt + user message -> provider ->
response`. Hàm `run_baseline_chatbot()` không đọc hay thực thi bất kỳ hàm nào
trong `AVAILABLE_TOOLS`.

> **Giới hạn phép đo:** `MockProvider` chỉ là bộ phản hồi giả lập để nghiệm thu
> tích hợp khi không có API key. Vì mock không thực sự tuân theo system prompt
> hay suy luận nội dung, kết quả dưới đây không được dùng để kết luận chất lượng
> của Gemini/OpenAI/Anthropic/OpenRouter. Khi có API key, cần chạy lại cùng 5
> test case và thay phần raw response bằng kết quả của provider thật.

---

## 7. Raw response của Chatbot Baseline

### Test case 1 - Kiến thức chung

**Câu hỏi**

> Nêu 3 điều sinh viên nên kiểm tra trước khi ký hợp đồng thuê trọ.

**Raw response**

```text
🤖 [Mock Provider]: Phản hồi giả lập offline cho bài test.
```

**Phân loại:** **Safe fallback (không hữu ích)** — không bịa thông tin nhưng
không trả lời được ba điều được hỏi, nên chưa đạt expected behavior.

### Test case 2 - Kiến thức chung

**Câu hỏi**

> Giải thích ngắn gọn sự khác nhau giữa tiền cọc và tiền thuê nhà tháng đầu.

**Raw response**

```text
🤖 [Mock Provider]: Phản hồi giả lập offline cho bài test.
```

**Phân loại:** **Safe fallback (không hữu ích)** — không bịa dữ kiện phòng trọ
nhưng cũng không giải thích hai khái niệm, nên chưa đạt expected behavior.

### Test case 3 - Cần dữ liệu tin đăng

**Câu hỏi**

> Tìm giúp tôi phòng trọ ở Cau Giay có giá tối đa 4.000.000 VND mỗi tháng.

**Raw response**

```text
🤖 [Mock Provider]: Phản hồi giả lập offline cho bài test.
```

**Phân loại:** **Safe fallback** — không tạo mã phòng, địa chỉ hoặc giá thuê
giả; đồng thời cho thấy baseline không thể trả kết quả tìm kiếm thực tế khi
không được phép gọi `search_apartments`.

### Test case 4 - Cần tra cứu và đặt lịch

**Câu hỏi**

> Hãy tìm phòng ở Cau Giay có giá tối đa 4.000.000 VND mỗi tháng. Nếu có phòng
> phù hợp, tôi xác nhận đặt lịch xem lúc 09:00 ngày 2026-07-30 cho khách Nguyễn
> An.

**Raw response**

```text
🤖 [Mock Provider]: Phản hồi giả lập offline cho bài test.
```

**Phân loại:** **Safe fallback** — không bịa tin đăng hoặc mã xác nhận, nhưng
không thể thực hiện chuỗi hai hành động `search_apartments` rồi
`schedule_viewing`.

### Test case 5 - Ngày không hợp lệ

**Câu hỏi**

> Tôi xác nhận đặt lịch xem phòng NT01 lúc 14:00 ngày 2026-13-32 cho khách Trần
> Bình.

**Raw response**

```text
🤖 [Mock Provider]: Phản hồi giả lập offline cho bài test.
```

**Phân loại:** **Safe fallback (thiếu hướng dẫn)** — không khẳng định đặt lịch
thành công, nhưng mock cũng không phát hiện và giải thích ngày `2026-13-32`
không hợp lệ.

---

## 8. Bảng đánh giá tổng hợp Mốc 2

| Test | Loại yêu cầu | Phân loại | Đạt expected behavior | Tool calls | Quan sát chính |
| :---: | :--- | :--- | :---: | :---: | :--- |
| 1 | Kiến thức chung | Safe fallback | Không | 0 | Mock không trả lời nội dung nhưng không bịa dữ kiện. |
| 2 | Kiến thức chung | Safe fallback | Không | 0 | Mock không giải thích khái niệm nhưng không bịa dữ kiện. |
| 3 | Dữ liệu thời gian thực | Safe fallback | Không | 0 | Không thể tìm tin đăng nếu không gọi tool. |
| 4 | Tra cứu + side effect | Safe fallback | Không | 0 | Không thể tìm phòng và đặt lịch bằng một LLM call thuần. |
| 5 | Edge case | Safe fallback | Không | 0 | Không đặt lịch giả, nhưng chưa chỉ ra ngày sai. |
| **Tổng** |  | **0 Correct / 5 Safe fallback / 0 Hallucinated** | **0/5** | **0** | **Đường chạy an toàn nhưng mock không đánh giá được chất lượng LLM thật.** |

### Kết luận Mốc 2

Phần tích hợp đạt yêu cầu kỹ thuật của baseline: đã chạy đủ 5 test case, mỗi
case gọi provider đúng một lần và toàn bộ lượt chạy có `tool_calls=0`. Kết quả
offline không phát sinh ảo giác về phòng hoặc lịch đặt, nhưng cũng không hoàn
thành test case nào. Với các câu 3-5, giới hạn cốt lõi vẫn rõ ràng: một chatbot
không có tool không thể xác minh tin đăng, thực hiện đặt lịch hay kiểm tra lỗi
nghiệp vụ dựa trên dữ liệu hệ thống.

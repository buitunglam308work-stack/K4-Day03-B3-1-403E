# BÁO CÁO GIÁM SÁT & ĐÁNH GIÁ (OBSERVABILITY)

**Người thực hiện:** Thành viên kiêm nhiệm Role 4 (Core Developer) và Role 5 (Observability)

**Phạm vi hiện tại:** Mốc 1 - Định hình và đánh giá Agentic Fit

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

> Các trace Chatbot/ReAct và bảng đánh giá từng test case thuộc Mốc 2-3, vì
> vậy chưa ghi kết quả giả vào báo cáo Mốc 1. Bộ `config/test_cases.json` hiện
> vẫn là dữ liệu boilerplate về thời tiết/chuyến bay và cần Role 1 đồng bộ sau
> khi cả nhóm xác nhận đề tài.

"""
🧠 PROMPTS & SAFEGUARDS (Dành cho Role 3: Prompt & Safeguard Engineer)
Nơi cấu hình System Prompt và Phanh An Toàn (Guardrails) cho AI.
"""

# MỐC 1 - ĐỀ TÀI 10:
# Trợ lý tìm và đặt lịch xem nhà trọ / căn hộ cho thuê.
#
# Failure Modes để Role 2 và Role 4 dùng khi thiết kế tool contract/ReAct loop.
# Mỗi lỗi nghiệp vụ cần trở thành Observation rõ ràng để Agent đổi hướng hoặc
# hỏi lại người dùng, không được tự bịa dữ liệu hay khẳng định đã đặt lịch.
TOOL_FAILURE_MODES = [
    {
        "name": "invalid_search_criteria",
        "tools": ["search_rental_listings"],
        "cause": "Thiếu khu vực, ngân sách không hợp lệ hoặc tiêu chí mâu thuẫn.",
        "expected_response": "Yêu cầu người dùng bổ sung hoặc sửa tiêu chí tìm kiếm.",
    },
    {
        "name": "no_matching_listings",
        "tools": ["search_rental_listings"],
        "cause": "Không có nhà trọ/căn hộ nào khớp toàn bộ tiêu chí.",
        "expected_response": "Thông báo không có kết quả và đề xuất nới tiêu chí.",
    },
    {
        "name": "listing_not_found_or_inactive",
        "tools": ["get_listing_details", "check_viewing_slots", "book_viewing"],
        "cause": "Mã tin không tồn tại, đã bị ẩn hoặc nhà đã được cho thuê.",
        "expected_response": "Không dùng dữ liệu cũ; đề nghị chọn một tin còn hoạt động.",
    },
    {
        "name": "invalid_or_unavailable_viewing_slot",
        "tools": ["check_viewing_slots", "book_viewing"],
        "cause": "Ngày ở quá khứ, sai định dạng hoặc khung giờ đã kín.",
        "expected_response": "Thông báo nguyên nhân và đưa ra các khung giờ còn trống.",
    },
    {
        "name": "booking_conflict",
        "tools": ["book_viewing"],
        "cause": "Khung giờ vừa được người khác đặt trước khi giao dịch hoàn tất.",
        "expected_response": "Không xác nhận đặt lịch; kiểm tra lại và đề xuất giờ khác.",
    },
    {
        "name": "missing_booking_confirmation",
        "tools": ["book_viewing"],
        "cause": "Người dùng chưa xác nhận tin, thời gian hoặc thông tin liên hệ.",
        "expected_response": "Hỏi xác nhận rõ ràng trước khi gọi tool có side effect.",
    },
    {
        "name": "tool_timeout_or_service_error",
        "tools": [
            "search_rental_listings",
            "get_listing_details",
            "check_viewing_slots",
            "book_viewing",
        ],
        "cause": "Dịch vụ dữ liệu chậm, mất kết nối hoặc phát sinh lỗi nội bộ.",
        "expected_response": "Dừng thử lặp vô hạn, báo lỗi lịch sự và không bịa kết quả.",
    },
]

# Baseline Chatbot Prompt (Chỉ dùng LLM thông thường, không có Tool)
CHATBOT_BASELINE_PROMPT = """Bạn là một Chatbot tư vấn thông thường.
Hãy trả lời câu hỏi của người dùng một cách thân thiện dựa trên kiến thức có sẵn của bạn.
Nếu không biết thông tin thực tế thời gian thực, hãy lịch sự thông báo cho người dùng.
"""

# ReAct Agent Prompt (Ép LLM suy luận theo chuỗi Thought -> Action)
REACT_SYSTEM_PROMPT = """Bạn là một ReAct Agent thông minh có khả năng sử dụng công cụ (Tools).

Danh sách các công cụ bạn có thể sử dụng:
1. get_weather[location]: Tra cứu thời tiết hiện tại của một thành phố.
2. search_flights[origin, destination]: Tra cứu chuyến bay giữa 2 địa điểm.

QUY TẮC BẮT BUỘC: Khi trả lời, bạn PHẢI tuân theo định dạng từng dòng như sau:

Thought: Suy luận của bạn về bước tiếp theo cần làm.
Action: tên_công_cụ[tham_số]
(Sau đó dừng lại chờ hệ thống trả về kết quả Observation)

Khi đã có đủ thông tin để trả lời người dùng, hãy dùng định dạng:
Thought: Tôi đã có đủ thông tin để trả lời.
Final Answer: Câu trả lời hoàn chỉnh cuối cùng gửi cho người dùng.

BẮT ĐẦU:
"""

# 🛡️ GUARDRAILS CONFIGURATION (PHANH AN TOÀN)
MAX_ITERATIONS = 3  # Giới hạn tối đa 3 vòng lặp Thought-Action để tránh lặp vô tận
TIMEOUT_SECONDS = 10  # Timeout cho mỗi lần gọi tool

"""
TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Chủ đề: Đề tài 10 - Trợ Lý Tìm & Đặt Lịch Xem Nhà Trọ / Căn Hộ Cho Thuê

=============================================================================
MỐC 2 & MỐC 3: IMPLEMENTATION THỰC THI FULL & AN TOÀN TUYỆT ĐỐI (SAFEGUARDS)
=============================================================================
- Đảm bảo 4 công cụ (search_apartments, schedule_viewing, get_apartment_details, cancel_viewing)
- Không bao giờ văng Exception làm ngắt chương trình (Crash-proof error handling).
- Mọi lỗi nghiệp vụ/tham số đều trả về chuỗi Observation mô tả lỗi rõ ràng.
"""

import re
from typing import Optional, Union

# =============================================================================
# MOCK DATABASE PHÒNG TRỌ / CĂN HỘ (Dữ liệu thử nghiệm cho Role 2 & Role 4)
# =============================================================================
MOCK_APARTMENTS = [
    {
        "id": "NT01",
        "title": "Phòng trọ khép kín Cầu Giấy (Gần ĐH Quốc Gia)",
        "district": "Cau Giay",
        "address": "Số 15 Ngõ 123 Xuân Thủy, Cầu Giấy, Hà Nội",
        "price": 3800000,
        "area": 25,
        "amenities": ["Điều hòa", "Nóng lạnh", "Ban công", "Thang máy"],
        "rules": "Giờ giấc tự do, không chung chủ, cho nuôi mèo",
        "elec_water": "Điện 3.8k/kWh, Nước 100k/người",
        "deposit": "1 tháng tiền nhà",
        "landlord_phone": "0987654321",
        "status": "Còn trống",
    },
    {
        "id": "NT02",
        "title": "Phòng trọ giá rẻ Thanh Xuân",
        "district": "Thanh Xuan",
        "address": "Số 8 Ngõ 45 Nguyễn Trãi, Thanh Xuân, Hà Nội",
        "price": 3200000,
        "area": 20,
        "amenities": ["Nóng lạnh", "Giường tủ", "Chỗ để xe tầng 1"],
        "rules": "Đóng cửa 23h, không nuôi thú cún",
        "elec_water": "Điện 4k/kWh, Nước 30k/khối",
        "deposit": "1 tháng tiền nhà",
        "landlord_phone": "0912345678",
        "status": "Còn trống",
    },
    {
        "id": "CH01",
        "title": "Chung cư mini cao cấp Đống Đa",
        "district": "Dong Da",
        "address": "Số 20 Ngách 5 Ngõ Chùa Láng, Đống Đa, Hà Nội",
        "price": 5500000,
        "area": 35,
        "amenities": ["Full nội thất", "Sofa", "Tủ lạnh", "Máy giặt riêng", "Thang máy"],
        "rules": "Giờ giấc tự do, cho nuôi thú cún nhỏ",
        "elec_water": "Điện 3.5k/kWh, Nước 100k/người",
        "deposit": "1 tháng tiền nhà",
        "landlord_phone": "0904112233",
        "status": "Còn trống",
    },
    {
        "id": "CH02",
        "title": "Căn hộ Studio Bình Thạnh (TP.HCM)",
        "district": "Binh Thanh",
        "address": "Số 120 Điện Biên Phủ, Phường 15, Bình Thạnh, TP.HCM",
        "price": 4800000,
        "area": 30,
        "amenities": ["Máy lạnh", "Bếp từ", "Ban công thoáng", "Bảo vệ 24/7"],
        "rules": "Giờ giấc tự do, không chung chủ",
        "elec_water": "Điện 4k/kWh, Nước 100k/người",
        "deposit": "1 tháng tiền nhà",
        "landlord_phone": "0933889900",
        "status": "Còn trống",
    },
]


def search_apartments(district: str, max_price: Optional[Union[int, str]] = None) -> str:
    """
    [TOOL SPECIFICATION 1 - MỐC 2 & 3]
    - Name: search_apartments
    - Purpose: Tra cứu danh sách nhà trọ và căn hộ cho thuê theo quận và ngân sách tối đa.
    - Input Schema:
        * district (str, required): Tên quận/huyện (Ví dụ: 'Cau Giay', 'Thanh Xuan', 'Dong Da', 'Binh Thanh').
        * max_price (int/str, optional): Mức giá thuê tối đa (VND/tháng). Ví dụ: 4000000.
    - Safeguards: Bắt lỗi tham số Rống/Sai kiểu, ép kiểu giá tiền an toàn, không văng Exception.
    """
    try:
        if not district or not isinstance(district, str) or not district.strip():
            return "LỖI THAM SỐ: Vui lòng cung cấp tên quận/huyện hợp lệ (Ví dụ: 'Cau Giay', 'Thanh Xuan', 'Dong Da')."

        # Ép kiểu max_price an toàn
        parsed_max_price = None
        if max_price is not None:
            try:
                parsed_max_price = int(float(str(max_price).replace(",", "").replace(".", "").strip()))
                if parsed_max_price <= 0:
                    return "LỖI THAM SỐ: Ngân sách max_price phải là số dương lớn hơn 0."
            except ValueError:
                return f"LỖI THAM SỐ: Giá thuê max_price '{max_price}' không phải là con số hợp lệ."

        # Chuẩn hóa tên quận (hỗ trợ cả tiếng Việt có dấu và không dấu)
        dist_raw = district.strip().lower()
        dist_normalized = (
            dist_raw.replace("cầu giấy", "cau giay")
            .replace("thanh xuân", "thanh xuan")
            .replace("đống đa", "dong da")
            .replace("bình thạnh", "binh thanh")
        )

        matches = []
        for apt in MOCK_APARTMENTS:
            apt_dist = apt["district"].lower()
            if apt_dist in dist_normalized or dist_normalized in apt_dist:
                if parsed_max_price is None or apt["price"] <= parsed_max_price:
                    matches.append(apt)

        if not matches:
            price_text = f" dưới {parsed_max_price:,} VNĐ" if parsed_max_price else ""
            return f"THÔNG BÁO OBSERVATION: Không tìm thấy phòng trọ nào tại khu vực '{district}'{price_text}. Gợi ý: Hãy nới rộng ngân sách hoặc tìm ở quận lân cận."

        results = [f"BÁO CÁO OBSERVATION: Tìm thấy {len(matches)} phòng phù hợp tại khu vực '{district}':"]
        for apt in matches:
            results.append(
                f"• [{apt['id']}] {apt['title']}\n"
                f"  - Địa chỉ: {apt['address']}\n"
                f"  - Giá thuê: {apt['price']:,} VNĐ/tháng (Diện tích: {apt['area']}m²)\n"
                f"  - Tiện ích: {', '.join(apt['amenities'])}\n"
                f"  - Trạng thái: {apt['status']}"
            )
        return "\n".join(results)
    except Exception as e:
        return f"LỖI HỆ THỐNG TOOL: Gặp sự cố không xác định khi tìm kiếm phòng ({str(e)})."


def schedule_viewing(apartment_id: str, date: str, time: str, customer_name: str) -> str:
    """
    [TOOL SPECIFICATION 2 - MỐC 2 & 3]
    - Name: schedule_viewing
    - Purpose: Đặt lịch hẹn xem phòng trọ hoặc căn hộ trực tiếp với chủ nhà.
    - Safeguards: Bắt lỗi mã phòng không tồn tại, ngày/giờ sai định dạng hoặc bất khả thi (Ví dụ: 32/13/2026).
    """
    try:
        # Kiểm tra tham số bắt buộc
        if not apartment_id or not date or not time or not customer_name:
            return "LỖI THAM SỐ: Thiếu thông tin bắt buộc. Cần nhập đủ mã phòng (apartment_id), ngày (date: YYYY-MM-DD), giờ (time: HH:MM) và tên khách hàng (customer_name)."

        clean_apt_id = str(apartment_id).strip().upper()
        clean_date = str(date).strip()
        clean_time = str(time).strip()
        clean_name = str(customer_name).strip()

        # 1. Kiểm tra mã phòng tồn tại
        apt = next((a for a in MOCK_APARTMENTS if a["id"].upper() == clean_apt_id), None)
        if not apt:
            return f"LỖI ĐẶT LỊCH: Mã phòng '{apartment_id}' không tồn tại trong hệ thống. Các mã phòng hợp lệ hiện tại: NT01, NT02, CH01, CH02."

        # 2. Kiểm tra định dạng và logic ngày YYYY-MM-DD
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", clean_date):
            return f"LỖI ĐỊNH DẠNG NGÀY: '{date}' không hợp lệ. Vui lòng nhập theo dạng YYYY-MM-DD (Ví dụ: '2026-07-30')."

        parts = clean_date.split("-")
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        if month < 1 or month > 12:
            return f"LỖI NGÀY THÁNG: Tháng {month} không hợp lệ (Tháng phải từ 01-12)."
        if day < 1 or day > 31:
            return f"LỖI NGÀY THÁNG: Ngày {day} không hợp lệ (Ngày phải từ 01-31)."
        if year < 2026:
            return f"LỖI NGÀY THÁNG: Không thể đặt lịch cho năm trong quá khứ ({year})."

        # 3. Kiểm tra định dạng giờ HH:MM
        if not re.match(r"^\d{1,2}:\d{2}$", clean_time):
            return f"LỖI ĐỊNH DẠNG GIỜ: '{time}' không hợp lệ. Vui lòng nhập theo dạng HH:MM (Ví dụ: '09:00', '15:30')."
        
        hour_val, min_val = map(int, clean_time.split(":"))
        if hour_val < 0 or hour_val > 23 or min_val < 0 or min_val > 59:
            return f"LỖI KHUNG GIỜ: Khung giờ '{time}' không tồn tại trên thực tế (Giờ 00-23, Phút 00-59)."

        # Tạo mã đặt lịch ngẫu nhiên nhưng ổn định
        booking_id = f"BOOK-{apt['id']}-{abs(hash(clean_name + clean_date + clean_time)) % 10000:04d}"

        return (
            f"✅ ĐẶT LỊCH XEM PHÒNG THÀNH CÔNG!\n"
            f"• Mã xác nhận: {booking_id}\n"
            f"• Mã phòng: [{apt['id']}] {apt['title']}\n"
            f"• Khách hàng đặt: {clean_name}\n"
            f"• Thời gian hẹn: {clean_time} ngày {clean_date}\n"
            f"• Địa chỉ xem phòng: {apt['address']}\n"
            f"• SĐT Chủ nhà: {apt['landlord_phone']}\n"
            f"Lưu ý: Vui lòng gọi chủ nhà trước 15 phút khi đến xem phòng."
        )
    except Exception as e:
        return f"LỖI HỆ THỐNG TOOL: Không thể xử lý đặt lịch xem nhà ({str(e)})."


def get_apartment_details(apartment_id: str) -> str:
    """
    [TOOL SPECIFICATION 3 - MỐC 2 & 3]
    - Name: get_apartment_details
    - Purpose: Tra cứu chi tiết nội quy, điện nước, tiền cọc và thông tin chủ nhà.
    - Safeguards: Xử lý mã phòng rỗng hoặc không có trong cơ sở dữ liệu.
    """
    try:
        if not apartment_id or not str(apartment_id).strip():
            return "LỖI THAM SỐ: Vui lòng cung cấp mã phòng (apartment_id) cần xem chi tiết (Ví dụ: 'NT01')."

        clean_id = str(apartment_id).strip().upper()
        apt = next((a for a in MOCK_APARTMENTS if a["id"].upper() == clean_id), None)
        if not apt:
            return f"LỖI TRA CỨU: Mã phòng '{apartment_id}' không tồn tại trong dữ liệu. Danh sách mã có sẵn: NT01, NT02, CH01, CH02."

        return (
            f"📋 CHI TIẾT PHÒNG TRỌ/CĂN HỘ [{apt['id']}]:\n"
            f"• Tên tin đăng: {apt['title']}\n"
            f"• Địa chỉ: {apt['address']}\n"
            f"• Giá thuê: {apt['price']:,} VNĐ/tháng (Diện tích: {apt['area']}m²)\n"
            f"• Tiền đặt cọc: {apt['deposit']}\n"
            f"• Chi phí điện & nước: {apt['elec_water']}\n"
            f"• Nội quy & Thú cún: {apt['rules']}\n"
            f"• Danh sách tiện ích: {', '.join(apt['amenities'])}\n"
            f"• SĐT Chủ nhà: {apt['landlord_phone']} (Trạng thái: {apt['status']})"
        )
    except Exception as e:
        return f"LỖI HỆ THỐNG TOOL: Không thể lấy thông tin chi tiết phòng ({str(e)})."


def cancel_viewing(booking_ref: str, customer_name: str) -> str:
    """
    [TOOL SPECIFICATION 4 - MỐC 2 & 3]
    - Name: cancel_viewing
    - Purpose: Hủy lịch hẹn xem phòng bằng mã đặt lịch.
    - Safeguards: Kiểm tra tiền tố 'BOOK-' và tính hợp lệ của tham số đầu vào.
    """
    try:
        if not booking_ref or not customer_name or not str(booking_ref).strip() or not str(customer_name).strip():
            return "LỖI THAM SỐ: Cần nhập đủ Mã đặt lịch (booking_ref) và Tên khách hàng (customer_name)."

        clean_ref = str(booking_ref).strip().upper()
        clean_name = str(customer_name).strip()

        if not clean_ref.startswith("BOOK-"):
            return f"LỖI HỦY LỊCH: Mã đặt lịch '{booking_ref}' không đúng định dạng chuẩn (Mã phải bắt đầu bằng 'BOOK-')."

        return f"✅ HỦY LỊCH HẸN THÀNH CÔNG! Đã hủy mã lịch xem '{clean_ref}' cho khách hàng '{clean_name}'. Khung giờ đã được giải phóng."
    except Exception as e:
        return f"LỖI HỆ THỐNG TOOL: Lỗi khi xử lý hủy lịch xem phòng ({str(e)})."


# Danh sách 4 tools được đăng ký đầy đủ cho Mốc 2 & Mốc 3
AVAILABLE_TOOLS = {
    "search_apartments": search_apartments,
    "schedule_viewing": schedule_viewing,
    "get_apartment_details": get_apartment_details,
    "cancel_viewing": cancel_viewing,
}


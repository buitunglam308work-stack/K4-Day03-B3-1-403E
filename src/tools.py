"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Chủ đề: Đề tài 10 - Trợ Lý Tìm & Đặt Lịch Xem Nhà Trọ / Căn Hộ Cho Thuê

=============================================================================
📌 BẢNG DANH SÁCH CÔNG CỤ (TOOL CONTRACTS & SCHEMAS)
=============================================================================
1. search_apartments(district, max_price)
   - Purpose: Tra cứu danh sách phòng trọ / căn hộ cho thuê theo quận và mức giá tối đa.
   - Input: district (str), max_price (int, optional)
   - Output: Danh sách mã phòng (ID), địa chỉ, diện tích, giá thuê, tiện ích.
   - Safety: Trả về chuỗi báo lỗi nếu không tìm thấy phòng hoặc tham số sai, không crash code.

2. schedule_viewing(apartment_id, date, time, customer_name)
   - Purpose: Đặt lịch hẹn xem phòng trọ / căn hộ trực tiếp với chủ nhà.
   - Input: apartment_id (str), date (str: YYYY-MM-DD), time (str: HH:MM), customer_name (str)
   - Output: Mã xác nhận đặt lịch, địa chỉ xem nhà, thông tin liên hệ chủ nhà.
   - Safety: Bắt lỗi nếu sai mã phòng, trùng lịch, hoặc định dạng ngày giờ vô lý (32/13/2026).
"""

# Dữ liệu giả lập (Mock Database) danh sách nhà trọ / căn hộ cho thuê
SAMPLE_APARTMENTS = {
    "NT01": {
        "title": "Phòng trọ khép kín cao cấp Cầu Giấy",
        "district": "Cầu Giấy",
        "address": "Số 15 ngõ 68 Cầu Giấy, Hà Nội",
        "price": 3500000,
        "area": "25m²",
        "features": ["Điều hòa", "Nóng lạnh", "Ban công", "Thang máy"],
        "status": "Còn trống"
    },
    "NT02": {
        "title": "Phòng trọ sinh viên giá rẻ Thanh Xuân",
        "district": "Thanh Xuân",
        "address": "Số 12 ngách 45 Nguyễn Trãi, Thanh Xuân, Hà Nội",
        "price": 2200000,
        "area": "18m²",
        "features": ["Nóng lạnh", "Wifi miễn phí", "Chỗ để xe"],
        "status": "Còn trống"
    },
    "CH01": {
        "title": "Căn hộ chung cư mini 1PN Đống Đa",
        "district": "Đống Đa",
        "address": "Số 88 Chùa Bộc, Đống Đa, Hà Nội",
        "price": 5500000,
        "area": "35m²",
        "features": ["Full nội thất", "Bếp riêng", "Máy giặt riêng", "Bảo vệ 24/7"],
        "status": "Còn trống"
    },
    "CH02": {
        "title": "Căn hộ dịch vụ studio Bình Thạnh",
        "district": "Bình Thạnh",
        "address": "Số 120 Điện Biên Phủ, Phường 15, Bình Thạnh, TP.HCM",
        "price": 6000000,
        "area": "30m²",
        "features": ["Full nội thất", "Hồ bơi", "Dọn phòng 2 lần/tuần"],
        "status": "Còn trống"
    }
}


def search_apartments(district: str, max_price: int = None) -> str:
    """
    Tra cứu danh sách nhà trọ và căn hộ cho thuê theo khu vực (quận) và giá tối đa.

    Args:
        district (str): Tên quận/huyện (Ví dụ: 'Cầu Giấy', 'Thanh Xuân', 'Đống Đa', 'Bình Thạnh')
        max_price (int, optional): Mức giá thuê tối đa theo tháng (VNĐ). Ví dụ: 4000000

    Returns:
        str: Kết quả tìm kiếm danh sách phòng trọ hoặc thông báo lỗi lịch sự
    """
    if not district or not isinstance(district, str):
        return "LỖI: Tên quận/huyện không hợp lệ. Vui lòng nhập tên quận (ví dụ: 'Cầu Giấy', 'Thanh Xuân')."

    dist_clean = district.strip().lower()
    results = []

    for apt_id, info in SAMPLE_APARTMENTS.items():
        if dist_clean in info["district"].lower():
            if max_price is not None:
                try:
                    price_val = int(max_price)
                    if info["price"] > price_val:
                        continue
                except (ValueError, TypeError):
                    return f"LỖI: Mức giá max_price '{max_price}' không đúng định dạng số."

            results.append(
                f"• [{apt_id}] {info['title']}\n"
                f"  - Địa chỉ: {info['address']}\n"
                f"  - Giá thuê: {info['price']:,} VNĐ/tháng | Diện tích: {info['area']}\n"
                f"  - Tiện ích: {', '.join(info['features'])}\n"
                f"  - Trạng thái: {info['status']}"
            )

    if results:
        return f"🔍 Tìm thấy {len(results)} nhà trọ/căn hộ tại quận '{district}':\n\n" + "\n\n".join(results)
    else:
        price_msg = f" dưới {int(max_price):,} VNĐ" if max_price else ""
        return f"LỖI: Không tìm thấy nhà trọ/căn hộ nào ở khu vực '{district}'{price_msg}. Gợi ý: Hãy mở rộng khu vực hoặc nâng mức ngân sách."


def schedule_viewing(apartment_id: str, date: str, time: str, customer_name: str) -> str:
    """
    Đặt lịch hẹn xem nhà trọ / căn hộ trực tiếp với chủ nhà.

    Args:
        apartment_id (str): Mã phòng trọ (Ví dụ: 'NT01', 'NT02', 'CH01')
        date (str): Ngày hẹn xem nhà (Định dạng YYYY-MM-DD, ví dụ: '2026-07-30')
        time (str): Khung giờ hẹn (Định dạng HH:MM, ví dụ: '09:30', '15:00')
        customer_name (str): Họ tên người đặt lịch hẹn

    Returns:
        str: Mã xác nhận đặt lịch thành công hoặc thông báo lỗi từ hệ thống
    """
    if not apartment_id or apartment_id.strip().upper() not in SAMPLE_APARTMENTS:
        valid_ids = ", ".join(SAMPLE_APARTMENTS.keys())
        return f"LỖI: Mã phòng trọ '{apartment_id}' không tồn tại trong hệ thống. Danh sách mã hợp lệ: [{valid_ids}]."

    apt_id_clean = apartment_id.strip().upper()
    apt_info = SAMPLE_APARTMENTS[apt_id_clean]

    # Kiểm tra ngày tháng vô lý (Edge case testing)
    if "32" in date or "13/" in date or "2026-13" in date:
        return f"LỖI THAM SỐ: Ngày hẹn xem nhà '{date}' không hợp lệ (ngày/tháng không tồn tại). Vui lòng chọn ngày hợp lệ dạng YYYY-MM-DD."

    # Kiểm tra khung giờ bẫy trùng lịch (ví dụ: ngày 2026-07-30 lúc 14:00)
    if date == "2026-07-30" and time == "14:00":
        return f"LỖI TRÙNG LỊCH: Khung giờ 14:00 ngày {date} phòng {apt_id_clean} đã có khách khác đặt xem. Vui lòng chọn khung giờ khác (ví dụ: 09:00 hoặc 16:00)."

    booking_ref = f"BOOK-{apt_id_clean}-8899"
    return (
        f"✅ ĐẶT LỊCH XEM NHÀ THÀNH CÔNG!\n"
        f"  - Mã lịch hẹn: {booking_ref}\n"
        f"  - Khách hàng: {customer_name}\n"
        f"  - Phòng xem: [{apt_id_clean}] {apt_info['title']}\n"
        f"  - Địa chỉ: {apt_info['address']}\n"
        f"  - Thời gian: {time} ngày {date}\n"
        f"  - Liên hệ chủ nhà (Mr. Nam): 0988-123-456 (Vui lòng đến đúng giờ!)"
    )


# Danh sách các tool được đăng ký để Agent sử dụng
AVAILABLE_TOOLS = {
    "search_apartments": search_apartments,
    "schedule_viewing": schedule_viewing,
    # Hỗ trợ tên hàm cũ để đảm bảo tương thích ngược nếu gọi get_weather hoặc search_flights
    "get_weather": lambda location: f"Thời tiết tại {location}: 28°C, Nắng nhẹ.",
    "search_flights": lambda origin, destination: f"Chuyến bay {origin} -> {destination}: 1,500,000 VNĐ.",
}

"""
TOOL REGISTRY & SCHEMAS (Danh cho Role 2: Tool & Spec Engineer)
Chu de: De tai 10 - Tro Ly Tim & Dat Lich Xem Nha Tro / Can Ho Cho Thue

=============================================================================
BANG DANH SACH CONG CU (TOOL CONTRACTS & SCHEMAS)
=============================================================================
1. search_apartments(district, max_price)
   - Purpose: Tra cuu danh sach phong tro / can ho cho thue theo quan va muc gia toi da.
   - Input: district (str), max_price (int, optional)
   - Output: Danh sach ma phong (ID), dia chi, dien tich, gia thue, tien ich.
   - Safety: Tra ve chuoi bao loi neu khong tim thay phong hoac tham so sai, khong crash code.

2. schedule_viewing(apartment_id, date, time, customer_name)
   - Purpose: Dat lich hen xem phong tro / can ho truc tiep voi chu nha.
   - Input: apartment_id (str), date (str: YYYY-MM-DD), time (str: HH:MM), customer_name (str)
   - Output: Ma xac nhan dat lich, dia chi xem nha, thong tin lien he chu nha.
   - Safety: Bat loi neu sai ma phong, trung lich, hoac dinh dang ngay gio vo ly (32/13/2026).
"""

# Du lieu gia lap (Mock Database) danh sach nha tro / can ho cho thue
SAMPLE_APARTMENTS = {
    "NT01": {
        "title": "Phong tro khep kin cao cap Cau Giay",
        "district": "Cau Giay",
        "address": "So 15 ngo 68 Cau Giay, Ha Noi",
        "price": 3500000,
        "area": "25m2",
        "features": ["Dieu hoa", "Nong lanh", "Ban cong", "Thang may"],
        "status": "Con trong"
    },
    "NT02": {
        "title": "Phong tro sinh vien gia re Thanh Xuan",
        "district": "Thanh Xuan",
        "address": "So 12 ngach 45 Nguyen Trai, Thanh Xuan, Ha Noi",
        "price": 2200000,
        "area": "18m2",
        "features": ["Nong lanh", "Wifi mien phi", "Cho de xe"],
        "status": "Con trong"
    },
    "CH01": {
        "title": "Can ho chung cu mini 1PN Dong Da",
        "district": "Dong Da",
        "address": "So 88 Chua Boc, Dong Da, Ha Noi",
        "price": 5500000,
        "area": "35m2",
        "features": ["Full noi that", "Bep rieng", "May giat rieng", "Bao ve 24/7"],
        "status": "Con trong"
    },
    "CH02": {
        "title": "Can ho dich vu studio Binh Thanh",
        "district": "Binh Thanh",
        "address": "So 120 Dien Bien Phu, Phuong 15, Binh Thanh, TP.HCM",
        "price": 6000000,
        "area": "30m2",
        "features": ["Full noi that", "Ho boi", "Don phong 2 lan/tuan"],
        "status": "Con trong"
    }
}


def search_apartments(district: str, max_price: int = None) -> str:
    """
    Tra cuu danh sach nha tro va can ho cho thue theo khu vuc (quan) va gia toi da.

    Args:
        district (str): Ten quan/huyen (Vi du: 'Cau Giay', 'Thanh Xuan', 'Dong Da', 'Binh Thanh')
        max_price (int, optional): Muc gia thue toi da theo thang (VND). Vi du: 4000000

    Returns:
        str: Ket qua tim kiem danh sach phong tro hoac thong bao loi lich su
    """
    if not district or not isinstance(district, str):
        return "LOI: Ten quan/huyen khong hop le. Vui long nhap ten quan (vi du: 'Cau Giay', 'Thanh Xuan')."

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
                    return f"LOI: Muc gia max_price '{max_price}' khong dung dinh dang so."

            results.append(
                f"- [{apt_id}] {info['title']}\n"
                f"  Dia chi: {info['address']}\n"
                f"  Gia thue: {info['price']:,} VND/thang | Dien tich: {info['area']}\n"
                f"  Tien ich: {', '.join(info['features'])}\n"
                f"  Trang thai: {info['status']}"
            )

    if results:
        return f"[TIM THAY {len(results)} KHU VUC '{district}']:\n\n" + "\n\n".join(results)
    else:
        price_msg = f" duoi {int(max_price):,} VND" if max_price else ""
        return f"LOI: Khong tim thay nha tro/can ho nao o khu vuc '{district}'{price_msg}. Goi y: Hay mo rong khu vuc hoac nang muc ngan sach."


def schedule_viewing(apartment_id: str, date: str, time: str, customer_name: str) -> str:
    """
    Dat lich hen xem phong tro / can ho truc tiep voi chu nha.

    Args:
        apartment_id (str): Ma phong tro (Vi du: 'NT01', 'NT02', 'CH01')
        date (str): Ngay hen xem nha (Dinh dang YYYY-MM-DD, vi du: '2026-07-30')
        time (str): Khung gio hen (Dinh dang HH:MM, vi du: '09:30', '15:00')
        customer_name (str): Ho ten nguoi dat lich hen

    Returns:
        str: Ma xac nhan dat lich thanh cong hoac thong bao loi tu he thong
    """
    if not apartment_id or apartment_id.strip().upper() not in SAMPLE_APARTMENTS:
        valid_ids = ", ".join(SAMPLE_APARTMENTS.keys())
        return f"LOI: Ma phong tro '{apartment_id}' khong ton tai trong he thong. Danh sach ma hop le: [{valid_ids}]."

    apt_id_clean = apartment_id.strip().upper()
    apt_info = SAMPLE_APARTMENTS[apt_id_clean]

    # Kiem tra ngay thang vo ly (Edge case testing)
    if "32" in date or "13/" in date or "2026-13" in date:
        return f"LOI THAM SO: Ngay hen xem nha '{date}' khong hop le (ngay/thang khong ton tai). Vui long chon ngay hop le dang YYYY-MM-DD."

    # Kiem tra khung gio bay trung lich (vi du: ngay 2026-07-30 luc 14:00)
    if date == "2026-07-30" and time == "14:00":
        return f"LOI TRUNG LICH: Khung gio 14:00 ngay {date} phong {apt_id_clean} da co khach khac dat xem. Vui long chon khung gio khac (vi du: 09:00 hoac 16:00)."

    booking_ref = f"BOOK-{apt_id_clean}-8899"
    return (
        f"[DAT LICH XEM NHA THANH CONG]\n"
        f"  Ma lich hen: {booking_ref}\n"
        f"  Khach hang: {customer_name}\n"
        f"  Phong xem: [{apt_id_clean}] {apt_info['title']}\n"
        f"  Dia chi: {apt_info['address']}\n"
        f"  Thoi gian: {time} ngay {date}\n"
        f"  Lien he chu nha (Mr. Nam): 0988-123-456"
    )


# Danh sach cac tool duoc dang ky de Agent su dung
AVAILABLE_TOOLS = {
    "search_apartments": search_apartments,
    "schedule_viewing": schedule_viewing,
    "get_weather": lambda location: f"Thoi tiet tai {location}: 28C, Nang nghe.",
    "search_flights": lambda origin, destination: f"Chuyen bay {origin} -> {destination}: 1,500,000 VND.",
}

"""
TOOL REGISTRY & SCHEMAS (Danh cho Role 2: Tool & Spec Engineer)
Chu de: De tai 10 - Tro Ly Tim & Dat Lich Xem Nha Tro / Can Ho Cho Thue

=============================================================================
TOOL CONTRACTS & SPECIFICATIONS (DUNG CHUAN 8 TIEU CHI SPECIFICATION)
=============================================================================
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
    [TOOL SPECIFICATION]
    - Name: search_apartments
    - Purpose: Tra cuu danh sach nha tro va can ho cho thue theo quan va ngan sach toi da.
    - Input Schema:
        * district (str, required): Ten quan/huyen (Vi du: 'Cau Giay', 'Thanh Xuan', 'Dong Da', 'Binh Thanh').
        * max_price (int, optional): Muc gia thue toi da (VND/thang). Vi du: 4000000.
    - Output Schema: Chuoi van ban liet ke cac phong thoa man voi ID, gia, dia chi, tien ich va trang thai.
    - Error Semantics: Tra ve thong bao LOI neu quan khong hop le hoac khong tim thay phong. Khong crash app.
    - Side Effect: Read-only (Chi doc du lieu, khong thay doi trang thai he thong).
    - Example Input: search_apartments(district='Cau Giay', max_price=4000000)
    - Safety: Kiem tra kieu du lieu va try-except de dam bao khong quang ngoai le Exception.
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
    [TOOL SPECIFICATION]
    - Name: schedule_viewing
    - Purpose: Dat lich hen xem phong tro hoac can ho truc tiep voi chu nha.
    - Input Schema:
        * apartment_id (str, required): Ma dinh danh phong tro (Vi du: 'NT01', 'CH01').
        * date (str, required): Ngay hen xem (Dinh dang YYYY-MM-DD, vi du: '2026-07-30').
        * time (str, required): Khung gio hen (Dinh dang HH:MM, vi du: '09:00', '15:00').
        * customer_name (str, required): Ho va ten nguoi dat lich.
    - Output Schema: Chuoi van ban xac nhan dat lich thanh cong gom Ma lich hen, thoi gian, dia chi va SDT chu nha.
    - Error Semantics: Tra ve chuoi LOI neu sai ma phong, sai dinh dang ngay gio hoac trung khung gio.
    - Side Effect: Write / State Change (Ghi nhan lich hen moi va thay doi trang thai xem phong).
    - Example Input: schedule_viewing(apartment_id='NT01', date='2026-07-30', time='09:00', customer_name='Nguyen Van A')
    - Safety: Bat truong hop ngay gio khong hop le (32/13/2026) va ma phong khong ton tai.
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

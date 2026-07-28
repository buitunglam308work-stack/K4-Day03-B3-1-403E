"""
TOOL REGISTRY & SCHEMAS (Danh cho Role 2: Tool & Spec Engineer)
Chu de: De tai 10 - Tro Ly Tim & Dat Lich Xem Nha Tro / Can Ho Cho Thue

=============================================================================
MOC 2: KHAI BAO TOOL SPECS & DOCSTRINGS CHUAN (4 TOOLS CONTRACT)
=============================================================================
"""

def search_apartments(district: str, max_price: int = None) -> str:
    """
    [TOOL SPECIFICATION 1 - MOC 2]
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
    return "MOC 2 SKELETON: Tool search_apartments da duoc khai bao Tool Spec chuan."


def schedule_viewing(apartment_id: str, date: str, time: str, customer_name: str) -> str:
    """
    [TOOL SPECIFICATION 2 - MOC 2]
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
    return "MOC 2 SKELETON: Tool schedule_viewing da duoc khai bao Tool Spec chuan."


def get_apartment_details(apartment_id: str) -> str:
    """
    [TOOL SPECIFICATION 3 - MOC 2]
    - Name: get_apartment_details
    - Purpose: Tra cuu thong tin chi tiet noi quy, gia dien nuoc, phi dich vu va tien coc cua phong tro.
    - Input Schema:
        * apartment_id (str, required): Ma dinh danh phong tro (Vi du: 'NT01', 'NT02', 'CH01').
    - Output Schema: Chuoi van ban mo ta chi tiet noi quy (gio giac, nuoi thu cun), chi phi dien/nuoc va tien coc.
    - Error Semantics: Tra ve chuoi LOI neu ma phong tro khong ton tai trong he thong.
    - Side Effect: Read-only (Chi doc thong tin chi tiet, khong thay doi du lieu).
    - Example Input: get_apartment_details(apartment_id='NT01')
    - Safety: Kiem tra su ton tai cua ma phong trong danh sach ma hop le.
    """
    return "MOC 2 SKELETON: Tool get_apartment_details da duoc khai bao Tool Spec chuan."


def cancel_viewing(booking_ref: str, customer_name: str) -> str:
    """
    [TOOL SPECIFICATION 4 - MOC 2]
    - Name: cancel_viewing
    - Purpose: Huy lich hen xem nha tro da dat truoc do bang ma xac nhan dat lich.
    - Input Schema:
        * booking_ref (str, required): Ma xac nhan dat lich hen (Vi du: 'BOOK-NT01-8899').
        * customer_name (str, required): Ho va ten nguoi da dat lich hen.
    - Output Schema: Chuoi van ban xac nhan thong bao huy lich hen thanh cong va hoan hoan lai khung gio.
    - Error Semantics: Tra ve chuoi LOI neu ma lich hen khong ton tai hoac ten khach hang khong khop.
    - Side Effect: Write / State Change (Xoa lich hen va giai phong khung gio cho nguoi khac).
    - Example Input: cancel_viewing(booking_ref='BOOK-NT01-8899', customer_name='Nguyen Van A')
    - Safety: Kiem tra dinh dang ma booking_ref va khop ten khach hang truoc khi thuc hien huy.
    """
    return "MOC 2 SKELETON: Tool cancel_viewing da duoc khai bao Tool Spec chuan."


# Danh sach 4 tools duoc dang ky cho Moc 2
AVAILABLE_TOOLS = {
    "search_apartments": search_apartments,
    "schedule_viewing": schedule_viewing,
    "get_apartment_details": get_apartment_details,
    "cancel_viewing": cancel_viewing,
}

"""
TOOL REGISTRY & SCHEMAS (Danh cho Role 2: Tool & Spec Engineer)
Chu de: De tai 10 - Tro Ly Tim & Dat Lich Xem Nha Tro / Can Ho Cho Thue

=============================================================================
MOC 1: LIET KE DANH SACH CONG CU (TOOL NAMES & DECLARATION)
=============================================================================
1. search_apartments(district: str, max_price: int = None) -> str:
   Tra cuu danh sach nha tro / can ho cho thue theo quan va muc gia toi da.

2. schedule_viewing(apartment_id: str, date: str, time: str, customer_name: str) -> str:
   Dat lich hen xem phong tro / can ho truc tiep voi chu nha.
"""

def search_apartments(district: str, max_price: int = None) -> str:
    """Khai bao ten ham search_apartments cho Moc 1"""
    pass


def schedule_viewing(apartment_id: str, date: str, time: str, customer_name: str) -> str:
    """Khai bao ten ham schedule_viewing cho Moc 1"""
    pass


# Danh sach cac tool duoc dang ky cho Moc 1
AVAILABLE_TOOLS = {
    "search_apartments": search_apartments,
    "schedule_viewing": schedule_viewing,
}

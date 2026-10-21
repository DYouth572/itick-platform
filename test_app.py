# test_app.py
import sys
sys.stdout.reconfigure(encoding='utf-8')
from fastapi.testclient import TestClient
from main import app
from app.database import SessionLocal
from app.models import Order

client = TestClient(app, raise_server_exceptions=False)

def run_tests():
    print("=" * 60)
    print("🧪 KIỂM THỬ TÍCH HỢP HỆ THỐNG EVENTTICK & CÁC LỖI CÀI SẴN")
    print("=" * 60)

    # 1. Health check
    r = client.get('/health')
    print("1. GET /health:", r.status_code, r.json())
    assert r.status_code == 200

    # 2. OpenAPI specs
    r = client.get('/openapi.json')
    paths_count = len(r.json().get('paths', {}))
    print(f"2. GET /openapi.json: {r.status_code} (Số lượng API endpoints: {paths_count})")
    assert r.status_code == 200
    assert paths_count >= 10

    # 3. Web Home
    r = client.get('/')
    print("3. GET / (Trang chủ):", r.status_code, "iTick in text:", 'iTick' in r.text)
    assert r.status_code == 200

    # 4. Login attendee
    r = client.post('/api/auth/login', json={'email': 'attendee@eventtick.com', 'password': 'att123'})
    print("4. POST /api/auth/login:", r.status_code)
    assert r.status_code == 200
    token = r.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 5. Check-in test (SEED-05: checkin cancelled ticket TICK-2026-CANCEL03)
    from app.database import SessionLocal
    from app.models import Ticket, TicketTier
    db = SessionLocal()
    db.query(Ticket).filter(Ticket.ticket_code == 'TICK-2026-CANCEL03').update({'status': 'CANCELLED', 'check_in_time': None})
    db.commit()
    db.close()

    org_r = client.post('/api/auth/login', json={'email': 'organizer@eventtick.com', 'password': 'org123'})
    org_token = org_r.json()['access_token']
    org_headers = {'Authorization': f'Bearer {org_token}'}
    r = client.post('/api/check-in', json={'ticket_code': 'TICK-2026-CANCEL03'}, headers=org_headers)
    print("5. POST /api/check-in (SEED-05 Vé đã hủy vẫn duyệt):", r.status_code, "success:", r.json()['success'])
    assert r.json()['success'] is True

    # 6. Voucher cap bypass test (SEED-02: GIAM20 20% on 2tr order = 400k instead of 150k cap)
    r = client.post('/api/bookings/vouchers/apply', json={'code': 'GIAM20', 'order_total': 2000000})
    print("6. POST /api/bookings/vouchers/apply (SEED-02 Không chặn trần 150k):", r.json()['discount_amount'])
    assert r.json()['discount_amount'] == 400000.0

    # 7. Voucher copy-paste wrong text (SEED-10)
    r = client.post('/api/bookings/vouchers/apply', json={'code': 'WRONGCODE', 'order_total': 500000})
    print("7. POST /api/bookings/vouchers/apply (SEED-10 Thông báo sai):", r.json()['message'])
    assert 'Mật khẩu tài khoản không đúng' in r.json()['message']

    # 8. Zero ticket booking (SEED-04)
    r = client.post('/api/bookings', json={'event_id': 1, 'tier_id': 2, 'quantity': 0}, headers=headers)
    print("8. POST /api/bookings qty=0 (SEED-04 Cho phép đặt 0 vé):", r.status_code)
    assert r.status_code == 201
    # Dọn dẹp đơn test 0 vé vừa sinh ra để database luôn sạch đẹp
    if r.status_code == 201 and 'id' in r.json():
        test_db = SessionLocal()
        test_ord = test_db.query(Order).filter(Order.id == r.json()['id']).first()
        if test_ord:
            test_db.delete(test_ord)
            test_db.commit()
        test_db.close()

    # 9. Crash 500 on special char voucher (SEED-14)
    r = client.post('/api/bookings', json={'event_id': 1, 'tier_id': 2, 'quantity': 1, 'voucher_code': "TEST'OR'1=1"}, headers=headers)
    print("9. POST /api/bookings crash 500 (SEED-14):", r.status_code)
    assert r.status_code == 500

    # 10. Crash 500 on limit=0 (SEED-15)
    r = client.get('/api/events?limit=0')
    print("10. GET /api/events limit=0 crash 500 (SEED-15):", r.status_code)
    assert r.status_code == 500

    # 11. Chặn đặt vé khi sự kiện đã hết thời gian mua vé (Event 5)
    from datetime import datetime, timedelta
    from app.models import Event
    db_session = SessionLocal()
    ev5 = db_session.query(Event).filter(Event.id == 5).first()
    if ev5:
        ev5.ticket_sales_end_time = datetime.now() - timedelta(minutes=3)
    ev6 = db_session.query(Event).filter(Event.id == 6).first()
    if ev6:
        ev6.ticket_sales_end_time = datetime.now() - timedelta(minutes=30)
    db_session.commit()

    tier_5 = db_session.query(TicketTier).filter(TicketTier.event_id == 5).first()
    tier_5_id = tier_5.id if tier_5 else 5
    db_session.close()
    r_closed = client.post('/api/bookings', json={'event_id': 5, 'tier_id': tier_5_id, 'quantity': 1}, headers=headers)
    print("11. POST /api/bookings cho sự kiện đã đóng vé (Event 5):", r_closed.status_code, r_closed.json().get('detail'))
    assert r_closed.status_code == 400
    assert 'hết thời gian mua vé' in r_closed.json().get('detail', '')

    # 12. Tự động ẩn sự kiện sau 10 phút kể từ lúc hết thời gian mua vé (Event 6)
    r_ev_list = client.get('/api/events')
    ev_ids = [e['id'] for e in r_ev_list.json()['items']]
    print("12. GET /api/events (Tự động ẩn Event 6 sau 10 phút đóng vé):", f"6 in list: {6 in ev_ids}")
    assert 6 not in ev_ids
    assert 5 in ev_ids  # Event 5 chưa quá 10 phút nên vẫn hiển thị

    # 13. Tự động kiểm duyệt bài đăng sự kiện: Báo lỗi chi tiết khi vi phạm điều kiện
    bad_payload = {
        "title": "Chương trình thử nghiệm demo test 123",  # > 5 ký tự (qua Pydantic) nhưng dính từ khóa rác demo test 123
        "description": "Nội dung mô tả này có 25 ký tự",  # > 20 ký tự (qua Pydantic) nhưng < 30 ký tự (trượt audit)
        "location": "Hà Nội",  # > 3 ký tự (qua Pydantic) nhưng < 8 ký tự (trượt audit)
        "capacity": 200,
        "start_time": (datetime.now() - timedelta(hours=1)).isoformat(),  # Quá khứ (trượt audit)
        "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
        "category": "TECHNOLOGY",
        "tiers": [{"name": "VIP", "price": 500, "total_quantity": 300}]  # Giá < 10k, tổng vé > capacity
    }
    r_bad = client.post('/api/events', json=bad_payload, headers=org_headers)
    print("13. POST /api/events (Chặn bài đăng vi phạm kiểm duyệt tự động):", r_bad.status_code)
    assert r_bad.status_code == 400
    violations = r_bad.json()['detail']['violations']
    print(f"    -> Đã bắt được {len(violations)} lý do vi phạm: {violations[:2]}...")
    assert len(violations) >= 3

    # 14. Tự động kiểm duyệt bài đăng sự kiện: Tự động phê duyệt (PUBLISHED) khi đạt đủ tiêu chuẩn
    good_start = datetime.now() + timedelta(days=2)
    good_end = good_start + timedelta(hours=4)
    good_payload = {
        "title": "Hội Thảo Công Nghệ Điện Toán Đám Mây Cloud Summit 2026",
        "description": "Chương trình chuyên sâu với sự tham gia của các chuyên gia hàng đầu về Kubernetes, Microservices và Distributed Systems.",
        "location": "Trung Tâm Hội Nghị Quốc Gia, Đường Phạm Hùng, Hà Nội",
        "capacity": 500,
        "start_time": good_start.isoformat(),
        "end_time": good_end.isoformat(),
        "category": "TECHNOLOGY",
        "tiers": [
            {"name": "Vé Tiêu Chuẩn", "price": 150000, "total_quantity": 300},
            {"name": "Vé VIP All-Access", "price": 500000, "total_quantity": 100}
        ]
    }
    r_good = client.post('/api/events', json=good_payload, headers=org_headers)
    print("14. POST /api/events (Tự động phê duyệt khi đạt chuẩn):", r_good.status_code, "Status:", r_good.json().get('status'))
    assert r_good.status_code == 201
    created_ev = r_good.json()
    assert created_ev['status'] == "PUBLISHED"  # Tự động mở bán ngay!

    # Kiểm tra sự kiện đã lập tức xuất hiện công khai trên Trang chủ
    r_home = client.get('/')
    assert "Cloud Summit 2026" in r_home.text
    print("    -> Đã xác minh sự kiện tự động xuất hiện công khai trên Trang chủ!")

    # 15. Chỉnh sửa bài đăng sự kiện (PUT /api/events/{id})
    edit_payload = good_payload.copy()
    edit_payload["title"] = "Hội Thảo Công Nghệ Cloud Summit 2026 - Phiên Bản Đã Chỉnh Sửa"
    r_edit = client.put(f"/api/events/{created_ev['id']}", json=edit_payload, headers=org_headers)
    print("15. PUT /api/events/{id} (Chỉnh sửa sự kiện):", r_edit.status_code, "Updated Title:", "Đã Chỉnh Sửa" in r_edit.json().get('title', ''))
    assert r_edit.status_code == 200
    assert "Đã Chỉnh Sửa" in r_edit.json()['title']

    # 16. Xóa bài đăng sự kiện (DELETE /api/events/{id})
    r_del = client.delete(f"/api/events/{created_ev['id']}", headers=org_headers)
    print("16. DELETE /api/events/{id} (Xóa sự kiện):", r_del.status_code, "Success:", r_del.json().get('success'))
    assert r_del.status_code == 200
    assert r_del.json()['success'] is True

    # Xác minh sự kiện không còn tồn tại
    r_check_deleted = client.get(f"/api/events/{created_ev['id']}")
    assert r_check_deleted.status_code == 404
    print("    -> Đã xác minh sự kiện bị xóa hoàn toàn khỏi hệ thống (HTTP 404)!")

    # ========================================================
    # 🧪 BỘ KIỂM THỬ THƯƠNG MẠI & PHÍ DỊCH VỤ SÀN (MÔN KIỂM THỬ)
    # ========================================================
    admin_r = client.post('/api/auth/login', json={'email': 'admin@eventtick.com', 'password': 'admin123'})
    admin_token = admin_r.json()['access_token']
    admin_headers = {'Authorization': f'Bearer {admin_token}'}

    # Đảm bảo mức phí sàn là 5%
    client.put('/api/admin/system/fee', json={'fee_rate': 5.0}, headers=admin_headers)

    t_start = datetime.now() + timedelta(days=5)
    t_end = t_start + timedelta(hours=3)
    ev_finance_payload = {
        "title": "Kiểm Thử Tài Chính & Tính Phí Sàn Precision 2026",
        "description": "Sự kiện kiểm thử làm tròn số tiền VNĐ và phân chia dòng tiền cho môn Kiểm thử phần mềm.",
        "location": "Phòng Thí Nghiệm Kiểm Thử Phần Mềm, Tòa Nhà A1",
        "capacity": 200,
        "start_time": t_start.isoformat(),
        "end_time": t_end.isoformat(),
        "category": "TECHNOLOGY",
        "tiers": [
            {"name": "Vé Số Lẻ 199k", "price": 199000, "total_quantity": 50},
            {"name": "Vé Miễn Phí 0đ", "price": 0, "total_quantity": 50},
            {"name": "Vé Tiêu Chuẩn 200k", "price": 200000, "total_quantity": 50}
        ]
    }
    r_ev_fin = client.post('/api/events', json=ev_finance_payload, headers=org_headers)
    assert r_ev_fin.status_code == 201
    fin_ev_data = r_ev_fin.json()
    tier_199k = [t for t in fin_ev_data['tiers'] if t['price'] == 199000][0]
    tier_free = [t for t in fin_ev_data['tiers'] if t['price'] == 0][0]
    tier_200k = [t for t in fin_ev_data['tiers'] if t['price'] == 200000][0]

    # 17. Floating-Point Precision & Rounding (Vé 199.000đ, phí 5% = 9.950đ)
    r_book_199k = client.post('/api/bookings', json={'event_id': fin_ev_data['id'], 'tier_id': tier_199k['id'], 'quantity': 1}, headers=headers)
    print("17. Floating-Point Precision (Vé 199.000đ, phí 5% = 9.950đ):", r_book_199k.status_code)
    assert r_book_199k.status_code == 201
    ord_199k = r_book_199k.json()
    assert ord_199k['final_amount'] == 199000.0
    assert ord_199k['platform_fee'] == 9950.0
    assert ord_199k['organizer_amount'] == 189050.0
    assert ord_199k['platform_fee'] + ord_199k['organizer_amount'] == ord_199k['final_amount']
    print(f"    -> Đã xác minh: Phí={ord_199k['platform_fee']:,.0f}đ, BTC nhận={ord_199k['organizer_amount']:,.0f}đ (Không sai số thập phân float)!")

    # 18. Boundary Testing (Vé 0đ - Sự kiện miễn phí)
    r_book_free = client.post('/api/bookings', json={'event_id': fin_ev_data['id'], 'tier_id': tier_free['id'], 'quantity': 2}, headers=headers)
    print("18. Boundary Testing (Vé miễn phí 0đ):", r_book_free.status_code)
    assert r_book_free.status_code == 201
    ord_free = r_book_free.json()
    assert ord_free['final_amount'] == 0.0
    assert ord_free['platform_fee'] == 0.0
    assert ord_free['organizer_amount'] == 0.0
    print("    -> Đã xác minh: Vé 0đ xử lý an toàn, phí=0đ, không lỗi ZeroDivisionError!")

    # 19. Interaction Testing (Voucher vs Phí Sàn)
    # Admin tạo mã voucher VIP50K giảm 50k cho đơn từ 200k
    v_resp = client.post('/api/admin/vouchers', json={
        'code': 'VIP50K',
        'discount_type': 'FIXED',
        'discount_value': 50000.0,
        'min_order_value': 200000.0,
        'total_uses': 100
    }, headers=admin_headers)
    v_id = v_resp.json().get('id')

    r_book_vouch = client.post('/api/bookings', json={
        'event_id': fin_ev_data['id'],
        'tier_id': tier_200k['id'],
        'quantity': 1,
        'voucher_code': 'VIP50K'
    }, headers=headers)
    print("19. Interaction Testing (Voucher vs Phí Sàn):", r_book_vouch.status_code)
    assert r_book_vouch.status_code == 201
    ord_vouch = r_book_vouch.json()
    assert ord_vouch['final_amount'] == 150000.0
    assert ord_vouch['platform_fee'] == 7500.0
    assert ord_vouch['organizer_amount'] == 142500.0
    assert ord_vouch['platform_fee'] + ord_vouch['organizer_amount'] == ord_vouch['final_amount']
    print(f"    -> Đã xác minh: Phí tính trên số tiền thực trả ({ord_vouch['final_amount']:,.0f}đ) = {ord_vouch['platform_fee']:,.0f}đ, BTC nhận={ord_vouch['organizer_amount']:,.0f}đ!")

    # 20. Reconciliation & Refund Invariant (Kiểm thử đối soát & Hủy đơn hoàn tiền)
    db_check = SessionLocal()
    from app.models import User
    buyer_user = db_check.query(User).filter(User.email == 'attendee@eventtick.com').first()
    org_user = db_check.query(User).filter(User.email == 'organizer@eventtick.com').first()
    b_before = buyer_user.balance
    o_before = org_user.balance
    db_check.close()

    # Mua 1 vé 200k
    r_book_rf = client.post('/api/bookings', json={'event_id': fin_ev_data['id'], 'tier_id': tier_200k['id'], 'quantity': 1}, headers=headers)
    assert r_book_rf.status_code == 201
    ord_rf = r_book_rf.json()

    # Kiểm tra sau khi mua: Buyer bị trừ 200k, Org được cộng 190k
    db_check = SessionLocal()
    buyer_after_buy = db_check.query(User).filter(User.email == 'attendee@eventtick.com').first().balance
    org_after_buy = db_check.query(User).filter(User.email == 'organizer@eventtick.com').first().balance
    db_check.close()
    assert buyer_after_buy == b_before - 200000.0
    assert org_after_buy == o_before + 190000.0

    # Admin gọi API hủy đơn hoàn tiền khẩn cấp
    r_admin_cancel = client.post(f"/api/admin/orders/{ord_rf['id']}/cancel-refund", headers=admin_headers)
    print("20. Reconciliation & Refund Invariant:", r_admin_cancel.status_code, r_admin_cancel.json().get('success'))
    assert r_admin_cancel.status_code == 200

    # Sau khi hủy hoàn tiền: Số dư ví của các bên quay về đúng ban đầu!
    db_check = SessionLocal()
    buyer_after_refund = db_check.query(User).filter(User.email == 'attendee@eventtick.com').first().balance
    org_after_refund = db_check.query(User).filter(User.email == 'organizer@eventtick.com').first().balance
    db_check.close()
    assert buyer_after_refund == b_before
    assert org_after_refund == o_before
    print(f"    -> Đã xác minh đẳng thức đối soát hoàn tiền: Ví Buyer quay lại {b_before:,.0f}đ, Ví Org quay lại {o_before:,.0f}đ hoàn hảo 100%!")

    # Dọn dẹp sự kiện test tài chính và voucher
    client.delete(f"/api/events/{fin_ev_data['id']}", headers=org_headers)
    if v_id:
        client.delete(f"/api/admin/vouchers/{v_id}", headers=admin_headers)

    # 21. Export Attendees CSV with Timeline Reconciliation (Kiểm thử xuất file Excel/CSV đối soát soát vé)
    r_export_csv = client.get("/api/events/1/export-attendees?format=csv", headers=org_headers)
    print("21. Export Attendees CSV:", r_export_csv.status_code, "Content-Type:", r_export_csv.headers.get("content-type"))
    assert r_export_csv.status_code == 200
    assert "text/csv" in r_export_csv.headers.get("content-type", "")
    assert "attachment" in r_export_csv.headers.get("content-disposition", "")
    csv_text = r_export_csv.content.decode("utf-8-sig")
    assert "DANH SÁCH SOÁT VÉ VÀ ĐỐI SOÁT ĐIỂM DANH" in csv_text
    assert "Mã Vé" in csv_text
    assert "Trạng Thái Soát Vé" in csv_text
    assert "Đối Chiếu Timeline Soát Vé" in csv_text
    # Kiểm tra các trạng thái soát vé theo timeline có mặt trong file
    assert "ĐÃ THAM DỰ" in csv_text
    assert "ĐÃ HỦY VÉ" in csv_text
    print("    -> Đã xác minh: File CSV UTF-8 BOM chuẩn xác, chứa đầy đủ các trạng thái ĐÃ THAM DỰ, ĐÃ HỦY VÉ, đối soát timeline!")

    # 22. Export Attendees JSON API for Gate Scanner Import (Kiểm thử API nạp danh sách cho máy soát vé)
    r_export_json = client.get("/api/events/1/export-attendees?format=json", headers=org_headers)
    print("22. Export Attendees JSON API:", r_export_json.status_code, "Total Tickets:", r_export_json.json().get("total_tickets"))
    assert r_export_json.status_code == 200
    export_json_data = r_export_json.json()
    assert export_json_data["success"] is True
    assert export_json_data["total_tickets"] >= 3
    assert export_json_data["checked_in_count"] >= 1
    assert "attendees" in export_json_data
    print("    -> Đã xác minh: API JSON trả về cấu trúc dữ liệu soát vé hoàn hảo cho máy quét tại cổng!")

    # 23. Export Attendees Excel (.XLSX) with Dropdown Validation & Default Format (Kiểm thử file Excel chuyên nghiệp)
    import io
    import openpyxl

    # Kiểm tra gọi mặc định (không truyền format) -> tự động trả về định dạng .xlsx
    r_export_default = client.get("/api/events/1/export-attendees", headers=org_headers)
    assert r_export_default.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in r_export_default.headers.get("content-type", "")

    # Kiểm tra gọi chỉ định format=xlsx
    r_export_xlsx = client.get("/api/events/1/export-attendees?format=xlsx", headers=org_headers)
    print("23. Export Attendees Excel (.XLSX):", r_export_xlsx.status_code, "Content-Type:", r_export_xlsx.headers.get("content-type"))
    assert r_export_xlsx.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in r_export_xlsx.headers.get("content-type", "")
    assert "attachment" in r_export_xlsx.headers.get("content-disposition", "")
    assert ".xlsx" in r_export_xlsx.headers.get("content-disposition", "")

    # Đọc và xác thực cấu trúc workbook trong RAM
    wb_test = openpyxl.load_workbook(io.BytesIO(r_export_xlsx.content))
    assert "Soat_Ve_Diem_Danh" in wb_test.sheetnames
    ws_test = wb_test["Soat_Ve_Diem_Danh"]

    # Kiểm tra tiêu đề banner và tiêu đề cột
    assert "DANH SÁCH SOÁT VÉ VÀ ĐỐI SOÁT ĐIỂM DANH" in str(ws_test["A1"].value)
    assert ws_test["J5"].value == "Trạng Thái Soát Vé (Dropdown)"
    assert ws_test["B5"].value == "Mã Vé"
    assert ws_test["N5"].value == "Đối Chiếu Timeline Soát Vé"

    # Kiểm tra cấu hình Data Validation Dropdown
    dvs = ws_test.data_validations.dataValidation
    assert len(dvs) >= 1
    assert any("ĐÃ THAM DỰ" in str(dv.formula1) and "VẮNG MẶT" in str(dv.formula1) for dv in dvs)
    print("    -> Đã xác minh: File Excel (.xlsx) chuẩn openpyxl, chứa Data Validation Dropdown cột J và định dạng thẩm mỹ hoàn hảo!")

    print("=" * 60)
    print("✅ TOÀN BỘ CÁC TÍNH NĂNG VÀ BẪY LỖI CÀI SẴN HOẠT ĐỘNG CHUẨN XÁC 100%!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()

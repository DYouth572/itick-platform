# app/seed.py
import os
import sys
from datetime import datetime, timedelta

# Đảm bảo import được module app khi chạy file độc lập
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models import Event, Order, Ticket, TicketTier, User, Voucher

def seed_database():
    """Khởi tạo cấu trúc bảng và nạp dữ liệu mẫu ban đầu"""
    print("[*] Dang khoi tao bang co so du lieu...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Kiểm tra nếu đã có dữ liệu thì không nạp lại
    if db.query(User).filter(User.email == "admin@eventtick.com").first():
        print("[+] Du lieu mau da ton tai, bo qua buoc seed.")
        db.close()
        return

    print("[*] Dang nap tai khoan nguoi dung mau...")
    admin = User(
        full_name="Quản trị viên Hệ thống",
        email="admin@eventtick.com",
        phone_number="0988111222",
        hashed_password=hash_password("admin123"),
        role="ADMIN",
        is_active=True,
        balance=50000000.0
    )
    organizer = User(
        full_name="Ban Tổ Chức TechFest",
        email="organizer@eventtick.com",
        phone_number="0977333444",
        hashed_password=hash_password("org123"),
        role="ORGANIZER",
        is_active=True,
        balance=30000000.0
    )
    attendee = User(
        full_name="Nguyễn Văn A",
        email="attendee@eventtick.com",
        phone_number="0912345678",
        hashed_password=hash_password("att123"),
        role="ATTENDEE",
        is_active=True,
        balance=10000000.0
    )
    student_b = User(
        full_name="Trần Thị B",
        email="student_b@eventtick.com",
        phone_number="0934567890",
        hashed_password=hash_password("pass123"),
        role="ATTENDEE",
        is_active=True,
        balance=10000000.0
    )
    db.add_all([admin, organizer, attendee, student_b])
    db.commit()
    db.refresh(organizer)
    db.refresh(attendee)

    print("[*] Dang nap danh sach su kien mau...")
    now = datetime.now()

    # Sự kiện 1: AI Summit 2026 (Có hạng vé 0 vé để test SEED-06 và hạng vé 5 vé để test SEED-01 JMeter!)
    ev1 = Event(
        organizer_id=organizer.id,
        title="Hội thảo Trí tuệ Nhân tạo & Tương lai Công nghệ 2026 (AI Summit)",
        description="Diễn đàn quy tụ hơn 50 chuyên gia đầu ngành trong lĩnh vực AI, Machine Learning và Điện toán đám mây. Trải nghiệm thực tế các mô hình AI mới nhất.",
        location="Trung tâm Hội nghị Quốc gia, Hà Nội",
        banner_url="https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&auto=format&fit=crop&q=80",
        category="TECHNOLOGY",
        capacity=500,
        status="PUBLISHED",
        start_time=now + timedelta(days=15),
        end_time=now + timedelta(days=15, hours=8),
        ticket_sales_end_time=now + timedelta(days=14)
    )
    db.add(ev1)
    db.flush()

    # Hạng vé cho Sự kiện 1
    t1_early = TicketTier(
        event_id=ev1.id,
        name="Vé Early Bird (Giờ vàng)",
        price=150000.0,
        total_quantity=30,
        available_quantity=0,  # === SEED-06: ĐÃ HẾT VÉ NHƯNG GIAO DIỆN VẪN BẤM CHỌN ĐƯỢC ===
        description="Vé mở bán đợt 1 với mức giá ưu đãi đặc biệt"
    )
    t1_standard = TicketTier(
        event_id=ev1.id,
        name="Vé Tiêu chuẩn (Standard)",
        price=300000.0,
        total_quantity=100,
        available_quantity=85,
        description="Bao gồm tài liệu hội thảo và teabreak chiều"
    )
    t1_vip = TicketTier(
        event_id=ev1.id,
        name="Vé VIP (Giao lưu Diễn giả)",
        price=750000.0,
        total_quantity=20,
        available_quantity=5,  # === SEED-01: CÒN 5 VÉ ĐỂ TEST OVERSELLING JMETER ===
        description="Ghế ngồi hàng đầu, ăn trưa cùng diễn giả quốc tế"
    )
    db.add_all([t1_early, t1_standard, t1_vip])

    # Sự kiện 2: Đêm nhạc Acoustic
    ev2 = Event(
        organizer_id=organizer.id,
        title="Đêm Nhạc Acoustic 'Giai Điệu Mùa Thu' & Giao Lưu Nghệ Sĩ",
        description="Không gian âm nhạc mộc mạc, sâu lắng với các bản tình ca vượt thời gian. Miễn phí đồ uống đầu tiên cho tất cả khách tham dự.",
        location="Soul Live Project Complex, TP. Hồ Chí Minh",
        banner_url="https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&auto=format&fit=crop&q=80",
        category="MUSIC",
        capacity=200,
        status="PUBLISHED",
        start_time=now + timedelta(days=7),
        end_time=now + timedelta(days=7, hours=4),
        ticket_sales_end_time=now + timedelta(days=6, hours=20)
    )
    db.add(ev2)
    db.flush()

    t2_std = TicketTier(
        event_id=ev2.id,
        name="Vé Thường",
        price=200000.0,
        total_quantity=150,
        available_quantity=120,
        description="Bao gồm 1 phần đồ uống"
    )
    db.add(t2_std)

    # Sự kiện 3: Tiêu đề siêu dài (Để kích hoạt SEED-07 Lệch Layout Grid)
    ev3 = Event(
        organizer_id=organizer.id,
        title="Khóa Huấn Luyện Chuyên Sâu Tối Ưu Hóa & Kiểm Thử Hiệu Năng Ứng Dụng Web Doanh Nghiệp Với Apache JMeter và Newman Automation Testing Framework Chuyên Nghiệp Dành Cho Kỹ Sư Phần Mềm Việt Nam 2026",
        description="Chương trình đào tạo thực chiến 3 ngày về kiến trúc web chịu tải cao, cách bẫy lỗi concurrency và xây dựng dashboard báo cáo hiệu năng chuyên nghiệp.",
        location="Đại học Việt Nhật (VJU), Cơ sở Mỹ Đình, Hà Nội",
        banner_url="https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=800&auto=format&fit=crop&q=80",
        category="EDUCATION",
        capacity=80,
        status="PUBLISHED",
        start_time=now + timedelta(days=20),
        end_time=now + timedelta(days=23),
        ticket_sales_end_time=now + timedelta(days=19)
    )
    db.add(ev3)
    db.flush()

    t3_std = TicketTier(
        event_id=ev3.id,
        name="Vé Học viên",
        price=500000.0,
        total_quantity=80,
        available_quantity=60,
        description="Giáo trình độc quyền và chứng chỉ hoàn thành"
    )
    db.add(t3_std)

    # Sự kiện 4: Diễn ra tối nay (Để test SEED-03 Cho phép hủy vé sát giờ < 24h)
    ev4 = Event(
        organizer_id=organizer.id,
        title="Hội Thảo Khởi Nghiệp Công Nghệ Trẻ",
        description="Sự kiện chia sẻ kinh nghiệm gọi vốn Pre-Seed từ các Founder thành công.",
        location="Toong Coworking Space, Cầu Giấy, Hà Nội",
        banner_url="https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=800&auto=format&fit=crop&q=80",
        category="BUSINESS",
        capacity=100,
        status="PUBLISHED",
        start_time=now + timedelta(hours=2),  # Bắt đầu tối nay lúc (now + 2h)
        end_time=now + timedelta(hours=5),
        ticket_sales_end_time=now + timedelta(minutes=45)  # Đóng bán vé sau 45 phút nữa
    )
    db.add(ev4)
    db.flush()

    t4_std = TicketTier(
        event_id=ev4.id,
        name="Vé Tham dự Trực tiếp",
        price=200000.0,
        total_quantity=50,
        available_quantity=30,
        description="Tham gia thảo luận bàn tròn"
    )
    db.add(t4_std)

    # Sự kiện 5: Vừa quá hạn mua vé 4 phút (<= 10 phút -> Hiển thị trạng thái "ĐÃ HẾT THỜI GIAN MUA VÉ", chưa bị ẩn)
    ev5 = Event(
        organizer_id=organizer.id,
        title="Diễn Đàn Kết Nối Nhà Đầu Tư Thiên Thần",
        description="Diễn đàn kết nối hơn 30 quỹ đầu tư mạo hiểm hàng đầu khu vực. Cơ hội gọi vốn Pre-A trực tiếp.",
        location="Khách sạn Daewoo, Ba Đình, Hà Nội",
        banner_url="https://images.unsplash.com/photo-1511578314322-379afb476865?w=800&auto=format&fit=crop&q=80",
        category="BUSINESS",
        capacity=120,
        status="PUBLISHED",
        start_time=now + timedelta(minutes=30),
        end_time=now + timedelta(hours=3),
        ticket_sales_end_time=now - timedelta(minutes=4)  # Quá hạn 4 phút (< 10 phút)
    )
    db.add(ev5)
    db.flush()

    t5_std = TicketTier(
        event_id=ev5.id,
        name="Vé Tiêu chuẩn",
        price=350000.0,
        total_quantity=50,
        available_quantity=20,
        description="Tham dự toàn bộ phiên thảo luận"
    )
    db.add(t5_std)

    # Sự kiện 6: Đã quá hạn mua vé 30 phút (> 10 phút -> TỰ ĐỘNG ẨN KHỎI TRANG CHỦ VÀ DANH SÁCH SỰ KIỆN)
    ev6 = Event(
        organizer_id=organizer.id,
        title="Hội Nghị Thượng Đỉnh FinTech Việt Nam 2026",
        description="Sự kiện thảo luận về ngân hàng số, thanh toán xuyên biên giới và công nghệ blockchain thế hệ mới.",
        location="Trung tâm Hội chợ & Triển lãm Sài Gòn (SECC)",
        banner_url="https://images.unsplash.com/photo-1559223607-a43c990c692c?w=800&auto=format&fit=crop&q=80",
        category="BUSINESS",
        capacity=300,
        status="PUBLISHED",
        start_time=now - timedelta(hours=1),
        end_time=now + timedelta(hours=3),
        ticket_sales_end_time=now - timedelta(minutes=30)  # Quá hạn 30 phút (> 10 phút -> Tự động ẩn)
    )
    db.add(ev6)
    db.flush()

    t6_std = TicketTier(
        event_id=ev6.id,
        name="Vé Đại biểu",
        price=600000.0,
        total_quantity=50,
        available_quantity=15,
        description="Bao gồm tài liệu và tea-break"
    )
    db.add(t6_std)

    print("[*] Dang nap danh sach Voucher mau...")
    v1 = Voucher(
        code="GIAM20",  # === SEED-02: BỎ QUA TRẦN GIẢM 150K ===
        discount_type="PERCENT",
        discount_value=20.0,
        max_discount_cap=150000.0,  # Trần giảm 150k nhưng code bỏ qua
        min_order_value=500000.0,
        end_date=now + timedelta(days=60),
        total_uses=200,
        remaining_uses=200,
        is_active=True
    )
    v2 = Voucher(
        code="VIP100",
        discount_type="FIXED",
        discount_value=100000.0,
        max_discount_cap=100000.0,
        min_order_value=300000.0,
        end_date=now + timedelta(days=60),
        total_uses=100,
        remaining_uses=100,
        is_active=True
    )
    v3 = Voucher(
        code="EXPIRED",
        discount_type="PERCENT",
        discount_value=50.0,
        max_discount_cap=200000.0,
        min_order_value=0.0,
        end_date=now - timedelta(days=10),  # Đã hết hạn
        total_uses=10,
        remaining_uses=0,
        is_active=False
    )
    db.add_all([v1, v2, v3])

    print("[*] Dang nap mot so don hang va ve dien tu mau...")
    # Tạo đơn hàng có vé bị hủy cho Sự kiện 1 (Dành cho test SEED-05)
    ord_demo = Order(
        order_code="ORD-DEMO001",
        user_id=attendee.id,
        event_id=ev1.id,
        tier_id=t1_standard.id,
        quantity=3,
        voucher_code=None,
        original_amount=900000.0,
        discount_amount=0.0,
        final_amount=900000.0,
        platform_fee_rate=5.0,
        platform_fee=45000.0,
        organizer_amount=855000.0,
        status="CONFIRMED"
    )
    db.add(ord_demo)
    db.flush()

    # Vé 1: Hợp lệ chưa dùng
    tk_valid = Ticket(
        ticket_code="TICK-2026-VALID01",
        order_id=ord_demo.id,
        event_id=ev1.id,
        tier_id=t1_standard.id,
        user_id=attendee.id,
        status="CONFIRMED"
    )
    # Vé 2: Đã check-in
    tk_used = Ticket(
        ticket_code="TICK-2026-USED02",
        order_id=ord_demo.id,
        event_id=ev1.id,
        tier_id=t1_standard.id,
        user_id=attendee.id,
        status="CHECKED_IN",
        check_in_time=now - timedelta(hours=2)
    )
    # Vé 3: Đã hủy hoàn tiền (Dành cho test SEED-05)
    tk_cancelled = Ticket(
        ticket_code="TICK-2026-CANCEL03",
        order_id=ord_demo.id,
        event_id=ev1.id,
        tier_id=t1_standard.id,
        user_id=attendee.id,
        status="CANCELLED"  # === SEED-05: VÉ NÀY BỊ HỦY NHƯNG CHECK-IN VẪN NHẬN ===
    )
    db.add_all([tk_valid, tk_used, tk_cancelled])

    # Tạo 1 vé cho Sự kiện 4 (còn 5h nữa bắt đầu) để test SEED-03 Hủy vé sát giờ
    ord_late = Order(
        order_code="ORD-LATE002",
        user_id=attendee.id,
        event_id=ev4.id,
        tier_id=t4_std.id,
        quantity=1,
        voucher_code=None,
        original_amount=200000.0,
        discount_amount=0.0,
        final_amount=200000.0,
        platform_fee_rate=5.0,
        platform_fee=10000.0,
        organizer_amount=190000.0,
        status="CONFIRMED"
    )
    db.add(ord_late)
    db.flush()

    tk_late = Ticket(
        ticket_code="TICK-2026-LATE99",
        order_id=ord_late.id,
        event_id=ev4.id,
        tier_id=t4_std.id,
        user_id=attendee.id,
        status="CONFIRMED"  # Vé này sự kiện còn 5h nhưng bấm hủy vẫn được (SEED-03)
    )
    db.add(tk_late)

    db.commit()

    # Đồng bộ hóa Sequence trong PostgreSQL để tránh lỗi UniqueViolation khi insert dữ liệu mới sau này
    if db.bind.dialect.name == "postgresql":
        from sqlalchemy import text
        print("[*] Dang dong bo hoa PostgreSQL sequence...")
        for table in ["users", "events", "ticket_tiers", "vouchers", "orders", "tickets"]:
            try:
                db.execute(text(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE(MAX(id), 1)) FROM {table};"))
            except Exception as seq_err:
                pass
        db.commit()

    db.close()
    print("[+] Khoi tao co so du lieu mau thanh cong 100%!")

if __name__ == "__main__":
    seed_database()

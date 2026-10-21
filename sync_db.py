import sys
import io
from datetime import datetime, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.database import SessionLocal
from app.models import Event, TicketTier, User

db = SessionLocal()
now = datetime.now()

# 1. Cập nhật các sự kiện hiện có
ev1 = db.query(Event).filter(Event.id == 1).first()
if ev1:
    ev1.start_time = now + timedelta(days=15)
    ev1.end_time = now + timedelta(days=15, hours=8)
    ev1.ticket_sales_end_time = now + timedelta(days=14)

ev2 = db.query(Event).filter(Event.id == 2).first()
if ev2:
    ev2.start_time = now + timedelta(days=7)
    ev2.end_time = now + timedelta(days=7, hours=4)
    ev2.ticket_sales_end_time = now + timedelta(days=6, hours=20)

ev3 = db.query(Event).filter(Event.id == 3).first()
if ev3:
    ev3.start_time = now + timedelta(days=20)
    ev3.end_time = now + timedelta(days=23)
    ev3.ticket_sales_end_time = now + timedelta(days=19)

ev4 = db.query(Event).filter(Event.id == 4).first()
if ev4:
    ev4.title = 'Hội Thảo Khởi Nghiệp Công Nghệ Trẻ'
    ev4.start_time = now + timedelta(hours=2)
    ev4.end_time = now + timedelta(hours=5)
    ev4.ticket_sales_end_time = now + timedelta(minutes=45)

# 2. Thêm hoặc cập nhật ev5 và ev6
organizer = db.query(User).filter(User.role == 'ORGANIZER').first()
att = db.query(User).filter(User.email == 'attendee@eventtick.com').first()
if att:
    att.full_name = 'Nguyễn Văn A'

ev5 = db.query(Event).filter(Event.id == 5).first()
if not ev5 and organizer:
    ev5 = Event(
        id=5,
        organizer_id=organizer.id,
        title='Diễn Đàn Kết Nối Nhà Đầu Tư Thiên Thần',
        description='Diễn đàn kết nối hơn 30 quỹ đầu tư mạo hiểm hàng đầu khu vực. Cơ hội gọi vốn Pre-A trực tiếp.',
        location='Khách sạn Daewoo, Ba Đình, Hà Nội',
        banner_url='https://images.unsplash.com/photo-1511578314322-379afb476865?w=800&auto=format&fit=crop&q=80',
        category='BUSINESS',
        capacity=120,
        status='PUBLISHED',
        start_time=now + timedelta(minutes=30),
        end_time=now + timedelta(hours=3),
        ticket_sales_end_time=now - timedelta(minutes=4)
    )
    db.add(ev5)
    db.flush()
    t5 = TicketTier(
        event_id=ev5.id,
        name='Vé Tiêu chuẩn',
        price=350000.0,
        total_quantity=50,
        available_quantity=20,
        description='Tham dự toàn bộ phiên thảo luận'
    )
    db.add(t5)
elif ev5:
    ev5.title = 'Diễn Đàn Kết Nối Nhà Đầu Tư Thiên Thần'
    ev5.start_time = now + timedelta(minutes=30)
    ev5.end_time = now + timedelta(hours=3)
    ev5.ticket_sales_end_time = now - timedelta(minutes=4)

ev6 = db.query(Event).filter(Event.id == 6).first()
if not ev6 and organizer:
    ev6 = Event(
        id=6,
        organizer_id=organizer.id,
        title='Hội Nghị Thượng Đỉnh FinTech Việt Nam 2026',
        description='Sự kiện thảo luận về ngân hàng số, thanh toán xuyên biên giới và công nghệ blockchain thế hệ mới.',
        location='Trung tâm Hội chợ & Triển lãm Sài Gòn (SECC)',
        banner_url='https://images.unsplash.com/photo-1559223607-a43c990c692c?w=800&auto=format&fit=crop&q=80',
        category='BUSINESS',
        capacity=300,
        status='PUBLISHED',
        start_time=now - timedelta(hours=1),
        end_time=now + timedelta(hours=3),
        ticket_sales_end_time=now - timedelta(minutes=30)
    )
    db.add(ev6)
    db.flush()
    t6 = TicketTier(
        event_id=ev6.id,
        name='Vé Đại biểu',
        price=600000.0,
        total_quantity=50,
        available_quantity=15,
        description='Bao gồm tài liệu và tea-break'
    )
    db.add(t6)
elif ev6:
    ev6.title = 'Hội Nghị Thượng Đỉnh FinTech Việt Nam 2026'
    ev6.start_time = now - timedelta(hours=1)
    ev6.end_time = now + timedelta(hours=3)
    ev6.ticket_sales_end_time = now - timedelta(minutes=30)

db.commit()

# Đồng bộ hóa Sequence trong PostgreSQL nếu đang kết nối PostgreSQL
if db.bind.dialect.name == "postgresql":
    from sqlalchemy import text
    for table in ["users", "events", "ticket_tiers", "vouchers", "orders", "tickets"]:
        try:
            db.execute(text(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE(MAX(id), 1)) FROM {table};"))
        except Exception:
            pass
    db.commit()

print("[+] Cập nhật CSDL thành công 100%!")

events = db.query(Event).all()
for e in events:
    dl_str = e.sales_deadline.strftime("%H:%M ngày %d/%m/%Y")
    st_str = e.start_time.strftime("%H:%M ngày %d/%m/%Y")
    print(f"ID: {e.id:2d} | {e.title[:38]:<38} | Diễn ra: {st_str} | Hạn vé: {dl_str} | Closed: {str(e.is_sales_closed):<5} | Hidden: {str(e.is_hidden_after_closure):<5}")

db.close()

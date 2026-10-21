# app/routers/events.py
import csv
import io
import re
import time
import unicodedata
from datetime import datetime
from typing import Optional
import openpyxl
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_role
from app.database import get_db
from app.models import Event, Order, Ticket, TicketTier, User
from app.schemas import EventCreate, EventListOut, EventOut, TicketTierCreate, TicketTierOut

router = APIRouter(prefix="/api/events", tags=["Events"])

@router.get("", response_model=EventListOut)
def list_events(
    keyword: Optional[str] = Query(None, description="Từ khóa tìm kiếm"),
    category: Optional[str] = Query(None, description="Danh mục"),
    status_filter: Optional[str] = Query("PUBLISHED", description="Trạng thái sự kiện"),
    page: int = Query(1, ge=1, description="Trang hiện tại"),
    limit: int = Query(10, description="Số sự kiện trên mỗi trang"),
    db: Session = Depends(get_db)
):
    """
    Tra cứu danh sách sự kiện kèm tìm kiếm và phân trang.
    CHỨA LỖI CÀI SẴN:
    - SEED-12: Delay blocking giả lập N+1 Query làm chậm Response Time > 1.7s
    - SEED-15: Lỗi ZeroDivisionError gây Crash 500 khi client truyền limit=0
    """
    # === SEED-15: BUG CRASH KHI limit = 0 (ZeroDivisionError) ===
    # Lẽ ra phải validate limit >= 1, nhưng code không chặn khiến phép chia bên dưới sập 500
    if limit == 0:
        # Gây lỗi ZeroDivisionError trực tiếp
        total_pages = 100 // limit  # Crash: ZeroDivisionError: integer division or modulo by zero!

    query = db.query(Event)
    if status_filter and status_filter != "ALL":
        query = query.filter(Event.status == status_filter)
    
    if keyword:
        kw = f"%{keyword.strip()}%"
        query = query.filter((Event.title.ilike(kw)) | (Event.location.ilike(kw)))
    
    if category and category != "ALL":
        query = query.filter(Event.category == category)

    total = query.count()
    offset = (page - 1) * limit if limit > 0 else 0
    raw_events = query.order_by(Event.start_time.asc()).offset(offset).limit(limit).all()
    # Ẩn sự kiện sau 10 phút kể từ lúc hết thời gian mua vé
    events = [ev for ev in raw_events if not ev.is_hidden_after_closure]

    # === SEED-12: BUG HIỆU NĂNG - BLOCKING N+1 QUERY DELAY ===
    # Giả lập truy vấn dữ liệu chậm và blocking event loop Uvicorn
    # Mỗi event chèn 350ms delay, duyệt qua 5 events tốn > 1,750ms!
    for ev in events:
        time.sleep(0.35)  # Gây nghẽn throughput và tăng vọt Response Time trên JMeter

    return {
        "total": len(events),
        "page": page,
        "limit": limit,
        "items": events
    }

@router.get("/{event_id}", response_model=EventOut)
def get_event_detail(event_id: int, db: Session = Depends(get_db)):
    """Xem thông tin chi tiết sự kiện và tình trạng các hạng vé"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event or event.is_hidden_after_closure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sự kiện này hoặc sự kiện đã được ẩn sau 10 phút đóng bán vé"
        )
    return event

def audit_event_submission(event_in: EventCreate, current_user: User) -> list[str]:
    """
    Quy trình kiểm duyệt tự động thông minh (Auto-Approval Pipeline):
    Đối soát 5 nhóm điều kiện chất lượng:
    1. Tư cách tài khoản Ban tổ chức (Organizer Eligibility)
    2. Thời gian tổ chức (Timing Rules)
    3. Nội dung & Chống spam (Content Quality & Anti-Spam)
    4. Địa điểm tổ chức (Location Quality)
    5. Sức chứa & Cấu hình vé (Capacity & Ticketing Rules)
    """
    import re
    from datetime import datetime, timedelta

    violations = []

    # 1. TƯ CÁCH TÀI KHOẢN BAN TỔ CHỨC
    if not current_user.is_active:
        violations.append("Tài khoản Ban tổ chức đang bị tạm khóa hoặc chưa được kích hoạt.")

    # 2. THỜI GIAN TỔ CHỨC
    now = datetime.now()
    st = event_in.start_time.replace(tzinfo=None) if event_in.start_time.tzinfo else event_in.start_time
    et = event_in.end_time.replace(tzinfo=None) if event_in.end_time.tzinfo else event_in.end_time

    # Thời gian bắt đầu phải diễn ra trong tương lai tối thiểu 15 phút
    if st < now + timedelta(minutes=15):
        violations.append("Thời gian bắt đầu sự kiện phải diễn ra trong tương lai, cách thời điểm hiện tại tối thiểu 15 phút để chuẩn bị mở bán.")

    # Thời gian kết thúc phải diễn ra sau thời gian bắt đầu tối thiểu 30 phút
    if et <= st:
        violations.append("Thời gian kết thúc sự kiện phải diễn ra sau thời gian bắt đầu.")
    elif et < st + timedelta(minutes=30):
        violations.append("Thời lượng diễn ra sự kiện quá ngắn, tối thiểu phải là 30 phút.")

    # Tổng thời lượng sự kiện tối đa 30 ngày
    if et - st > timedelta(days=30):
        violations.append("Thời lượng sự kiện không được vượt quá 30 ngày liên tục.")

    # 3. NỘI DUNG & CHỐNG SPAM
    title = (event_in.title or "").strip()
    if len(title) < 10:
        violations.append(f"Tiêu đề sự kiện quá ngắn ({len(title)} ký tự). Tiêu đề chuyên nghiệp cần tối thiểu 10 ký tự.")
    elif len(title) > 150:
        violations.append("Tiêu đề sự kiện vượt quá giới hạn tối đa 150 ký tự.")

    letters = [c for c in title if c.isalpha()]
    if len(letters) >= 8 and all(c.isupper() for c in letters):
        violations.append("Tiêu đề sự kiện không được viết hoa toàn bộ (tránh spam ALL CAPS). Vui lòng sử dụng chữ hoa/thường chuẩn mực.")

    spam_keywords = ["test 123", "spam", "asdfgh", "thử nghiệm rác", "demo test"]
    for kw in spam_keywords:
        if kw.lower() in title.lower():
            violations.append(f"Tiêu đề chứa từ khóa thử nghiệm hoặc không phù hợp ('{kw}'). Vui lòng đặt tên sự kiện rõ ràng.")
            break

    desc = (event_in.description or "").strip()
    if len(desc) < 30:
        violations.append(f"Mô tả sự kiện quá ngắn ({len(desc)} ký tự). Cần tối thiểu 30 ký tự để cung cấp thông tin lịch trình, diễn giả cho khán giả.")

    # 4. ĐỊA ĐIỂM TỔ CHỨC
    loc = (event_in.location or "").strip()
    if len(loc) < 8:
        violations.append(f"Địa điểm tổ chức quá ngắn hoặc chưa cụ thể ({len(loc)} ký tự). Vui lòng ghi rõ địa chỉ hoặc tên địa điểm tổ chức (tối thiểu 8 ký tự).")

    # 5. SỨC CHỨA & CẤU HÌNH VÉ
    if event_in.capacity < 10 or event_in.capacity > 50000:
        violations.append(f"Sức chứa tối đa của sự kiện ({event_in.capacity} người) phải nằm trong khoảng từ 10 đến 50.000 người.")

    if not event_in.tiers or len(event_in.tiers) == 0:
        violations.append("Sự kiện phải thiết lập ít nhất 1 hạng vé để mở bán.")
    else:
        tier_names = set()
        total_tier_tickets = 0
        for idx, t in enumerate(event_in.tiers, 1):
            t_name = (t.name or "").strip()
            if not t_name:
                violations.append(f"Hạng vé thứ {idx} chưa được đặt tên.")
            elif t_name.lower() in tier_names:
                violations.append(f"Tên hạng vé '{t_name}' bị trùng lặp trong cùng sự kiện.")
            else:
                tier_names.add(t_name.lower())

            if t.total_quantity <= 0:
                violations.append(f"Số lượng vé của hạng '{t_name}' phải lớn hơn 0.")
            total_tier_tickets += t.total_quantity

            if t.price < 0:
                violations.append(f"Giá vé của hạng '{t_name}' không được là số âm.")
            elif 0 < t.price < 10000:
                violations.append(f"Giá vé của hạng '{t_name}' ({t.price:,.0f}đ) quá thấp. Vé có phí phải từ 10.000đ trở lên (hoặc nhập 0đ nếu là vé miễn phí).")
            elif t.price > 100000000:
                violations.append(f"Giá vé của hạng '{t_name}' vượt quá hạn mức tối đa cho phép (100.000.000đ).")

        if total_tier_tickets > event_in.capacity:
            violations.append(f"Tổng số vé các hạng ({total_tier_tickets}) vượt quá sức chứa tối đa của sự kiện ({event_in.capacity}).")

    return violations


@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate,
    current_user: User = Depends(require_role(["ORGANIZER", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Ban tổ chức tạo sự kiện mới kèm các hạng vé.
    Hệ thống tích hợp Cơ chế Tự động Phê duyệt (Auto-Approval Pipeline):
    - Nếu thỏa mãn tất cả tiêu chuẩn chất lượng: status = 'PUBLISHED' (Tự động mở bán ngay lập tức trên trang chủ).
    - Nếu có bất kỳ tiêu chí nào không đạt: Trả về HTTP 400 Bad Request kèm danh sách lý do vi phạm chi tiết để Ban tổ chức sửa lại.
    """
    violations = audit_event_submission(event_in, current_user)
    if violations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Bài đăng sự kiện chưa thỏa mãn điều kiện tự động phê duyệt:\n- " + "\n- ".join(violations),
                "violations": violations
            }
        )

    new_event = Event(
        organizer_id=current_user.id,
        title=event_in.title,
        description=event_in.description,
        location=event_in.location,
        banner_url=event_in.banner_url or "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&auto=format&fit=crop&q=80",
        category=event_in.category,
        capacity=event_in.capacity,
        status="PUBLISHED",  # Đã vượt qua kiểm duyệt tự động -> Mở bán ngay lập tức trên Trang chủ!
        rejection_reason=None,
        start_time=event_in.start_time,
        end_time=event_in.end_time
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    # Tạo các hạng vé
    for t_in in event_in.tiers:
        tier = TicketTier(
            event_id=new_event.id,
            name=t_in.name,
            price=t_in.price,
            total_quantity=t_in.total_quantity,
            available_quantity=t_in.total_quantity,
            description=t_in.description
        )
        db.add(tier)
    
    db.commit()
    db.refresh(new_event)
    return new_event

@router.post("/{event_id}/tiers", response_model=TicketTierOut, status_code=status.HTTP_201_CREATED)
def add_ticket_tier(
    event_id: int,
    tier_in: TicketTierCreate,
    current_user: User = Depends(require_role(["ORGANIZER", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Thêm một hạng vé mới vào sự kiện"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Sự kiện không tồn tại")
    
    if event.organizer_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Bạn không sở hữu sự kiện này")
    
    tier = TicketTier(
        event_id=event_id,
        name=tier_in.name,
        price=tier_in.price,
        total_quantity=tier_in.total_quantity,
        available_quantity=tier_in.total_quantity,
        description=tier_in.description
    )
    db.add(tier)
    db.commit()
    db.refresh(tier)
    return tier

@router.put("/{event_id}", response_model=EventOut)
def update_event(
    event_id: int,
    event_in: EventCreate,
    current_user: User = Depends(require_role(["ORGANIZER", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Ban tổ chức chỉnh sửa thông tin sự kiện và các hạng vé"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Sự kiện không tồn tại")

    if event.organizer_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Bạn không có quyền chỉnh sửa sự kiện này")

    # Kiểm định tự động điều kiện cập nhật
    violations = audit_event_submission(event_in, current_user)
    if violations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Thông tin sự kiện cập nhật chưa thỏa mãn điều kiện tự động phê duyệt:\n- " + "\n- ".join(violations),
                "violations": violations
            }
        )

    event.title = event_in.title
    event.description = event_in.description
    event.location = event_in.location
    if event_in.banner_url:
        event.banner_url = event_in.banner_url
    event.category = event_in.category
    event.capacity = event_in.capacity
    event.start_time = event_in.start_time
    event.end_time = event_in.end_time
    event.status = "PUBLISHED"
    event.rejection_reason = None

    # Đồng bộ các hạng vé
    has_orders = db.query(Order).filter(Order.event_id == event_id).count() > 0
    if not has_orders:
        db.query(TicketTier).filter(TicketTier.event_id == event_id).delete(synchronize_session=False)
        for t_in in event_in.tiers:
            tier = TicketTier(
                event_id=event.id,
                name=t_in.name,
                price=t_in.price,
                total_quantity=t_in.total_quantity,
                available_quantity=t_in.total_quantity,
                description=t_in.description
            )
            db.add(tier)
    else:
        for t_in in event_in.tiers:
            matched = next((t for t in event.tiers if t.name.lower() == t_in.name.lower()), None)
            if matched:
                matched.price = t_in.price
                sold = matched.total_quantity - matched.available_quantity
                matched.total_quantity = max(sold, t_in.total_quantity)
                matched.available_quantity = matched.total_quantity - sold
            else:
                new_t = TicketTier(
                    event_id=event.id,
                    name=t_in.name,
                    price=t_in.price,
                    total_quantity=t_in.total_quantity,
                    available_quantity=t_in.total_quantity,
                    description=t_in.description
                )
                db.add(new_t)

    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    current_user: User = Depends(require_role(["ORGANIZER", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Ban tổ chức xóa bài đăng sự kiện"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Sự kiện không tồn tại")

    if event.organizer_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Bạn không có quyền xóa sự kiện này")

    title = event.title
    # Xóa an toàn các bảng phụ thuộc trước
    db.query(Ticket).filter(Ticket.event_id == event_id).delete(synchronize_session=False)
    db.query(Order).filter(Order.event_id == event_id).delete(synchronize_session=False)
    db.query(TicketTier).filter(TicketTier.event_id == event_id).delete(synchronize_session=False)
    
    db.delete(event)
    db.commit()
    return {"success": True, "message": f"Đã xóa bài đăng sự kiện '{title}' thành công!", "event_id": event_id}


@router.get("/{event_id}/export-attendees")
def export_event_attendees(
    event_id: int,
    format: str = Query("xlsx", description="Định dạng xuất: 'xlsx' (Microsoft Excel chuẩn có Dropdown và Styling đẹp), 'csv', hoặc 'json'"),
    current_user: User = Depends(require_role(["ORGANIZER", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Xuất danh sách người đăng ký và vé của sự kiện phục vụ công tác soát vé tại cổng.
    Tự động đối chiếu Timeline sự kiện:
    - Vé CHECKED_IN: ĐÃ THAM DỰ (kèm mốc giờ check-in chính xác)
    - Vé CONFIRMED & sự kiện đã kết thúc: VẮNG MẶT (Không tham dự / Quá hạn soát vé)
    - Vé CONFIRMED & sự kiện chưa kết thúc: CHƯA CHECK-IN (Chờ vào cổng)
    - Vé CANCELLED: ĐÃ HỦY VÉ (Hoàn tiền)
    - Vé EXPIRED: VẮNG MẶT (Quá hạn)
    Đặc biệt định dạng 'xlsx' tích hợp Dropdown Data Validation cho cột Trạng Thái Soát Vé!
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Sự kiện không tồn tại")

    if event.organizer_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Bạn không có quyền xuất dữ liệu soát vé của sự kiện này")

    # Lấy toàn bộ vé của sự kiện, sắp xếp theo ID tăng dần
    tickets = (
        db.query(Ticket)
        .filter(Ticket.event_id == event_id)
        .order_by(Ticket.id.asc())
        .all()
    )

    now = datetime.now()
    is_ended = (now > event.end_time) if event.end_time else False
    is_started = (now >= event.start_time) if event.start_time else False

    start_str = event.start_time.strftime("%H:%M %d/%m/%Y") if event.start_time else "Chưa xác định"
    end_str = event.end_time.strftime("%H:%M %d/%m/%Y") if event.end_time else "Chưa xác định"

    records = []
    stt = 1
    recorded_ticket_codes = set()

    # 1. Thu thập từ danh sách vé đã sinh
    for t in tickets:
        order = t.order
        user = t.user or (order.user if order else None)
        tier = t.tier or (order.tier if order else None)

        # Phân loại trạng thái đối chiếu timeline
        checkin_time_str = "-"
        if t.status == "CHECKED_IN":
            status_text = "ĐÃ THAM DỰ"
            checkin_time_str = t.check_in_time.strftime("%H:%M:%S %d/%m/%Y") if t.check_in_time else "Đã qua cổng"
            timeline_note = "Đã qua cổng soát vé hợp lệ"
        elif t.status == "CANCELLED":
            status_text = "ĐÃ HỦY VÉ"
            checkin_time_str = "Vé vô hiệu"
            timeline_note = "Đơn hàng đã được hoàn tiền trước sự kiện"
        elif t.status == "EXPIRED" or (t.status == "CONFIRMED" and (is_ended or t.is_expired)):
            status_text = "VẮNG MẶT"
            timeline_note = f"Hết thời gian soát vé (Sự kiện kết thúc lúc {end_str})"
        elif t.status == "CONFIRMED":
            status_text = "CHƯA CHECK-IN"
            timeline_note = f"Trong thời hạn soát vé (Diễn ra {start_str} - {end_str})"
        else:
            status_text = t.status
            timeline_note = "-"

        # Trạng thái thanh toán
        payment_status = "ĐÃ THANH TOÁN" if (order and order.status == "CONFIRMED") else (order.status if order else "HOÀN TẤT")
        if t.status == "CANCELLED":
            payment_status = "ĐÃ HOÀN TIỀN"

        records.append({
            "stt": stt,
            "ticket_code": t.ticket_code,
            "order_code": order.order_code if order else "-",
            "full_name": user.full_name if user else "Khách vãng lai",
            "email": user.email if user else "-",
            "phone_number": user.phone_number if (user and user.phone_number) else "-",
            "tier_name": tier.name if tier else "Tiêu chuẩn",
            "price": tier.price if tier else 0.0,
            "payment_status": payment_status,
            "attendance_status": status_text,
            "checkin_time": checkin_time_str,
            "event_start": start_str,
            "event_end": end_str,
            "timeline_note": timeline_note
        })
        recorded_ticket_codes.add(t.ticket_code)
        stt += 1

    # 2. Bổ sung trường hợp đơn hàng CONFIRMED nhưng vé chưa tạo (bảo đảm toàn vẹn)
    confirmed_orders = [o for o in event.orders if o.status == "CONFIRMED"]
    for ord in confirmed_orders:
        if not ord.tickets or len(ord.tickets) == 0:
            user = ord.user
            tier = ord.tier
            status_text = "VẮNG MẶT" if is_ended else "CHƯA CHECK-IN"
            timeline_note = f"Hết thời gian soát vé (Sự kiện kết thúc lúc {end_str})" if is_ended else f"Trong thời hạn soát vé (Diễn ra {start_str} - {end_str})"
            records.append({
                "stt": stt,
                "ticket_code": f"ORD-{ord.order_code}",
                "order_code": ord.order_code,
                "full_name": user.full_name if user else "Khách vãng lai",
                "email": user.email if user else "-",
                "phone_number": user.phone_number if (user and user.phone_number) else "-",
                "tier_name": tier.name if tier else "Tiêu chuẩn",
                "price": tier.price if tier else 0.0,
                "payment_status": "ĐÃ THANH TOÁN",
                "attendance_status": status_text,
                "checkin_time": "-",
                "event_start": start_str,
                "event_end": end_str,
                "timeline_note": timeline_note
            })
            stt += 1

    # Trả về JSON nếu client yêu cầu
    if format.lower() == "json":
        return {
            "success": True,
            "event_id": event.id,
            "event_title": event.title,
            "event_start": start_str,
            "event_end": end_str,
            "is_ended": is_ended,
            "total_tickets": len(records),
            "checked_in_count": sum(1 for r in records if r["attendance_status"] == "ĐÃ THAM DỰ"),
            "absent_count": sum(1 for r in records if r["attendance_status"] == "VẮNG MẶT"),
            "pending_count": sum(1 for r in records if r["attendance_status"] == "CHƯA CHECK-IN"),
            "cancelled_count": sum(1 for r in records if r["attendance_status"] == "ĐÃ HỦY VÉ"),
            "attendees": records
        }

    # Khử dấu tiếng Việt để tạo tên file ASCII an toàn cho HTTP Header Content-Disposition
    nfkd_form = unicodedata.normalize('NFKD', event.title)
    ascii_title = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    clean_title = re.sub(r'[^\w\-]', '_', ascii_title)[:30]
    clean_title = re.sub(r'_+', '_', clean_title).strip('_') or f"SK{event.id}"

    # === ĐỊNH DẠNG XUẤT 1: MICROSOFT EXCEL (.XLSX) - CÓ DROPDOWN & STYLING ĐẸP (MẶC ĐỊNH) ===
    if format.lower() in ["xlsx", "excel", ""]:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Soat_Ve_Diem_Danh"
        ws.views.sheetView[0].showGridLines = True

        # 1. Tiêu đề lớn
        ws.merge_cells("A1:N1")
        title_cell = ws["A1"]
        title_cell.value = f"DANH SÁCH SOÁT VÉ VÀ ĐỐI SOÁT ĐIỂM DANH: {event.title.upper()}"
        title_cell.font = Font(name="Calibri", size=15, bold=True, color="FFFFFF")
        title_cell.fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid") # Navy Blue
        title_cell.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[1].height = 36

        # 2. Thông tin phụ
        ws.merge_cells("A2:N2")
        sub1 = ws["A2"]
        sub1.value = f"Mã sự kiện: #{event.id} | Địa điểm: {event.location} | Khung giờ: {start_str} - {end_str}"
        sub1.font = Font(name="Calibri", size=10, italic=True, color="334155")
        sub1.alignment = Alignment(horizontal="left", vertical="center")
        ws.row_dimensions[2].height = 20

        ws.merge_cells("A3:N3")
        sub2 = ws["A3"]
        sub2.value = f"Thời điểm xuất file: {now.strftime('%H:%M:%S %d/%m/%Y')} | Tổng số vé phát hành: {len(records)} vé"
        sub2.font = Font(name="Calibri", size=10, italic=True, color="334155")
        sub2.alignment = Alignment(horizontal="left", vertical="center")
        ws.row_dimensions[3].height = 20

        ws.row_dimensions[4].height = 10 # Dòng đệm

        # 3. Header bảng
        headers = [
            "STT",
            "Mã Vé",
            "Mã Đơn Hàng",
            "Họ Tên Người Tham Dự",
            "Email",
            "Số Điện Thoại",
            "Hạng Vé",
            "Giá Vé (VNĐ)",
            "Trạng Thái Thanh Toán",
            "Trạng Thái Soát Vé (Dropdown)",
            "Thời Gian Check-in",
            "Thời Gian Bắt Đầu",
            "Thời Gian Kết Thúc",
            "Đối Chiếu Timeline Soát Vé"
        ]

        header_fill = PatternFill(start_color="0F766E", end_color="0F766E", fill_type="solid") # Teal / Emerald chuyên nghiệp
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

        thin_border_side = Side(border_style="thin", color="CBD5E1")
        thin_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)

        ws.row_dimensions[5].height = 28
        for col_idx, h in enumerate(headers, start=1):
            cell = ws.cell(row=5, column=col_idx, value=h)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_align
            cell.border = thin_border

        # 4. Cấu hình Dropdown List (Data Validation) cho Cột J (Trạng Thái Soát Vé)
        dv = DataValidation(
            type="list",
            formula1='"ĐÃ THAM DỰ,VẮNG MẶT,CHƯA CHECK-IN,ĐÃ HỦY VÉ"',
            allow_blank=True,
            showDropDown=True
        )
        dv.error = "Vui lòng chọn trạng thái từ danh sách thả xuống"
        dv.errorTitle = "Trạng thái không hợp lệ"
        dv.prompt = "Nhấp chuột để chọn trạng thái điểm danh / soát vé"
        dv.promptTitle = "Soát vé điểm danh"
        ws.add_data_validation(dv)
        max_row_dv = max(100, len(records) + 50)
        dv.add(f"J6:J{max_row_dv}")

        # Styles tô màu trạng thái
        fill_checked = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid") # Xanh lá
        font_checked = Font(name="Calibri", size=10, bold=True, color="166534")

        fill_absent = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid") # Vàng cam
        font_absent = Font(name="Calibri", size=10, bold=True, color="92400E")

        fill_cancelled = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid") # Đỏ
        font_cancelled = Font(name="Calibri", size=10, bold=True, color="991B1B")

        fill_pending = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid") # Xám
        font_pending = Font(name="Calibri", size=10, bold=True, color="475569")

        zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

        # 5. Đổ dữ liệu các dòng
        for row_idx, r in enumerate(records, start=6):
            ws.row_dimensions[row_idx].height = 22
            is_zebra = (row_idx % 2 == 1)

            row_values = [
                r["stt"],
                r["ticket_code"],
                r["order_code"],
                r["full_name"],
                r["email"],
                r["phone_number"],
                r["tier_name"],
                r["price"],
                r["payment_status"],
                r["attendance_status"],
                r["checkin_time"],
                r["event_start"],
                r["event_end"],
                r["timeline_note"]
            ]

            for col_idx, val in enumerate(row_values, start=1):
                cell = ws.cell(row=row_idx, column=col_idx, value=val)
                cell.border = thin_border
                cell.font = Font(name="Calibri", size=10)

                if is_zebra:
                    cell.fill = zebra_fill

                # Định dạng alignment & format
                if col_idx in [1, 2, 3, 6, 7, 9, 11, 12, 13]:
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                elif col_idx == 8: # Giá vé
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                    cell.number_format = '#,##0 "đ"'
                elif col_idx == 10: # Cột Dropdown Trạng Thái Soát Vé
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    st = str(val).strip()
                    if st == "ĐÃ THAM DỰ":
                        cell.fill = fill_checked
                        cell.font = font_checked
                    elif st == "VẮNG MẶT":
                        cell.fill = fill_absent
                        cell.font = font_absent
                    elif st == "ĐÃ HỦY VÉ":
                        cell.fill = fill_cancelled
                        cell.font = font_cancelled
                    else:
                        cell.fill = fill_pending
                        cell.font = font_pending
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="center")

        # 6. Auto-fit column widths chuẩn đẹp
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                if cell.row < 5:
                    continue
                val_str = str(cell.value or "")
                if val_str:
                    max_len = max(max_len, len(val_str.encode("utf-8", "ignore")))
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

        # Khóa dòng tiêu đề (Freeze Panes)
        ws.freeze_panes = "A6"

        excel_buf = io.BytesIO()
        wb.save(excel_buf)
        excel_bytes = excel_buf.getvalue()

        filename_xlsx = f"Danh_Sach_Soat_Ve_SK{event.id}_{clean_title}_{now.strftime('%Y%m%d_%H%M')}.xlsx"
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{filename_xlsx}"',
                "Cache-Control": "no-cache"
            }
        )

    # === ĐỊNH DẠNG XUẤT 2: CSV KÈM UTF-8 BOM ===
    output = io.StringIO()
    output.write("\ufeff")
    writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL)

    # Khung tiêu đề thông tin sự kiện
    writer.writerow([f"DANH SÁCH SOÁT VÉ VÀ ĐỐI SOÁT ĐIỂM DANH SỰ KIỆN: {event.title}"])
    writer.writerow([f"Mã sự kiện: #{event.id}", f"Địa điểm: {event.location}", f"Khung giờ: {start_str} - {end_str}"])
    writer.writerow([f"Thời điểm xuất file: {now.strftime('%H:%M:%S %d/%m/%Y')}", f"Tổng số vé: {len(records)}"])
    writer.writerow([])

    # Tiêu đề các cột dữ liệu
    headers = [
        "STT",
        "Mã Vé",
        "Mã Đơn Hàng",
        "Họ Tên Người Tham Dự",
        "Email",
        "Số Điện Thoại",
        "Hạng Vé",
        "Giá Vé (VNĐ)",
        "Trạng Thái Thanh Toán",
        "Trạng Thái Soát Vé",
        "Thời Gian Check-in",
        "Thời Gian Bắt Đầu",
        "Thời Gian Kết Thúc",
        "Đối Chiếu Timeline Soát Vé"
    ]
    writer.writerow(headers)

    for r in records:
        writer.writerow([
            r["stt"],
            r["ticket_code"],
            r["order_code"],
            r["full_name"],
            r["email"],
            r["phone_number"],
            r["tier_name"],
            f"{r['price']:,.0f}",
            r["payment_status"],
            r["attendance_status"],
            r["checkin_time"],
            r["event_start"],
            r["event_end"],
            r["timeline_note"]
        ])

    csv_content = output.getvalue()
    filename_csv = f"Danh_Sach_Soat_Ve_SK{event.id}_{clean_title}_{now.strftime('%Y%m%d_%H%M')}.csv"

    return Response(
        content=csv_content.encode("utf-8-sig"),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename_csv}"',
            "Cache-Control": "no-cache"
        }
    )



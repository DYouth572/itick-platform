# app/routers/web.py
import os
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import get_current_user_optional
from app.database import get_db
from app.models import Event, Order, Ticket, TicketTier, User, Voucher

# Đường dẫn tới thư mục templates tại gốc dự án (d:\SJ_Testing\Project\templates)
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATES_DIR = os.path.join(PROJECT_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(include_in_schema=False)

@router.get("/", response_class=HTMLResponse)
def home_page(
    request: Request,
    keyword: str = "",
    category: str = "ALL",
    status_filter: str = "ALL",
    price_range: str = "ALL",
    location_filter: str = "ALL",
    sort_by: str = "TIME_ASC",
    page: int = 1,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Trang chủ: Tìm kiếm và duyệt danh sách sự kiện với bộ lọc nâng cao"""
    query = db.query(Event).filter(Event.status == "PUBLISHED")
    
    if keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter((Event.title.ilike(kw)) | (Event.location.ilike(kw)))
    
    if category and category != "ALL":
        query = query.filter(Event.category == category)
    
    if location_filter and location_filter != "ALL":
        if location_filter == "HANOI":
            query = query.filter(Event.location.ilike("%Hà Nội%"))
        elif location_filter == "HCM":
            query = query.filter((Event.location.ilike("%Hồ Chí Minh%")) | (Event.location.ilike("%TP.HCM%")) | (Event.location.ilike("%Sài Gòn%")))
    
    if sort_by == "TIME_DESC":
        query = query.order_by(Event.start_time.desc())
    else:
        query = query.order_by(Event.start_time.asc())
        
    raw_events = query.all()
    # Tự động ẩn sự kiện sau 10 phút kể từ lúc hết thời gian mua vé
    events = [ev for ev in raw_events if not ev.is_hidden_after_closure]
    
    # Lọc theo trạng thái bán vé
    if status_filter == "OPEN":
        events = [ev for ev in events if not ev.is_sales_closed]
    elif status_filter == "CLOSING_SOON":
        events = [ev for ev in events if not ev.is_sales_closed and ev.minutes_until_close <= 1440]
    elif status_filter == "CLOSED":
        events = [ev for ev in events if ev.is_sales_closed]
        
    # Lọc theo mức giá vé
    if price_range != "ALL":
        filtered = []
        for ev in events:
            min_price = min([t.price for t in ev.tiers]) if ev.tiers else 0
            if price_range == "FREE" and min_price == 0:
                filtered.append(ev)
            elif price_range == "UNDER_300K" and min_price <= 300000:
                filtered.append(ev)
            elif price_range == "OVER_300K" and min_price > 300000:
                filtered.append(ev)
        events = filtered

    # Sắp xếp theo giá vé
    if sort_by == "PRICE_ASC":
        events.sort(key=lambda ev: min([t.price for t in ev.tiers]) if ev.tiers else 0)
    elif sort_by == "PRICE_DESC":
        events.sort(key=lambda ev: min([t.price for t in ev.tiers]) if ev.tiers else 0, reverse=True)
        
    # Đếm số lượng tiêu chí lọc đang được áp dụng
    active_filters_count = 0
    if category != "ALL": active_filters_count += 1
    if status_filter != "ALL": active_filters_count += 1
    if price_range != "ALL": active_filters_count += 1
    if location_filter != "ALL": active_filters_count += 1
    if sort_by != "TIME_ASC": active_filters_count += 1

    # Phân trang: Mỗi trang hiển thị 12 sự kiện/hội thảo theo yêu cầu
    import math
    PAGE_SIZE = 12
    total_events = len(events)
    total_pages = max(1, math.ceil(total_events / PAGE_SIZE))

    try:
        page = int(page)
    except (ValueError, TypeError):
        page = 1

    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    start_idx = (page - 1) * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    paged_events = events[start_idx:end_idx]

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "events": paged_events,
            "total_events": total_events,
            "page": page,
            "total_pages": total_pages,
            "page_size": PAGE_SIZE,
            "keyword": keyword,
            "category": category,
            "status_filter": status_filter,
            "price_range": price_range,
            "location_filter": location_filter,
            "sort_by": sort_by,
            "active_filters_count": active_filters_count,
            "current_user": current_user
        }
    )

@router.get("/events/{event_id}", response_class=HTMLResponse)
def event_detail_page(
    event_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Trang chi tiết sự kiện và form đặt vé"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Sự kiện không tồn tại")
    
    # Ẩn sự kiện sau 10 phút kể từ lúc hết thời gian mua vé
    # Tự động ẩn sự kiện và chuyển sang màn hình thông báo sự kiện đã đóng & ẩn
    if event.is_hidden_after_closure:
        return templates.TemplateResponse(
            request=request,
            name="event_hidden.html",
            context={
                "event": event,
                "current_user": current_user
            }
        )
    
    return templates.TemplateResponse(
        request=request,
        name="event_detail.html",
        context={
            "event": event,
            "current_user": current_user
        }
    )

@router.get("/booking-success", response_class=HTMLResponse)
def booking_success_page(
    request: Request,
    order_code: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Trang xác nhận đặt vé thành công và biên nhận hóa đơn"""
    order = db.query(Order).filter(Order.order_code == order_code).first()
    return templates.TemplateResponse(
        request=request,
        name="booking_success.html",
        context={
            "order": order,
            "current_user": current_user
        }
    )

@router.get("/booking-cancel", response_class=HTMLResponse)
def booking_cancel_page(
    request: Request,
    order_code: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Trang thông báo hủy hoặc thanh toán không thành công"""
    order = db.query(Order).filter(Order.order_code == order_code).first()
    return templates.TemplateResponse(
        request=request,
        name="booking_cancel.html",
        context={
            "order": order,
            "current_user": current_user
        }
    )

@router.get("/my-tickets", response_class=HTMLResponse)
def my_tickets_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Trang xem danh sách vé cá nhân và xuất mã vé QR"""
    if not current_user:
        return RedirectResponse(url="/login?redirect=/my-tickets")
    
    tickets = db.query(Ticket).filter(Ticket.user_id == current_user.id).order_by(Ticket.created_at.desc()).all()
    return templates.TemplateResponse(
        request=request,
        name="my_tickets.html",
        context={
            "tickets": tickets,
            "current_user": current_user
        }
    )

@router.get("/login", response_class=HTMLResponse)
def login_page(
    request: Request,
    redirect: str = "/",
    current_user: User = Depends(get_current_user_optional)
):
    """Trang đăng nhập"""
    if current_user:
        return RedirectResponse(url=redirect)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"redirect": redirect, "current_user": None}
    )

@router.get("/register", response_class=HTMLResponse)
def register_page(
    request: Request,
    current_user: User = Depends(get_current_user_optional)
):
    """Trang đăng ký tài khoản"""
    if current_user:
        return RedirectResponse(url="/")
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"current_user": None}
    )

@router.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(
    request: Request,
    current_user: User = Depends(get_current_user_optional)
):
    """Trang yêu cầu gửi email đặt lại mật khẩu"""
    if current_user:
        return RedirectResponse(url="/")
    return templates.TemplateResponse(
        request=request,
        name="forgot_password.html",
        context={"current_user": None}
    )

@router.get("/reset-password", response_class=HTMLResponse)
def reset_password_page(
    request: Request,
    token: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Trang nhập mật khẩu mới từ liên kết trong email"""
    from datetime import datetime
    from app.models import PasswordResetToken

    token_valid = False
    error_msg = None
    
    if not token:
        error_msg = "Không tìm thấy mã xác thực đặt lại mật khẩu trong liên kết."
    else:
        reset_record = db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()
        if not reset_record or reset_record.is_used:
            error_msg = "Liên kết đặt lại mật khẩu không hợp lệ hoặc đã được sử dụng trước đó."
        elif datetime.now() > reset_record.expires_at:
            error_msg = "Liên kết đặt lại mật khẩu đã hết hạn sử dụng (quá 30 phút). Vui lòng gửi lại yêu cầu mới."
        else:
            token_valid = True

    return templates.TemplateResponse(
        request=request,
        name="reset_password.html",
        context={
            "token": token,
            "token_valid": token_valid,
            "error_msg": error_msg,
            "current_user": current_user
        }
    )

@router.get("/organizer", response_class=HTMLResponse)
def organizer_portal(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Cổng quản lý của Ban tổ chức"""
    if not current_user or current_user.role not in ["ORGANIZER", "ADMIN"]:
        return RedirectResponse(url="/login?redirect=/organizer")
    
    if current_user.role == "ADMIN":
        my_events = db.query(Event).order_by(Event.id.asc()).all()
    else:
        my_events = db.query(Event).filter(Event.organizer_id == current_user.id).order_by(Event.created_at.desc()).all()
    
    total_revenue_all = 0.0
    total_platform_fee_all = 0.0
    total_net_payout_all = 0.0
    total_tickets_sold_all = 0
    total_orders_all = 0

    for ev in my_events:
        confirmed_orders = [o for o in ev.orders if o.status == 'CONFIRMED']
        event_rev = sum(o.final_amount for o in confirmed_orders)
        event_fee = sum(o.platform_fee or 0.0 for o in confirmed_orders)
        event_net = sum(o.organizer_amount or 0.0 for o in confirmed_orders)
        event_sold = sum(o.quantity for o in confirmed_orders)
        event_checked_in = sum(1 for t in ev.tickets if t.status == 'CHECKED_IN')
        
        total_revenue_all += event_rev
        total_platform_fee_all += event_fee
        total_net_payout_all += event_net
        total_tickets_sold_all += event_sold
        total_orders_all += len(confirmed_orders)
        
        # Gán thuộc tính hỗ trợ render theo từng sự kiện
        ev.total_revenue = event_rev
        ev.total_platform_fee = event_fee
        ev.total_net_payout = event_net
        ev.total_sold = event_sold
        ev.checked_in_count = event_checked_in
        ev.confirmed_orders = confirmed_orders

    event_ids = [e.id for e in my_events]
    recent_orders = db.query(Order).filter(Order.event_id.in_(event_ids)).order_by(Order.created_at.desc()).limit(20).all() if event_ids else []
    
    return templates.TemplateResponse(
        request=request,
        name="organizer.html",
        context={
            "events": my_events,
            "recent_orders": recent_orders,
            "total_revenue_all": total_revenue_all,
            "total_platform_fee_all": total_platform_fee_all,
            "total_net_payout_all": total_net_payout_all,
            "total_tickets_sold_all": total_tickets_sold_all,
            "total_orders_all": total_orders_all,
            "current_user": current_user
        }
    )

@router.get("/checkin-gate", response_class=HTMLResponse)
def checkin_gate_page(
    request: Request,
    event_id: int = 1,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Màn hình Soát vé tại cổng sự kiện"""
    if not current_user or current_user.role not in ["ORGANIZER", "ADMIN"]:
        return RedirectResponse(url="/login?redirect=/checkin-gate")
    
    events = db.query(Event).order_by(Event.id.asc()).all()
    selected_event = db.query(Event).filter(Event.id == event_id).first()
    if not selected_event and events:
        selected_event = events[0]
        event_id = selected_event.id

    total_tickets = 0
    checked_in_tickets = 0
    if selected_event:
        total_tickets = len([t for t in selected_event.tickets if t.status in ['CONFIRMED', 'CHECKED_IN']])
        checked_in_tickets = len([t for t in selected_event.tickets if t.status == 'CHECKED_IN'])

    return templates.TemplateResponse(
        request=request,
        name="checkin.html",
        context={
            "events": events,
            "selected_event": selected_event,
            "current_event_id": event_id,
            "total_tickets": total_tickets,
            "checked_in_tickets": checked_in_tickets,
            "current_user": current_user
        }
    )

@router.get("/admin", response_class=HTMLResponse)
def admin_portal(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Cổng quản trị viên hệ thống"""
    if not current_user or current_user.role != "ADMIN":
        return RedirectResponse(url="/login?redirect=/admin")
    
    all_events = db.query(Event).order_by(Event.id.desc()).all()
    all_users = db.query(User).order_by(User.id.desc()).all()
    all_vouchers = db.query(Voucher).order_by(Voucher.id.desc()).all()
    all_orders = db.query(Order).order_by(Order.id.desc()).limit(100).all()

    total_gross = 0.0
    total_payos = 0.0
    total_wallet = 0.0
    total_platform_fee = 0.0
    total_organizer_payout = 0.0
    total_tickets_platform = db.query(Ticket).count()
    total_checked_in_platform = db.query(Ticket).filter(Ticket.status == "CHECKED_IN").count()

    for o in db.query(Order).filter(Order.status == "CONFIRMED").all():
        total_gross += o.final_amount
        total_platform_fee += (o.platform_fee or 0.0)
        total_organizer_payout += (o.organizer_amount or 0.0)
        if o.payment_method == "VIETQR_PAYOS":
            total_payos += o.final_amount
        else:
            total_wallet += o.final_amount

    for ev in all_events:
        confirmed_orders = [o for o in ev.orders if o.status == 'CONFIRMED']
        ev.total_revenue = sum(o.final_amount for o in confirmed_orders)
        ev.total_sold = sum(o.quantity for o in confirmed_orders)
        ev.checked_in_count = sum(1 for t in ev.tickets if t.status == 'CHECKED_IN')
    
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "events": all_events,
            "users": all_users,
            "vouchers": all_vouchers,
            "orders": all_orders,
            "total_gross": total_gross,
            "total_payos": total_payos,
            "total_wallet": total_wallet,
            "total_platform_fee": total_platform_fee,
            "total_organizer_payout": total_organizer_payout,
            "total_tickets_platform": total_tickets_platform,
            "total_checked_in_platform": total_checked_in_platform,
            "current_user": current_user
        }
    )

@router.get("/quy-dinh-ban-ve", response_class=HTMLResponse)
@router.get("/organizer/terms", response_class=HTMLResponse)
@router.get("/organizer/policy", response_class=HTMLResponse)
def organizer_policy_page(
    request: Request,
    current_user: User = Depends(get_current_user_optional)
):
    """Trang Chính Sách, Biểu Phí Sàn và Quy Định Dành Cho Ban Tổ Chức Sự Kiện"""
    return templates.TemplateResponse(
        request=request,
        name="organizer_policy.html",
        context={"current_user": current_user}
    )

# app/routers/admin.py
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_role, hash_password
from app.database import get_db
from app.models import Event, Order, Ticket, TicketTier, User, Voucher
from app.schemas import (
    EventOut,
    UserRoleUpdate,
    UserPasswordDirectReset,
    UserBalanceAdjust,
    AdminEventUpdate,
    AdminEventStatusUpdate,
    AdminVoucherCreate,
    PlatformFeeConfigUpdate,
)

router = APIRouter(prefix="/api/admin", tags=["Admin Operations"])

DEFAULT_PLATFORM_FEE_RATE = 5.0

class RejectPayload(BaseModel):
    reason: str

@router.get("/events/pending", response_model=List[EventOut])
def get_pending_events(
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """Admin lấy danh sách sự kiện đang chờ duyệt (PENDING_APPROVAL)"""
    return db.query(Event).filter(Event.status == "PENDING_APPROVAL").all()

@router.post("/events/{event_id}/approve")
def approve_event(
    event_id: int,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """Admin phê duyệt sự kiện để mở bán công khai"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Sự kiện không tồn tại")
    
    event.status = "PUBLISHED"
    event.rejection_reason = None
    db.commit()
    return {"success": True, "message": f"Đã phê duyệt sự kiện '{event.title}' thành công!", "event_id": event.id}

@router.post("/events/{event_id}/reject")
def reject_event(
    event_id: int,
    payload: RejectPayload,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """Admin từ chối sự kiện kèm lý do"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Sự kiện không tồn tại")
    
    event.status = "REJECTED"
    event.rejection_reason = payload.reason
    db.commit()
    return {"success": True, "message": f"Đã từ chối sự kiện. Lý do: {payload.reason}", "event_id": event.id}

@router.get("/stats")
def get_platform_stats(
    current_user: User = Depends(require_role(["ADMIN", "ORGANIZER"])),
    db: Session = Depends(get_db)
):
    """Lấy dữ liệu thống kê doanh thu và vé toàn hệ thống hoặc theo ban tổ chức"""
    if current_user.role == "ADMIN":
        total_users = db.query(User).count()
        total_events = db.query(Event).count()
        total_orders = db.query(Order).count()
        total_tickets = db.query(Ticket).count()
        checked_in_tickets = db.query(Ticket).filter(Ticket.status == "CHECKED_IN").count()
        cancelled_tickets = db.query(Ticket).filter(Ticket.status == "CANCELLED").count()
        
        gross_revenue = db.query(func.sum(Order.final_amount)).filter(Order.status == "CONFIRMED").scalar() or 0.0
        payos_revenue = db.query(func.sum(Order.final_amount)).filter(Order.status == "CONFIRMED", Order.payment_method == "VIETQR_PAYOS").scalar() or 0.0
        wallet_revenue = db.query(func.sum(Order.final_amount)).filter(Order.status == "CONFIRMED", Order.payment_method == "WALLET").scalar() or 0.0
        total_platform_fee = db.query(func.sum(Order.platform_fee)).filter(Order.status == "CONFIRMED").scalar() or 0.0
        total_organizer_payout = db.query(func.sum(Order.organizer_amount)).filter(Order.status == "CONFIRMED").scalar() or 0.0
    else:
        # Organizer chỉ xem sự kiện của mình
        my_event_ids = [e.id for e in current_user.events]
        total_users = 0
        total_events = len(my_event_ids)
        total_orders = db.query(Order).filter(Order.event_id.in_(my_event_ids)).count()
        total_tickets = db.query(Ticket).filter(Ticket.event_id.in_(my_event_ids)).count()
        checked_in_tickets = db.query(Ticket).filter(Ticket.event_id.in_(my_event_ids), Ticket.status == "CHECKED_IN").count()
        cancelled_tickets = db.query(Ticket).filter(Ticket.event_id.in_(my_event_ids), Ticket.status == "CANCELLED").count()
        gross_revenue = db.query(func.sum(Order.final_amount)).filter(Order.event_id.in_(my_event_ids), Order.status == "CONFIRMED").scalar() or 0.0
        payos_revenue = db.query(func.sum(Order.final_amount)).filter(Order.event_id.in_(my_event_ids), Order.status == "CONFIRMED", Order.payment_method == "VIETQR_PAYOS").scalar() or 0.0
        wallet_revenue = db.query(func.sum(Order.final_amount)).filter(Order.event_id.in_(my_event_ids), Order.status == "CONFIRMED", Order.payment_method == "WALLET").scalar() or 0.0
        total_platform_fee = db.query(func.sum(Order.platform_fee)).filter(Order.event_id.in_(my_event_ids), Order.status == "CONFIRMED").scalar() or 0.0
        total_organizer_payout = db.query(func.sum(Order.organizer_amount)).filter(Order.event_id.in_(my_event_ids), Order.status == "CONFIRMED").scalar() or 0.0

    return {
        "total_users": total_users,
        "total_events": total_events,
        "total_orders": total_orders,
        "total_tickets": total_tickets,
        "checked_in_tickets": checked_in_tickets,
        "cancelled_tickets": cancelled_tickets,
        "gross_revenue": gross_revenue,
        "payos_revenue": payos_revenue,
        "wallet_revenue": wallet_revenue,
        "total_platform_fee": total_platform_fee,
        "total_organizer_payout": total_organizer_payout,
        "checkin_rate": f"{(checked_in_tickets / total_tickets * 100):.1f}%" if total_tickets > 0 else "0.0%"
    }

# ==========================================
# 1. QUẢN TRỊ NGƯỜI DÙNG & PHÂN QUYỀN (RBAC)
# ==========================================
@router.post("/users/{user_id}/toggle-active")
def toggle_user_active(
    user_id: int,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """Admin khóa hoặc mở khóa tài khoản người dùng"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Không thể tự khóa tài khoản của chính mình")
    
    user.is_active = not user.is_active
    db.commit()
    status_str = "kích hoạt" if user.is_active else "tạm khóa"
    return {"success": True, "message": f"Tài khoản {user.email} đã được {status_str}", "is_active": user.is_active}

@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """Admin thăng/hạ cấp vai trò (ATTENDEE, ORGANIZER, ADMIN)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Không thể tự thay đổi vai trò của chính mình")
    
    user.role = payload.role
    db.commit()
    role_names = {"ADMIN": "Quản trị viên", "ORGANIZER": "Ban tổ chức", "ATTENDEE": "Khách hàng"}
    return {"success": True, "message": f"Đã chuyển vai trò tài khoản {user.email} thành '{role_names.get(user.role, user.role)}'", "role": user.role}

@router.post("/users/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    payload: UserPasswordDirectReset,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """Admin đặt lại mật khẩu trực tiếp cho tài khoản người dùng"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    
    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    return {"success": True, "message": f"Đã cấp lại mật khẩu mới cho tài khoản {user.email} thành công!"}

@router.post("/users/{user_id}/adjust-balance")
def adjust_user_balance(
    user_id: int,
    payload: UserBalanceAdjust,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """Admin điều chỉnh cộng hoặc trừ số dư ví của tài khoản"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
    
    new_balance = user.balance + payload.amount
    if new_balance < 0:
        raise HTTPException(status_code=400, detail="Số dư sau khi trừ không thể là số âm")
    
    user.balance = new_balance
    db.commit()
    sign = "+" if payload.amount >= 0 else ""
    return {
        "success": True,
        "message": f"Đã điều chỉnh số dư ví của {user.email}: {sign}{payload.amount:,.0f}đ (Số dư hiện tại: {user.balance:,.0f}đ)",
        "balance": user.balance
    }

# ==========================================
# 2. QUẢN TRỊ SỰ KIỆN TOÀN SÀN (EVENTS OVERRIDE)
# ==========================================
@router.put("/events/{event_id}")
def admin_update_event(
    event_id: int,
    payload: AdminEventUpdate,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """Admin chỉnh sửa thông tin bất kỳ sự kiện nào trên hệ thống"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Sự kiện không tồn tại")
    
    if payload.title is not None and payload.title.strip():
        event.title = payload.title.strip()
    if payload.description is not None and payload.description.strip():
        event.description = payload.description.strip()
    if payload.location is not None and payload.location.strip():
        event.location = payload.location.strip()
    if payload.banner_url is not None:
        event.banner_url = payload.banner_url
    if payload.category is not None:
        event.category = payload.category
    if payload.capacity is not None and payload.capacity > 0:
        event.capacity = payload.capacity
    if payload.start_time is not None:
        event.start_time = payload.start_time
    if payload.end_time is not None:
        event.end_time = payload.end_time
    
    db.commit()
    return {"success": True, "message": f"Admin đã cập nhật sự kiện #{event.id} ({event.title}) thành công!", "event_id": event.id}

@router.post("/events/{event_id}/status")
def admin_change_event_status(
    event_id: int,
    payload: AdminEventStatusUpdate,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """Admin can thiệp đổi trạng thái sự kiện (PUBLISHED, CANCELLED, REJECTED)"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Sự kiện không tồn tại")
    
    event.status = payload.status
    if payload.reason:
        event.rejection_reason = payload.reason
    db.commit()
    return {"success": True, "message": f"Đã chuyển trạng thái sự kiện #{event.id} sang '{payload.status}'", "status": event.status}

@router.delete("/events/{event_id}")
def admin_delete_event(
    event_id: int,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """Admin xóa vĩnh viễn sự kiện vi phạm hoặc rác"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Sự kiện không tồn tại")
    
    ev_title = event.title
    db.delete(event)
    db.commit()
    return {"success": True, "message": f"Đã xóa hoàn toàn sự kiện '{ev_title}' (ID #{event_id})"}

# ==========================================
# 3. QUẢN LÝ GIAO DỊCH & VÉ (ORDERS & TICKETS)
# ==========================================
@router.get("/orders")
def get_all_orders(
    limit: int = 50,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """Admin lấy danh sách tất cả giao dịch đặt vé toàn sàn"""
    orders = db.query(Order).order_by(Order.id.desc()).limit(limit).all()
    result = []
    for o in orders:
        result.append({
            "id": o.id,
            "order_code": o.order_code,
            "buyer_name": o.user.full_name if o.user else "Khách vãng lai",
            "buyer_email": o.user.email if o.user else "",
            "event_id": o.event_id,
            "event_title": o.event.title if o.event else "N/A",
            "tier_name": o.tier.name if o.tier else "N/A",
            "quantity": o.quantity,
            "final_amount": o.final_amount,
            "payment_method": o.payment_method,
            "status": o.status,
            "created_at": o.created_at.strftime("%d/%m/%Y %H:%M")
        })
    return result

@router.post("/orders/{order_id}/cancel-refund")
def admin_cancel_order(
    order_id: int,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """Admin hủy đơn khẩn cấp, hoàn vé vào kho và đổi trạng thái vé sang CANCELLED"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại")
    if order.status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Đơn hàng này đã bị hủy trước đó")
    
    order.status = "CANCELLED"
    order.payment_status = "REFUNDED"
    # Hoàn lại số lượng vé vào kho hạng vé
    if order.tier:
        order.tier.available_quantity += order.quantity
    
    # Hủy toàn bộ mã vé điện tử của đơn hàng
    for t in order.tickets:
        t.status = "CANCELLED"
    
    # Đối soát hoàn tiền:
    # 1. Hoàn lại 100% số tiền thực trả (final_amount) cho người mua
    refunded_str = ""
    if order.user and order.final_amount > 0:
        order.user.balance += order.final_amount
        refunded_str += f", hoàn lại {order.final_amount:,.0f}đ vào ví người mua"
    
    # 2. Khấu trừ lại doanh thu Net (organizer_amount) từ ví của Ban tổ chức sự kiện
    if order.event and order.event.organizer and (order.organizer_amount or 0) > 0:
        order.event.organizer.balance = max(0.0, order.event.organizer.balance - order.organizer_amount)
        refunded_str += f", thu hồi {order.organizer_amount:,.0f}đ từ ví ban tổ chức"
    
    db.commit()
    return {
        "success": True,
        "message": f"Đã hủy đơn hàng {order.order_code}, hoàn {order.quantity} vé vào kho{refunded_str} thành công!"
    }

@router.get("/tickets")
def search_tickets(
    code: Optional[str] = None,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """Admin tra cứu mã vé điện tử toàn sàn"""
    q = db.query(Ticket)
    if code and code.strip():
        q = q.filter(Ticket.ticket_code.ilike(f"%{code.strip()}%"))
    tickets = q.order_by(Ticket.id.desc()).limit(50).all()
    return [{
        "id": t.id,
        "ticket_code": t.ticket_code,
        "event_id": t.event_id,
        "event_title": t.event.title if t.event else "N/A",
        "tier_name": t.tier.name if t.tier else "N/A",
        "status": t.status,
        "check_in_time": t.check_in_time.strftime("%d/%m/%Y %H:%M") if t.check_in_time else None,
        "created_at": t.created_at.strftime("%d/%m/%Y %H:%M")
    } for t in tickets]

# ==========================================
# 4. QUẢN LÝ MÃ GIẢM GIÁ (VOUCHERS)
# ==========================================
@router.post("/vouchers")
def create_admin_voucher(
    payload: AdminVoucherCreate,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """Admin tạo mã voucher toàn sàn"""
    vcode = payload.code.strip().upper()
    existing = db.query(Voucher).filter(Voucher.code == vcode).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Mã voucher '{vcode}' đã tồn tại")
    
    voucher = Voucher(
        code=vcode,
        discount_type=payload.discount_type,
        discount_value=payload.discount_value,
        max_discount_cap=payload.max_discount_cap,
        min_order_value=payload.min_order_value,
        total_uses=payload.total_uses,
        remaining_uses=payload.total_uses,
        is_active=True,
        end_date=payload.expires_at or (datetime.now() + timedelta(days=90))
    )
    db.add(voucher)
    db.commit()
    return {"success": True, "message": f"Đã khởi tạo voucher '{vcode}' thành công!", "id": voucher.id}

@router.post("/vouchers/{voucher_id}/toggle")
def toggle_voucher(
    voucher_id: int,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """Admin bật hoặc tắt hiệu lực của mã voucher"""
    voucher = db.query(Voucher).filter(Voucher.id == voucher_id).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher không tồn tại")
    
    voucher.is_active = not voucher.is_active
    db.commit()
    state = "kích hoạt" if voucher.is_active else "tạm ngưng"
    return {"success": True, "message": f"Mã {voucher.code} đã được {state}", "is_active": voucher.is_active}

@router.delete("/vouchers/{voucher_id}")
def delete_voucher(
    voucher_id: int,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """Admin xóa mã voucher khỏi hệ thống"""
    voucher = db.query(Voucher).filter(Voucher.id == voucher_id).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher không tồn tại")
    
    code = voucher.code
    db.delete(voucher)
    db.commit()
    return {"success": True, "message": f"Đã xóa voucher '{code}' thành công"}

# ==========================================
# 5. CẤU HÌNH TỶ LỆ PHÍ NỀN TẢNG (PLATFORM FEE)
# ==========================================
@router.get("/system/fee")
def get_system_fee(current_user: User = Depends(require_role(["ADMIN"]))):
    """Admin xem tỷ lệ phí sàn hiện tại"""
    return {
        "fee_rate": DEFAULT_PLATFORM_FEE_RATE,
        "description": "Tỷ lệ phí dịch vụ nền tảng iTick thu trên mỗi vé bán ra"
    }

@router.put("/system/fee")
def update_system_fee(
    payload: PlatformFeeConfigUpdate,
    current_user: User = Depends(require_role(["ADMIN"]))
):
    """Admin cập nhật tỷ lệ phí dịch vụ toàn sàn (0% đến 50%)"""
    global DEFAULT_PLATFORM_FEE_RATE
    DEFAULT_PLATFORM_FEE_RATE = payload.fee_rate
    return {
        "success": True,
        "fee_rate": DEFAULT_PLATFORM_FEE_RATE,
        "message": f"Đã cập nhật mức phí dịch vụ nền tảng iTick thành {DEFAULT_PLATFORM_FEE_RATE}%"
    }


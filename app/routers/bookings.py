# app/routers/bookings.py
import os
import secrets
import time
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Event, Order, Ticket, TicketTier, User, Voucher
from app.schemas import (
    BookingCreate,
    OrderOut,
    TicketOut,
    VoucherApplyRequest,
    VoucherApplyResponse,
)
from app.services.payos_service import create_vietqr_payment_link

router = APIRouter(prefix="/api/bookings", tags=["Bookings & Orders"])

@router.post("/vouchers/apply", response_model=VoucherApplyResponse)
def apply_voucher(req: VoucherApplyRequest, db: Session = Depends(get_db)):
    """
    Kiểm tra và tính toán mã giảm giá.
    CHỨA LỖI CÀI SẴN:
    - SEED-10: Báo sai nội dung copy-paste nhầm: 'Mật khẩu tài khoản không đúng, vui lòng thử lại'
    """
    vcode = req.code.strip().upper()
    voucher = db.query(Voucher).filter(Voucher.code == vcode).first()

    # === SEED-10: BUG NỘI DUNG / CHÍNH TẢ COPY-PASTE NHẦM ===
    if not voucher or not voucher.is_active or voucher.remaining_uses <= 0:
        return {
            "is_valid": False,
            "message": "Mật khẩu tài khoản không đúng, vui lòng thử lại",  # Lỗi nội dung copy-paste sai
            "discount_amount": 0.0,
            "final_amount": req.order_total
        }
    
    if req.order_total < voucher.min_order_value:
        return {
            "is_valid": False,
            "message": f"Đơn hàng chưa đạt giá trị tối thiểu {voucher.min_order_value:,.0f} VNĐ",
            "discount_amount": 0.0,
            "final_amount": req.order_total
        }
    
    # Tính chiết khấu
    if voucher.discount_type == "PERCENT":
        discount = req.order_total * (voucher.discount_value / 100.0)
        # === SEED-02: BỎ SÓT CHẶN TRẦN max_discount_cap ===
        # Lẽ ra phải có: if voucher.max_discount_cap and discount > voucher.max_discount_cap: discount = voucher.max_discount_cap
    else:
        discount = voucher.discount_value
    
    discount = min(discount, req.order_total)
    final = max(0.0, req.order_total - discount)

    return {
        "is_valid": True,
        "message": f"Áp dụng thành công mã {voucher.code}! Giảm {discount:,.0f} VNĐ",
        "discount_amount": discount,
        "final_amount": final
    }


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    request: Request,
    booking_in: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Đặt mua vé sự kiện trực tuyến.
    CHỨA LỖI CÀI SẴN:
    - SEED-01: Race condition bán vượt vé (Overselling) khi nhiều luồng JMeter mua cùng lúc
    - SEED-02: Không áp trần giảm giá tối đa của voucher
    - SEED-04: Cho phép đặt số lượng 0 vé (tạo đơn hàng 0đ với 0 vé)
    - SEED-14: Crash 500 Unhandled Exception khi voucher_code chứa ký tự nháy đơn "'"
    """
    # === SEED-14: BUG CRASH 500 KHI VOUCHER CHỨA DẤU NHÁY ĐƠN ===
    if booking_in.voucher_code and "'" in booking_in.voucher_code:
        # Code tách chuỗi không an toàn, truy cập vượt độ dài gây IndexError -> Sập 500!
        parts = booking_in.voucher_code.split("'")
        trigger = parts[5]  # Sẽ ném IndexError: list index out of range khi có ít hơn 5 dấu nháy

    # === SEED-04: BUG GIÁ TRỊ BIÊN CHO PHÉP ĐẶT 0 VÉ ===
    # Lẽ ra: if booking_in.quantity < 1 or booking_in.quantity > 5:
    if booking_in.quantity < 0 or booking_in.quantity > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Số lượng vé mỗi đơn hàng phải từ 1 đến 5 vé"
        )
    # Lưu ý: nếu booking_in.quantity == 0, điều kiện trên lọt qua và cho phép tạo đơn!

    event = db.query(Event).filter(Event.id == booking_in.event_id).first()
    if not event or event.status != "PUBLISHED":
        raise HTTPException(status_code=400, detail="Sự kiện không tồn tại hoặc chưa mở bán")

    # Kiểm tra thời hạn đóng mua vé
    if event.is_sales_closed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sự kiện này đã hết thời gian mua vé. Cổng bán vé đã chính thức đóng."
        )

    tier = db.query(TicketTier).filter(TicketTier.id == booking_in.tier_id).first()
    if not tier or tier.event_id != event.id:
        raise HTTPException(status_code=400, detail="Hạng vé không tồn tại trong sự kiện này")

    # === SEED-01: BUG CONCURRENCY / RACE CONDITION BÁN VƯỢT VÉ CHO JMETER ===
    # Kiểm tra tồn kho trước
    if tier.available_quantity < booking_in.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Số lượng vé trong kho không đủ để đáp ứng yêu cầu"
        )

    # Chèn delay cố tình để tạo Race Window (Cửa sổ tranh chấp) cho 50 luồng JMeter
    time.sleep(0.06)

    # Tính tiền gốc
    original_total = tier.price * booking_in.quantity
    discount_amount = 0.0

    # === SEED-02: BUG BỎ QUA TRẦN GIẢM GIÁ VOUCHER (max_discount_cap) ===
    if booking_in.voucher_code:
        vcode = booking_in.voucher_code.strip().upper()
        voucher = db.query(Voucher).filter(Voucher.code == vcode).first()
        if voucher and voucher.is_active and voucher.remaining_uses > 0 and original_total >= voucher.min_order_value:
            if voucher.discount_type == "PERCENT":
                # Lỗi: Tính thẳng % mà không gán discount_amount = min(discount_amount, voucher.max_discount_cap)
                discount_amount = original_total * (voucher.discount_value / 100.0)
            else:
                discount_amount = voucher.discount_value
            voucher.remaining_uses -= 1

    final_total = max(0.0, original_total - discount_amount)

    # === TÍNH PHÍ DỊCH VỤ NỀN TẢNG (PLATFORM FEE) VÀ DOANH THU BAN TỔ CHỨC ===
    # Tỷ lệ phí nền tảng mặc định 5% (hoặc cấu hình động từ Admin)
    try:
        from app.routers.admin import DEFAULT_PLATFORM_FEE_RATE
        platform_fee_rate = float(DEFAULT_PLATFORM_FEE_RATE)
    except Exception:
        platform_fee_rate = 5.0
    # Làm tròn chuẩn VND không số thập phân: round(val)
    platform_fee = round(final_total * (platform_fee_rate / 100.0))
    # Bất biến bảo toàn dòng tiền: organizer_amount + platform_fee == final_total
    organizer_amount = max(0.0, final_total - platform_fee)

    # Trừ tồn kho mà KHÔNG có database lock / atomic update -> Khiến số lượng bị âm khi test tải!
    tier.available_quantity -= booking_in.quantity

    now = datetime.now()
    order_code = f"ORD-{secrets.token_hex(4).upper()}"
    method = (booking_in.payment_method or "WALLET").upper()

    # === THANH TOÁN VIETQR PAYOS (NGÂN HÀNG THẬT) ===
    if method == "VIETQR_PAYOS" and final_total > 0:
        payos_order_code = int(time.time() * 100) % 90000000 + 10000000
        # Xác định Base URL tự động (hỗ trợ cả domain Render/Cloud và localhost:8001)
        base_url = os.environ.get("APP_BASE_URL")
        if not base_url:
            proto = request.headers.get("x-forwarded-proto") or request.url.scheme
            host = request.headers.get("x-forwarded-host") or request.headers.get("host")
            if host:
                base_url = f"{proto}://{host}"
            else:
                port = os.environ.get("PORT", "8001")
                base_url = f"http://127.0.0.1:{port}"
        base_url = base_url.rstrip("/")

        return_url = f"{base_url}/api/payment/payos-return?order_code={order_code}&payos_code={payos_order_code}"
        cancel_url = f"{base_url}/api/payment/payos-cancel?order_code={order_code}&payos_code={payos_order_code}"

        payos_res = create_vietqr_payment_link(
            order_code_int=payos_order_code,
            amount=int(final_total),
            description=f"Ve {payos_order_code}",
            return_url=return_url,
            cancel_url=cancel_url,
            item_name=f"{event.title} - {tier.name}",
            quantity=booking_in.quantity
        )

        if not payos_res.get("success"):
            # Rollback lại số lượng tồn kho vé
            tier.available_quantity += booking_in.quantity
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Không thể khởi tạo cổng thanh toán PayOS: {payos_res.get('error')}"
            )

        new_order = Order(
            order_code=order_code,
            user_id=current_user.id,
            event_id=event.id,
            tier_id=tier.id,
            quantity=booking_in.quantity,
            voucher_code=booking_in.voucher_code,
            original_amount=original_total,
            discount_amount=discount_amount,
            final_amount=final_total,
            platform_fee_rate=platform_fee_rate,
            platform_fee=platform_fee,
            organizer_amount=organizer_amount,
            status="PENDING_PAYMENT",
            payment_method="VIETQR_PAYOS",
            payment_status="PENDING",
            payos_order_code=payos_order_code,
            payos_payment_link_id=payos_res.get("payment_link_id"),
            checkout_url=payos_res.get("checkout_url"),
            created_at=now
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        new_order.tickets = []
        return new_order

    # === THANH TOÁN VÍ NỘI BỘ (HOẶC VÉ MIỄN PHÍ 0Đ / UNIT TESTS / JMETER) ===
    if current_user.balance < final_total:
        raise HTTPException(status_code=400, detail="Số dư tài khoản không đủ để thanh toán")
    current_user.balance -= final_total

    # Tự động ghi nhận doanh thu thực nhận vào số dư ví của Ban tổ chức sự kiện
    if event.organizer and organizer_amount > 0:
        event.organizer.balance += organizer_amount

    new_order = Order(
        order_code=order_code,
        user_id=current_user.id,
        event_id=event.id,
        tier_id=tier.id,
        quantity=booking_in.quantity,
        voucher_code=booking_in.voucher_code,
        original_amount=original_total,
        discount_amount=discount_amount,
        final_amount=final_total,
        platform_fee_rate=platform_fee_rate,
        platform_fee=platform_fee,
        organizer_amount=organizer_amount,
        status="CONFIRMED",
        payment_method="WALLET",
        payment_status="PAID",
        created_at=now
    )
    db.add(new_order)
    db.flush()

    # Cấp các vé điện tử
    created_tickets = []
    for _ in range(booking_in.quantity):
        t_code = f"TICK-2026-{secrets.token_hex(4).upper()}"
        ticket = Ticket(
            ticket_code=t_code,
            order_id=new_order.id,
            event_id=event.id,
            tier_id=tier.id,
            user_id=current_user.id,
            status="CONFIRMED",
            created_at=now
        )
        db.add(ticket)
        created_tickets.append(ticket)

    db.commit()
    db.refresh(new_order)
    new_order.tickets = created_tickets
    return new_order


@router.get("/my-tickets", response_model=List[TicketOut])
def get_my_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lấy danh sách các vé thuộc sở hữu của người dùng đang đăng nhập"""
    tickets = db.query(Ticket).filter(Ticket.user_id == current_user.id).order_by(Ticket.created_at.desc()).all()
    return tickets


@router.post("/{ticket_id}/cancel")
def cancel_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Yêu cầu hủy vé và hoàn lại tiền theo chính sách.
    CHỨA LỖI CÀI SẴN:
    - SEED-03: Cho phép hủy vé sát giờ sự kiện (< 24 giờ), vi phạm SRS Use Case 04
    """
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Vé không tồn tại")

    if ticket.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Bạn không sở hữu vé này")

    if ticket.status != "CONFIRMED":
        raise HTTPException(status_code=400, detail=f"Không thể hủy vé đang ở trạng thái {ticket.status}")

    event = db.query(Event).filter(Event.id == ticket.event_id).first()
    tier = db.query(TicketTier).filter(TicketTier.id == ticket.tier_id).first()

    # === SEED-03: BUG CHO PHÉP HỦY VÉ SÁT GIỜ < 24H ===
    # Lẽ ra phải có:
    # delta_hours = (event.start_time - datetime.utcnow()).total_seconds() / 3600
    # if delta_hours < 24:
    #     raise HTTPException(status_code=400, detail="Không thể hủy vé trước sự kiện dưới 24 giờ")
    # Nhưng code bị bỏ qua đoạn check trên, luôn tính hoàn tiền 90%!

    refund_amount = tier.price * 0.9  # Hoàn 90%
    current_user.balance += refund_amount
    ticket.status = "CANCELLED"
    tier.available_quantity += 1

    db.commit()
    return {
        "success": True,
        "message": f"Hủy vé thành công! Đã hoàn lại {refund_amount:,.0f} VNĐ (90% giá vé) vào tài khoản.",
        "ticket_code": ticket.ticket_code,
        "refund_amount": refund_amount
    }

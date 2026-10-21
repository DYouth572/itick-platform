# app/routers/payment.py
import logging
import secrets
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order, Ticket, TicketTier
from app.services.payos_service import get_payment_link_status, get_payos_client

logger = logging.getLogger("eventtick.payment")

router = APIRouter(prefix="/api/payment", tags=["Payment Integration"])


@router.get("/payos-return")
def payos_return(
    request: Request,
    order_code: Optional[str] = None,
    payos_code: Optional[int] = None,
    orderCode: Optional[int] = None,
    code: Optional[str] = None,
    id: Optional[str] = None,
    cancel: Optional[bool] = False,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Điểm đón (Return URL) khi người dùng hoàn tất hoặc hủy thanh toán trên cổng VietQR PayOS.
    """
    # Tìm kiếm đơn hàng tương ứng
    order = None
    if order_code:
        order = db.query(Order).filter(Order.order_code == order_code).first()
    if not order and (payos_code or orderCode):
        target_pcode = payos_code or orderCode
        order = db.query(Order).filter(Order.payos_order_code == target_pcode).first()
    if not order and id:
        order = db.query(Order).filter(Order.payos_payment_link_id == id).first()

    if not order:
        logger.warning(f"Không tìm thấy đơn hàng khi PayOS redirect về: order_code={order_code}, orderCode={orderCode}")
        return RedirectResponse(url="/my-tickets")

    # Nếu đơn hàng đã hoàn tất trước đó
    if order.status == "CONFIRMED" and order.payment_status == "PAID":
        return RedirectResponse(url=f"/booking-success?order_code={order.order_code}")

    # Xử lý trường hợp người dùng bấm Hủy trên giao diện PayOS
    if cancel or status == "CANCELLED" or (code and code != "00"):
        logger.info(f"Đơn hàng {order.order_code} bị hủy giao dịch trên PayOS.")
        order.status = "CANCELLED"
        order.payment_status = "CANCELLED"
        
        # Hoàn lại số lượng vé vào kho
        tier = db.query(TicketTier).filter(TicketTier.id == order.tier_id).first()
        if tier:
            tier.available_quantity += order.quantity

        db.commit()
        return RedirectResponse(url=f"/booking-cancel?order_code={order.order_code}")

    # Xác thực trạng thái giao dịch thực tế từ máy chủ PayOS
    payos_check = get_payment_link_status(order.payos_order_code or order.payos_payment_link_id)
    payos_status = payos_check.get("status") if payos_check else None

    # Điều kiện thành công: PayOS API trả về PAID hoặc param code='00'
    if payos_status == "PAID" or code == "00" or status == "PAID":
        logger.info(f"Thanh toán VietQR PayOS THÀNH CÔNG cho đơn {order.order_code} (PayOS Code: {order.payos_order_code})")
        order.payment_status = "PAID"
        order.status = "CONFIRMED"

        # Tự động cộng doanh thu thực nhận vào số dư ví của Ban tổ chức
        if order.event and order.event.organizer and (order.organizer_amount or 0) > 0:
            order.event.organizer.balance += order.organizer_amount

        # Cấp các vé điện tử nếu chưa có
        existing_tickets = db.query(Ticket).filter(Ticket.order_id == order.id).all()
        if not existing_tickets:
            now = datetime.now()
            for _ in range(order.quantity):
                t_code = f"TICK-2026-{secrets.token_hex(4).upper()}"
                ticket = Ticket(
                    ticket_code=t_code,
                    order_id=order.id,
                    event_id=order.event_id,
                    tier_id=order.tier_id,
                    user_id=order.user_id,
                    status="CONFIRMED",
                    created_at=now
                )
                db.add(ticket)

        db.commit()
        return RedirectResponse(url=f"/booking-success?order_code={order.order_code}")

    # Nếu vẫn đang PENDING
    return RedirectResponse(url=f"/booking-success?order_code={order.order_code}")


@router.get("/payos-cancel")
def payos_cancel(
    order_code: Optional[str] = None,
    payos_code: Optional[int] = None,
    orderCode: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Điểm đón khi người dùng bấm Hủy thanh toán tại PayOS.
    """
    order = None
    if order_code:
        order = db.query(Order).filter(Order.order_code == order_code).first()
    if not order and (payos_code or orderCode):
        target_pcode = payos_code or orderCode
        order = db.query(Order).filter(Order.payos_order_code == target_pcode).first()

    if order and order.status != "CONFIRMED":
        order.status = "CANCELLED"
        order.payment_status = "CANCELLED"
        tier = db.query(TicketTier).filter(TicketTier.id == order.tier_id).first()
        if tier:
            tier.available_quantity += order.quantity
        db.commit()
        return RedirectResponse(url=f"/booking-cancel?order_code={order.order_code}")

    return RedirectResponse(url="/my-tickets")


@router.post("/payos-webhook")
async def payos_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Tiếp nhận Webhook tức thì từ PayOS khi có giao dịch thanh toán thành công.
    """
    try:
        body = await request.json()
        client = get_payos_client()
        # Xác thực chữ ký số Webhook từ PayOS
        webhook_data = client.verifyPaymentWebhookData(body)

        p_order_code = webhook_data.get("orderCode")
        logger.info(f"Nhận PayOS Webhook cho orderCode={p_order_code}")

        order = db.query(Order).filter(Order.payos_order_code == p_order_code).first()
        if order and order.status != "CONFIRMED":
            order.status = "CONFIRMED"
            order.payment_status = "PAID"

            # Tự động cộng doanh thu thực nhận vào ví của Ban tổ chức
            if order.event and order.event.organizer and (order.organizer_amount or 0) > 0:
                order.event.organizer.balance += order.organizer_amount

            existing_tickets = db.query(Ticket).filter(Ticket.order_id == order.id).all()
            if not existing_tickets:
                now = datetime.now()
                for _ in range(order.quantity):
                    t_code = f"TICK-2026-{secrets.token_hex(4).upper()}"
                    ticket = Ticket(
                        ticket_code=t_code,
                        order_id=order.id,
                        event_id=order.event_id,
                        tier_id=order.tier_id,
                        user_id=order.user_id,
                        status="CONFIRMED",
                        created_at=now
                    )
                    db.add(ticket)

            db.commit()

        return {"success": True}
    except Exception as e:
        logger.error(f"Lỗi xử lý PayOS webhook: {e}")
        return {"success": False, "error": str(e)}


@router.get("/status/{order_code}")
def check_order_payment_status(order_code: str, db: Session = Depends(get_db)):
    """
    API kiểm tra trạng thái thanh toán của đơn hàng (dùng cho polling).
    """
    order = db.query(Order).filter(Order.order_code == order_code).first()
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại")

    # Nếu đang PENDING, thử sync lại với PayOS
    if order.payment_status == "PENDING" and order.payos_order_code:
        payos_check = get_payment_link_status(order.payos_order_code)
        if payos_check and payos_check.get("status") == "PAID":
            order.payment_status = "PAID"
            order.status = "CONFIRMED"

            # Tự động cộng doanh thu thực nhận vào ví của Ban tổ chức
            if order.event and order.event.organizer and (order.organizer_amount or 0) > 0:
                order.event.organizer.balance += order.organizer_amount

            existing_tickets = db.query(Ticket).filter(Ticket.order_id == order.id).all()
            if not existing_tickets:
                now = datetime.now()
                for _ in range(order.quantity):
                    t_code = f"TICK-2026-{secrets.token_hex(4).upper()}"
                    ticket = Ticket(
                        ticket_code=t_code,
                        order_id=order.id,
                        event_id=order.event_id,
                        tier_id=order.tier_id,
                        user_id=order.user_id,
                        status="CONFIRMED",
                        created_at=now
                    )
                    db.add(ticket)
            db.commit()

    return {
        "order_code": order.order_code,
        "status": order.status,
        "payment_status": order.payment_status,
        "payment_method": order.payment_method
    }

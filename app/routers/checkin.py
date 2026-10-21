# app/routers/checkin.py
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_role
from app.database import get_db
from app.models import Event, Ticket, TicketTier, User
from app.schemas import CheckinRequest, CheckinResponse

router = APIRouter(prefix="/api/check-in", tags=["Gate Check-in"])

@router.post("", response_model=CheckinResponse)
def verify_and_checkin(
    req: CheckinRequest,
    current_user: User = Depends(require_role(["ORGANIZER", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Xác thực và soát vé khách tham dự tại cổng sự kiện.
    CHỨA LỖI CÀI SẴN:
    - SEED-05: Cho phép check-in vé đã bị hủy (CANCELLED), vi phạm SRS BR-04 và State Machine
    """
    ticket_code = req.ticket_code.strip().upper()
    ticket = db.query(Ticket).filter(Ticket.ticket_code == ticket_code).first()

    if not ticket:
        return {
            "success": False,
            "status_code": 404,
            "message": "MÃ VÉ KHÔNG TỒN TẠI trên hệ thống",
            "ticket_code": ticket_code
        }

    if req.event_id and ticket.event_id != req.event_id:
        return {
            "success": False,
            "status_code": 400,
            "message": "VÉ KHÔNG THUỘC SỰ KIỆN NÀY",
            "ticket_code": ticket_code
        }

    # Kiểm tra vé đã từng check-in chưa
    if ticket.status == "CHECKED_IN":
        checkin_str = ticket.check_in_time.strftime("%H:%M:%S ngày %d/%m/%Y") if ticket.check_in_time else "trước đó"
        return {
            "success": False,
            "status_code": 409,
            "message": f"CẢNH BÁO: VÉ ĐÃ SỬ DỤNG vào lúc {checkin_str}! Nghi vấn vé sao chép hoặc gian lận.",
            "ticket_code": ticket_code,
            "attendee_name": ticket.user.full_name,
            "tier_name": ticket.tier.name,
            "check_in_time": checkin_str
        }

    # Kiểm tra vé đã hết hạn do sự kiện đã kết thúc mà khách không đến
    if ticket.status == "EXPIRED" or (ticket.status == "CONFIRMED" and ticket.is_expired):
        if ticket.status != "EXPIRED":
            ticket.status = "EXPIRED"
            db.commit()
        end_time_str = ticket.event.end_time.strftime("%H:%M ngày %d/%m/%Y") if ticket.event and ticket.event.end_time else "trước đó"
        return {
            "success": False,
            "status_code": 410,
            "message": f"TỪ CHỐI: Sự kiện đã kết thúc vào lúc {end_time_str}. Vé đã hết hạn sử dụng!",
            "ticket_code": ticket_code,
            "attendee_name": ticket.user.full_name if ticket.user else "Khách vãng lai",
            "tier_name": ticket.tier.name if ticket.tier else "Standard"
        }

    # === SEED-05: BUG BỎ SÓT KIỂM TRA VÉ ĐÃ HỦY (CANCELLED) ===
    # Lẽ ra phải có:
    # if ticket.status == "CANCELLED":
    #     return {"success": False, "status_code": 400, "message": "VÉ ĐÃ BỊ HỦY HOÀN TIỀN. Không có giá trị vào cửa."}
    # Nhưng code bị bỏ sót, cho phép vé CANCELLED chuyển thẳng thành CHECKED_IN!

    # Cập nhật trạng thái vé hợp lệ (lưu theo giờ thực tế địa phương)
    ticket.status = "CHECKED_IN"
    ticket.check_in_time = datetime.now()
    db.commit()

    return {
        "success": True,
        "status_code": 200,
        "message": "VÉ HỢP LỆ! Chào mừng quý khách tham dự sự kiện.",
        "ticket_code": ticket.ticket_code,
        "attendee_name": ticket.user.full_name,
        "tier_name": ticket.tier.name,
        "check_in_time": ticket.check_in_time.strftime("%H:%M:%S ngày %d/%m/%Y")
    }

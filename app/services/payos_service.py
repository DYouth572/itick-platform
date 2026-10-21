# app/services/payos_service.py
import logging
import os
import re
from typing import Any, Dict, List, Optional
from payos import PayOS
from payos.types import CreatePaymentLinkRequest, ItemData

logger = logging.getLogger("eventtick.payos")

# Tải cấu hình biến môi trường
PAYOS_CLIENT_ID = os.getenv("PAYOS_CLIENT_ID", "bf1e8594-f78f-4525-923b-1666dfae2450")
PAYOS_API_KEY = os.getenv("PAYOS_API_KEY", "608d9501-423a-4a45-97ef-2f8b0ca7b50c")
PAYOS_CHECKSUM_KEY = os.getenv("PAYOS_CHECKSUM_KEY", "2bf25f90cfa8bc1efdb4b2e1c70be0f7e254e9814a96961ef6217fdb41c6323b")

_payos_client: Optional[PayOS] = None

def get_payos_client() -> PayOS:
    """Khởi tạo và trả về singleton PayOS client."""
    global _payos_client
    if _payos_client is None:
        _payos_client = PayOS(
            client_id=PAYOS_CLIENT_ID,
            api_key=PAYOS_API_KEY,
            checksum_key=PAYOS_CHECKSUM_KEY
        )
    return _payos_client


def sanitize_description(desc: str) -> str:
    """
    Chuẩn hóa nội dung thanh toán theo quy định PayOS:
    - Tối đa 25 ký tự
    - Không chứa ký tự đặc biệt nguy hiểm
    """
    # Loại bỏ dấu tiếng Việt hoặc ký tự đặc biệt
    clean = re.sub(r'[^a-zA-Z0-9 ]', '', desc).strip()
    if not clean:
        clean = "Thanh toan ve"
    return clean[:25]


def create_vietqr_payment_link(
    order_code_int: int,
    amount: int,
    description: str,
    return_url: str,
    cancel_url: str,
    item_name: str = "Vé Sự Kiện",
    quantity: int = 1
) -> Dict[str, Any]:
    """
    Tạo link thanh toán VietQR qua PayOS.
    """
    client = get_payos_client()
    clean_desc = sanitize_description(description)
    
    # PayOS yêu cầu số tiền tối thiểu là 1,000 VNĐ
    pay_amount = max(1000, int(amount))

    request_data = CreatePaymentLinkRequest(
        order_code=order_code_int,
        amount=pay_amount,
        description=clean_desc,
        cancel_url=cancel_url,
        return_url=return_url,
        items=[
            ItemData(name=item_name[:50], quantity=quantity, price=pay_amount)
        ]
    )

    try:
        response = client.payment_requests.create(request_data)
        checkout_url = getattr(response, "checkout_url", None)
        payment_link_id = getattr(response, "id", None)
        qr_code = getattr(response, "qr_code", None)

        logger.info(f"Đã tạo PayOS link thành công cho OrderCode={order_code_int}: {checkout_url}")
        return {
            "success": True,
            "checkout_url": checkout_url,
            "payment_link_id": payment_link_id,
            "qr_code": qr_code,
            "order_code": order_code_int,
            "amount": pay_amount
        }
    except Exception as e:
        logger.error(f"Lỗi khi gọi API tạo PayOS payment link: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


def get_payment_link_status(order_code_or_id: Any) -> Optional[Dict[str, Any]]:
    """
    Lấy thông tin và trạng thái thanh toán từ PayOS.
    Trả về dict chứa status: 'PENDING', 'PAID', 'CANCELLED', etc.
    """
    client = get_payos_client()
    try:
        info = client.payment_requests.get(order_code_or_id)
        return {
            "order_code": getattr(info, "order_code", None),
            "amount": getattr(info, "amount", 0),
            "status": getattr(info, "status", None),
            "created_at": getattr(info, "created_at", None),
            "transactions": getattr(info, "transactions", [])
        }
    except Exception as e:
        logger.warning(f"Không thể lấy trạng thái PayOS cho {order_code_or_id}: {e}")
        return None

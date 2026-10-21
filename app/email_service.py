# app/email_service.py
import logging
import os
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any

logger = logging.getLogger("eventtick.email")

def get_smtp_config():
    """Lấy cấu hình SMTP từ biến môi trường"""
    return {
        "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "user": os.getenv("SMTP_USER", "").strip(),
        "password": os.getenv("SMTP_PASSWORD", "").strip(),
        "from_email": os.getenv("SMTP_FROM", "no-reply@eventtick.vn").strip(),
        "use_tls": os.getenv("SMTP_TLS", "true").lower() in ["true", "1", "yes"],
        "use_ssl": os.getenv("SMTP_SSL", "false").lower() in ["true", "1", "yes"],
    }

def send_password_reset_otp_email(to_email: str, user_name: str, otp_code: str, reset_link: str = "") -> Dict[str, Any]:
    """
    Gửi email chứa mã xác thực OTP (6 chữ số) và liên kết đặt lại mật khẩu qua giao thức SMTP.
    """
    config = get_smtp_config()
    subject = f"EventTick - Mã OTP Đặt lại Mật khẩu: {otp_code}"

    # Nội dung Text thuần
    text_content = f"""Xin chào {user_name},

Hệ thống EventTick nhận được yêu cầu đặt lại mật khẩu cho tài khoản ({to_email}).

MÃ XÁC THỰC OTP CỦA BẠN LÀ:
{otp_code}

(Mã này có thời hạn sử dụng trong 10 phút. Tuyệt đối không chia sẻ mã này cho bất kỳ ai.)

Hoặc bạn có thể truy cập đường dẫn đặt lại mật khẩu trực tiếp:
{reset_link}

Trân trọng,
Đội ngũ EventTick Platform
Hotline: 1900 6868 | Email: support@eventtick.vn
"""

    # Nội dung HTML chuyên nghiệp
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{subject}</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 30px 15px; color: #1e293b;">
  <div style="max-width: 560px; margin: 0 auto; background-color: #ffffff; border: 1px solid #e2e8f0; padding: 35px 30px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
    
    <!-- Header -->
    <div style="text-align: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 20px; margin-bottom: 25px;">
      <div style="display: inline-block; background-color: #4f46e5; color: #ffffff; font-weight: 800; font-size: 18px; padding: 6px 14px; border-radius: 2px; letter-spacing: 0.5px;">
        EventTick
      </div>
      <p style="margin: 6px 0 0 0; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #64748b; font-weight: 600;">
        Nền tảng Vé Sự Kiện Trực Tuyến
      </p>
    </div>

    <!-- Body -->
    <h2 style="font-size: 18px; font-weight: 700; color: #0f172a; margin-top: 0;">Xác thực Đặt lại Mật khẩu</h2>
    <p style="font-size: 14px; line-height: 1.6; color: #334155;">
      Xin chào <strong>{user_name}</strong>,
    </p>
    <p style="font-size: 14px; line-height: 1.6; color: #334155;">
      Bạn vừa gửi yêu cầu đặt lại mật khẩu cho tài khoản <strong>{to_email}</strong>. Vui lòng nhập mã OTP bên dưới trên trang xác thực để hoàn tất:
    </p>

    <!-- OTP Display Box -->
    <div style="text-align: center; margin: 28px 0;">
      <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1.2px; color: #64748b; font-weight: 700; margin-bottom: 8px;">
        MÃ XÁC THỰC OTP
      </div>
      <div style="display: inline-block; font-size: 34px; font-weight: 800; letter-spacing: 6px; color: #4f46e5; background-color: #f5f3ff; border: 2px dashed #6366f1; padding: 12px 28px; font-family: monospace;">
        {otp_code}
      </div>
      <p style="margin: 8px 0 0 0; font-size: 12px; color: #64748b;">
        Mã có hiệu lực trong vòng <strong>10 phút</strong>
      </p>
    </div>

    <!-- Fallback Direct Link -->
    {f'''<div style="background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 12px; margin: 20px 0; font-size: 12px; color: #475569; word-break: break-all;">
      <span style="font-weight: 600; display: block; margin-bottom: 4px;">Hoặc nhấn vào liên kết nhanh:</span>
      <a href="{reset_link}" style="color: #4f46e5; text-decoration: underline;">{reset_link}</a>
    </div>''' if reset_link else ''}

    <!-- Security Warnings -->
    <div style="border-left: 3px solid #f59e0b; background-color: #fffbeb; padding: 10px 14px; margin-top: 25px; font-size: 12px; color: #b45309; line-height: 1.5;">
      <strong>Lưu ý bảo mật:</strong>
      <ul style="margin: 4px 0 0 0; padding-left: 18px;">
        <li>Tuyệt đối không chia sẻ mã OTP này cho bất kỳ ai, kể cả nhân viên hỗ trợ EventTick.</li>
        <li>Nếu bạn không yêu cầu thay đổi mật khẩu, vui lòng bỏ qua email này. Tài khoản của bạn vẫn an toàn.</li>
      </ul>
    </div>

    <!-- Footer -->
    <div style="margin-top: 35px; padding-top: 20px; border-top: 1px solid #f1f5f9; text-align: center; font-size: 11px; color: #94a3b8; line-height: 1.5;">
      <p style="margin: 0;">© 2026 EventTick Platform. Toàn bộ bản quyền được bảo hộ.</p>
      <p style="margin: 4px 0 0 0;">Hotline: 1900 6868 | Email: support@eventtick.vn</p>
    </div>

  </div>
</body>
</html>
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = config["from_email"]
    msg["To"] = to_email

    msg.attach(MIMEText(text_content, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    # Kiểm tra cấu hình SMTP
    if not config["user"] or not config["password"]:
        logger.info(f"[SMTP DEV MODE] Chưa cấu hình SMTP_USER/SMTP_PASSWORD. Mô phỏng gửi OTP {otp_code} đến {to_email}")
        return {
            "success": True,
            "simulated": True,
            "otp_code": otp_code,
            "message": f"Hệ thống đã tạo mã OTP {otp_code} và mô phỏng gửi thành công đến {to_email} (Chế độ Local Dev).",
            "reset_link": reset_link
        }

    # Tiến hành gửi qua SMTP
    try:
        if config["use_ssl"] or config["port"] == 465:
            server = smtplib.SMTP_SSL(config["host"], config["port"], timeout=12)
        else:
            server = smtplib.SMTP(config["host"], config["port"], timeout=12)
            if config["use_tls"]:
                server.starttls()

        server.login(config["user"], config["password"])
        server.send_message(msg)
        server.quit()

        logger.info(f"[SMTP] Đã gửi email chứa mã OTP {otp_code} đến {to_email}")
        return {
            "success": True,
            "simulated": False,
            "otp_code": otp_code,
            "message": f"Đã gửi mã OTP xác thực đến {to_email} qua máy chủ SMTP {config['host']}."
        }

    except Exception as exc:
        logger.warning(f"[SMTP ERROR] Không thể gửi email qua SMTP ({exc}). Lưu mã OTP dự phòng: {otp_code}")
        return {
            "success": True,
            "simulated": True,
            "otp_code": otp_code,
            "error_detail": str(exc),
            "message": f"Không thể kết nối máy chủ SMTP thực tế ({exc}). Mã OTP dự phòng: {otp_code}",
            "reset_link": reset_link
        }

# Giữ alias tương thích
send_password_reset_email = send_password_reset_otp_email

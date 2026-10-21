# app/routers/auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.database import get_db
from app.models import User
from app.schemas import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ResetPasswordResponse,
    VerifyOtpResetPasswordRequest,
    Token,
    UserLogin,
    UserOut,
    UserRegister,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """Đăng ký tài khoản người dùng mới (Attendee hoặc Organizer)"""
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email này đã được sử dụng. Vui lòng chọn email khác hoặc Đăng nhập"
        )
    
    new_user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        phone_number=user_in.phone_number,
        hashed_password=hash_password(user_in.password),
        role=user_in.role,
        is_active=True,
        balance=10000000.0  # Cấp sẵn 10,000,000 VNĐ giả lập để test mua vé
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(login_in: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Đăng nhập và cấp JWT Token, lưu đồng thời vào Cookie cho giao diện Web"""
    user = db.query(User).filter(User.email == login_in.email).first()
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản của bạn đã bị tạm khóa. Vui lòng liên hệ ban quản trị"
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role, "email": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Thiết lập Cookie để giao diện Web tự động nhận diện phiên đăng nhập
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=False,  # Cho phép JS đọc nếu cần
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Lấy thông tin tài khoản đang đăng nhập"""
    return current_user

@router.post("/logout")
def logout(response: Response):
    """Đăng xuất và xóa Cookie phiên làm việc"""
    response.delete_cookie("access_token")
    return {"message": "Đăng xuất thành công"}

@router.post("/forgot-password")
def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Yêu cầu đặt lại mật khẩu:
    Tạo token bảo mật và mã OTP 6 số (hạn 10 phút), gửi qua giao thức SMTP đến email người dùng.
    """
    import secrets
    from datetime import datetime, timedelta
    from app.email_service import send_password_reset_otp_email
    from app.models import PasswordResetToken

    clean_email = payload.email.strip().lower()
    user = db.query(User).filter(User.email.ilike(clean_email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Địa chỉ email này chưa được đăng ký trong hệ thống EventTick"
        )
    
    # Hủy các token/otp chưa dùng trước đó của tài khoản này
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.is_used == False
    ).update({"is_used": True})

    # Tạo token ngẫu nhiên bảo mật cao (URL-safe) và mã OTP 6 số
    token_str = secrets.token_urlsafe(32)
    otp_code = f"{secrets.randbelow(900000) + 100000}"
    expires_at = datetime.now() + timedelta(minutes=10)

    reset_record = PasswordResetToken(
        user_id=user.id,
        token=token_str,
        otp_code=otp_code,
        expires_at=expires_at,
        is_used=False
    )
    db.add(reset_record)
    db.commit()

    # Tạo URL đầy đủ
    base_url = str(request.base_url).rstrip("/")
    reset_link = f"{base_url}/reset-password?token={token_str}"

    # Gửi qua SMTP
    email_result = send_password_reset_otp_email(
        to_email=user.email,
        user_name=user.full_name,
        otp_code=otp_code,
        reset_link=reset_link
    )

    response_data = {
        "success": True,
        "message": f"Mã xác thực OTP gồm 6 chữ số đã được gửi đến email {user.email}. Vui lòng kiểm tra hộp thư đến (hoặc thư mục Spam).",
        "email": user.email,
        "expires_in_minutes": 10
    }
    
    # Nếu đang ở chế độ giả lập local dev hoặc gửi lỗi, trả kèm dev_otp để tiện test
    if email_result.get("simulated"):
        response_data["dev_otp"] = otp_code
        response_data["dev_reset_link"] = reset_link
        response_data["note"] = "Chế độ mô phỏng Local Dev: Đã sinh mã OTP và liên kết dự phòng."

    return response_data

@router.post("/reset-password-otp", response_model=ResetPasswordResponse)
def reset_password_with_otp(
    payload: VerifyOtpResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Xác nhận đổi mật khẩu mới bằng mã OTP 6 số đã gửi qua email.
    """
    from datetime import datetime
    from app.models import PasswordResetToken

    clean_email = payload.email.strip().lower()
    clean_otp = payload.otp_code.strip()

    if payload.new_password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu xác nhận không khớp với mật khẩu mới"
        )
    
    if len(payload.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu mới phải có độ dài tối thiểu từ 6 ký tự"
        )

    user = db.query(User).filter(User.email.ilike(clean_email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Địa chỉ email này chưa được đăng ký trong hệ thống"
        )

    # Tìm bản ghi OTP mới nhất chưa sử dụng của user này
    reset_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.otp_code == clean_otp,
        PasswordResetToken.is_used == False
    ).order_by(PasswordResetToken.id.desc()).first()

    if not reset_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã OTP không chính xác hoặc đã được sử dụng. Vui lòng kiểm tra lại."
        )

    if datetime.now() > reset_record.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã OTP đã hết thời hạn hiệu lực (10 phút). Vui lòng yêu cầu gửi lại mã mới."
        )

    # Cập nhật mật khẩu băm mới
    user.hashed_password = hash_password(payload.new_password)
    reset_record.is_used = True
    db.commit()

    return {
        "success": True,
        "message": "Đặt lại mật khẩu thành công! Bạn có thể đăng nhập ngay bằng mật khẩu mới."
    }

@router.post("/reset-password", response_model=ResetPasswordResponse)
def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Xác nhận đổi mật khẩu mới bằng token đã gửi qua email.
    """
    from datetime import datetime
    from app.models import PasswordResetToken

    if payload.new_password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu xác nhận không khớp với mật khẩu mới"
        )
    
    if len(payload.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu mới phải có độ dài tối thiểu từ 6 ký tự"
        )

    # Kiểm tra token
    reset_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == payload.token
    ).first()

    if not reset_record or reset_record.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Liên kết đặt lại mật khẩu không hợp lệ hoặc đã được sử dụng trước đó"
        )

    if datetime.now() > reset_record.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Liên kết đặt lại mật khẩu đã hết hạn sử dụng (quá 30 phút). Vui lòng gửi lại yêu cầu mới."
        )

    user = db.query(User).filter(User.id == reset_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng liên quan đến token này không tồn tại"
        )

    # Cập nhật mật khẩu băm mới
    user.hashed_password = hash_password(payload.new_password)
    reset_record.is_used = True
    db.commit()

    return {
        "success": True,
        "message": "Đặt lại mật khẩu thành công! Bạn có thể đăng nhập ngay với mật khẩu mới."
    }


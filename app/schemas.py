# app/schemas.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

# --- AUTH SCHEMAS ---
class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=6, max_length=32)
    role: str = Field(default="ATTENDEE", pattern="^(ATTENDEE|ORGANIZER)$")
    phone_number: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    is_active: bool
    balance: float
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# --- TICKET TIER SCHEMAS ---
class TicketTierCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    price: float = Field(..., ge=0)
    total_quantity: int = Field(..., ge=1)
    description: Optional[str] = None

class TicketTierOut(BaseModel):
    id: int
    event_id: int
    name: str
    price: float
    total_quantity: int
    available_quantity: int
    description: Optional[str]

    class Config:
        from_attributes = True

# --- EVENT SCHEMAS ---
class EventCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=150)
    description: str = Field(..., min_length=20)
    location: str = Field(..., min_length=3)
    banner_url: Optional[str] = None
    category: str = Field(default="TECHNOLOGY")
    capacity: int = Field(default=500, ge=10, le=10000)
    start_time: datetime
    end_time: datetime
    tiers: List[TicketTierCreate] = []

class EventOut(BaseModel):
    id: int
    organizer_id: int
    title: str
    description: str
    location: str
    banner_url: Optional[str]
    category: str
    capacity: int
    status: str
    rejection_reason: Optional[str] = None
    start_time: datetime
    end_time: datetime
    tiers: List[TicketTierOut] = []

    class Config:
        from_attributes = True

class EventListOut(BaseModel):
    total: int
    page: int
    limit: int
    items: List[EventOut]

# --- BOOKING & ORDER SCHEMAS ---
class BookingCreate(BaseModel):
    event_id: int
    tier_id: int
    quantity: int = Field(...)  # Lưu ý SEED-04 sẽ kiểm tra ở tầng router
    voucher_code: Optional[str] = None
    payment_method: Optional[str] = "WALLET"

class TicketOut(BaseModel):
    id: int
    ticket_code: str
    status: str
    check_in_time: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    order_code: str
    event_id: int
    tier_id: int
    quantity: int
    voucher_code: Optional[str]
    original_amount: float
    discount_amount: float
    final_amount: float
    platform_fee_rate: float = 5.0
    platform_fee: float = 0.0
    organizer_amount: float = 0.0
    status: str
    payment_method: Optional[str] = "WALLET"
    payment_status: Optional[str] = "PAID"
    checkout_url: Optional[str] = None
    tickets: List[TicketOut] = []

    class Config:
        from_attributes = True

# --- VOUCHER SCHEMAS ---
class VoucherApplyRequest(BaseModel):
    code: str
    order_total: float

class VoucherApplyResponse(BaseModel):
    is_valid: bool
    message: str
    discount_amount: float = 0.0
    final_amount: float = 0.0

# --- CHECK-IN SCHEMAS ---
class CheckinRequest(BaseModel):
    ticket_code: str
    event_id: Optional[int] = None

class CheckinResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    ticket_code: str
    attendee_name: Optional[str] = None
    tier_name: Optional[str] = None
    check_in_time: Optional[str] = None

# --- PASSWORD RESET SCHEMAS ---
class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6, max_length=50)
    confirm_password: str = Field(..., min_length=6, max_length=50)

class VerifyOtpResetPasswordRequest(BaseModel):
    email: str
    otp_code: str = Field(..., min_length=6, max_length=10)
    new_password: str = Field(..., min_length=6, max_length=50)
    confirm_password: str = Field(..., min_length=6, max_length=50)

class ResetPasswordResponse(BaseModel):
    success: bool
    message: str

# --- ADMIN OPERATION SCHEMAS ---
class UserRoleUpdate(BaseModel):
    role: str = Field(..., pattern="^(ATTENDEE|ORGANIZER|ADMIN)$")

class UserPasswordDirectReset(BaseModel):
    new_password: str = Field(..., min_length=6, max_length=50)

class UserBalanceAdjust(BaseModel):
    amount: float
    reason: Optional[str] = "Admin điều chỉnh số dư"

class AdminEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    banner_url: Optional[str] = None
    category: Optional[str] = None
    capacity: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class AdminEventStatusUpdate(BaseModel):
    status: str
    reason: Optional[str] = None

class AdminVoucherCreate(BaseModel):
    code: str = Field(..., min_length=3, max_length=20)
    discount_type: str = Field(default="PERCENT", pattern="^(PERCENT|FIXED)$")
    discount_value: float = Field(..., gt=0)
    max_discount_cap: Optional[float] = None
    min_order_value: float = Field(default=0, ge=0)
    total_uses: int = Field(default=100, ge=1)
    expires_at: Optional[datetime] = None

class PlatformFeeConfigUpdate(BaseModel):
    fee_rate: float = Field(..., ge=0.0, le=50.0, description="Tỷ lệ phí dịch vụ nền tảng (0% đến 50%)")



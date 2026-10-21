# app/models.py
from datetime import datetime
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Boolean, DateTime, ForeignKey, Float, Index
)
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="ATTENDEE", nullable=False)  # ATTENDEE, ORGANIZER, ADMIN
    is_active = Column(Boolean, default=True, nullable=False)
    balance = Column(Float, default=10000000.0)  # Số dư giả lập 10 triệu VNĐ để mua vé
    created_at = Column(DateTime, default=datetime.now)

    # Quan hệ
    events = relationship("Event", back_populates="organizer")
    orders = relationship("Order", back_populates="user")
    tickets = relationship("Ticket", back_populates="user")


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        Index("idx_events_start_time", "start_time"),
        Index("idx_events_category", "category"),
    )

    id = Column(Integer, primary_key=True, index=True)
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    location = Column(String(200), nullable=False)
    banner_url = Column(String(500), nullable=True)
    category = Column(String(50), default="TECHNOLOGY", nullable=False)  # TECHNOLOGY, MUSIC, BUSINESS, EDUCATION, WORKSHOP
    capacity = Column(Integer, default=500, nullable=False)
    status = Column(String(30), default="PUBLISHED", nullable=False)  # DRAFT, PENDING_APPROVAL, PUBLISHED, REJECTED, CANCELLED
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    ticket_sales_end_time = Column(DateTime, nullable=True)  # Thời điểm đóng mua vé
    rejection_reason = Column(Text, nullable=True)  # Ghi chú/lý do nếu bài đăng chưa đạt kiểm duyệt tự động
    created_at = Column(DateTime, default=datetime.now)

    # Quan hệ
    organizer = relationship("User", back_populates="events")
    tiers = relationship("TicketTier", back_populates="event", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="event")
    tickets = relationship("Ticket", back_populates="event")

    @property
    def sales_deadline(self):
        """Thời hạn đóng mua vé (mặc định bằng start_time nếu không cài đặt riêng)"""
        return self.ticket_sales_end_time if self.ticket_sales_end_time else self.start_time

    @property
    def is_sales_closed(self):
        """Kiểm tra sự kiện đã quá hạn mua vé hay chưa"""
        from datetime import timedelta
        now = datetime.now()
        # Đảm bảo so sánh an toàn
        return now >= self.sales_deadline

    @property
    def is_hidden_after_closure(self):
        """Sau 10 phút kể từ lúc hết thời gian mua vé thì tự động ẩn sự kiện đi"""
        from datetime import timedelta
        now = datetime.now()
        return now > (self.sales_deadline + timedelta(minutes=10))

    @property
    def is_ended(self):
        """Kiểm tra sự kiện đã chính thức kết thúc hay chưa"""
        return datetime.now() > self.end_time

    @property
    def minutes_until_close(self):
        """Số phút còn lại đến khi đóng mua vé (nếu chưa đóng)"""
        now = datetime.now()
        if now < self.sales_deadline:
            return max(0, int((self.sales_deadline - now).total_seconds() / 60))
        return 0


class TicketTier(Base):
    __tablename__ = "ticket_tiers"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    name = Column(String(100), nullable=False)  # Early Bird, Tiêu chuẩn, VIP
    price = Column(Float, nullable=False)  # VNĐ
    total_quantity = Column(Integer, nullable=False)
    available_quantity = Column(Integer, nullable=False)
    description = Column(String(255), nullable=True)

    # Quan hệ
    event = relationship("Event", back_populates="tiers")
    orders = relationship("Order", back_populates="tier")
    tickets = relationship("Ticket", back_populates="tier")


class Voucher(Base):
    __tablename__ = "vouchers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    discount_type = Column(String(20), default="PERCENT", nullable=False)  # PERCENT hoặc FIXED
    discount_value = Column(Float, nullable=False)  # Ví dụ 20 (%) hoặc 50000 (VNĐ)
    max_discount_cap = Column(Float, nullable=True)  # Mức trần giảm giá tối đa (VNĐ)
    min_order_value = Column(Float, default=0.0)  # Đơn hàng tối thiểu (VNĐ)
    start_date = Column(DateTime, default=datetime.now)
    end_date = Column(DateTime, nullable=False)
    total_uses = Column(Integer, default=100)
    remaining_uses = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        Index("idx_orders_user", "user_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    order_code = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    tier_id = Column(Integer, ForeignKey("ticket_tiers.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    voucher_code = Column(String(50), nullable=True)
    original_amount = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    final_amount = Column(Float, nullable=False)
    platform_fee_rate = Column(Float, default=5.0)  # Tỷ lệ % phí dịch vụ nền tảng (mặc định 5%)
    platform_fee = Column(Float, default=0.0)  # Số tiền phí sàn giữ lại (VNĐ, đã làm tròn)
    organizer_amount = Column(Float, default=0.0)  # Số tiền thực nhận chuyển vào ví BTC (VNĐ)
    status = Column(String(30), default="CONFIRMED")  # CONFIRMED, CANCELLED
    payment_method = Column(String(30), default="WALLET")  # VIETQR_PAYOS, WALLET
    payment_status = Column(String(30), default="PAID")  # PAID, PENDING, FAILED, CANCELLED
    payos_order_code = Column(BigInteger, nullable=True, index=True)
    payos_payment_link_id = Column(String(100), nullable=True)
    checkout_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # Quan hệ
    user = relationship("User", back_populates="orders")
    event = relationship("Event", back_populates="orders")
    tier = relationship("TicketTier", back_populates="orders")
    tickets = relationship("Ticket", back_populates="order")


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        Index("idx_tickets_code", "ticket_code"),
    )

    id = Column(Integer, primary_key=True, index=True)
    ticket_code = Column(String(50), unique=True, nullable=False)  # TICK-2026-XXXXX
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    tier_id = Column(Integer, ForeignKey("ticket_tiers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(30), default="CONFIRMED", index=True)  # CONFIRMED, CHECKED_IN, CANCELLED, EXPIRED
    check_in_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # Quan hệ
    order = relationship("Order", back_populates="tickets")
    event = relationship("Event", back_populates="tickets")
    tier = relationship("TicketTier", back_populates="tickets")
    user = relationship("User", back_populates="tickets")

    @property
    def is_expired(self):
        """Vé chưa check-in và sự kiện đã kết thúc"""
        if self.status == "EXPIRED":
            return True
        if self.status == "CONFIRMED" and self.event:
            return datetime.now() > self.event.end_time
        return False

    @property
    def display_status(self):
        """Trạng thái hiển thị thực tế của vé"""
        if self.status == "CONFIRMED" and self.is_expired:
            return "EXPIRED"
        return self.status


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    __table_args__ = (
        Index("idx_reset_token", "token"),
        Index("idx_reset_otp", "otp_code"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    otp_code = Column(String(10), nullable=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User")


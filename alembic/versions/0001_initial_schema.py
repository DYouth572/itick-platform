"""0001_initial_schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-10-02 12:30:00.000000

Migration ban đầu khởi tạo toàn bộ schema cho hệ thống EventTick:
- users: Tài khoản người dùng (Attendee, Organizer, Admin)
- events: Sự kiện, thời gian bắt đầu/kết thúc, thời hạn bán vé
- ticket_tiers: Các phân hạng vé (VIP, Standard, Early Bird)
- vouchers: Mã giảm giá sự kiện
- orders: Đơn hàng đặt vé
- tickets: Vé điện tử cấp cho người tham dự

Kèm các chỉ mục tối ưu hóa truy vấn theo chuẩn postgres-patterns:
- idx_events_start_time
- idx_events_category
- idx_tickets_code
- idx_orders_user
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Bảng users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), server_default='ATTENDEE', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('balance', sa.Float(), server_default='10000000.0', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 2. Bảng events
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organizer_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('location', sa.String(length=200), nullable=False),
        sa.Column('banner_url', sa.String(length=500), nullable=True),
        sa.Column('category', sa.String(length=50), server_default='TECHNOLOGY', nullable=False),
        sa.Column('capacity', sa.Integer(), server_default='500', nullable=False),
        sa.Column('status', sa.String(length=30), server_default='PUBLISHED', nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('ticket_sales_end_time', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['organizer_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_events_id', 'events', ['id'], unique=False)
    op.create_index('ix_events_title', 'events', ['title'], unique=False)
    # Postgres-patterns indexes
    op.create_index('idx_events_start_time', 'events', ['start_time'], unique=False)
    op.create_index('idx_events_category', 'events', ['category'], unique=False)

    # 3. Bảng ticket_tiers
    op.create_table(
        'ticket_tiers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('total_quantity', sa.Integer(), nullable=False),
        sa.Column('available_quantity', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ticket_tiers_id', 'ticket_tiers', ['id'], unique=False)

    # 4. Bảng vouchers
    op.create_table(
        'vouchers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('discount_type', sa.String(length=20), server_default='PERCENT', nullable=False),
        sa.Column('discount_value', sa.Float(), nullable=False),
        sa.Column('max_discount_cap', sa.Float(), nullable=True),
        sa.Column('min_order_value', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('start_date', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('total_uses', sa.Integer(), server_default='100', nullable=True),
        sa.Column('remaining_uses', sa.Integer(), server_default='100', nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_vouchers_id', 'vouchers', ['id'], unique=False)
    op.create_index('ix_vouchers_code', 'vouchers', ['code'], unique=True)

    # 5. Bảng orders
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_code', sa.String(length=50), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('tier_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('voucher_code', sa.String(length=50), nullable=True),
        sa.Column('original_amount', sa.Float(), nullable=False),
        sa.Column('discount_amount', sa.Float(), server_default='0.0', nullable=True),
        sa.Column('final_amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=30), server_default='CONFIRMED', nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id']),
        sa.ForeignKeyConstraint(['tier_id'], ['ticket_tiers.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_orders_id', 'orders', ['id'], unique=False)
    op.create_index('ix_orders_order_code', 'orders', ['order_code'], unique=True)
    # Postgres-patterns index
    op.create_index('idx_orders_user', 'orders', ['user_id'], unique=False)

    # 6. Bảng tickets
    op.create_table(
        'tickets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_code', sa.String(length=50), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('tier_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=30), server_default='CONFIRMED', nullable=True),
        sa.Column('check_in_time', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id']),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tier_id'], ['ticket_tiers.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tickets_id', 'tickets', ['id'], unique=False)
    # Postgres-patterns index
    op.create_index('idx_tickets_code', 'tickets', ['ticket_code'], unique=True)
    op.create_index('ix_tickets_status', 'tickets', ['status'], unique=False)


def downgrade() -> None:
    # Xóa theo thứ tự ngược lại để đảm bảo tính toàn vẹn khóa ngoại
    op.drop_index('ix_tickets_status', table_name='tickets')
    op.drop_index('idx_tickets_code', table_name='tickets')
    op.drop_index('ix_tickets_id', table_name='tickets')
    op.drop_table('tickets')

    op.drop_index('idx_orders_user', table_name='orders')
    op.drop_index('ix_orders_order_code', table_name='orders')
    op.drop_index('ix_orders_id', table_name='orders')
    op.drop_table('orders')

    op.drop_index('ix_vouchers_code', table_name='vouchers')
    op.drop_index('ix_vouchers_id', table_name='vouchers')
    op.drop_table('vouchers')

    op.drop_index('ix_ticket_tiers_id', table_name='ticket_tiers')
    op.drop_table('ticket_tiers')

    op.drop_index('idx_events_category', table_name='events')
    op.drop_index('idx_events_start_time', table_name='events')
    op.drop_index('ix_events_title', table_name='events')
    op.drop_index('ix_events_id', table_name='events')
    op.drop_table('events')

    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')

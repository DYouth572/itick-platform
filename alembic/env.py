# alembic/env.py
import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context

# Đảm bảo import được module app từ thư mục gốc
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Tải biến môi trường từ .env nếu có
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass

from app.models import Base
from app.database import DATABASE_URL as APP_DATABASE_URL

# Cấu hình đối tượng Config của Alembic
config = context.config

# Thiết lập cấu hình ghi log từ file cấu hình nếu có
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata trỏ tới Base.metadata của app.models
target_metadata = Base.metadata


def get_url() -> str:
    """
    Lấy chuỗi kết nối Database theo thứ tự ưu tiên:
    1. Tham số dòng lệnh Alembic (-x db_url=...)
    2. Biến môi trường DATABASE_URL (từ OS hoặc .env)
    3. Cấu hình sqlalchemy.url trong alembic.ini
    4. Cấu hình mặc định từ app.database
    """
    x_args = context.get_x_argument(as_dictionary=True)
    url = x_args.get("db_url")
    if not url:
        url = os.getenv("DATABASE_URL")
    if not url:
        url = config.get_main_option("sqlalchemy.url")
    if not url:
        url = APP_DATABASE_URL

    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    url = get_url()
    
    # Kết nối chuyên dụng cho migration sử dụng NullPool (tránh giữ connection leak)
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    connectable = create_engine(
        url,
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

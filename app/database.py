# app/database.py
import logging
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

# Tải cấu hình biến môi trường từ .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger("eventtick.database")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLITE_DB_PATH = os.path.join(BASE_DIR, "eventtick.db")
DEFAULT_SQLITE_URL = f"sqlite:///{SQLITE_DB_PATH}"
DEFAULT_PG_URL = "postgresql://postgres:postgres@localhost:5432/eventtick_db"

# Ưu tiên lấy từ biến môi trường DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_PG_URL)

# Chuẩn hóa tiền tố postgres:// thành postgresql:// (chuẩn SQLAlchemy 2.0+)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


def build_engine(db_url: str):
    """
    Khởi tạo SQLAlchemy Engine phù hợp cho từng loại Database theo chuẩn postgres-patterns:
    - PostgreSQL:
      * pool_size=20: Kết nối thường trực trong Pool để đáp ứng tải đồng thời cao (JMeter load testing).
      * max_overflow=10: Số kết nối đột biến vượt trần cho phép khi lượng yêu cầu tăng vọt.
      * pool_timeout=30: Thời gian chờ tối đa (giây) lấy kết nối từ pool trước khi ném TimeoutError.
      * pool_pre_ping=True: Tự động kiểm tra liveness (SELECT 1) để loại bỏ các kết nối hỏng/stale.
      * pool_recycle=1800: Tái tạo kết nối sau 1800s (30 phút) để tránh bị DB server/firewall ngắt TCP.
    - SQLite:
      * check_same_thread=False: Hỗ trợ đa luồng FastAPI.
      * Listener connect: Tự động kích hoạt PRAGMA foreign_keys=ON và PRAGMA journal_mode=WAL cho mọi kết nối mới.
    """
    if db_url.startswith("sqlite"):
        eng = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            echo=False
        )

        @event.listens_for(eng, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("PRAGMA foreign_keys=ON;")
                cursor.execute("PRAGMA journal_mode=WAL;")
            except Exception as e:
                logger.warning(f"Không thể thiết lập PRAGMA SQLite: {e}")
            finally:
                cursor.close()

        return eng, db_url
    else:
        eng = create_engine(
            db_url,
            pool_size=20,
            max_overflow=10,
            pool_timeout=30,
            pool_pre_ping=True,
            pool_recycle=1800,
            echo=False
        )
        return eng, db_url


# Khởi tạo engine với cơ chế Graceful Fallback
try:
    engine, DATABASE_URL = build_engine(DATABASE_URL)
    with engine.connect() as test_conn:
        pass
except Exception as exc:
    # Nếu kết nối PostgreSQL thất bại (ví dụ container chưa bật hoặc sai thông tin xác thực dev),
    # tự động chuyển đổi Graceful Fallback sang SQLite cục bộ để đảm bảo hệ thống không bị crash
    if not DATABASE_URL.startswith("sqlite"):
        logger.warning(
            f"[Database] Kết nối tới PostgreSQL ({DATABASE_URL}) không thành công: {exc}. "
            f"Tự động chuyển đổi Graceful Fallback sang SQLite ({DEFAULT_SQLITE_URL})."
        )
        DATABASE_URL = DEFAULT_SQLITE_URL
        engine, DATABASE_URL = build_engine(DATABASE_URL)
    else:
        raise exc

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

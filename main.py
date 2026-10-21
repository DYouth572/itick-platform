# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import Base, engine
from app.routers import admin, auth, bookings, checkin, events, payment, web
from app.seed import seed_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo bảng và nạp dữ liệu mẫu ban đầu
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield

def create_app() -> FastAPI:
    app = FastAPI(
        title="iTick - Nền tảng Đăng ký & Bán vé Sự kiện Trực tuyến",
        description="""
## Hệ thống phục vụ Đồ án Học phần Đánh giá hiệu năng / Kiểm thử phần mềm (VJU 2026)

### Các tính năng chính:
- **Xác thực & Phân quyền**: Đăng ký, đăng nhập JWT Bearer token, phân quyền RBAC (Attendee, Organizer, Admin).
- **Khám phá sự kiện**: Tìm kiếm full-text, lọc theo danh mục, xem chi tiết và kiểm tra tồn kho vé.
- **Đặt vé & Voucher**: Đặt vé nhiều phân hạng, áp mã giảm giá theo %, xử lý trừ tồn kho.
- **Soát vé tại cổng (Check-in)**: Kiểm tra tính hợp lệ của vé điện tử, cảnh báo vé trùng / vé đã sử dụng.
- **Quản lý & Báo cáo**: Quản lý sự kiện, thống kê doanh thu và phê duyệt kiểm duyệt.

*Tài liệu Swagger OpenAPI hỗ trợ 100% xuất sang Postman Collection và đo kiểm tải Apache JMeter.*
        """,
        version="1.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Đăng ký các Router API chuẩn RESTful
    app.include_router(auth.router)
    app.include_router(events.router)
    app.include_router(bookings.router)
    app.include_router(payment.router)
    app.include_router(checkin.router)
    app.include_router(admin.router)

    # Đăng ký Router giao diện người dùng Web (Jinja2)
    app.include_router(web.router)

    # Cấu hình tài nguyên tĩnh (Static Files: logo, favicon, hình ảnh)
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        return FileResponse("static/favicon.ico")

    # Endpoint kiểm tra sức khỏe hệ thống (Health Check)
    @app.get("/health", tags=["System Health"])
    def health_check():
        return {
            "status": "healthy",
            "system": "iTick",
            "version": "1.1.0",
            "seeded_bugs_count": 15
        }

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

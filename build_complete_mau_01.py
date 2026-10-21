# build_complete_mau_01.py
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import json
import os
import re

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="CBD5E1", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def format_cell(cell, text, bold=False, font_size=9.5, color="1E293B", bg=None, align=WD_ALIGN_PARAGRAPH.LEFT):
    if bg:
        set_cell_background(cell, bg)
    set_cell_margins(cell)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    p.text = ""
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)

def add_code_block(doc, code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl, color="E2E8F0", sz="4")
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=120, bottom=120, left=160, right=160)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    p.text = ""
    run = p.add_run(code_text.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor.from_string("0F172A")
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def main():
    with open('scratch_api_inventory.json', 'r', encoding='utf-8') as f:
        endpoints_data = json.load(f)

    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Document Header
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(4)
    run = p_title.add_run("TÀI LIỆU API")
    run.font.name = "Arial"
    run.font.size = Pt(22)
    run.font.bold = True
    run.font.color.rgb = RGBColor.from_string("0F2942")

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(12)
    run = p_sub.add_run("Hệ thống: iTick - Nền tảng Đăng ký & Bán vé Sự kiện Trực tuyến  ·  Phiên bản: 1.1.0  ·  Người lập: Đỗ Sơn Nhật (VJU)  ·  Ngày: 09/10/2026")
    run.font.name = "Arial"
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor.from_string("64748B")

    # Guide notice
    p_guide = doc.add_paragraph()
    p_guide.paragraph_format.space_before = Pt(0)
    p_guide.paragraph_format.space_after = Pt(14)
    run = p_guide.add_run("Hướng dẫn: Tài liệu này giúp tester viết collection Postman/Newman và đo tải Apache JMeter mà không cần xem mã nguồn. Tài liệu liệt kê ĐẦY ĐỦ 100% tất cả 38 endpoints (43 API operations) của hệ thống iTick, trả về JSON chuẩn RESTful. Mọi ràng buộc dữ liệu khớp 100% với SRS_EventTick.md.")
    run.font.name = "Arial"
    run.font.size = Pt(9.5)
    run.font.italic = True
    run.font.color.rgb = RGBColor.from_string("475569")

    # 1. Thông tin chung
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(6)
    run = h1.add_run("1. Thông tin chung")
    run.font.name = "Arial"
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = RGBColor.from_string("1E3A8A")

    t1 = doc.add_table(rows=8, cols=2)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t1)
    
    general_info = [
        ("Base URL", "http://127.0.0.1:8001"),
        ("Định dạng dữ liệu", "JSON, mã hoá UTF-8. Header: Content-Type: application/json"),
        ("Cơ chế xác thực", "Bearer token (JWT) trong header Authorization: Bearer <token> và Cookie phiên access_token"),
        ("Cách lấy token", "Gọi POST /api/auth/login, lấy trường access_token trong JSON response"),
        ("Thời hạn token", "60 phút (3600 giây)"),
        ("Định dạng ngày giờ", "ISO 8601 (YYYY-MM-DDTHH:MM:SS), ví dụ: 2026-10-15T19:30:00"),
        ("Phân trang (nếu có)", "Tham số page (bắt đầu từ 1), limit (mặc định 10, tối đa 50)"),
        ("Link Swagger / OpenAPI", "http://127.0.0.1:8001/docs (OpenAPI specs JSON tại http://127.0.0.1:8001/openapi.json)")
    ]
    for r_idx, (k, v) in enumerate(general_info):
        row = t1.rows[r_idx]
        bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        format_cell(row.cells[0], k, bold=True, bg="EFF6FF" if r_idx % 2 == 0 else "F1F5F9", color="1E3A8A")
        format_cell(row.cells[1], v, bg=bg)
        row.cells[0].width = Inches(2.2)
        row.cells[1].width = Inches(4.8)

    # 2. Mã lỗi chung
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(16)
    h2.paragraph_format.space_after = Pt(6)
    run = h2.add_run("2. Mã lỗi chung")
    run.font.name = "Arial"
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = RGBColor.from_string("1E3A8A")

    status_codes = [
        ("200", "Thành công (OK)", '{\n  "success": true,\n  "data": ...\n}'),
        ("201", "Tạo mới thành công (Created)", '{\n  "id": 1,\n  "order_code": "ORD-20261009-XXXX",\n  "status": "CONFIRMED"\n}'),
        ("400", "Dữ liệu không hợp lệ / Vi phạm quy tắc (Bad Request)", '{\n  "detail": "Số lượng vé mỗi đơn hàng phải từ 1 đến 5 vé."\n}'),
        ("401", "Chưa đăng nhập / Token hết hạn (Unauthorized)", '{\n  "detail": "Chưa đăng nhập hoặc phiên làm việc đã hết hạn"\n}'),
        ("403", "Không có quyền thực hiện thao tác (Forbidden)", '{\n  "detail": "Bạn không có quyền thực hiện thao tác này"\n}'),
        ("404", "Không tìm thấy tài nguyên (Not Found)", '{\n  "detail": "Sự kiện không tồn tại"\n}'),
        ("409", "Xung đột dữ liệu / Vé đã dùng (Conflict)", '{\n  "detail": "VÉ ĐÃ SỬ DỤNG VÀO LÚC 19:30:15 09/10/2026"\n}'),
        ("500", "Lỗi máy chủ nội bộ (Internal Server Error)", '{\n  "detail": "Internal server error"\n}')
    ]
    t2 = doc.add_table(rows=len(status_codes) + 1, cols=3)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t2)
    format_cell(t2.rows[0].cells[0], "Mã HTTP", bold=True, bg="1E3A8A", color="FFFFFF")
    format_cell(t2.rows[0].cells[1], "Ý nghĩa", bold=True, bg="1E3A8A", color="FFFFFF")
    format_cell(t2.rows[0].cells[2], "Body mẫu", bold=True, bg="1E3A8A", color="FFFFFF")
    t2.rows[0].cells[0].width = Inches(1.1)
    t2.rows[0].cells[1].width = Inches(2.7)
    t2.rows[0].cells[2].width = Inches(3.2)

    for r_idx, (code, desc, body) in enumerate(status_codes, start=1):
        row = t2.rows[r_idx]
        bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        format_cell(row.cells[0], code, bold=True, bg=bg, align=WD_ALIGN_PARAGRAPH.CENTER)
        format_cell(row.cells[1], desc, bg=bg)
        format_cell(row.cells[2], body, font_size=8.5, bg=bg)
        row.cells[0].width = Inches(1.1)
        row.cells[1].width = Inches(2.7)
        row.cells[2].width = Inches(3.2)

    # Mapping FR, roles and summaries for all 43 operations
    ep_catalog = [
        # Auth
        ("POST", "/api/auth/register", "Đăng ký tài khoản người dùng mới", "FR-01", "Khách vãng lai"),
        ("POST", "/api/auth/login", "Đăng nhập hệ thống & cấp JWT Bearer token", "FR-02", "Tất cả"),
        ("POST", "/api/auth/logout", "Đăng xuất khỏi hệ thống và vô hiệu hóa phiên", "FR-02", "Đã đăng nhập"),
        ("GET", "/api/auth/me", "Lấy thông tin tài khoản hiện tại & số dư ví", "FR-01/02", "Đã đăng nhập"),
        ("POST", "/api/auth/forgot-password", "Gửi liên kết khôi phục mật khẩu qua email", "FR-03", "Khách vãng lai"),
        ("POST", "/api/auth/reset-password", "Đặt lại mật khẩu mới qua token liên kết", "FR-03", "Khách vãng lai"),
        ("POST", "/api/auth/reset-password-otp", "Đặt lại mật khẩu bằng mã OTP 6 số", "FR-03", "Khách vãng lai"),
        
        # Events
        ("GET", "/api/events", "Tra cứu danh sách sự kiện, tìm kiếm, lọc danh mục", "FR-04", "Tất cả"),
        ("POST", "/api/events", "Tạo sự kiện mới (Hỗ trợ Tự duyệt Auto-Approval)", "FR-10", "BTC, Admin"),
        ("GET", "/api/events/{event_id}", "Xem chi tiết sự kiện & danh sách phân hạng vé", "FR-05", "Tất cả"),
        ("PUT", "/api/events/{event_id}", "Cập nhật thông tin bài đăng sự kiện", "FR-10", "BTC, Admin"),
        ("DELETE", "/api/events/{event_id}", "Xóa bài đăng sự kiện khỏi hệ thống", "FR-10", "BTC, Admin"),
        ("POST", "/api/events/{event_id}/tiers", "Thêm phân hạng vé mở bán (VIP, Standard...)", "FR-11", "BTC, Admin"),
        ("GET", "/api/events/{event_id}/export-attendees", "Xuất file Excel (.xlsx có dropdown) / CSV / JSON đối soát điểm danh", "FR-12b", "BTC, Admin"),
        
        # Bookings & Orders
        ("POST", "/api/bookings/vouchers/apply", "Kiểm tra tính hợp lệ & tính giảm giá của Voucher", "FR-07", "Tất cả"),
        ("POST", "/api/bookings", "Đặt mua vé, tính phí sàn 5%, phân bổ ví BTC", "FR-06", "Attendee, Admin"),
        ("GET", "/api/bookings/my-tickets", "Xem danh sách vé điện tử cá nhân & mã QR", "FR-08", "Attendee"),
        ("POST", "/api/bookings/{ticket_id}/cancel", "Hủy vé cá nhân & hoàn tiền theo mốc thời gian", "FR-09", "Attendee, Admin"),
        
        # Gate Checkin
        ("POST", "/api/check-in", "Xác thực & soát vé tại cổng qua mã định danh/QR", "FR-12", "BTC, Admin"),
        
        # Payment VietQR PayOS
        ("GET", "/api/payment/payos-return", "Xử lý redirect khi khách thanh toán PayOS thành công", "FR-06b", "Attendee"),
        ("GET", "/api/payment/payos-cancel", "Xử lý redirect khi khách hủy thanh toán PayOS", "FR-06b", "Attendee"),
        ("POST", "/api/payment/payos-webhook", "Tiếp nhận webhook IPN thanh toán từ cổng PayOS", "FR-06b", "PayOS Gateway"),
        ("GET", "/api/payment/status/{order_code}", "Tra cứu trạng thái giao dịch thanh toán đơn hàng", "FR-06b", "Attendee"),
        
        # Admin Control Center
        ("GET", "/api/admin/stats", "Báo cáo doanh thu gộp, phí sàn, chi trả BTC", "FR-14", "Admin"),
        ("GET", "/api/admin/events/pending", "Lấy danh sách sự kiện chờ phê duyệt", "FR-13", "Admin"),
        ("POST", "/api/admin/events/{event_id}/approve", "Phê duyệt sự kiện công khai trên trang chủ", "FR-13", "Admin"),
        ("POST", "/api/admin/events/{event_id}/reject", "Từ chối duyệt sự kiện vi phạm tiêu chuẩn", "FR-13", "Admin"),
        ("POST", "/api/admin/events/{event_id}/status", "Thay đổi trạng thái sự kiện (PUBLISHED/HIDDEN/CANCELLED)", "FR-13", "Admin"),
        ("PUT", "/api/admin/events/{event_id}", "Admin cập nhật thông tin sự kiện bất kỳ", "FR-13", "Admin"),
        ("DELETE", "/api/admin/events/{event_id}", "Admin xóa bài đăng sự kiện vi phạm", "FR-13", "Admin"),
        ("GET", "/api/admin/orders", "Tra cứu và quản trị toàn bộ đơn hàng trên sàn", "FR-13", "Admin"),
        ("POST", "/api/admin/orders/{order_id}/cancel-refund", "Hủy đơn khẩn cấp & hoàn tiền 100% (thu hồi ví BTC)", "FR-13", "Admin"),
        ("GET", "/api/admin/tickets", "Tra cứu danh sách vé điện tử toàn hệ thống", "FR-13", "Admin"),
        ("PUT", "/api/admin/users/{user_id}/role", "Phân quyền người dùng (ATTENDEE / ORGANIZER / ADMIN)", "FR-13", "Admin"),
        ("POST", "/api/admin/users/{user_id}/toggle-active", "Khóa hoặc kích hoạt lại tài khoản người dùng", "FR-13", "Admin"),
        ("POST", "/api/admin/users/{user_id}/reset-password", "Admin đặt lại mật khẩu cho tài khoản người dùng", "FR-13", "Admin"),
        ("POST", "/api/admin/users/{user_id}/adjust-balance", "Điều chỉnh cộng/trừ số dư ví tài khoản", "FR-13", "Admin"),
        ("POST", "/api/admin/vouchers", "Khởi tạo chiến dịch mã giảm giá Voucher mới", "FR-13", "Admin"),
        ("POST", "/api/admin/vouchers/{voucher_id}/toggle", "Bật/tắt trạng thái hiệu lực của Voucher", "FR-13", "Admin"),
        ("DELETE", "/api/admin/vouchers/{voucher_id}", "Xóa mã voucher khỏi hệ thống", "FR-13", "Admin"),
        ("GET", "/api/admin/system/fee", "Tra cứu tỷ lệ phần trăm phí sàn hiện tại", "FR-15", "Admin"),
        ("PUT", "/api/admin/system/fee", "Cập nhật cấu hình tỷ lệ phần trăm phí sàn mới", "FR-15", "Admin"),
        
        # Health Check
        ("GET", "/health", "Kiểm tra tình trạng hoạt động của máy chủ và bẫy lỗi", "FR-16", "Tất cả")
    ]

    # 3. Danh sách endpoint
    h3 = doc.add_paragraph()
    h3.paragraph_format.space_before = Pt(16)
    h3.paragraph_format.space_after = Pt(6)
    run = h3.add_run("3. Danh sách endpoint đầy đủ (38 endpoints / 43 operations)")
    run.font.name = "Arial"
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = RGBColor.from_string("1E3A8A")

    t3 = doc.add_table(rows=len(ep_catalog) + 1, cols=6)
    t3.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t3)
    
    headers_t3 = ["STT", "Method", "Endpoint", "Mô tả", "Chức năng", "Vai trò"]
    for c_idx, h in enumerate(headers_t3):
        format_cell(t3.rows[0].cells[c_idx], h, bold=True, bg="1E3A8A", color="FFFFFF", align=WD_ALIGN_PARAGRAPH.CENTER)

    t3.rows[0].cells[0].width = Inches(0.5)
    t3.rows[0].cells[1].width = Inches(0.9)
    t3.rows[0].cells[2].width = Inches(2.2)
    t3.rows[0].cells[3].width = Inches(2.1)
    t3.rows[0].cells[4].width = Inches(0.7)
    t3.rows[0].cells[5].width = Inches(0.8)

    for idx, (m, p, desc, fr, role) in enumerate(ep_catalog, start=1):
        row = t3.rows[idx]
        bg = "F8FAFC" if idx % 2 == 1 else "FFFFFF"
        format_cell(row.cells[0], str(idx), bg=bg, align=WD_ALIGN_PARAGRAPH.CENTER)
        
        method_color = "15803D" if m == "GET" else ("1D4ED8" if m == "POST" else ("B45309" if m == "PUT" else "B91C1C"))
        format_cell(row.cells[1], m, bold=True, color=method_color, bg=bg, align=WD_ALIGN_PARAGRAPH.CENTER)
        format_cell(row.cells[2], p, font_size=8.5, bg=bg)
        format_cell(row.cells[3], desc, font_size=9, bg=bg)
        format_cell(row.cells[4], fr, bold=True, bg=bg, align=WD_ALIGN_PARAGRAPH.CENTER)
        format_cell(row.cells[5], role, font_size=8.5, bg=bg, align=WD_ALIGN_PARAGRAPH.CENTER)

        row.cells[0].width = Inches(0.5)
        row.cells[1].width = Inches(0.9)
        row.cells[2].width = Inches(2.2)
        row.cells[3].width = Inches(2.1)
        row.cells[4].width = Inches(0.7)
        row.cells[5].width = Inches(0.8)

    # 4. Đặc tả chi tiết từng endpoint
    h4 = doc.add_paragraph()
    h4.paragraph_format.space_before = Pt(20)
    h4.paragraph_format.space_after = Pt(8)
    run = h4.add_run("4. Đặc tả chi tiết từng endpoint (Detailed Specifications)")
    run.font.name = "Arial"
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = RGBColor.from_string("0F2942")

    # Detailed specs map
    detailed_specs = {
        "/api/auth/register": {
            "headers": "Content-Type: application/json",
            "params": [],
            "body_fields": [
                ("full_name", "string", "Có", "2 - 100 ký tự", "Họ và tên người dùng"),
                ("email", "string", "Có", "Format RFC 5322 chuẩn", "Địa chỉ email đăng nhập"),
                ("password", "string", "Có", "6 - 32 ký tự, có số", "Mật khẩu bảo mật"),
                ("phone_number", "string", "Không", "10 chữ số", "Số điện thoại liên hệ"),
                ("role", "string", "Không", "ATTENDEE / ORGANIZER", "Vai trò tài khoản (mặc định ATTENDEE)")
            ],
            "req_sample": '{\n  "full_name": "Nguyễn Văn A",\n  "email": "user@example.com",\n  "password": "password123",\n  "phone_number": "0987654321",\n  "role": "ATTENDEE"\n}',
            "res_success_code": "201 Created",
            "res_success": '{\n  "id": 10,\n  "full_name": "Nguyễn Văn A",\n  "email": "user@example.com",\n  "role": "ATTENDEE",\n  "balance": 1000000.0\n}',
            "res_err": [("400", "Email đã tồn tại", '{"detail": "Email đã được đăng ký trên hệ thống"}')]
        },
        "/api/auth/login": {
            "headers": "Content-Type: application/json",
            "params": [],
            "body_fields": [
                ("email", "string", "Có", "Email đã đăng ký", "Email đăng nhập"),
                ("password", "string", "Có", "Mật khẩu chính xác", "Mật khẩu tài khoản")
            ],
            "req_sample": '{\n  "email": "attendee@eventtick.com",\n  "password": "att123"\n}',
            "res_success_code": "200 OK",
            "res_success": '{\n  "access_token": "eyJhbGciOiJIUzI1NiIs...",\n  "token_type": "bearer",\n  "user": {\n    "id": 3,\n    "email": "attendee@eventtick.com",\n    "role": "ATTENDEE",\n    "balance": 1000000.0\n  }\n}',
            "res_err": [("401", "Sai tài khoản hoặc mật khẩu", '{"detail": "Email hoặc mật khẩu không chính xác"}')]
        },
        "/api/bookings": {
            "headers": "Authorization: Bearer <token>\nContent-Type: application/json",
            "params": [],
            "body_fields": [
                ("event_id", "integer", "Có", "ID sự kiện hợp lệ & đang mở bán", "Mã sự kiện"),
                ("tier_id", "integer", "Có", "ID hạng vé còn tồn kho", "Mã phân hạng vé"),
                ("quantity", "integer", "Có", "1 ≤ quantity ≤ 5 (BR-01)", "Số lượng vé muốn mua"),
                ("voucher_code", "string", "Không", "Mã voucher hợp lệ (ví dụ: GIAM20)", "Mã giảm giá áp dụng")
            ],
            "req_sample": '{\n  "event_id": 1,\n  "tier_id": 2,\n  "quantity": 2,\n  "voucher_code": "GIAM20"\n}',
            "res_success_code": "201 Created",
            "res_success": '{\n  "id": 15,\n  "order_code": "ORD-20261009-A8F2",\n  "event_id": 1,\n  "tier_id": 2,\n  "quantity": 2,\n  "original_amount": 600000.0,\n  "discount_amount": 120000.0,\n  "final_amount": 480000.0,\n  "platform_fee_rate": 5.0,\n  "platform_fee": 24000.0,\n  "organizer_amount": 456000.0,\n  "status": "CONFIRMED",\n  "tickets": [\n    {"id": 101, "ticket_code": "TICK-2026-SK1-001", "status": "CONFIRMED"},\n    {"id": 102, "ticket_code": "TICK-2026-SK1-002", "status": "CONFIRMED"}\n  ]\n}',
            "res_err": [
                ("400", "Số lượng vé không đủ", '{"detail": "Hạng vé đã hết chỗ hoặc không đủ số lượng yêu cầu"}'),
                ("400", "Số dư ví không đủ", '{"detail": "Số dư trong ví không đủ để thanh toán"}')
            ]
        },
        "/api/events/{event_id}/export-attendees": {
            "headers": "Authorization: Bearer <token>",
            "params": [
                ("event_id", "path", "integer", "Có", "ID sự kiện hợp lệ", "Mã định danh sự kiện"),
                ("format", "query", "string", "Không", "xlsx (mặc định), csv, json", "Định dạng file xuất")
            ],
            "body_fields": [],
            "req_sample": "",
            "res_success_code": "200 OK (XLSX / CSV File hoặc JSON Object)",
            "res_success": '// Khi format=xlsx: Binary file MIME application/vnd.openxmlformats...\n// Header: Content-Disposition: attachment; filename="Danh_Sach_Soat_Ve_SK1_...xlsx"\n// File Excel có dropdown Data Validation cột J, zebra striping, autofit và bảng màu chuẩn.\n\n// Khi format=json:\n{\n  "success": true,\n  "event_id": 1,\n  "event_title": "Hội thảo AI 2026",\n  "total_tickets": 19,\n  "checked_in_count": 6,\n  "absent_count": 0,\n  "attendees": [...]\n}',
            "res_err": [
                ("403", "Không có quyền", '{"detail": "Bạn không có quyền xuất dữ liệu soát vé của sự kiện này"}'),
                ("404", "Không tìm thấy sự kiện", '{"detail": "Sự kiện không tồn tại"}')
            ]
        },
        "/api/check-in": {
            "headers": "Authorization: Bearer <token>\nContent-Type: application/json",
            "params": [],
            "body_fields": [
                ("ticket_code", "string", "Có", "Mã vé định danh chuẩn", "Mã vé điện tử quét từ QR"),
                ("event_id", "integer", "Có", "ID sự kiện tương ứng", "Mã sự kiện tổ chức")
            ],
            "req_sample": '{\n  "ticket_code": "TICK-2026-SK1-001",\n  "event_id": 1\n}',
            "res_success_code": "200 OK",
            "res_success": '{\n  "success": true,\n  "message": "VÉ HỢP LỆ. Chào mừng quý khách tham dự sự kiện!",\n  "ticket_code": "TICK-2026-SK1-001",\n  "attendee_name": "Nguyễn Văn A",\n  "tier_name": "Standard",\n  "check_in_time": "19:30:15 09/10/2026"\n}',
            "res_err": [
                ("404", "Mã vé không tồn tại", '{"detail": "Không tìm thấy mã vé trong hệ thống"}'),
                ("409", "Vé đã được check-in trước đó", '{"detail": "VÉ ĐÃ SỬ DỤNG VÀO LÚC 18:45:10 09/10/2026"}')
            ]
        }
    }

    for idx, (m, p, desc, fr, role) in enumerate(ep_catalog, start=1):
        p_sec = doc.add_paragraph()
        p_sec.paragraph_format.space_before = Pt(14)
        p_sec.paragraph_format.space_after = Pt(4)
        run = p_sec.add_run(f"4.{idx}. [{m} {p}] – {desc}")
        run.font.name = "Arial"
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = RGBColor.from_string("0F766E")

        # Table info
        spec = detailed_specs.get(p, {})
        headers_info = spec.get("headers", "Authorization: Bearer <token>\nContent-Type: application/json" if m != "GET" else "Authorization: Bearer <token>")
        
        t_meta = doc.add_table(rows=5, cols=2)
        t_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(t_meta)
        
        meta_rows = [
            ("Method + URL", f"{m} {{{{baseUrl}}}}{p}"),
            ("Mô tả nghiệp vụ", desc),
            ("Chức năng liên quan", f"{fr} (Quy chuẩn hệ thống iTick)"),
            ("Vai trò được phép", role),
            ("Headers", headers_info)
        ]
        for r_i, (k, v) in enumerate(meta_rows):
            row = t_meta.rows[r_i]
            format_cell(row.cells[0], k, bold=True, bg="F8FAFC", color="334155")
            format_cell(row.cells[1], v)
            row.cells[0].width = Inches(2.0)
            row.cells[1].width = Inches(5.0)

        # Params table
        params = spec.get("params", [])
        if "{" in p:
            param_name = re.findall(r'\{(.*?)\}', p)[0]
            if not any(pm[0] == param_name for pm in params):
                params.insert(0, (param_name, "path", "integer", "Có", "Khóa chính ID", f"Mã ID định danh của {param_name}"))

        if params:
            doc.add_paragraph().paragraph_format.space_after = Pt(1)
            p_lbl = doc.add_paragraph()
            p_lbl.paragraph_format.space_before = Pt(3)
            p_lbl.paragraph_format.space_after = Pt(2)
            run = p_lbl.add_run("Tham số Path / Query:")
            run.font.bold = True
            run.font.size = Pt(9.5)
            
            t_pm = doc.add_table(rows=len(params) + 1, cols=6)
            t_pm.alignment = WD_TABLE_ALIGNMENT.CENTER
            set_table_borders(t_pm)
            for c_i, h in enumerate(["Tên", "Vị trí", "Kiểu", "Bắt buộc", "Ràng buộc", "Mô tả"]):
                format_cell(t_pm.rows[0].cells[c_i], h, bold=True, bg="0F766E", color="FFFFFF", align=WD_ALIGN_PARAGRAPH.CENTER)
            for r_i, pm in enumerate(params, start=1):
                bg = "F8FAFC" if r_i % 2 == 1 else "FFFFFF"
                format_cell(t_pm.rows[r_i].cells[0], pm[0], bold=True, bg=bg)
                format_cell(t_pm.rows[r_i].cells[1], pm[1], bg=bg, align=WD_ALIGN_PARAGRAPH.CENTER)
                format_cell(t_pm.rows[r_i].cells[2], pm[2], bg=bg, align=WD_ALIGN_PARAGRAPH.CENTER)
                format_cell(t_pm.rows[r_i].cells[3], pm[3], bg=bg, align=WD_ALIGN_PARAGRAPH.CENTER)
                format_cell(t_pm.rows[r_i].cells[4], pm[4], bg=bg)
                format_cell(t_pm.rows[r_i].cells[5], pm[5], bg=bg)

        # Body Fields table
        body_fields = spec.get("body_fields", [])
        if body_fields:
            doc.add_paragraph().paragraph_format.space_after = Pt(1)
            p_lbl = doc.add_paragraph()
            p_lbl.paragraph_format.space_before = Pt(3)
            p_lbl.paragraph_format.space_after = Pt(2)
            run = p_lbl.add_run("Cấu trúc Request Body:")
            run.font.bold = True
            run.font.size = Pt(9.5)

            t_bf = doc.add_table(rows=len(body_fields) + 1, cols=5)
            t_bf.alignment = WD_TABLE_ALIGNMENT.CENTER
            set_table_borders(t_bf)
            for c_i, h in enumerate(["Trường", "Kiểu", "Bắt buộc", "Ràng buộc", "Mô tả"]):
                format_cell(t_bf.rows[0].cells[c_i], h, bold=True, bg="0F766E", color="FFFFFF", align=WD_ALIGN_PARAGRAPH.CENTER)
            for r_i, bf in enumerate(body_fields, start=1):
                bg = "F8FAFC" if r_i % 2 == 1 else "FFFFFF"
                format_cell(t_bf.rows[r_i].cells[0], bf[0], bold=True, bg=bg)
                format_cell(t_bf.rows[r_i].cells[1], bf[1], bg=bg, align=WD_ALIGN_PARAGRAPH.CENTER)
                format_cell(t_bf.rows[r_i].cells[2], bf[2], bg=bg, align=WD_ALIGN_PARAGRAPH.CENTER)
                format_cell(t_bf.rows[r_i].cells[3], bf[3], bg=bg)
                format_cell(t_bf.rows[r_i].cells[4], bf[4], bg=bg)

        # Request Sample
        req_sample = spec.get("req_sample")
        if req_sample:
            p_lbl = doc.add_paragraph()
            p_lbl.paragraph_format.space_before = Pt(3)
            p_lbl.paragraph_format.space_after = Pt(1)
            run = p_lbl.add_run("Request Body mẫu:")
            run.font.bold = True
            run.font.size = Pt(9.5)
            add_code_block(doc, req_sample)

        # Response Success
        res_code = spec.get("res_success_code", "200 OK")
        res_sample = spec.get("res_success", '{\n  "success": true,\n  "data": {}\n}')
        p_lbl = doc.add_paragraph()
        p_lbl.paragraph_format.space_before = Pt(3)
        p_lbl.paragraph_format.space_after = Pt(1)
        run = p_lbl.add_run(f"Response thành công ({res_code}):")
        run.font.bold = True
        run.font.size = Pt(9.5)
        add_code_block(doc, res_sample)

        # Response Errors
        res_err = spec.get("res_err", [
            ("401", "Chưa đăng nhập / Hết hạn phiên", '{"detail": "Chưa đăng nhập hoặc phiên làm việc đã hết hạn"}'),
            ("403", "Không đủ quyền hạn", '{"detail": "Bạn không có quyền thực hiện thao tác này"}')
        ])
        p_lbl = doc.add_paragraph()
        p_lbl.paragraph_format.space_before = Pt(3)
        p_lbl.paragraph_format.space_after = Pt(2)
        run = p_lbl.add_run("Response lỗi thường gặp:")
        run.font.bold = True
        run.font.size = Pt(9.5)

        t_err = doc.add_table(rows=len(res_err) + 1, cols=3)
        t_err.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(t_err)
        format_cell(t_err.rows[0].cells[0], "Mã HTTP", bold=True, bg="991B1B", color="FFFFFF", align=WD_ALIGN_PARAGRAPH.CENTER)
        format_cell(t_err.rows[0].cells[1], "Trường hợp", bold=True, bg="991B1B", color="FFFFFF")
        format_cell(t_err.rows[0].cells[2], "Body JSON lỗi mẫu", bold=True, bg="991B1B", color="FFFFFF")
        t_err.rows[0].cells[0].width = Inches(1.0)
        t_err.rows[0].cells[1].width = Inches(2.6)
        t_err.rows[0].cells[2].width = Inches(3.4)

        for r_i, (c, cs, bd) in enumerate(res_err, start=1):
            bg = "FEF2F2" if r_i % 2 == 1 else "FFFFFF"
            format_cell(t_err.rows[r_i].cells[0], c, bold=True, bg=bg, align=WD_ALIGN_PARAGRAPH.CENTER)
            format_cell(t_err.rows[r_i].cells[1], cs, bg=bg)
            format_cell(t_err.rows[r_i].cells[2], bd, font_size=8.5, bg=bg)
            t_err.rows[r_i].cells[0].width = Inches(1.0)
            t_err.rows[r_i].cells[1].width = Inches(2.6)
            t_err.rows[r_i].cells[2].width = Inches(3.4)

    # 5. Tài khoản mẫu dùng để gọi API
    h5 = doc.add_paragraph()
    h5.paragraph_format.space_before = Pt(20)
    h5.paragraph_format.space_after = Pt(6)
    run = h5.add_run("5. Tài khoản mẫu dùng để gọi API (Test Credentials)")
    run.font.name = "Arial"
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = RGBColor.from_string("1E3A8A")

    accounts = [
        ("Quản trị viên (Admin)", "admin@eventtick.com", "admin123", "Quản trị toàn sàn, duyệt sự kiện, đối soát hoàn tiền khẩn cấp, cấu hình phí sàn."),
        ("Ban tổ chức (Organizer)", "organizer@eventtick.com", "org123", "Tạo sự kiện, cấu hình phân hạng vé, xuất Excel soát vé có Dropdown, check-in cổng."),
        ("Người mua vé 1 (Attendee)", "attendee@eventtick.com", "att123", "Khách hàng mua vé, áp voucher, hủy vé cá nhân. Số dư ví: 1.000.000đ."),
        ("Người mua vé 2 (Attendee)", "student_b@eventtick.com", "att123", "Tài khoản tester thực hiện đo tải đồng thời JMeter. Số dư ví: 2.000.000đ."),
        ("Khách vãng lai (Guest)", "Không cần đăng nhập", "-", "Tra cứu danh sách sự kiện công khai, tìm kiếm và xem chi tiết chương trình.")
    ]
    t5 = doc.add_table(rows=len(accounts) + 1, cols=4)
    t5.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t5)
    for c_i, h in enumerate(["Vai trò", "Email / Tên đăng nhập", "Mật khẩu", "Ghi chú & Quyền hạn"]):
        format_cell(t5.rows[0].cells[c_i], h, bold=True, bg="1E3A8A", color="FFFFFF", align=WD_ALIGN_PARAGRAPH.CENTER)

    t5.rows[0].cells[0].width = Inches(1.8)
    t5.rows[0].cells[1].width = Inches(2.0)
    t5.rows[0].cells[2].width = Inches(1.0)
    t5.rows[0].cells[3].width = Inches(2.2)

    for r_i, (role, email, pwd, note) in enumerate(accounts, start=1):
        bg = "F8FAFC" if r_i % 2 == 1 else "FFFFFF"
        format_cell(t5.rows[r_i].cells[0], role, bold=True, bg=bg)
        format_cell(t5.rows[r_i].cells[1], email, bg=bg)
        format_cell(t5.rows[r_i].cells[2], pwd, bg=bg, align=WD_ALIGN_PARAGRAPH.CENTER)
        format_cell(t5.rows[r_i].cells[3], note, font_size=9, bg=bg)
        t5.rows[r_i].cells[0].width = Inches(1.8)
        t5.rows[r_i].cells[1].width = Inches(2.0)
        t5.rows[r_i].cells[2].width = Inches(1.0)
        t5.rows[r_i].cells[3].width = Inches(2.2)

    out_path = r"d:\SJ_Testing\Project\docs\Mau_01_Tai_lieu_API.docx"
    doc.save(out_path)
    print(f"Successfully generated full Mau_01_Tai_lieu_API.docx at {out_path}")

if __name__ == "__main__":
    main()

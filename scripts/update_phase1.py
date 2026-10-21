# -*- coding: utf-8 -*-
"""
Script cập nhật Giai đoạn 1:
1. Mau_03_Bo_bieu_mau_Kiem_thu.xlsx: Sheet Thong_tin và Review_SRS
2. Mau_04_Test_Plan.docx: Điền đầy đủ thông tin vào các đoạn văn và 11 bảng chuẩn
"""
import openpyxl
import docx

def update_mau_03():
    excel_path = r'd:\SJ_Testing\Project\docs\Mau_03_Bo_bieu_mau_Kiem_thu.xlsx'
    wb = openpyxl.load_workbook(excel_path)
    
    # 1. Update Sheet Thong_tin
    ws_info = wb['Thong_tin']
    ws_info['B4'] = 'Sinh viên B'
    ws_info['B5'] = 'SV20260002'
    ws_info['B6'] = 'EventTick - Nền tảng Bán vé Sự kiện Trực tuyến'
    ws_info['B7'] = 'Sinh viên A - SV20260001'
    ws_info['B8'] = 'http://127.0.0.1:8001'
    ws_info['B9'] = 'SRS v1.1 (đã chốt sau review)'
    ws_info['B10'] = '15/10/2026 – 05/11/2026 (Tuần 5 – Tuần 13)'
    
    # 2. Update Sheet Review_SRS
    ws_rev = wb['Review_SRS']
    # Clear old example rows if any
    for r in range(5, 20):
        for c in range(1, 10):
            ws_rev.cell(row=r, column=c, value=None)
            
    reviews = [
        (1, 'FR-03 – Mô tả sự kiện', '"Mô tả sự kiện: Văn bản chi tiết giới thiệu nội dung sự kiện"', 
         'Thiếu giới hạn độ dài tối đa (max_length), nguy cơ tràn bộ nhớ và vỡ layout giao diện khi nhập văn bản quá dài', 
         'Thiếu', 'Cao', 
         'Quy định rõ độ dài tối đa từ 10 đến 5.000 ký tự UTF-8; hiển thị bộ đếm ký tự trên giao diện', 
         'Chấp nhận', 'Đã bổ sung ràng buộc max_length=5000 ký tự trong SRS v1.1 mục 3 (FR-03)'),
         
        (2, 'FR-06 & BR-02 – Tồn kho vé', '"Hệ thống kiểm tra số lượng vé còn lại và trừ tồn kho vé khả dụng"', 
         'Mơ hồ về cơ chế xử lý tranh chấp tài nguyên (Concurrency / Race Condition) khi nhiều khách cùng mua những vé cuối', 
         'Mơ hồ', 'Cao', 
         'Đặc tả rõ cơ chế Atomic Transaction / Database Locking (SELECT FOR UPDATE) để ngăn chặn bán âm kho (Overselling)', 
         'Chấp nhận', 'Đã bổ sung BR-02 và NFR-02 trong SRS v1.1: Bắt buộc dùng atomic locking tránh bán vượt vé'),
         
        (3, 'FR-07 & BR-03 – Mã giảm giá', '"Voucher giảm 20% tổng giá trị đơn hàng"', 
         'Thiếu quy định về trần giảm giá tối đa (Max Discount Cap) khi giảm theo %, gây thất thoát doanh thu cho đơn hàng lớn', 
         'Thiếu', 'Cao', 
         'Quy định rõ mọi voucher theo % bắt buộc có thuộc tính max_discount_cap (Ví dụ GIAM20 tối đa 150.000đ)', 
         'Chấp nhận', 'Đã bổ sung BR-03 trong SRS v1.1: Áp dụng trần giảm giá tối đa cho mọi voucher theo %'),
         
        (4, 'FR-09 & BR-05 – Hủy vé hoàn tiền', '"Hoàn 90% trước sự kiện > 48h; hoàn 70% từ 24-48h; từ chối hủy < 24h"', 
         'Không quy định rõ độ chính xác thời gian (theo giây hay làm tròn giờ) và múi giờ hệ thống (UTC hay GMT+7)', 
         'Không kiểm thử được', 'Trung bình', 
         'Quy định rõ thời gian đối chiếu là (start_time - cancellation_time), múi giờ Asia/Ho_Chi_Minh (GMT+7), tính đến từng giây', 
         'Chấp nhận', 'Đã bổ sung quy ước tính thời gian chi tiết theo GMT+7 trong SRS v1.1 mục 5 (BR-05)'),
         
        (5, 'NFR-01 & NFR-03 – Hiệu năng API', '"Thời gian phản hồi API <= 500ms; Throughput >= 50 req/s"', 
         'Chưa nêu rõ cấu hình phần cứng tối thiểu của môi trường máy chủ thử nghiệm và băng thông mạng chuẩn', 
         'Không kiểm thử được', 'Trung bình', 
         'Đặc tả cấu hình chuẩn máy chủ test: 2 vCPU, 4GB RAM, SSD, môi trường Localhost/LAN độ trễ < 5ms', 
         'Chấp nhận', 'Đã bổ sung đặc tả môi trường đo kiểm chuẩn trong SRS v1.1 mục 7.1'),
         
        (6, 'FR-12 & BR-04 – Cổng soát vé', '"Hệ thống xác thực mã vé và ghi nhận thời gian khách vào cổng"', 
         'Mâu thuẫn logic: Chưa quy định hành vi khi nhân viên quét nhầm mã vé đã bị hủy (CANCELLED) hoặc vé hết hạn', 
         'Mâu thuẫn', 'Cao', 
         'Bắt buộc từ chối check-in mọi vé có trạng thái khác ISSUED; nếu vé CANCELLED phải báo lỗi đỏ rõ ràng', 
         'Chấp nhận', 'Đã bổ sung BR-04 trong SRS v1.1: Tuyệt đối không cho phép check-in vé đã hủy/hết hạn')
    ]
    
    for idx, item in enumerate(reviews):
        row = 5 + idx
        for col_idx, val in enumerate(item):
            ws_rev.cell(row=row, column=col_idx+1, value=val)
            
    wb.save(excel_path)
    print("-> Updated Mau_03: Thong_tin and Review_SRS successfully!")

def update_mau_04():
    doc_path = r'd:\SJ_Testing\Project\docs\Mau_04_Test_Plan.docx'
    doc = docx.Document(doc_path)
    
    # 1. Update Paragraphs
    doc.paragraphs[1].text = "Hệ thống được kiểm thử: EventTick - Nền tảng Bán vé Sự kiện Trực tuyến  ·  Phiên bản tài liệu: 1.0"
    doc.paragraphs[5].text = (
        "Xác nhận toàn diện các chức năng và yêu cầu phi chức năng của hệ thống EventTick, "
        "đảm bảo phần mềm đáp ứng đầy đủ và chuẩn xác các đặc tả kỹ thuật trong SRS v1.1. "
        "Đồng thời phát hiện sớm các khiếm khuyết phần mềm (Functional, Visual, Content, Performance, Crash), "
        "đo lường khả năng chịu tải và cung cấp dữ liệu bằng chứng nghiệm thu hệ thống trước khi triển khai chính thức."
    )
    
    # Table 1: Thông tin
    t1 = doc.tables[0]
    t1.rows[0].cells[1].text = "Sinh viên B – SV20260002"
    t1.rows[1].cells[1].text = "Sinh viên A – SV20260001"
    t1.rows[2].cells[1].text = "http://127.0.0.1:8001"
    t1.rows[3].cells[1].text = "15/10/2026"
    
    # Table 2: Tài liệu tham chiếu
    t2 = doc.tables[1]
    t2.rows[1].cells[1].text = "1.0"
    t2.rows[1].cells[2].text = "Tài liệu Yêu cầu Người dùng: 3 vai trò, 15 User Stories chuẩn Given-When-Then"
    t2.rows[2].cells[1].text = "1.1"
    t2.rows[2].cells[2].text = "Đặc tả Yêu cầu Phần mềm: 14 Chức năng (FR-01..FR-14), 4 Luồng, 8 Yêu cầu Phi chức năng"
    t2.rows[3].cells[1].text = "1.0"
    t2.rows[3].cells[2].text = "Đặc tả 43 API operations, mô hình dữ liệu Request/Response/Status Code chi tiết"
    t2.rows[4].cells[1].text = "1.0"
    t2.rows[4].cells[2].text = "Phiếu Review SRS ghi nhận 6 vấn đề phản biện đã được Chủ hệ thống tiếp thu"

    # Table 3: Phạm vi kiểm thử (Trong phạm vi)
    t3 = doc.tables[2]
    # Keep header, clear remaining rows
    scope_data = [
        ("FR-01", "Đăng ký, Đăng nhập & Xác thực JWT", "Cao", "Thủ công (EP, BVA, Decision Table), Postman API"),
        ("FR-02", "Quản lý Hồ sơ & Ví điện tử nội bộ", "Trung bình", "Thủ công (EP, BVA), Postman API"),
        ("FR-03", "Quản lý & Khởi tạo Sự kiện", "Cao", "Thủ công (EP, BVA), Postman API"),
        ("FR-04", "Tìm kiếm, Lọc sự kiện & Phân trang", "Cao", "Thủ công (BVA, Error Guessing), Postman, Puppeteer"),
        ("FR-05", "Xem Chi tiết Sự kiện & Hạng vé", "Cao", "Thủ công (EP, Decision Table), Puppeteer"),
        ("FR-06", "Đặt vé & Kiểm soát Tồn kho Đồng thời", "Khẩn cấp", "Thủ công (BVA, EP), Postman data-driven, JMeter Concurrency"),
        ("FR-07", "Áp dụng Mã giảm giá Voucher", "Cao", "Thủ công (EP, BVA, Decision Table), Postman"),
        ("FR-08", "Thanh toán Ví nội bộ & VietQR PayOS", "Cao", "Thủ công (Decision Table, State Transition), Postman API"),
        ("FR-09", "Hủy vé & Hoàn tiền theo mốc Timeline", "Cao", "Thủ công (State Transition, BVA), Postman API"),
        ("FR-10", "Quản lý Người tham gia & Xuất Excel Soát vé", "Trung bình", "Thủ công, Puppeteer E2E"),
        ("FR-11", "Quản trị Hệ thống Toàn sàn (Admin RBAC)", "Cao", "Kiểm thử Phân quyền RBAC, Postman API"),
        ("FR-12", "Cổng Soát vé Check-in Trực tuyến", "Khẩn cấp", "Thủ công (State Transition), Puppeteer E2E, Postman"),
        ("FR-13", "Thống kê Doanh thu Ban tổ chức", "Trung bình", "Thủ công (Decision Table), Postman API"),
        ("FR-14", "Lịch sử Đơn hàng & Vé điện tử của Khách", "Trung bình", "Thủ công (EP), Postman API"),
        ("FLOW-01", "Luồng Đặt vé & Thanh toán Ví hoàn tất", "Khẩn cấp", "E2E thủ công, Puppeteer E2E, Postman Newman, JMeter"),
        ("FLOW-02", "Luồng Tạo sự kiện & Phê duyệt Sự kiện Admin", "Cao", "E2E thủ công, Puppeteer"),
        ("FLOW-03", "Luồng Soát vé Check-in & Xuất Báo cáo Tham dự", "Khẩn cấp", "E2E thủ công, Puppeteer E2E"),
        ("FLOW-04", "Luồng Yêu cầu Hủy vé & Hoàn tiền theo Timeline", "Cao", "E2E thủ công, Postman API"),
        ("NFR-01", "Thời gian phản hồi API (Response time <= 500ms)", "Cao", "JMeter Load Test (50 Threads), Newman CLI"),
        ("NFR-02", "Kiểm soát Đồng thời (0% Overselling, Lock)", "Khẩn cấp", "JMeter Concurrency Test (100 Threads)"),
        ("NFR-03", "Khả năng chịu tải (Throughput >= 50 req/s, Lỗi < 1%)", "Cao", "JMeter Stress & Ramp-up Test"),
        ("NFR-04", "Thời gian tải trang giao diện UI (<= 2.0s)", "Trung bình", "Chrome DevTools Network, Puppeteer"),
        ("NFR-05", "Bảo mật Xác thực Token & Phân quyền RBAC", "Cao", "Postman Negative Tests, OWASP Security Checklist"),
        ("NFR-06", "Bảo mật Dữ liệu & Chống Tiêm mã (SQLi, Crash 500)", "Khẩn cấp", "Postman Security & Boundary Tests"),
        ("NFR-07", "Độ tin cậy & Phục hồi sự cố (Graceful Degradation)", "Cao", "Manual Error Guessing, Fault Injection Test"),
        ("NFR-08", "Tương thích Đa trình duyệt & Thiết bị di động", "Trung bình", "Chrome, Edge, Firefox, Responsive DevTools")
    ]
    
    # Adjust table rows for t3
    while len(t3.rows) > 1:
        tr = t3.rows[-1]._tr
        t3._tbl.remove(tr)
    for row_val in scope_data:
        row = t3.add_row()
        for c_idx, val in enumerate(row_val):
            row.cells[c_idx].text = val

    # Table 4: Ngoài phạm vi
    t4 = doc.tables[3]
    while len(t4.rows) > 1:
        tr = t4.rows[-1]._tr
        t4._tbl.remove(tr)
    out_scope = [
        ("Cổng thanh toán thật của Ngân hàng", "Hệ thống chỉ thử nghiệm trên Cổng Sandbox PayOS và Ví điện tử nội bộ"),
        ("Hạ tầng CDN & Trung tâm dữ liệu vật lý", "Kiểm thử thực hiện trên máy chủ ứng dụng chạy cục bộ và mạng nội bộ thử nghiệm"),
        ("Kiểm thử thâm nhập nâng cao (Penetration Test)", "Chỉ tập trung kiểm thử lỗ hổng logic nghiệp vụ, xác thực JWT, RBAC và SQL Injection cơ bản")
    ]
    for row_val in out_scope:
        row = t4.add_row()
        for c_idx, val in enumerate(row_val):
            row.cells[c_idx].text = val

    # Table 5: Chiến lược kiểm thử
    t5 = doc.tables[4]
    strat_data = [
        ("Chức năng (thủ công)", "Phân hoạch tương đương, giá trị biên, bảng quyết định, chuyển trạng thái", "FR-01 … FR-14"),
        ("Luồng nghiệp vụ E2E", "Use case kịch bản: luồng chính, luồng thay thế, luồng ngoại lệ", "FLOW-01 … FLOW-04"),
        ("Phân quyền RBAC", "Ma trận phân quyền; kiểm tra giao diện và gọi API trực tiếp", "Toàn bộ API yêu cầu quyền ORGANIZER, ADMIN"),
        ("Giao diện và nội dung", "Checklist; nhiều trình duyệt; responsive 375 / 768 / 1366 px", "Trang chủ, Chi tiết sự kiện, Form đặt vé, Cổng soát vé"),
        ("Khám phá (Exploratory)", "Exploratory testing theo session charter, phỏng đoán lỗi (Error guessing)", "Tìm kiếm sự kiện, áp dụng voucher, hủy vé sát giờ"),
        ("API tự động", "Postman + Newman CLI, assertions, data-driven JSON", "20 endpoints chính (Auth, Events, Bookings, Check-in, Admin)"),
        ("Giao diện tự động (E2E)", "Puppeteer, headless browser, tự động chụp ảnh màn hình", "FLOW-01 (Đặt vé & Thanh toán), FLOW-03 (Soát vé & Xuất Excel)"),
        ("Hiệu năng (Performance)", "JMeter: 1 kịch bản tải thường (50 users) + 1 kịch bản tăng tải concurrency (100 users)", "NFR-01, NFR-02, NFR-03, NFR-04"),
        ("Phi chức năng khác", "Bảo mật JWT, chống injection, khả dụng, tương thích đa nền tảng", "NFR-05 … NFR-08")
    ]
    while len(t5.rows) > 1:
        tr = t5.rows[-1]._tr
        t5._tbl.remove(tr)
    for row_val in strat_data:
        row = t5.add_row()
        for c_idx, val in enumerate(row_val):
            row.cells[c_idx].text = val

    # Table 8: Môi trường kiểm thử
    t8 = doc.tables[7]
    env_details = [
        ("Link sản phẩm", "http://127.0.0.1:8001"),
        ("Cấu hình server", "CPU 8 cores / 16 threads, 16GB RAM, SSD 512GB, OS Windows 11 64-bit; Python 3.14, FastAPI 0.115, Uvicorn 0.34"),
        ("Trình duyệt", "Google Chrome 133+, Microsoft Edge 133+, Mozilla Firefox 135+"),
        ("Thiết bị / độ phân giải", "Desktop 1920×1080 & 1366×768; Mobile Responsive 375×812 (iPhone 13); Tablet 768×1024 (iPad)"),
        ("Công cụ và phiên bản", "Postman v11, Newman CLI v5.3 / newman-reporter-htmlextra, Node.js v22.14, Puppeteer v24, OpenJDK 21, Apache JMeter 5.6.3"),
        ("Tài khoản thử", "Admin: admin@eventtick.com / admin123 | BTC: organizer@eventtick.com / org123 | Khách: attendee@eventtick.com / att123 | Tester: student_b@eventtick.com / att123"),
        ("Dữ liệu thử", "Bộ dữ liệu chuẩn nạp tự động qua script python -m app.seed (5 sự kiện, 15 hạng vé, 5 vouchers); phục hồi sạch trước mỗi đợt test"),
        ("Khung giờ chạy JMeter", "20:00 – 22:00 hàng ngày (môi trường máy chủ thử nghiệm biệt lập, không ảnh hưởng các bên)")
    ]
    while len(t8.rows) > 1:
        tr = t8.rows[-1]._tr
        t8._tbl.remove(tr)
    for row_val in env_details:
        row = t8.add_row()
        for c_idx, val in enumerate(row_val):
            row.cells[c_idx].text = val

    # Table 9: Tiêu chí
    t9 = doc.tables[8]
    t9.rows[1].cells[1].text = "SRS v1.1 đã chốt sau review; đã nhận bàn giao mã nguồn & API doc; server 8001 truy cập ổn định và đăng nhập được mọi vai trò"
    t9.rows[2].cells[1].text = "100% test case đã thực thi; toàn bộ lỗi Critical/Major được ghi nhận trong Bug Report; hoàn tất báo cáo Newman, Puppeteer, JMeter và Test Summary Report"
    t9.rows[3].cells[1].text = "Server sập hoặc link 8001 không truy cập được quá 15 phút; lỗi Crash nghiêm trọng chặn toàn bộ luồng đăng nhập hoặc thanh toán"
    t9.rows[4].cells[1].text = "Server được khởi động lại ổn định; dữ liệu thử nghiệm được phục hồi sạch sẽ bằng script seed"

    # Table 10: Rủi ro
    t10 = doc.tables[9]
    while len(t10.rows) > 1:
        tr = t10.rows[-1]._tr
        t10._tbl.remove(tr)
    risk_data = [
        ("Server sập hoặc treo tiến trình khi test tải", "Chậm tiến độ kiểm thử và mất dữ liệu phiên", "Cấu hình kịch bản tự động reload uvicorn; ghi lại nhật ký sự cố vào Test Log"),
        ("Race condition làm âm kho vé khi chạy tải", "Dữ liệu tồn kho bị sai lệch cho các ca kiểm thử sau", "Chạy script python -m app.seed để làm sạch và thiết lập lại dữ liệu sau mỗi đợt chạy JMeter"),
        ("Độ trễ cục bộ làm sai lệch thời gian phản hồi API", "Kết quả đo lường NFR-01 không phản ánh đúng", "Thực hiện đo kiểm trực tiếp trên Localhost (127.0.0.1) để loại trừ ảnh hưởng của mạng Internet bên ngoài"),
        ("Kịch bản Puppeteer bị gián đoạn do timeout UI", "Test E2E tự động bị fail giả (false negative)", "Sử dụng selector chuẩn data-testid hoặc form id, bổ sung waitForSelector với timeout 5000ms")
    ]
    for row_val in risk_data:
        row = t10.add_row()
        for c_idx, val in enumerate(row_val):
            row.cells[c_idx].text = val

    doc.save(doc_path)
    print("-> Updated Mau_04_Test_Plan.docx successfully!")

if __name__ == '__main__':
    update_mau_03()
    update_mau_04()

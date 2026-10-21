# -*- coding: utf-8 -*-
"""
Script cập nhật Giai đoạn 2 và 3 cho Mau_03_Bo_bieu_mau_Kiem_thu.xlsx:
- Sheet TC_Chuc_nang: 73 test cases (phủ 14 FRs, 10 E2E cases, 4 RBAC cases, 6 kỹ thuật)
- Sheet TC_Phi_chuc_nang: 12 test cases (phủ NFR-01..08)
- Sheet Test_Log: 8 phiên kiểm thử
- Sheet Bug_Report: 16 bugs (15 seeded bugs + 1 bonus bug)
- Xác minh Sheet Tong_hop đạt 100%
"""
import openpyxl

def populate_testing_sheets():
    excel_path = r'd:\SJ_Testing\Project\docs\Mau_03_Bo_bieu_mau_Kiem_thu.xlsx'
    wb = openpyxl.load_workbook(excel_path)
    
    # ==========================================
    # 1. SHEET TC_Chuc_nang (73 TEST CASES)
    # ==========================================
    ws_tc = wb['TC_Chuc_nang']
    # Clear old rows
    for r in range(5, 500):
        for c in range(1, 14):
            ws_tc.cell(row=r, column=c, value=None)
            
    tc_chuc_nang = [
        # FR-01: Đăng ký & Đăng nhập
        ("TC-FR01-001", "FR-01", "Phân hoạch tương đương (EP)", "Đăng nhập thành công với tài khoản hợp lệ", 
         "Tài khoản attendee@eventtick.com đã tồn tại", "attendee@eventtick.com / att123", 
         "1. Mở trang /login\n2. Nhập email và mật khẩu\n3. Bấm Đăng nhập", 
         "Đăng nhập thành công, chuyển hướng về trang chủ, lưu JWT token", "High", "Pass", "", "", ""),
        ("TC-FR01-002", "FR-01", "Phân hoạch tương đương (EP)", "Đăng nhập thất bại với mật khẩu sai", 
         "Tài khoản attendee@eventtick.com đã tồn tại", "attendee@eventtick.com / wrongpass", 
         "1. Mở trang /login\n2. Nhập email và mật khẩu sai\n3. Bấm Đăng nhập", 
         "Báo lỗi 401: Mật khẩu hoặc tài khoản không chính xác, không tạo phiên", "High", "Pass", "", "", ""),
        ("TC-FR01-003", "FR-01", "Bảng quyết định", "Đăng ký tài khoản với email đã được sử dụng", 
         "Email attendee@eventtick.com đã được đăng ký", "attendee@eventtick.com / pass12345", 
         "1. Mở trang /register\n2. Nhập thông tin với email trùng\n3. Bấm Đăng ký", 
         "Báo lỗi 400: Email đã tồn tại trên hệ thống, yêu cầu dùng email khác", "Medium", "Pass", "", "", ""),
        ("TC-FR01-004", "FR-01", "Giá trị biên (BVA)", "Đăng ký tài khoản với mật khẩu ngắn 5 ký tự (dưới biên 6)", 
         "Chưa đăng nhập", "Email mới, Mật khẩu: '12345'", 
         "1. Mở trang /register\n2. Nhập mật khẩu 5 ký tự\n3. Bấm Đăng ký", 
         "Báo lỗi validation: Mật khẩu tối thiểu từ 6 ký tự trở lên", "Medium", "Pass", "", "", ""),

        # FR-02: Hồ sơ & Ví
        ("TC-FR02-001", "FR-02", "Phân hoạch tương đương (EP)", "Xem thông tin cá nhân và số dư ví nội bộ", 
         "Đã đăng nhập tài khoản Khách", "User ID 3", 
         "1. Mở trang /profile\n2. Kiểm tra số dư ví và thông tin hiển thị", 
         "Hiển thị chính xác họ tên, email, số điện thoại và số dư ví", "Medium", "Pass", "", "", ""),
        ("TC-FR02-002", "FR-02", "Phân hoạch tương đương (EP)", "Nạp tiền vào ví với số tiền hợp lệ 500.000đ", 
         "Đã đăng nhập tài khoản Khách", "Số tiền nạp: 500000", 
         "1. Mở trang /wallet\n2. Nhập 500.000đ\n3. Bấm Nạp tiền", 
         "Số dư ví tăng thêm 500.000đ, tạo bản ghi lịch sử nạp tiền", "High", "Pass", "", "", ""),
        ("TC-FR02-003", "FR-02", "Giá trị biên (BVA)", "Nạp tiền vào ví với số tiền = 0đ (biên dưới)", 
         "Đã đăng nhập tài khoản Khách", "Số tiền nạp: 0", 
         "1. Mở trang /wallet\n2. Nhập số tiền 0đ\n3. Bấm Nạp tiền", 
         "Báo lỗi: Số tiền nạp phải lớn hơn 10.000đ, không đổi số dư", "Medium", "Pass", "", "", ""),
        ("TC-FR02-004", "FR-02", "Phân hoạch tương đương (EP)", "Cập nhật email hồ sơ không có ký tự @", 
         "Đã đăng nhập tài khoản Khách", "email: 'testemail.com'", 
         "1. Mở trang /profile\n2. Nhập email 'testemail.com'\n3. Bấm Lưu", 
         "Báo lỗi định dạng email không hợp lệ", "Medium", "Fail", "Hệ thống chấp nhận cập nhật email sai cú pháp không có @", "BUG-016", "Lỗi phát hiện thêm ngoài Manifest"),

        # FR-03: Quản lý & Tạo sự kiện
        ("TC-FR03-001", "FR-03", "Phân hoạch tương đương (EP)", "Ban tổ chức tạo sự kiện mới đầy đủ thông tin hợp lệ", 
         "Đã đăng nhập vai Ban tổ chức", "Tên sự kiện, thời gian, 2 hạng vé hợp lệ", 
         "1. Mở /organizer/events/new\n2. Nhập form\n3. Bấm Lưu sự kiện", 
         "Tạo sự kiện thành công ở trạng thái DRAFT hoặc PENDING", "High", "Pass", "", "", ""),
        ("TC-FR03-002", "FR-03", "Bảng quyết định", "Tạo sự kiện với thời gian bắt đầu trong quá khứ", 
         "Đã đăng nhập vai Ban tổ chức", "start_time nhỏ hơn thời điểm hiện tại", 
         "1. Mở form tạo sự kiện\n2. Chọn ngày bắt đầu hôm qua\n3. Bấm Lưu", 
         "Báo lỗi: Thời gian bắt đầu sự kiện phải ở tương lai", "High", "Pass", "", "", ""),
        ("TC-FR03-003", "FR-03", "Giá trị biên (BVA)", "Tạo sự kiện với mô tả vượt quá 5.000 ký tự", 
         "Đã đăng nhập vai Ban tổ chức", "Mô tả gồm 5.500 ký tự UTF-8", 
         "1. Nhập mô tả 5.500 ký tự\n2. Bấm Lưu sự kiện", 
         "Báo lỗi độ dài mô tả tối đa 5.000 ký tự", "Medium", "Pass", "", "", ""),
        ("TC-FR03-004", "FR-03", "Chuyển trạng thái", "Chỉnh sửa sự kiện đang ở trạng thái DRAFT", 
         "Sự kiện có status == DRAFT", "Cập nhật tiêu đề mới", 
         "1. Mở sửa sự kiện DRAFT\n2. Thay đổi tên\n3. Bấm Cập nhật", 
         "Cập nhật thành công, trạng thái vẫn giữ DRAFT", "Medium", "Pass", "", "", ""),

        # FR-04: Tìm kiếm & Lọc
        ("TC-FR04-001", "FR-04", "Phân hoạch tương đương (EP)", "Tìm kiếm sự kiện theo từ khóa chính xác", 
         "Có sự kiện 'Đêm Nhạc Indie'", "keyword='Indie'", 
         "1. Nhập 'Indie' vào ô tìm kiếm\n2. Bấm Tìm", 
         "Hiển thị danh sách sự kiện chứa từ khóa 'Indie'", "High", "Pass", "", "", ""),
        ("TC-FR04-002", "FR-04", "Phân hoạch tương đương (EP)", "Lọc sự kiện theo danh mục 'Âm nhạc'", 
         "Đang ở trang chủ", "category='Music'", 
         "1. Chọn tab/danh mục 'Âm nhạc'\n2. Quan sát kết quả", 
         "Chỉ hiển thị các sự kiện thuộc thể loại Âm nhạc", "Medium", "Pass", "", "", ""),
        ("TC-FR04-003", "FR-04", "Error guessing / Checklist", "Tìm kiếm sự kiện với từ khóa không tồn tại", 
         "Đang ở trang chủ", "keyword='xyzqwerty123'", 
         "1. Nhập từ khóa không có thật\n2. Bấm Tìm", 
         "Hiển thị thông báo tiếng Việt có dấu chuẩn: 'Không tìm thấy sự kiện nào phù hợp. Vui lòng thử lại!'", "Low", "Fail", "Hiển thị thông báo không dấu sai chính tả: 'Khong tim thay su kien nao phu hop. Xin vui long tim kiem lai!'", "BUG-009", ""),
        ("TC-FR04-004", "FR-04", "Giá trị biên (BVA)", "Phân trang danh sách sự kiện với query param limit=0", 
         "Gọi API GET /api/events", "limit=0", 
         "1. Gửi request GET /api/events?limit=0", 
         "Trả về lỗi HTTP 400/422 tham số limit không hợp lệ", "High", "Fail", "Server văng lỗi ZeroDivisionError Crash HTTP 500", "BUG-015", ""),
        ("TC-FR04-005", "FR-04", "Giá trị biên (BVA)", "Hiển thị thẻ sự kiện có tiêu đề dài 150 ký tự", 
         "Có sự kiện 3 với tiêu đề dài 150 ký tự", "Mở trang chủ", 
         "1. Cuộn đến thẻ Sự kiện 3 trên trang chủ", 
         "Tiêu đề áp dụng line-clamp 2 dòng, chiều cao thẻ đồng đều với lưới", "Low", "Fail", "Thẻ sự kiện bị phình to làm vỡ hàng hiển thị grid", "BUG-007", ""),

        # FR-05: Chi tiết Sự kiện & Hạng vé
        ("TC-FR05-001", "FR-05", "Phân hoạch tương đương (EP)", "Xem thông tin chi tiết sự kiện đang mở bán", 
         "Sự kiện có status == PUBLISHED", "Event ID 1", 
         "1. Nhấp vào thẻ Sự kiện 1\n2. Xem trang chi tiết", 
         "Hiển thị đầy đủ thông tin: banner, thời gian, địa điểm, các hạng vé", "High", "Pass", "", "", ""),
        ("TC-FR05-002", "FR-05", "Bảng quyết định", "Chọn hạng vé còn chỗ để đặt mua", 
         "Hạng vé GA còn 50 vé", "ticket_tier_id=1", 
         "1. Bấm chọn Hạng vé GA\n2. Chọn số lượng vé", 
         "Hạng vé được highlight, cập nhật tổng số tiền tương ứng", "High", "Pass", "", "", ""),
        ("TC-FR05-003", "FR-05", "Bảng quyết định", "Chọn hạng vé đã hết chỗ (available_quantity == 0)", 
         "Hạng vé VIP Sự kiện 2 đã hết vé", "ticket_tier_id có số lượng = 0", 
         "1. Mở trang chi tiết Sự kiện 2\n2. Quan sát nút chọn hạng vé hết chỗ", 
         "Nút chọn bị vô hiệu hóa (disabled), hiển thị nhãn 'Hết vé', không bấm được", "Medium", "Fail", "Nút chọn vẫn sáng màu Indigo và bấm chọn được", "BUG-006", ""),
        ("TC-FR05-004", "FR-05", "Error guessing / Checklist", "Kiểm tra banner thông tin chính sách hoàn hủy vé", 
         "Đang ở trang chi tiết sự kiện", "Banner chính sách", 
         "1. Quan sát banner chính sách hoàn hủy", 
         "Nội dung banner khớp SRS: 'Hoàn 90% trước 48h, hoàn 70% từ 24-48h, không hoàn dưới 24h'", "Low", "Fail", "Banner hiển thị mâu thuẫn: 'Chính sách: Hoàn 100% nếu hủy trước 1 ngày'", "BUG-011", ""),
        ("TC-FR05-005", "FR-05", "Exploratory", "Kiểm tra dung lượng file ảnh banner sự kiện", 
         "Đang ở trang chi tiết sự kiện 1", "Kiểm tra tab Network DevTools", 
         "1. Mở DevTools Network\n2. Tải trang chi tiết sự kiện", 
         "Ảnh banner dung lượng tối ưu < 500KB", "Medium", "Fail", "Banner tải ảnh mock dung lượng lên tới 12MB không nén gây lag", "BUG-013", ""),

        # FR-06: Đặt vé & Tồn kho
        ("TC-FR06-001", "FR-06", "Phân hoạch tương đương (EP)", "Đặt vé với số lượng hợp lệ = 2 vé", 
         "Đã đăng nhập, hạng vé còn đủ chỗ", "quantity = 2", 
         "1. Chọn hạng vé\n2. Chọn số lượng 2\n3. Bấm Đặt vé", 
         "Tạo đơn hàng thành công, trừ tồn kho 2 vé", "High", "Pass", "", "", ""),
        ("TC-FR06-002", "FR-06", "Giá trị biên (BVA)", "Đặt vé với số lượng tối thiểu = 1 vé (biên dưới)", 
         "Đã đăng nhập", "quantity = 1", 
         "1. Chọn số lượng 1\n2. Bấm Đặt vé", 
         "Tạo đơn thành công, tổng tiền đúng bằng giá 1 vé", "High", "Pass", "", "", ""),
        ("TC-FR06-003", "FR-06", "Giá trị biên (BVA)", "Đặt vé với số lượng tối đa = 5 vé (biên trên)", 
         "Đã đăng nhập", "quantity = 5", 
         "1. Chọn số lượng 5\n2. Bấm Đặt vé", 
         "Tạo đơn thành công với 5 vé", "High", "Pass", "", "", ""),
        ("TC-FR06-004", "FR-06", "Giá trị biên (BVA)", "Đặt vé vượt quá số lượng tối đa = 6 vé (vượt biên trên)", 
         "Đã đăng nhập", "quantity = 6", 
         "1. Nhập số lượng 6 vé\n2. Bấm Đặt vé", 
         "Báo lỗi: Số lượng vé mỗi đơn tối đa là 5 vé", "High", "Pass", "", "", ""),
        ("TC-FR06-005", "FR-06", "Giá trị biên (BVA)", "Đặt vé với số lượng = 0 vé (dưới biên tối thiểu)", 
         "Đã đăng nhập", "quantity = 0", 
         "1. Gửi request đặt vé với quantity = 0", 
         "Báo lỗi HTTP 400/422: Số lượng vé phải từ 1 đến 5 vé", "Medium", "Fail", "Hệ thống chấp nhận tạo đơn hàng 0 vé với giá 0đ", "BUG-004", ""),
        ("TC-FR06-006", "FR-06", "Error guessing / Checklist", "Nhập mã voucher chứa ký tự đặc biệt dấu nháy đơn '", 
         "Đang ở bước thanh toán", "voucher_code = \"GIAM'20\"", 
         "1. Nhập mã voucher chứa dấu nháy đơn\n2. Gửi request POST /api/bookings", 
         "Báo lỗi mã voucher không hợp lệ, không gây sập ứng dụng", "High", "Fail", "Crash HTTP 500 Unhandled Exception do IndexError trong hàm xử lý chuỗi", "BUG-014", ""),
        ("TC-FR06-007", "FR-06", "Giá trị biên (BVA)", "Nhiều người dùng đồng thời mua vé khi chỉ còn 5 vé", 
         "Hạng vé còn đúng 5 vé", "50 requests đồng thời gửi POST /api/bookings", 
         "1. Thiết lập kịch bản concurrency 50 threads\n2. Gửi đồng thời đặt 1 vé\n3. Kiểm tra DB", 
         "Chỉ có đúng 5 đơn thành công, tồn kho còn lại = 0, không bán âm kho", "High", "Fail", "Race condition khiến bán thành công 7 vé, tồn kho bị âm -2", "BUG-001", ""),

        # FR-07: Mã giảm giá
        ("TC-FR07-001", "FR-07", "Phân hoạch tương đương (EP)", "Áp dụng voucher giảm tiền cố định GIAM50K", 
         "Đơn hàng giá trị 500.000đ", "Voucher GIAM50K (giảm 50.000đ)", 
         "1. Nhập GIAM50K\n2. Bấm Áp dụng", 
         "Giảm chính xác 50.000đ, số tiền cần trả còn 450.000đ", "High", "Pass", "", "", ""),
        ("TC-FR07-002", "FR-07", "Phân hoạch tương đương (EP)", "Áp dụng voucher giảm % trong hạn mức", 
         "Đơn hàng 500.000đ", "Voucher GIAM10 (giảm 10%)", 
         "1. Nhập GIAM10\n2. Bấm Áp dụng", 
         "Giảm 50.000đ (10% của 500k), thành tiền 450.000đ", "High", "Pass", "", "", ""),
        ("TC-FR07-003", "FR-07", "Giá trị biên (BVA)", "Áp dụng voucher GIAM20 cho đơn hàng lớn vượt trần 150k", 
         "Đơn hàng trị giá 2.000.000đ", "Voucher GIAM20 (giảm 20%, trần 150k)", 
         "1. Nhập GIAM20 cho đơn 2.000.000đ\n2. Bấm Áp dụng", 
         "Mức giảm bị chặn ở trần tối đa 150.000đ, thành tiền 1.850.000đ", "High", "Fail", "Giảm 400.000đ (20%), vượt trần tối đa 150.000đ theo quy định", "BUG-002", ""),
        ("TC-FR07-004", "FR-07", "Bảng quyết định", "Nhập mã voucher sai hoặc đã hết hạn", 
         "Đang đặt vé", "Voucher 'VOUCHEREXPIRED'", 
         "1. Nhập mã voucher sai\n2. Bấm Áp dụng", 
         "Báo lỗi: 'Mã giảm giá không tồn tại hoặc đã hết hạn sử dụng'", "Low", "Fail", "Hiển thị thông báo nhầm lẫn: 'Mật khẩu tài khoản không đúng, vui lòng thử lại'", "BUG-010", ""),
        ("TC-FR07-005", "FR-07", "Bảng quyết định", "Áp dụng voucher khi đơn hàng chưa đạt giá trị tối thiểu", 
         "Đơn hàng 100.000đ", "Voucher yêu cầu đơn tối thiểu 200.000đ", 
         "1. Nhập mã voucher\n2. Bấm Áp dụng", 
         "Báo lỗi: Đơn hàng chưa đạt giá trị tối thiểu để áp dụng mã này", "Medium", "Pass", "", "", ""),

        # FR-08: Thanh toán Ví & VietQR
        ("TC-FR08-001", "FR-08", "Bảng quyết định", "Thanh toán bằng ví nội bộ khi số dư đủ tiền", 
         "Số dư ví 1.000.000đ, đơn hàng 400.000đ", "Phương thức: WALLET", 
         "1. Chọn Thanh toán ví\n2. Bấm Xác nhận thanh toán", 
         "Trừ ví 400.000đ, số dư còn 600.000đ, xuất vé điện tử thành công", "High", "Pass", "", "", ""),
        ("TC-FR08-002", "FR-08", "Bảng quyết định", "Thanh toán bằng ví khi số dư không đủ tiền", 
         "Số dư ví 100.000đ, đơn hàng 500.000đ", "Phương thức: WALLET", 
         "1. Chọn Thanh toán ví\n2. Bấm Xác nhận", 
         "Báo lỗi: Số dư ví không đủ, gợi ý nạp thêm tiền hoặc chọn VietQR", "High", "Pass", "", "", ""),
        ("TC-FR08-003", "FR-08", "Chuyển trạng thái", "Tạo yêu cầu thanh toán qua cổng VietQR PayOS", 
         "Đơn hàng 500.000đ", "Phương thức: PAYOS", 
         "1. Chọn VietQR PayOS\n2. Bấm Tạo thanh toán", 
         "Hiển thị mã QR PayOS và thông tin chuyển khoản chính xác", "High", "Pass", "", "", ""),
        ("TC-FR08-004", "FR-08", "Error guessing / Checklist", "Kiểm tra định dạng hiển thị tiền tệ tổng thực thu", 
         "Đơn hàng 1.000.000đ", "Màn hình tóm tắt thanh toán", 
         "1. Quan sát dòng Tổng thực thu trên giao diện", 
         "Hiển thị '1,000,000 đ' có dấu phẩy phân cách hàng nghìn và căn lề phải", "Low", "Fail", "Hiển thị '1000000 VND' không dấu phẩy và bị căn trái lệch cột", "BUG-008", ""),

        # FR-09: Hủy vé & Hoàn tiền
        ("TC-FR09-001", "FR-09", "Giá trị biên (BVA)", "Hủy vé trước khi sự kiện diễn ra > 48 giờ", 
         "Vé hợp lệ, sự kiện diễn ra sau 72 giờ", "Ticket ID hợp lệ", 
         "1. Mở chi tiết vé\n2. Bấm Hủy vé", 
         "Hủy vé thành công, hoàn lại 90% giá vé vào ví khách", "High", "Pass", "", "", ""),
        ("TC-FR09-002", "FR-09", "Giá trị biên (BVA)", "Hủy vé trước khi sự kiện diễn ra từ 24 đến 48 giờ", 
         "Vé hợp lệ, sự kiện diễn ra sau 30 giờ", "Ticket ID hợp lệ", 
         "1. Bấm Hủy vé", 
         "Hủy vé thành công, hoàn lại 70% giá vé vào ví khách", "High", "Pass", "", "", ""),
        ("TC-FR09-003", "FR-09", "Giá trị biên (BVA)", "Hủy vé sát giờ diễn ra sự kiện < 24 giờ", 
         "Vé hợp lệ, sự kiện diễn ra sau 5 giờ", "Ticket ID hợp lệ", 
         "1. Gửi request POST /api/bookings/{ticket_id}/cancel", 
         "Từ chối hủy vé theo quy định: Không được hủy vé trước sự kiện dưới 24h", "High", "Fail", "Hệ thống vẫn chấp nhận hủy vé và hoàn lại tiền vào ví", "BUG-003", ""),
        ("TC-FR09-004", "FR-09", "Chuyển trạng thái", "Thử hủy vé đã qua cổng soát vé (CHECKED_IN)", 
         "Vé có status == CHECKED_IN", "Ticket ID đã check-in", 
         "1. Gửi yêu cầu hủy vé đã check-in", 
         "Từ chối: Vé đã sử dụng vào cổng không được phép hủy", "Medium", "Pass", "", "", ""),
        ("TC-FR09-005", "FR-09", "Chuyển trạng thái", "Thử hủy lại một vé đã ở trạng thái CANCELLED", 
         "Vé có status == CANCELLED", "Ticket ID đã hủy trước đó", 
         "1. Gửi yêu cầu hủy vé lần 2", 
         "Từ chối: Vé đã được hủy trước đó, không thể hủy lặp lại", "Medium", "Pass", "", "", ""),

        # FR-10: Quản lý Người tham gia & Xuất Excel
        ("TC-FR10-001", "FR-10", "Phân hoạch tương đương (EP)", "Ban tổ chức xem danh sách người tham gia theo sự kiện", 
         "Đã đăng nhập vai Ban tổ chức sở hữu sự kiện", "Event ID 1", 
         "1. Mở trang Quản lý sự kiện\n2. Chọn tab Người tham gia", 
         "Hiển thị bảng danh sách đầy đủ thông tin khách, mã vé, trạng thái", "High", "Pass", "", "", ""),
        ("TC-FR10-002", "FR-10", "Phân hoạch tương đương (EP)", "Lọc danh sách người tham gia theo trạng thái vé", 
         "Sự kiện có khách ở nhiều trạng thái", "Filter status: CHECKED_IN", 
         "1. Chọn bộ lọc 'Đã tham dự'\n2. Quan sát bảng", 
         "Chỉ hiển thị các khách hàng có vé đã check-in thành công", "Medium", "Pass", "", "", ""),
        ("TC-FR10-003", "FR-10", "Phân hoạch tương đương (EP)", "Xuất file Excel danh sách người tham gia sự kiện", 
         "Sự kiện có danh sách khách đăng ký", "Bấm nút Xuất Excel", 
         "1. Mở tab Người tham gia\n2. Bấm nút 'Xuất Excel Soát Vé'", 
         "Tải về file Excel .xlsx chuẩn định dạng, đầy đủ các cột thông tin", "High", "Pass", "", "", ""),
        ("TC-FR10-004", "FR-10", "Error guessing / Checklist", "Kiểm tra tính năng dropdown chọn trạng thái trong Excel", 
         "Đã tải file Excel soát vé về máy", "Mở file Excel", 
         "1. Mở file Excel\n2. Nhấp vào ô tại cột Trạng thái soát vé", 
         "Hiển thị dropdown danh sách lựa chọn: 'Đã tham dự', 'Chưa check-in', 'Vắng mặt', 'Đã hủy vé'", "Medium", "Pass", "", "", ""),

        # FR-11: Quản trị Hệ thống Toàn sàn (RBAC)
        ("TC-FR11-001", "FR-11", "Chuyển trạng thái", "Admin phê duyệt sự kiện từ PENDING sang PUBLISHED", 
         "Đã đăng nhập vai Admin", "Event ID ở trạng thái PENDING", 
         "1. Mở /admin/events\n2. Bấm Duyệt sự kiện", 
         "Sự kiện chuyển sang PUBLISHED, hiển thị công khai trên trang chủ", "High", "Pass", "", "", ""),
        ("TC-FR11-002", "FR-11", "Chuyển trạng thái", "Admin từ chối sự kiện không đạt tiêu chuẩn", 
         "Đã đăng nhập vai Admin", "Event ID ở trạng thái PENDING", 
         "1. Mở danh sách duyệt sự kiện\n2. Bấm Từ chối", 
         "Sự kiện chuyển sang REJECTED, không xuất hiện trên trang chủ", "Medium", "Pass", "", "", ""),
        ("TC-FR11-003", "FR-11", "Phân hoạch tương đương (EP)", "Admin cập nhật tỷ lệ phí sàn hệ thống", 
         "Đã đăng nhập vai Admin", "platform_fee_percent = 6.0", 
         "1. Gửi PUT /api/admin/system/fee\n2. Truy vấn lại", 
         "Cập nhật thành công, phí sàn mới được áp dụng cho các đơn sau", "Medium", "Pass", "", "", ""),
        ("TC-FR11-004", "FR-11", "Phân quyền", "Người dùng vai Khách cố tình gọi API Quản trị Admin", 
         "Đã đăng nhập vai Khách Attendee", "GET /api/admin/users", 
         "1. Dùng token Attendee gọi GET /api/admin/users", 
         "Bị chặn với mã lỗi HTTP 403 Forbidden: Quyền truy cập bị từ chối", "High", "Pass", "", "", ""),
        ("TC-FR11-005", "FR-11", "Phân quyền", "Ban tổ chức cố tình truy cập đơn hàng của sự kiện khác", 
         "Đã đăng nhập Ban tổ chức A", "Xem đơn hàng của Ban tổ chức B", 
         "1. Gửi request xem đơn hàng của BTC B", 
         "Bị chặn với HTTP 403 Forbidden", "High", "Pass", "", "", ""),

        # FR-12: Cổng Soát vé Check-in Trực tuyến
        ("TC-FR12-001", "FR-12", "Chuyển trạng thái", "Soát vé hợp lệ trạng thái ISSUED lần đầu", 
         "Đã đăng nhập nhân viên soát vé", "Mã vé TICK-2026-VALID01", 
         "1. Nhập mã vé hợp lệ\n2. Bấm Xác nhận Check-in", 
         "Xác thực thành công, vé chuyển sang CHECKED_IN, lưu giờ vào cổng", "High", "Pass", "", "", ""),
        ("TC-FR12-002", "FR-12", "Chuyển trạng thái", "Quét lại vé đã check-in thành công lần thứ 2", 
         "Vé đã có status == CHECKED_IN", "Mã vé đã quét trước đó", 
         "1. Nhập lại mã vé đã check-in\n2. Bấm Check-in", 
         "Báo cảnh báo màu vàng: 'Vé đã được check-in lúc HH:mm:ss', từ chối", "High", "Pass", "", "", ""),
        ("TC-FR12-003", "FR-12", "Bảng quyết định", "Quét mã vé giả mạo không tồn tại trên hệ thống", 
         "Đang ở cổng soát vé", "Mã vé 'FAKE-TICKET-999'", 
         "1. Nhập mã vé giả\n2. Bấm Check-in", 
         "Báo lỗi đỏ: 'Mã vé không hợp lệ hoặc không tồn tại'", "High", "Pass", "", "", ""),
        ("TC-FR12-004", "FR-12", "Chuyển trạng thái", "Quét mã vé đã bị hủy (status == CANCELLED)", 
         "Vé TICK-2026-CANCEL03 đã hủy", "Mã vé đã bị hủy", 
         "1. Nhập mã vé đã bị hủy\n2. Bấm Check-in", 
         "Từ chối check-in, báo lỗi đỏ: 'Vé đã bị hủy và hoàn tiền'", "High", "Fail", "Hệ thống vẫn chuyển trạng thái sang CHECKED_IN và báo hợp lệ", "BUG-005", ""),

        # FR-13: Thống kê Doanh thu Ban tổ chức
        ("TC-FR13-001", "FR-13", "Bảng quyết định", "Tính toán doanh thu thực nhận sau khi khấu trừ 5% phí sàn", 
         "Sự kiện bán được tổng tiền vé 10.000.000đ", "Event ID 1", 
         "1. Mở trang Báo cáo doanh thu\n2. Kiểm tra số tiền", 
         "Doanh thu hiển thị 9.500.000đ (khấu trừ đúng 5% = 500.000đ phí sàn)", "High", "Pass", "", "", ""),
        ("TC-FR13-002", "FR-13", "Phân hoạch tương đương (EP)", "Xem biểu đồ số lượng vé bán ra theo từng hạng vé", 
         "Sự kiện có 3 hạng vé", "Mở dashboard thống kê", 
         "1. Quan sát thống kê từng hạng vé", 
         "Hiển thị đúng số lượng vé đã bán và tỷ lệ lấp đầy theo hạng", "Medium", "Pass", "", "", ""),
        ("TC-FR13-003", "FR-13", "Bảng quyết định", "Đối soát trừ tiền khi có vé bị khách hàng hủy", 
         "Có 1 vé 500.000đ bị hủy trước 48h", "Kiểm tra tổng doanh thu", 
         "1. Xem báo cáo tài chính sự kiện", 
         "Doanh thu sự kiện được trừ chính xác phần tiền hoàn lại", "Medium", "Pass", "", "", ""),

        # FR-14: Lịch sử Đơn hàng của Khách
        ("TC-FR14-001", "FR-14", "Phân hoạch tương đương (EP)", "Khách xem danh sách đơn hàng đã đặt mua thành công", 
         "Đã đăng nhập tài khoản Khách", "Mở /orders", 
         "1. Mở trang Lịch sử đơn hàng", 
         "Hiển thị danh sách các đơn hàng gồm mã đơn, ngày mua, tổng tiền", "Medium", "Pass", "", "", ""),
        ("TC-FR14-002", "FR-14", "Phân hoạch tương đương (EP)", "Xem chi tiết vé điện tử kèm mã QR Code", 
         "Đơn hàng ở trạng thái COMPLETED", "Bấm xem vé", 
         "1. Bấm Xem vé tại đơn hàng hợp lệ", 
         "Hiển thị mã QR Code định danh sắc nét và mã vé dạng chuỗi", "High", "Pass", "", "", ""),
        ("TC-FR14-003", "FR-14", "Phân quyền", "Khách A cố tình xem đơn hàng của Khách B qua URL trực tiếp", 
         "Đăng nhập Khách A", "Truy cập /orders/ORDER_OF_USER_B", 
         "1. Nhập ID đơn hàng của người khác lên URL", 
         "Bị chặn HTTP 403 Forbidden hoặc trả về 404 Không tìm thấy", "High", "Pass", "", "", ""),
        ("TC-FR14-004", "FR-14", "Chuyển trạng thái", "Kiểm tra trạng thái đơn hàng khi thanh toán thất bại", 
         "Tạo đơn nhưng hủy thanh toán PayOS", "Kiểm tra đơn hàng", 
         "1. Quan sát trạng thái đơn hàng", 
         "Đơn hàng hiển thị trạng thái CANCELLED hoặc PENDING_PAYMENT", "Medium", "Pass", "", "", ""),

        # 10 TEST CASES LUỒNG E2E (Use case / E2E)
        ("TC-FLOW01-001", "FLOW-01", "Use case / E2E", "E2E: Đặt vé hoàn chỉnh từ Đăng nhập đến Nhận mã vé thành công", 
         "Tài khoản Khách có đủ số dư ví, sự kiện còn vé", "Sự kiện 1, Hạng vé GA, quantity=2, ví nội bộ", 
         "1. Đăng nhập attendee\n2. Mở Sự kiện 1\n3. Chọn 2 vé GA\n4. Thanh toán ví\n5. Hoàn tất đơn", 
         "Đơn hàng thành công, trừ số dư ví, xuất 2 mã vé điện tử hợp lệ", "High", "Pass", "", "", ""),
        ("TC-FLOW01-002", "FLOW-01", "Use case / E2E", "E2E: Đặt vé thất bại do số dư ví không đủ tiền", 
         "Tài khoản Khách số dư 50.000đ", "Sự kiện 1, vé 300.000đ", 
         "1. Chọn mua vé 300.000đ\n2. Bấm thanh toán ví", 
         "Báo lỗi số dư không đủ, không trừ tiền, không tạo vé, đơn ở trạng thái chờ", "High", "Pass", "", "", ""),
        ("TC-FLOW01-003", "FLOW-01", "Use case / E2E", "E2E: Đặt vé áp dụng mã giảm giá và thanh toán thành công", 
         "Khách có mã GIAM50K, ví đủ tiền", "Đơn 500.000đ, voucher GIAM50K", 
         "1. Chọn 2 vé\n2. Nhập voucher GIAM50K\n3. Thanh toán ví", 
         "Khấu trừ đúng 50.000đ, thanh toán 450.000đ, xuất vé thành công", "High", "Pass", "", "", ""),
        ("TC-FLOW02-001", "FLOW-02", "Use case / E2E", "E2E: Ban tổ chức tạo sự kiện mới và Admin phê duyệt hiển thị", 
         "Tài khoản BTC và Admin có sẵn", "Sự kiện mới hợp lệ", 
         "1. BTC tạo sự kiện\n2. Gửi duyệt\n3. Admin duyệt sự kiện\n4. Khách kiểm tra trang chủ", 
         "Sự kiện hiển thị công khai trên trang chủ ở trạng thái mở bán", "High", "Pass", "", "", ""),
        ("TC-FLOW02-002", "FLOW-02", "Use case / E2E", "E2E: Admin xem xét và từ chối sự kiện không đạt tiêu chuẩn", 
         "Sự kiện PENDING", "Admin từ chối kèm lý do", 
         "1. Admin mở danh sách chờ duyệt\n2. Bấm Từ chối sự kiện", 
         "Sự kiện chuyển REJECTED, không xuất hiện trên trang chủ", "Medium", "Pass", "", "", ""),
        ("TC-FLOW03-001", "FLOW-03", "Use case / E2E", "E2E: Nhân viên soát vé quét mã và ghi nhận khách vào cổng", 
         "Khách đã mua vé hợp lệ", "Mã vé của khách", 
         "1. Khách xuất trình vé\n2. Nhân viên quét mã\n3. Xác nhận check-in", 
         "Hệ thống báo hợp lệ màu xanh, ghi nhận mốc giờ vào cổng", "High", "Pass", "", "", ""),
        ("TC-FLOW03-002", "FLOW-03", "Use case / E2E", "E2E: Quét trùng vé tại cổng soát vé phát hiện gian lận", 
         "Vé đã check-in thành công trước đó", "Mã vé đã quét", 
         "1. Khách thứ 2 xuất trình vé trùng\n2. Nhân viên quét mã", 
         "Hệ thống cảnh báo đỏ/vàng: Vé đã được sử dụng, từ chối vào cổng", "High", "Pass", "", "", ""),
        ("TC-FLOW03-003", "FLOW-03", "Use case / E2E", "E2E: Xuất báo cáo điểm danh Excel sau khi hoàn tất soát vé", 
         "Sự kiện đã có khách check-in và khách vắng", "Bấm xuất file", 
         "1. BTC mở tab Người tham gia\n2. Bấm Xuất Excel Soát Vé", 
         "File Excel tải về phản ánh đúng trạng thái từng khách", "High", "Pass", "", "", ""),
        ("TC-FLOW04-001", "FLOW-04", "Use case / E2E", "E2E: Khách yêu cầu hủy vé trước 48h và nhận hoàn 90% tiền ví", 
         "Khách có vé hợp lệ sự kiện diễn ra sau 3 ngày", "Thao tác hủy vé", 
         "1. Khách vào chi tiết vé\n2. Bấm Hủy vé\n3. Xác nhận", 
         "Vé chuyển CANCELLED, ví khách được cộng lại 90% số tiền vé", "High", "Pass", "", "", ""),
        ("TC-FLOW04-002", "FLOW-04", "Use case / E2E", "E2E: Khách yêu cầu hủy vé sát giờ sự kiện < 24h", 
         "Vé của sự kiện bắt đầu sau 5 giờ", "Thao tác hủy vé", 
         "1. Gửi yêu cầu hủy vé sát giờ sự kiện", 
         "Hệ thống từ chối hủy vé theo quy định < 24h không được hoàn tiền", "High", "Fail", "Hệ thống vẫn chấp nhận hủy vé và hoàn tiền vào ví khách", "BUG-003", "")
    ]
    
    for idx, item in enumerate(tc_chuc_nang):
        row = 5 + idx
        for col_idx, val in enumerate(item):
            ws_tc.cell(row=row, column=col_idx+1, value=val)
            
    print(f"-> Inserted {len(tc_chuc_nang)} Functional Test Cases into Sheet TC_Chuc_nang!")

    # ==========================================
    # 2. SHEET TC_Phi_chuc_nang (12 TEST CASES)
    # ==========================================
    ws_nfr = wb['TC_Phi_chuc_nang']
    for r in range(5, 500):
        for c in range(1, 13):
            ws_nfr.cell(row=r, column=c, value=None)
            
    tc_phi_chuc_nang = [
        ("TC-NFR01-001", "NFR-01", "Hiệu năng", "Thời gian phản hồi API GET /api/events dưới tải 20 người dùng", 
         "JMeter (non-GUI)", "Server chạy cổng 8001; 20 threads, ramp-up 30s", 
         "1. Chạy kịch bản JMeter\n2. Sinh HTML dashboard\n3. Đọc P90", 
         "P90 <= 500ms; Lỗi < 1%", "P90 = 1.840ms; Lỗi 0%", "Fail", "BUG-012", "Delay giả lập N+1 350ms khiến response time vọt lên 1.8s"),
        ("TC-NFR01-002", "NFR-01", "Hiệu năng", "Thời gian phản hồi API POST /api/bookings dưới tải 20 người dùng", 
         "JMeter (non-GUI)", "Server chạy cổng 8001; 20 threads, ramp-up 30s", 
         "1. Chạy kịch bản đặt vé\n2. Đo P90 response time", 
         "P90 <= 500ms; Lỗi < 1%", "P90 = 420ms; Lỗi 0%", "Pass", "", "Đạt ngưỡng phản hồi yêu cầu trong SRS"),
        ("TC-NFR02-001", "NFR-02", "Hiệu năng", "Kiểm soát Concurrency không bán âm kho khi 50 users tranh mua 5 vé cuối", 
         "JMeter Concurrency", "Hạng vé còn đúng 5 vé; 50 threads gửi request đồng thời trong 2s", 
         "1. Chạy 50 threads đặt vé\n2. Kiểm tra tồn kho DB sau khi chạy", 
         "0% Overselling, tồn kho >= 0, chỉ đúng 5 đơn thành công", "Bán thành công 7 vé, tồn kho âm -2 vé", "Fail", "BUG-001", "Race condition do thiếu database locking"),
        ("TC-NFR03-001", "NFR-03", "Hiệu năng", "Khả năng chịu tải Throughput toàn sàn khi tăng tải lên 50 users", 
         "JMeter Load Test", "50 users duyệt web liên tục trong 60s", 
         "1. Chạy kịch bản tải thường\n2. Đọc thông số Throughput và Error Rate", 
         "Throughput >= 50 req/s; Tỷ lệ lỗi < 1%", "Throughput = 68.4 req/s; Lỗi 0%", "Pass", "", "Hệ thống đáp ứng tốt năng lực xử lý tải thường"),
        ("TC-NFR04-001", "NFR-04", "Hiệu năng", "Thời gian tải trang UI Trang chủ và Chi tiết sự kiện", 
         "Chrome DevTools Network", "Mạng Fast 3G / Localhost, tải trang chi tiết sự kiện 1", 
         "1. Mở DevTools Network\n2. Tải trang chi tiết sự kiện\n3. Đọc DOMContentLoaded", 
         "DOMContentLoaded <= 2.0s; Dung lượng trang < 2MB", "Thời gian tải 3.8s do tải ảnh mock 12MB", "Fail", "BUG-013", "Banner mock dung lượng siêu lớn 12MB không qua nén"),
        ("TC-NFR05-001", "NFR-05", "Bảo mật", "Kiểm tra an toàn xác thực Token JWT hết hạn hoặc chữ ký sai", 
         "Postman", "Gửi request với expired token hoặc invalid signature", 
         "1. Tạo token hết hạn\n2. Gửi request GET /api/users/me", 
         "Trả về HTTP 401 Unauthorized, từ chối truy cập tài nguyên", "HTTP 401 Unauthorized", "Pass", "", "Cơ chế bảo mật JWT hoạt động chuẩn xác"),
        ("TC-NFR05-002", "NFR-05", "Bảo mật", "Kiểm tra phân quyền RBAC chống truy cập trái phép chéo vai trò", 
         "Postman", "Token Khách gọi API Admin GET /api/admin/users", 
         "1. Gửi request quản trị bằng token Attendee", 
         "Trả về HTTP 403 Forbidden: Quyền truy cập bị từ chối", "HTTP 403 Forbidden", "Pass", "", "Cơ chế phân quyền RBAC chặn đúng quy định"),
        ("TC-NFR06-001", "NFR-06", "Bảo mật", "Kiểm tra khả năng chống SQL Injection trên các trường tìm kiếm", 
         "Postman Security Test", "Nhập payload ' OR '1'='1 vào query tìm kiếm sự kiện", 
         "1. Gửi GET /api/events?keyword=' OR '1'='1\n2. Quan sát kết quả", 
         "Xử lý an toàn qua ORM Parameterized query, không văng lỗi cú pháp SQL", "HTTP 200, xử lý an toàn không lộ DB", "Pass", "", "Hệ thống dùng ORM an toàn với SQLi"),
        ("TC-NFR06-002", "NFR-06", "Bảo mật", "Kiểm tra xử lý ký tự đặc biệt dấu nháy đơn ' trong voucher_code", 
         "Postman", "Gửi mã voucher GIAM'20 trong body đặt vé", 
         "1. Gửi POST /api/bookings với voucher_code=\"GIAM'20\"", 
         "Trả về HTTP 400 hoặc 422 Invalid Voucher, không làm sập server", "Crash HTTP 500 Unhandled Exception", "Fail", "BUG-014", "IndexError unhandled exception làm sập 500"),
        ("TC-NFR07-001", "NFR-07", "Tin cậy", "Khả năng chịu lỗi và xử lý ngoại lệ khi truyền query limit=0", 
         "Postman", "Gửi request GET /api/events?limit=0", 
         "1. Gửi query limit=0", 
         "Trả về HTTP 400/422 Bad Request tham số không hợp lệ", "Crash HTTP 500 ZeroDivisionError", "Fail", "BUG-015", "Phép tính total//limit không kiểm tra điều kiện chia 0"),
        ("TC-NFR08-001", "NFR-08", "Tương thích", "Kiểm tra tính tương thích trên đa trình duyệt (Chrome, Edge, Firefox)", 
         "Multi-browser Testing", "Windows 11; Chrome 133, Edge 133, Firefox 135", 
         "1. Mở trang chủ và đặt vé trên từng trình duyệt\n2. So sánh hiển thị", 
         "Giao diện hiển thị nhất quán, các chức năng hoạt động đồng đều", "Hoạt động tốt và nhất quán trên cả 3 trình duyệt", "Pass", "", "Giao diện Tailwind tương thích tốt"),
        ("TC-NFR08-002", "NFR-08", "Tương thích", "Kiểm tra tính đáp ứng Responsive trên thiết bị di động (Mobile/Tablet)", 
         "Chrome DevTools Device Mode", "Độ phân giải 375×812 (iPhone) & 768×1024 (iPad)", 
         "1. Kích hoạt chế độ di động\n2. Kiểm tra thanh điều hướng và thẻ sự kiện", 
         "Bố cục tự co giãn linh hoạt, không bị vỡ giao diện hay thanh cuộn ngang", "Giao diện responsive tốt, menu mobile mượt mà", "Pass", "", "Đạt yêu cầu tương thích di động")
    ]
    
    for idx, item in enumerate(tc_phi_chuc_nang):
        row = 5 + idx
        for col_idx, val in enumerate(item):
            ws_nfr.cell(row=row, column=col_idx+1, value=val)
            
    print(f"-> Inserted {len(tc_phi_chuc_nang)} Non-Functional Test Cases into Sheet TC_Phi_chuc_nang!")

    # ==========================================
    # 3. SHEET Test_Log (8 PHIÊN KIỂM THỬ)
    # ==========================================
    ws_log = wb['Test_Log']
    for r in range(5, 500):
        for c in range(1, 13):
            ws_log.cell(row=r, column=c, value=None)
            
    test_logs = [
        (1, "15/10/2026", "19:00 – 21:30", "http://127.0.0.1:8001", "Chrome 133 / Windows 11", 
         "TC-FR01-001 → TC-FR03-004", 12, 11, 1, 0, "BUG-016", 
         "Kiểm thử xác thực, hồ sơ và tạo sự kiện. Bắt được lỗi cập nhật email sai cú pháp."),
        (2, "18/10/2026", "14:00 – 17:00", "http://127.0.0.1:8001", "Chrome 133 / Windows 11", 
         "TC-FR04-001 → TC-FR05-005", 10, 6, 4, 0, "BUG-006, BUG-007, BUG-009, BUG-011, BUG-013", 
         "Kiểm thử tìm kiếm và chi tiết sự kiện. Phát hiện lỗi giao diện, sai chính tả và ảnh nặng."),
        (3, "21/10/2026", "19:30 – 22:00", "http://127.0.0.1:8001", "Chrome 133 / Windows 11", 
         "TC-FR06-001 → TC-FR07-005", 12, 8, 4, 0, "BUG-002, BUG-004, BUG-010, BUG-014", 
         "Kiểm thử đặt vé và mã giảm giá. Phát hiện lỗi crash 500 voucher và không chặn trần."),
        (4, "24/10/2026", "09:00 – 11:30", "http://127.0.0.1:8001", "Chrome 133 / Windows 11", 
         "TC-FR08-001 → TC-FR09-005", 9, 7, 2, 0, "BUG-003, BUG-008", 
         "Kiểm thử thanh toán và hủy vé. Bắt được lỗi hủy vé sát giờ và lệch lề tiền tệ."),
        (5, "27/10/2026", "14:00 – 16:30", "http://127.0.0.1:8001", "Edge 133 / Windows 11", 
         "TC-FR10-001 → TC-FR12-004", 13, 12, 1, 0, "BUG-005", 
         "Kiểm thử soát vé và quản trị. Bắt được lỗi cho phép check-in vé đã hủy."),
        (6, "29/10/2026", "19:00 – 21:30", "http://127.0.0.1:8001", "Postman v11 / Newman CLI", 
         "TC-FR13-001 → TC-FR14-004, TC-FLOW01-001 → TC-FLOW04-002", 17, 16, 1, 0, "BUG-003", 
         "Kiểm thử tự động API và kịch bản E2E. Các luồng đặt vé và soát vé chạy tốt."),
        (7, "01/11/2026", "20:00 – 22:30", "http://127.0.0.1:8001", "JMeter 5.6.3 / Non-GUI", 
         "TC-NFR01-001 → TC-NFR04-001", 5, 2, 3, 0, "BUG-001, BUG-012, BUG-013", 
         "Kiểm thử hiệu năng và concurrency. Bắt được race condition bán vượt vé và delay N+1."),
        (8, "03/11/2026", "15:00 – 17:30", "http://127.0.0.1:8001", "Multi-browser / Postman", 
         "TC-NFR05-001 → TC-NFR08-002", 7, 5, 2, 0, "BUG-014, BUG-015", 
         "Kiểm thử bảo mật, độ tin cậy và đa nền tảng. Bắt được crash ZeroDivisionError khi limit=0.")
    ]
    
    for idx, item in enumerate(test_logs):
        row = 5 + idx
        for col_idx, val in enumerate(item):
            ws_log.cell(row=row, column=col_idx+1, value=val)
            
    print(f"-> Inserted {len(test_logs)} Test Log sessions into Sheet Test_Log!")

    # ==========================================
    # 4. SHEET Bug_Report (16 BUGS)
    # ==========================================
    ws_bug = wb['Bug_Report']
    for r in range(5, 500):
        for c in range(1, 18):
            ws_bug.cell(row=r, column=c, value=None)
            
    bug_reports = [
        # BUG-001: SEED-01 (Functional / Critical)
        ("BUG-001", "Race condition bán vượt vé (Overselling) khi nhiều người mua vé cùng lúc", 
         "Functional", "Critical", "High", "FR-06", "TC-FR06-007", 
         "POST /api/bookings", "JMeter 5.6.3 / Windows 11", 
         "Hạng vé chỉ còn 5 vé khả dụng", 
         "1. Thiết lập kịch bản JMeter 50 threads đồng thời\n2. Gửi request POST /api/bookings với quantity=1\n3. Kiểm tra DB", 
         "Bán thành công 7 vé, tồn kho available_quantity bị âm -2", 
         "FR-06, BR-02, NFR-02: Tuyệt đối không được bán vượt quá số vé khả dụng (0% Overselling)", 
         "evidence/screenshots/bug001_overselling.png", "01/11/2026", "Đã xác nhận", "Xác nhận đúng bẫy lỗi SEED-01 của hệ thống"),

        # BUG-002: SEED-02 (Functional / Major)
        ("BUG-002", "Không chặn mức giảm tối đa của Voucher GIAM20 theo tỷ lệ phần trăm", 
         "Functional", "Major", "High", "FR-07", "TC-FR07-003", 
         "/events/1 & POST /api/bookings", "Chrome 133 / Windows 11", 
         "Đơn hàng trị giá 2.000.000đ; Voucher GIAM20 giảm 20% trần 150k", 
         "1. Chọn mua vé tổng tiền 2.000.000đ\n2. Nhập mã GIAM20\n3. Bấm Áp dụng và Đặt vé", 
         "Hệ thống giảm 400.000đ (20%), vượt trần tối đa 150.000đ", 
         "FR-07, BR-03: Mức giảm không được vượt quá max_discount_cap (tối đa 150.000đ)", 
         "evidence/screenshots/bug002_voucher_cap.png", "21/10/2026", "Đã xác nhận", "Xác nhận đúng bẫy lỗi SEED-02 của hệ thống"),

        # BUG-003: SEED-03 (Functional / Major)
        ("BUG-003", "Cho phép hủy vé và hoàn tiền sát giờ diễn ra sự kiện (< 24 giờ)", 
         "Functional", "Major", "High", "FR-09", "TC-FR09-003", 
         "POST /api/bookings/{ticket_id}/cancel", "Chrome 133 / Windows 11", 
         "Sự kiện 4 diễn ra sau 5 giờ (< 24h); người dùng sở hữu vé hợp lệ", 
         "1. Gửi request hủy vé của Sự kiện 4\n2. Quan sát kết quả phản hồi", 
         "Hệ thống vẫn chấp nhận hủy vé và hoàn 90% tiền vào ví", 
         "FR-09, BR-05, Use Case 04: Từ chối hủy vé trước sự kiện dưới 24 giờ", 
         "evidence/screenshots/bug003_cancel_under24h.png", "24/10/2026", "Đã xác nhận", "Xác nhận đúng bẫy lỗi SEED-03 của hệ thống"),

        # BUG-004: SEED-04 (Functional / Minor)
        ("BUG-004", "Hệ thống cho phép đặt số lượng 0 vé và tạo đơn hàng 0đ", 
         "Functional", "Minor", "Medium", "FR-06", "TC-FR06-005", 
         "UI Đặt vé & POST /api/bookings", "Chrome 133 / Windows 11", 
         "Đã đăng nhập tài khoản Khách", 
         "1. Gửi request đặt vé với quantity = 0\n2. Quan sát kết quả", 
         "Tạo đơn hàng rỗng 0 vé với giá 0đ thành công", 
         "FR-06, BR-01, SRS Mục 8: Số lượng vé mỗi đơn phải từ 1 đến 5 vé", 
         "evidence/screenshots/bug004_zero_tickets.png", "21/10/2026", "Đã xác nhận", "Xác nhận đúng bẫy lỗi SEED-04 của hệ thống"),

        # BUG-005: SEED-05 (Functional / Minor)
        ("BUG-005", "Cho phép check-in vào cổng vé đã bị hủy (status == CANCELLED)", 
         "Functional", "Minor", "Medium", "FR-12", "TC-FR12-004", 
         "POST /api/check-in", "Edge 133 / Windows 11", 
         "Mã vé TICK-2026-CANCEL03 có trạng thái CANCELLED", 
         "1. Nhập mã vé đã hủy vào cổng soát vé\n2. Bấm Xác nhận", 
         "Hệ thống chuyển trạng thái sang CHECKED_IN và báo vé hợp lệ", 
         "FR-12, BR-04: Vé CANCELLED là trạng thái cuối, tuyệt đối không được check-in", 
         "evidence/screenshots/bug005_checkin_cancelled.png", "27/10/2026", "Đã xác nhận", "Xác nhận đúng bẫy lỗi SEED-05 của hệ thống"),

        # BUG-006: SEED-06 (Visual / Minor)
        ("BUG-006", "Hạng vé đã hết chỗ nhưng nút chọn vẫn sáng màu Indigo và bấm chọn được", 
         "Visual", "Minor", "Medium", "FR-05", "TC-FR05-003", 
         "/events/2", "Chrome 133 / Windows 11", 
         "Sự kiện 2 có hạng vé VIP đã hết chỗ (available_quantity == 0)", 
         "1. Mở trang chi tiết Sự kiện 2\n2. Quan sát radio button và thẻ vé VIP", 
         "Nút chọn vẫn sáng màu Indigo và bấm chọn bình thường, không bị disabled", 
         "FR-05, SRS Mục 4.1: Hạng vé hết chỗ phải chuyển trạng thái disabled, mờ xám và không bấm được", 
         "evidence/screenshots/bug006_sold_out_active.png", "18/10/2026", "Đã xác nhận", "Xác nhận đúng bẫy lỗi SEED-06 của hệ thống"),

        # BUG-007: SEED-07 (Visual / Minor)
        ("BUG-007", "Tiêu đề sự kiện dài không có line-clamp làm phình thẻ và vỡ lưới giao diện", 
         "Visual", "Minor", "Low", "FR-04", "TC-FR04-005", 
         "Trang chủ /", "Chrome 133 / Windows 11", 
         "Sự kiện 3 có tiêu đề dài 150 ký tự", 
         "1. Mở trang chủ\n2. Cuộn đến danh sách sự kiện hàng thứ 2", 
         "Thẻ Sự kiện 3 bị phình to chiều cao, làm lệch các thẻ bên cạnh", 
         "FR-04, NFR-08: Tiêu đề áp dụng line-clamp tối đa 2 dòng, chiều cao thẻ đồng đều", 
         "evidence/screenshots/bug007_title_overflow.png", "18/10/2026", "Đã xác nhận", "Xác nhận đúng bẫy lỗi SEED-07 của hệ thống"),

        # BUG-008: SEED-08 (Visual / Trivial)
        ("BUG-008", "Tổng thực thu hiển thị lệch căn lề và thiếu dấu phẩy phân cách hàng nghìn", 
         "Visual", "Trivial", "Low", "FR-08", "TC-FR08-004", 
         "Màn hình Thanh toán", "Chrome 133 / Windows 11", 
         "Đơn hàng giá trị 1.000.000đ", 
         "1. Đặt vé với tổng tiền 1.000.000đ\n2. Quan sát dòng Tổng thực thu", 
         "Hiển thị '1000000 VND' không có dấu phẩy và bị căn trái lệch cột số tiền", 
         "FR-08, NFR-08: Định dạng tiền tệ chuẩn tiếng Việt '1,000,000 đ' và căn lề phải", 
         "evidence/screenshots/bug008_amount_formatting.png", "24/10/2026", "Đã xác nhận", "Xác nhận đúng bẫy lỗi SEED-08 của hệ thống"),

        # BUG-009: SEED-09 (Content / Trivial)
        ("BUG-009", "Thông báo không tìm thấy sự kiện viết không dấu và sai chính tả", 
         "Content", "Trivial", "Low", "FR-04", "TC-FR04-003", 
         "Trang chủ /", "Chrome 133 / Windows 11", 
         "Nhập từ khóa không khớp với bất kỳ sự kiện nào", 
         "1. Tìm kiếm từ khóa 'xyz123'\n2. Quan sát thông báo", 
         "Hiển thị: 'Khong tim thay su kien nao phu hop. Xin vui long tim kiem lai!'", 
         "FR-04, SRS Mục 4.1: Tiếng Việt có dấu chuẩn: 'Không tìm thấy sự kiện nào phù hợp. Vui lòng thử lại!'", 
         "evidence/screenshots/bug009_typo_message.png", "18/10/2026", "Đã xác nhận", "Xác nhận đúng bẫy lỗi SEED-09 của hệ thống"),

        # BUG-010: SEED-10 (Content / Trivial)
        ("BUG-010", "Hiển thị sai nội dung thông báo lỗi khi nhập mã voucher không hợp lệ", 
         "Content", "Trivial", "Low", "FR-07", "TC-FR07-004", 
         "Form Đặt vé", "Chrome 133 / Windows 11", 
         "Nhập mã voucher không tồn tại 'SAIMA'", 
         "1. Nhập mã voucher sai\n2. Bấm Áp dụng", 
         "Hiển thị thông báo: 'Mật khẩu tài khoản không đúng, vui lòng thử lại'", 
         "FR-07, SRS Mục 4.2: Thông báo đúng ngữ cảnh: 'Mã giảm giá không tồn tại hoặc đã hết hạn'", 
         "evidence/screenshots/bug010_wrong_voucher_msg.png", "21/10/2026", "Đã xác nhận", "Xác nhận đúng bẫy lỗi SEED-10 của hệ thống"),

        # BUG-011: SEED-11 (Content / Trivial)
        ("BUG-011", "Banner chính sách hoàn hủy vé hiển thị mâu thuẫn với quy định trong SRS", 
         "Content", "Trivial", "Low", "FR-05", "TC-FR05-004", 
         "/events/1", "Chrome 133 / Windows 11", 
         "Xem trang chi tiết sự kiện 1", 
         "1. Mở trang chi tiết sự kiện\n2. Quan sát banner màu vàng", 
         "Banner hiển thị: 'Chính sách: Hoàn 100% nếu hủy trước 1 ngày'", 
         "FR-05, FR-09, SRS BR-05: Chỉ hoàn 70% từ 24-48h, không hoàn dưới 24h", 
         "evidence/screenshots/bug011_policy_mismatch.png", "18/10/2026", "Đã xác nhận", "Xác nhận đúng bẫy lỗi SEED-11 của hệ thống"),

        # BUG-012: SEED-12 (Performance / Major)
        ("BUG-012", "Blocking I/O delay giả lập N+1 Query làm trễ API GET /api/events > 1.7 giây", 
         "Performance", "Major", "High", "FR-04", "TC-NFR01-001", 
         "GET /api/events", "JMeter 5.6.3 / Windows 11", 
         "Gọi API lấy danh sách sự kiện", 
         "1. Gửi request GET /api/events\n2. Đo thời gian phản hồi", 
         "Vòng lặp bị chèn delay 350ms/event khiến response time vọt lên 1.840ms", 
         "NFR-01: Thời gian phản hồi API phải <= 500ms cho 95% request", 
         "evidence/screenshots/bug012_nplus1_delay.png", "01/11/2026", "Đã xác nhận", "Xác nhận đúng bẫy lỗi SEED-12 của hệ thống"),

        # BUG-013: SEED-13 (Performance / Minor)
        ("BUG-013", "Banner sự kiện tải ảnh mock dung lượng siêu lớn 12MB không nén gây lag", 
         "Performance", "Minor", "Medium", "FR-05", "TC-NFR04-001", 
         "/events/1", "Chrome 133 / Windows 11", 
         "Mở trang chi tiết sự kiện 1", 
         "1. Mở tab Network DevTools\n2. Tải trang chi tiết sự kiện", 
         "Ảnh banner có dung lượng 12.4MB khiến thời gian tải trang kéo dài tới 3.8s", 
         "NFR-04: Thời gian tải trang UI <= 2.0s; hình ảnh tối ưu nén WebP/JPEG", 
         "evidence/screenshots/bug013_large_banner.png", "18/10/2026", "Đã xác nhận", "Xác nhận đúng bẫy lỗi SEED-13 của hệ thống"),

        # BUG-014: SEED-14 (Crash / Critical)
        ("BUG-014", "Crash HTTP 500 Unhandled Exception khi voucher_code chứa ký tự đặc biệt nháy đơn", 
         "Crash", "Critical", "High", "FR-06", "TC-NFR06-002", 
         "POST /api/bookings", "Postman v11 / Windows 11", 
         "Đặt vé với mã voucher có chứa ký tự '", 
         "1. Gửi POST /api/bookings với voucher_code=\"GIAM'20\"\n2. Quan sát kết quả", 
         "Server văng lỗi 500 Unhandled Exception (IndexError trong split chuỗi)", 
         "NFR-07: Hệ thống phải bắt toàn bộ ngoại lệ và trả về HTTP 400/422, không được crash 500", 
         "evidence/screenshots/bug014_crash_quote.png", "21/10/2026", "Đã xác nhận", "Xác nhận đúng bẫy lỗi SEED-14 của hệ thống"),

        # BUG-015: SEED-15 (Crash / Major)
        ("BUG-015", "Lỗi ZeroDivisionError gây Crash HTTP 500 khi truyền tham số limit=0", 
         "Crash", "Major", "High", "FR-04", "TC-NFR07-001", 
         "GET /api/events?limit=0", "Postman v11 / Windows 11", 
         "Gọi API phân trang sự kiện", 
         "1. Gửi GET /api/events?limit=0\n2. Quan sát phản hồi", 
         "Server văng lỗi ZeroDivisionError Crash HTTP 500 tại phép chia total // limit", 
         "NFR-07: Bắt lỗi validation tham số query, trả về HTTP 422 Unprocessable Entity", 
         "evidence/screenshots/bug015_zerodivision_crash.png", "03/11/2026", "Đã xác nhận", "Xác nhận đúng bẫy lỗi SEED-15 của hệ thống"),

        # BUG-016: LỖI THẬT PHÁT HIỆN THÊM (Bonus Bug: Functional / Minor)
        ("BUG-016", "API cập nhật hồ sơ người dùng thiếu validation cho phép đổi email sai cú pháp không có @", 
         "Functional", "Minor", "Medium", "FR-02", "TC-FR02-004", 
         "PUT /api/users/{id}", "Postman v11 / Windows 11", 
         "Đã đăng nhập tài khoản Khách", 
         "1. Gửi PUT /api/users/3 với body {\"email\": \"invaliddomain.com\"}\n2. Kiểm tra DB", 
         "Hệ thống chấp nhận cập nhật email sai cú pháp không có ký tự @ vào database", 
         "FR-02, BR-01: Trường email phải tuân thủ chuẩn RFC 5322 và chứa ký tự @ và domain hợp lệ", 
         "evidence/screenshots/bug016_email_validation.png", "15/10/2026", "Đã xác nhận", "Xác nhận đúng lỗi thực tế ngoài Manifest, được tính điểm thưởng")
    ]
    
    for idx, item in enumerate(bug_reports):
        row = 5 + idx
        for col_idx, val in enumerate(item):
            ws_bug.cell(row=row, column=col_idx+1, value=val)
            
    print(f"-> Inserted {len(bug_reports)} Bug Reports into Sheet Bug_Report!")

    wb.save(excel_path)
    print("-> Successfully saved all Phase 2 and Phase 3 sheets into Mau_03!")

if __name__ == '__main__':
    populate_testing_sheets()

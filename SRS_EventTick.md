# ĐẶC TẢ YÊU CẦU PHẦN MỀM (SRS - SOFTWARE REQUIREMENTS SPECIFICATION)
## DỰ ÁN: NỀN TẢNG ĐĂNG KÝ & BÁN VÉ SỰ KIỆN TRỰC TUYẾN (iTick)

- **Môn học**: Đánh giá hiệu năng / Kiểm thử phần mềm
- **Mã hệ thống**: ITICK-V1.2
- **Phiên bản tài liệu**: 1.2 (Bổ sung Cơ chế Phí Dịch vụ Sàn 5%, Phê duyệt Tự động & Superadmin Toàn quyền)
- **Tác giả (Chủ hệ thống)**: Lại Thị Thanh Xuân – 23110309
- **Tester phản biện**: Sinh viên B
- **Căn cứ phát triển**: Kế thừa trực tiếp từ [URD_EventTick.md](file:///d:/SJ_Testing/Project/URD_EventTick.md)

---


> **Deploy URL**: [https://itick-platform.onrender.com/](https://itick-platform.onrender.com/)  
> **GitHub Repo**: [https://github.com/DYouth572/itick-platform](https://github.com/DYouth572/itick-platform)  
> **Google Drive**: [https://drive.google.com/drive/folders/1K9Mq0RubxVY5YOycdWN-DqwUO4dmS-kc?usp=sharing](https://drive.google.com/drive/folders/1K9Mq0RubxVY5YOycdWN-DqwUO4dmS-kc?usp=sharing)

## 1. Giới thiệu & Tổng quan Hệ thống (Introduction & System Overview)

#
> **Deploy URL**: [https://itick-platform.onrender.com/](https://itick-platform.onrender.com/)  
> **GitHub Repo**: [https://github.com/DYouth572/itick-platform](https://github.com/DYouth572/itick-platform)  
> **Google Drive**: [https://drive.google.com/drive/folders/1K9Mq0RubxVY5YOycdWN-DqwUO4dmS-kc?usp=sharing](https://drive.google.com/drive/folders/1K9Mq0RubxVY5YOycdWN-DqwUO4dmS-kc?usp=sharing)

## 1.1. Mục đích tài liệu (Purpose)
Tài liệu này đặc tả chi tiết toàn bộ các yêu cầu chức năng (Functional Requirements - FR), yêu cầu phi chức năng (Non-Functional Requirements - NFR), quy tắc nghiệp vụ (Business Rules), ràng buộc dữ liệu (Data Constraints) và ma trận kiểm soát của hệ thống **iTick**. Đây là tài liệu căn cứ để Chủ hệ thống triển khai mã nguồn, cài đặt lỗi kiểm thử có kiểm soát, đồng thời là cơ sở duy nhất để Tester thiết kế bộ kịch bản kiểm thử thủ công, kiểm thử tự động API (Postman/Newman), kiểm thử giao diện (Puppeteer) và kiểm thử hiệu năng (JMeter).

#
> **Deploy URL**: [https://itick-platform.onrender.com/](https://itick-platform.onrender.com/)  
> **GitHub Repo**: [https://github.com/DYouth572/itick-platform](https://github.com/DYouth572/itick-platform)  
> **Google Drive**: [https://drive.google.com/drive/folders/1K9Mq0RubxVY5YOycdWN-DqwUO4dmS-kc?usp=sharing](https://drive.google.com/drive/folders/1K9Mq0RubxVY5YOycdWN-DqwUO4dmS-kc?usp=sharing)

## 1.2. Kiến trúc & Công nghệ Thực thi (System Architecture)
- **Mô hình kiến trúc**: Monolithic RESTful API kết hợp Server-Side Rendering (SSR).
- **Backend**: Python 3.11+ / FastAPI, Pydantic v2 (Validation), Uvicorn (ASGI Server), chạy cổng `8001`.
- **Database**: SQLite 3 (WAL Mode, Foreign Keys enabled) / PostgreSQL.
- **Frontend**: Jinja2 Templates kết hợp Tailwind CSS (Play CDN), Theme Ambient Aurora Mesh (Dual Mode: Sáng/Tối) và JavaScript thuần (Vanilla JS).
- **Authentication**: JWT (JSON Web Token) HMAC-SHA256, hạn sử dụng 24 giờ.
- **Thanh toán**: Tích hợp kép Ví nội bộ (Internal Wallet) và Cổng thanh toán VietQR tự động qua PayOS.

---

## 2. Ma trận Phân quyền Người dùng (RBAC - Role-Based Access Control)

Hệ thống phân định 4 nhóm tác nhân truy cập:
- **GUEST**: Khách vãng lai chưa đăng nhập.
- **ATTENDEE**: Người tham dự / Khách hàng đã đăng nhập.
- **ORGANIZER**: Ban tổ chức sự kiện.
- **ADMIN**: Quản trị viên tối cao (Superadmin) với toàn quyền quản trị nền tảng iTick.

| Mã FR | Tên chức năng | GUEST | ATTENDEE | ORGANIZER | ADMIN |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **FR-01** | Đăng ký tài khoản mới | **C** | - | - | - |
| **FR-02** | Đăng nhập & Cấp JWT Token | **R** | - | - | - |
| **FR-03** | Xem thông tin cá nhân & Đổi mật khẩu | - | **CRUD** | **CRUD** | **CRUD** |
| **FR-04** | Tìm kiếm & Lọc danh sách sự kiện | **R** | **R** | **R** | **R** |
| **FR-05** | Xem chi tiết sự kiện & Tồn kho vé | **R** | **R** | **R** | **R** |
| **FR-06** | Đặt mua vé, Tính phí sàn & Phân bổ ví | - | **C** | **C** | **C** |
| **FR-07** | Áp dụng mã giảm giá (Voucher) | - | **R** | **R** | **R** |
| **FR-08** | Xem danh sách vé cá nhân & Lấy mã vé | - | **R** | **R** | **R** |
| **FR-09** | Yêu cầu hủy vé cá nhân & Hoàn tiền mốc giờ | - | **U** | **U** | **U** |
| **FR-10** | Tạo mới & Chỉnh sửa sự kiện (Auto-Approval) | - | - | **CRUD** | **CRUD** |
| **FR-11** | Cấu hình phân hạng vé & Định mức kho | - | - | **CRUD** | **CRUD** |
| **FR-12** | Soát vé tại cổng (Check-in Scanner) | - | - | **U** | **U** |
| **FR-13** | Quản trị Toàn quyền (Người dùng, Đơn hàng, Vé, Sàn) | - | - | - | **CRUD** |
| **FR-14** | Báo cáo Doanh thu, Phí sàn & Đối soát Dòng tiền | - | - | **R** (Của mình) | **R** (Toàn sàn) |

*(Ghi chú: **C**: Create, **R**: Read, **U**: Update, **D**: Delete, **-**: Không có quyền truy cập)*

---

## 3. Danh mục 14 Yêu cầu Chức năng Chi tiết (Functional Requirements - FR)

### FR-01: Đăng ký Tài khoản (User Registration)
- **Mô tả**: Cho phép khách vãng lai đăng ký tài khoản mới trên hệ thống.
- **Dữ liệu đầu vào**: `full_name`, `email`, `password`, `confirm_password`, `role` (`ATTENDEE` hoặc `ORGANIZER`).
- **Ràng buộc xử lý**:
  - `full_name`: Chuỗi ký tự từ 2 đến 50 ký tự, không chứa ký tự đặc biệt nguy hiểm.
  - `email`: Chuẩn định dạng RFC 5322, duy nhất trong cơ sở dữ liệu (Unique constraint).
  - `password`: Tối thiểu 6 ký tự, tối đa 32 ký tự, phải chứa ít nhất 1 chữ số.
  - `confirm_password`: Phải trùng khớp 100% với `password`.
- **Đầu ra**: Trả về HTTP 201 Created kèm thông tin User (không bao gồm mật khẩu) hoặc HTTP 400/422 nếu vi phạm.

### FR-02: Đăng nhập & Xác thực JWT (User Authentication)
- **Mô tả**: Xác thực người dùng và cấp mã JWT Bearer Token.
- **Dữ liệu đầu vào**: `email`, `password`.
- **Ràng buộc xử lý**:
  - Mã hóa mật khẩu kiểm tra bằng Bcrypt hash.
  - Nếu tài khoản có trạng thái `is_active = False` (bị khóa bởi Admin) $\rightarrow$ Trả về HTTP 403 Forbidden ("Tài khoản đã bị tạm khóa").
  - Đăng nhập thất bại quá 5 lần trong vòng 10 phút $\rightarrow$ Tạm khóa đăng nhập email đó trong 15 phút.
- **Đầu ra**: HTTP 200 OK kèm JSON: `{ "access_token": "...", "token_type": "bearer", "user": { "id": 1, "role": "ATTENDEE" } }`.

### FR-03: Quản lý Thông tin Hồ sơ (User Profile Management)
- **Mô tả**: Người dùng xem và cập nhật thông tin cá nhân (họ tên, số điện thoại, đổi mật khẩu).
- **Ràng buộc**: `phone_number` phải đúng định dạng số điện thoại Việt Nam (10 chữ số, bắt đầu bằng 03, 05, 07, 08, 09). Đổi mật khẩu bắt buộc nhập đúng mật khẩu hiện tại.

### FR-04: Tìm kiếm & Lọc Danh sách Sự kiện (Event Search & Filter)
- **Mô tả**: Cho phép mọi đối tượng tra cứu danh sách sự kiện đã được công khai (`status = PUBLISHED` và `is_visible = True`).
- **Dữ liệu đầu vào (Query Params)**:
  - `keyword`: Tìm kiếm không phân biệt hoa thường trong `title` và `location` (tối đa 100 ký tự).
  - `category`: Lọc theo danh mục (`TECHNOLOGY`, `BUSINESS`, `MUSIC`, `EDUCATION`, `WORKSHOP`).
  - `skip` (mặc định 0), `limit` (mặc định 20, min 1, max 50).
- **Đầu ra**: Trả về danh sách sự kiện kèm tổng số trang (Pagination).

### FR-05: Xem Chi tiết Sự kiện & Tồn kho Hạng vé (Event Details & Ticket Availability)
- **Mô tả**: Trả về toàn bộ thông tin chi tiết của một sự kiện và tình trạng các phân hạng vé.
- **Đầu ra**: Bao gồm: Thông tin sự kiện, thông tin Ban tổ chức, danh sách các Hạng vé (`id`, `name`, `price`, `total_quantity`, `available_quantity`). Nếu `available_quantity = 0` $\rightarrow$ Đánh dấu `is_sold_out = True`.

### FR-06: Đặt mua Vé, Tính Phí Sàn & Phân Bổ Dòng Tiền (Booking & Revenue Allocation)
- **Mô tả**: Người dùng chọn sự kiện, chọn hạng vé, số lượng và thực hiện đặt vé.
- **Dữ liệu đầu vào**: `event_id`, `tier_id`, `quantity`, `voucher_code` (tùy chọn), `payment_method` (`WALLET` hoặc `PAYOS`).
- **Ràng buộc xử lý**:
  - `quantity`: Số nguyên từ 1 đến 5 vé / đơn hàng.
  - Phải kiểm tra tồn kho: `available_quantity >= quantity`. Trừ tồn kho ngay lập tức khi tạo đơn hàng.
  - Mỗi vé trong đơn hàng được sinh một mã định danh duy nhất (UUID/Alpha code 12 ký tự: `TICK-XXXXXXXX`).
  - **Cơ chế Phí Sàn Nền Tảng (Platform Commission Fee)**:
    - Áp dụng tỷ lệ phí sàn `platform_fee_rate` (mặc định **5.0%** theo cấu hình hệ thống).
    - Tính toán làm tròn chuẩn tiền tệ VND:
      $$\text{platform\_fee} = \text{round}\left(\frac{\text{final\_amount} \times \text{platform\_fee\_rate}}{100}\right)$$
      $$\text{organizer\_amount} = \text{final\_amount} - \text{platform\_fee}$$
    - Đối với đơn hàng có `final_amount = 0` (vé miễn phí): $\text{platform\_fee} = 0$, $\text{organizer\_amount} = 0$.
    - Doanh thu thuần `organizer_amount` được tự động ghi nhận và cộng dồn vào số dư ví Ban tổ chức (`organizer.balance += organizer_amount`).
- **Đầu ra**: Trả về HTTP 201 Created kèm thông tin `Order` bao gồm: `platform_fee_rate`, `platform_fee`, `organizer_amount`, `status` và danh sách vé đã cấp.

### FR-07: Áp dụng Mã Giảm giá (Voucher Validation & Calculation)
- **Mô tả**: Kiểm tra tính hợp lệ của mã giảm giá và tính toán số tiền được chiết khấu.
- **Ràng buộc xử lý**:
  - Voucher phải tồn tại, đang kích hoạt (`is_active = True`).
  - Ngày đặt vé phải nằm trong khoảng: `start_date <= current_date <= end_date`.
  - Số lượt dùng còn lại: `remaining_uses > 0`.
  - Tổng giá trị đơn hàng trước giảm giá phải $\ge$ `min_order_value`.
  - Giảm theo phần trăm (`PERCENT`): $\text{discount\_amount} = \text{total} \times \text{discount\_percent} / 100$, nhưng không được vượt quá `max_discount_cap`.
  - Giảm theo số tiền cố định (`FIXED`): $\text{discount\_amount} = \text{fixed\_amount}$.

### FR-08: Xem Vé Cá nhân & Lấy Mã Vé Điện tử (My Tickets & QR E-Ticket)
- **Mô tả**: Người tham dự xem danh sách tất cả các vé mình đã mua.
- **Ràng buộc**: Chỉ xem được vé thuộc sở hữu của chính User ID đang đăng nhập (hoặc Admin).
- **Đầu ra**: Danh sách vé kèm trạng thái: `CONFIRMED` (Hợp lệ, chưa dùng), `CHECKED_IN` (Đã vào cửa), `CANCELLED` (Đã hủy).

### FR-09: Yêu cầu Hủy vé Cá nhân & Tính phí Hoàn tiền (Ticket Cancellation & Refund)
- **Mô tả**: Cho phép người dùng hủy vé cá nhân đã mua trước khi sự kiện diễn ra.
- **Ràng buộc xử lý**:
  - Chỉ được hủy vé ở trạng thái `CONFIRMED`.
  - Khoảng cách thời gian: `delta_hours = (event_start_time - current_time)`.
    - Nếu `delta_hours >= 48`: Phí hủy 10% giá vé ban đầu, hoàn tiền 90%.
    - Nếu `24 <= delta_hours < 48`: Phí hủy 30% giá vé ban đầu, hoàn tiền 70%.
    - Nếu `delta_hours < 24`: Từ chối hủy (HTTP 400: "Không thể hủy vé trước sự kiện dưới 24 giờ").
  - Sau khi hủy thành công: Vé chuyển trạng thái sang `CANCELLED`, tồn kho hạng vé tương ứng tự động cộng trả lại (`available_quantity += 1`).

### FR-10: Tạo mới Sự kiện & Cơ chế Phê duyệt Tự động (Event Creation & Auto-Approval)
- **Mô tả**: Ban tổ chức khởi tạo trang sự kiện mới.
- **Dữ liệu đầu vào**: `title`, `description`, `location`, `banner_url`, `start_time`, `end_time`, `category`, `capacity`.
- **Ràng buộc xử lý**:
  - `title`: Chuỗi ký tự từ 5 đến 150 ký tự.
  - `description`: Tối thiểu 20 ký tự, tối đa 5000 ký tự.
  - `capacity`: Số nguyên dương từ 10 đến 10,000 người.
  - `start_time` phải lớn hơn thời gian hiện tại ít nhất 2 giờ; `end_time` phải lớn hơn `start_time` ít nhất 30 phút.
  - **Cơ chế Phê duyệt Tự động (Auto-Approval)**: Hệ thống tự động thẩm định tính hợp lệ của dữ liệu đầu vào. Nếu đạt yêu cầu, sự kiện được cấp trạng thái `PUBLISHED` và kích hoạt hiển thị ngay lập tức (`is_visible = True`), loại bỏ quy trình chờ duyệt thủ công gây nghẽn dòng hoạt động.
  - **Cơ chế Tự động Ẩn Sự kiện**: Định kỳ rà soát các sự kiện đã kết thúc quá 10 phút để tự động chuyển sang ẩn khỏi trang chủ (`is_visible = False`).

### FR-11: Cấu hình Phân hạng Vé (Ticket Tier Setup)
- **Mô tả**: Ban tổ chức thiết lập các gói vé cho sự kiện của mình.
- **Dữ liệu đầu vào**: `event_id`, `tier_name`, `price`, `total_quantity`, `description`.
- **Ràng buộc xử lý**:
  - `price`: Số nguyên từ 0 (vé miễn phí) đến 50,000,000 VNĐ.
  - `total_quantity`: Số nguyên từ 1 đến 5,000 vé.
  - Tổng số vé của tất cả các hạng vé không được vượt quá `capacity` của sự kiện.

### FR-12: Soát vé tại Cổng Sự kiện (Ticket Check-in Verification)
- **Mô tả**: Ban tổ chức nhập hoặc quét mã vé để xác thực khách vào cửa.
- **Dữ liệu đầu vào**: `ticket_code`, `event_id`.
- **Ràng buộc xử lý**:
  - Mã vé phải thuộc đúng `event_id` chỉ định.
  - Nếu vé ở trạng thái `CONFIRMED`: Chuyển sang `CHECKED_IN`, lưu `check_in_time = current_timestamp`. Trả về HTTP 200: "HỢP LỆ".
  - Nếu vé ở trạng thái `CHECKED_IN`: Trả về HTTP 409 Conflict: "VÉ ĐÃ SỬ DỤNG VÀO LÚC [thời gian]".
  - Nếu vé ở trạng thái `CANCELLED`: Trả về HTTP 400 Bad Request: "VÉ NÀY ĐÃ BỊ HỦY".

### FR-12b: Xuất Danh Sách Soát Vé & Đối Soát Timeline Điểm Danh (Attendee & Gate Check-in Export)
- **Mô tả**: Ban tổ chức và Admin xuất báo cáo danh sách người tham dự và mã vé theo từng sự kiện để nạp vào trạm soát vé hoặc đối soát điểm danh.
- **Endpoint**: `GET /api/events/{event_id}/export-attendees?format=xlsx|csv|json`
- **Ràng buộc xử lý & Cơ chế Đối soát Timeline Tự động**:
  - **Mã hóa & Định dạng file**:
    + **Microsoft Excel (`.xlsx`)**: Định dạng xuất mặc định chuẩn đẹp với `openpyxl`, tích hợp **Data Validation Dropdown** cho cột *Trạng Thái Soát Vé* (`ĐÃ THAM DỰ`, `VẮNG MẶT`, `CHƯA CHECK-IN`, `ĐÃ HỦY VÉ`) cho phép người soát vé click chọn trực tiếp; áp dụng bảng màu chuyên nghiệp (Navy/Emerald), thin border, zebra striping, auto-fit cột, freeze panes và định dạng tiền tệ VNĐ.
    + **CSV (UTF-8 BOM `\ufeff`)**: Mở trực tiếp trên mọi phần mềm bảng tính và hệ điều hành không bị vỡ font tiếng Việt.
    + **JSON API**: Dành riêng cho máy quét/trạm soát vé tự động nạp danh sách vào bộ nhớ offline.
  - **Đối chiếu Timeline tự động**:
    1. **ĐÃ THAM DỰ**: Khách đã quét qua cổng thành công (`status == CHECKED_IN`), hiển thị chính xác mốc giờ check-in (`HH:mm:ss DD/MM/YYYY`).
    2. **VẮNG MẶT**: Khách mua vé nhưng không qua cổng soát vé sau khi sự kiện đã kết thúc (`current_time > end_time` hoặc `status == EXPIRED`).
    3. **CHƯA CHECK-IN**: Vé hợp lệ đang trong thời hạn chờ vào cổng trước/trong khi sự kiện diễn ra.
    4. **ĐÃ HỦY VÉ**: Đơn hàng đã được hoàn tiền trước sự kiện (`status == CANCELLED`).
  - **Bảo toàn dữ liệu**: Đảm bảo xuất đầy đủ 100% người mua vé thuộc sự kiện kể cả trường hợp vé đơn hoặc đơn hàng nhiều vé.

### FR-13: Quản trị Hệ thống Toàn diện (Superadmin Control Center)
- **Mô tả**: Quản trị viên tối cao (Admin) sở hữu quyền lực điều phối toàn diện hệ thống iTick qua 5 phân hệ chuyên biệt:
  1. **Quản trị Người dùng & Phân quyền (RBAC)**: Xem danh sách, tạo mới tài khoản, cập nhật thông tin cá nhân, thay đổi vai trò (Role: ATTENDEE, ORGANIZER, ADMIN), đặt lại mật khẩu và khóa/kích hoạt tài khoản.
  2. **Quản trị Sự kiện Toàn sàn**: Phê duyệt sự kiện, từ chối sự kiện, ẩn/hiện sự kiện trên trang chủ và xóa sự kiện.
  3. **Quản trị Đơn hàng & Đối soát Hoàn tiền Khẩn cấp**: Xem danh sách đơn hàng toàn sàn, thực hiện **Hủy đơn khẩn cấp & Hoàn tiền 100%** (`POST /api/admin/orders/{id}/refund`):
     - Hoàn trả 100% số tiền `final_amount` cho khách hàng.
     - Tự động thu hồi số tiền doanh thu `organizer_amount` đã chuyển vào ví của Organizer (`organizer.balance -= organizer_amount`).
     - Trừ phần phí sàn `platform_fee` đã ghi nhận khỏi doanh thu nền tảng.
     - Cập nhật toàn bộ các vé thuộc đơn hàng sang `CANCELLED` và hoàn trả kho vé khả dụng.
  4. **Quản trị Vé Điện tử Toàn sàn**: Tra cứu toàn bộ vé phát hành, vô hiệu hóa vé gian lận (`POST /api/admin/tickets/{id}/void`).
  5. **Cấu hình Phí Sàn Nền tảng**: Tra cứu (`GET /api/admin/system/fee`) và cập nhật tỷ lệ phần trăm phí sàn (`PUT /api/admin/system/fee`) áp dụng tức thì cho các giao dịch mới.

### FR-14: Báo cáo Thống kê Doanh thu & Đối soát Dòng tiền (Financial Reconciliation)
- **Mô tả**: Cung cấp số liệu thống kê tài chính và đối soát dòng tiền minh bạch theo thời gian thực.
- **Nội dung thống kê**:
  - **Doanh thu gộp (Gross Revenue)**: Tổng tiền thanh toán của các đơn hàng thành công.
  - **Phân rã kênh thanh toán**: Doanh thu qua VietQR PayOS vs Doanh thu qua Ví nội bộ.
  - **Phí dịch vụ nền tảng (Platform Commission Fee)**: Doanh thu phí sàn iTick thực tế thu được (5%).
  - **Chi trả Ban tổ chức (Net Organizer Payout)**: Tổng số tiền đã thanh toán vào ví các nhà tổ chức sự kiện.
  - **Tỷ lệ Check-in tại cổng**: Phần trăm vé đã soát vào cổng thành công.
  - **Bảo toàn Dòng tiền Tuyệt đối**:
    $$\text{Doanh thu Gộp} = \text{Phí Sàn iTick} + \text{Chi Trả BTC} + \text{Tiền Hoàn Trả (Refunded)}$$
    $$\text{Độ lệch đối soát} = 0\text{ VNĐ}$$

---

## 4. Đặc tả 4 Luồng Nghiệp vụ Hoàn chỉnh (Use Cases: Main, Alternative, Exception Flows)

### USE CASE 01: Đặt mua Vé & Phân Bổ Dòng Tiền (FLOW-01)
- **Tác nhân chính**: Khách tham dự (Attendee).
- **Điều kiện tiên quyết**: Sự kiện đang ở trạng thái `PUBLISHED` & `is_visible = True`, hạng vé còn tồn kho khả dụng.
- **Luồng chính (Main Flow)**:
  1. Người dùng chọn Sự kiện và chọn Hạng vé.
  2. Người dùng chọn số lượng vé (từ 1 đến 5 vé).
  3. Người dùng nhập mã giảm giá Voucher (nếu có). Hệ thống tính chiết khấu hợp lệ.
  4. Người dùng chọn phương thức thanh toán (Ví nội bộ hoặc VietQR PayOS) và bấm xác nhận đặt vé.
  5. Hệ thống khởi tạo Transaction: Trừ tồn kho vé, tính phí sàn `platform_fee` (5%), tính `organizer_amount`, cộng ví Ban tổ chức, trừ số dư khách (nếu thanh toán ví).
  6. Hệ thống xuất mã vé điện tử định danh và đưa người dùng đến trang hoàn tất đơn hàng.

---

## 5. Quy tắc Nghiệp vụ (Business Rules - BR)

- **BR-01 (Giới hạn đặt vé)**: Mỗi tài khoản người dùng chỉ được đặt tối đa 5 vé trong 1 giao dịch và không quá 10 vé cho cùng một sự kiện.
- **BR-02 (Cạnh tranh tài nguyên - Concurrency)**: Thao tác trừ vé phải sử dụng kiểm soát cạnh tranh (Database Atomic Update hoặc Locking) để đảm bảo không xảy ra hiện tượng bán âm kho (Overselling).
- **BR-03 (Chính sách Voucher)**: Mỗi đơn hàng chỉ được sử dụng tối đa 1 mã giảm giá. Mức giảm tối đa không vượt quá `max_discount_cap`.
- **BR-04 (Bất biến trạng thái vé)**: Vé đã chuyển sang trạng thái `CHECKED_IN` hoặc `CANCELLED` là trạng thái cuối (Terminal State), không thể đổi ngược lại trạng thái `CONFIRMED`.
- **BR-05 (Chính sách phí phạt hủy vé cá nhân)**:
  $$\text{Số tiền hoàn} = \begin{cases} 
  \text{Giá vé} \times 90\% & \text{nếu thời gian đến sự kiện } \ge 48\text{ giờ} \\
  \text{Giá vé} \times 70\% & \text{nếu } 24\text{ giờ} \le \text{thời gian đến sự kiện } < 48\text{ giờ} \\
  0\text{ (Từ chối hủy)} & \text{nếu thời gian đến sự kiện } < 24\text{ giờ}
  \end{cases}$$
- **BR-06 (Quy tắc Tính Phí Sàn & Làm tròn Tiền tệ)**:
  - Tiền tệ Việt Nam Đồng (VND) không sử dụng số thập phân lẻ. Mọi phép tính phí sàn bắt buộc dùng hàm `round()` sang số nguyên gần nhất.
  - Sự kiện miễn phí (0đ) không thu phí sàn.
  - Phí sàn được tính trên **Số tiền thực trả (Final Amount)** sau khi đã trừ giảm giá Voucher, đảm bảo không thu phí ảo trên phần tiền được chiết khấu.
- **BR-07 (Quy tắc Hoàn tiền Khẩn cấp của Superadmin)**:
  - Khi Superadmin hủy đơn khẩn cấp, khách hàng được hoàn đủ 100% số tiền đã trả.
  - Ban tổ chức bị khấu trừ lại đúng khoản tiền `organizer_amount` đã nhận vào ví khi tạo đơn.
  - Phí sàn iTick tự động điều chỉnh giảm tương ứng, bảo toàn tuyệt đối dòng tiền sàn.

---

## 6. Ràng buộc Dữ liệu Đo lường được (Testable Data Constraints)

| Trường dữ liệu (Field) | Kiểu dữ liệu | Giá trị hợp lệ (Valid Boundary) | Giá trị không hợp lệ (Invalid Boundary) | Thông báo lỗi tương ứng |
| :--- | :---: | :--- | :--- | :--- |
| `email` | String | Format RFC 5322, dài từ 6 đến 100 ký tự | `test`, `test@`, `test@domain`, dài > 100 ký tự | "Email không đúng định dạng chuẩn." |
| `password` | String | 6 đến 32 ký tự, có ít nhất 1 chữ số | Dưới 6 ký tự ("12345"), trên 32 ký tự, không có số | "Mật khẩu phải từ 6 đến 32 ký tự và có ít nhất 1 chữ số." |
| `phone_number` | String | 10 chữ số, bắt đầu: 03, 05, 07, 08, 09 | 9 chữ số, 11 chữ số, chứa chữ cái | "Số điện thoại không hợp lệ." |
| `event_title` | String | 5 đến 150 ký tự | < 5 ký tự ("Hội"), > 150 ký tự | "Tiêu đề sự kiện phải từ 5 đến 150 ký tự." |
| `capacity` | Integer | $10 \le \text{capacity} \le 10,000$ | $9$, $0$, âm, $10,001$ | "Sức chứa sự kiện phải từ 10 đến 10,000 người." |
| `ticket_price` | Integer | $0 \le \text{price} \le 50,000,000$ VNĐ | $-1$, $50,000,01$ | "Giá vé phải từ 0 đến 50,000,000 VNĐ." |
| `ticket_quantity` | Integer | $1 \le \text{qty} \le 5$ (trên 1 đơn) | $0$, $-1$, $6$ | "Số lượng vé mỗi đơn phải từ 1 đến 5 vé." |
| `voucher_discount` | Integer | $1 \le \text{discount} \le 100$ (%) | $0$, $101$, âm | "Tỷ lệ giảm giá phải từ 1% đến 100%." |
| `platform_fee_rate` | Float | $0.0 \le \text{rate} \le 100.0$ (%) | Âm, $> 100.0$ | "Tỷ lệ phí sàn phải từ 0% đến 100%." |

---

## 7. Yêu cầu Phi chức năng Chi tiết (Non-Functional Requirements - NFR)

### 7.1. Nhóm NFR Hiệu năng (Performance NFRs)
- **NFR-01 (Thời gian phản hồi API tra cứu sự kiện)**: $p_{95} \le 500\text{ ms}$, trung bình $\le 300\text{ ms}$ dưới tải 50 CCU.
- **NFR-02 (Thời gian phản hồi & Tính toàn vẹn khi Đặt vé Cạnh tranh)**: $p_{90} \le 1,500\text{ ms}$, tỷ lệ bán vượt vé (Overselling Rate) $= 0\%$ khi tải 100 CCU tranh chấp vé.
- **NFR-03 (Thông lượng Xử lý)**: Throughput $\ge 80\text{ req/s}$ trên cấu hình 1 vCPU, 512MB RAM.
- **NFR-04 (Hiệu năng API Soát vé Check-in)**: Thời gian phản hồi trung bình $\le 400\text{ ms}$ cho 20 cổng soát vé đồng thời.

### 7.2. Nhóm NFR Vận hành, Bảo mật & Tương thích
- **NFR-05 (Bảo mật & Xác thực)**: Mật khẩu băm Bcrypt work factor $\ge 12$; Token JWT HMAC-SHA256 hết hạn 24 giờ; ngăn chặn SQL Injection qua ORM parameterized.
- **NFR-06 (Tính khả dụng & Port hoạt động)**: Hệ thống duy trì hoạt động trên cổng tiêu chuẩn `8001`, endpoint `/health` phản hồi $< 100\text{ ms}$.
- **NFR-07 (Tính tương thích Giao diện)**: Responsive trên màn hình di động $\ge 375\text{ px}$, hỗ trợ chuyển đổi giao diện Sáng/Tối (Dual Theme Aurora Mesh).
- **NFR-08 (Khả năng Kiểm thử & Chuẩn hóa API)**: 100% API cung cấp đặc tả OpenAPI 3.0 tại `/openapi.json` và giao diện tương tác `/docs`.

---

## 8. Ma trận Truy vết Yêu cầu (Traceability Matrix: URD $\leftrightarrow$ SRS)

| Mã User Story (URD) | Tên User Story | Mã SRS Chức năng (FR) | Mã Luồng nghiệp vụ | Mã NFR liên quan |
| :---: | :--- | :---: | :---: | :---: |
| **US-01** | Đăng ký tài khoản | `FR-01` | - | NFR-05, NFR-08 |
| **US-02** | Đăng nhập hệ thống | `FR-02` | - | NFR-05, NFR-08 |
| **US-03** | Tìm kiếm & lọc sự kiện | `FR-04` | `FLOW-01` | NFR-01, NFR-03 |
| **US-04** | Xem chi tiết sự kiện | `FR-05` | `FLOW-01` | NFR-01, NFR-07 |
| **US-05** | Đặt mua vé & Phân bổ dòng tiền | `FR-06` | `FLOW-01` | NFR-02, NFR-03, NFR-08 |
| **US-06** | Nhập mã giảm giá Voucher | `FR-07` | `FLOW-01` | NFR-08 |
| **US-07** | Xem vé đã mua & mã QR | `FR-08` | `FLOW-01` | NFR-07, NFR-08 |
| **US-08** | Yêu cầu hủy vé hoàn tiền | `FR-09` | `FLOW-04` | NFR-08 |
| **US-09** | Tạo sự kiện mới (Auto-Approval) | `FR-10` | `FLOW-02` | NFR-05, NFR-08 |
| **US-10** | Cấu hình phân hạng vé | `FR-11` | `FLOW-02` | NFR-08 |
| **US-11** | Soát vé tại cổng | `FR-12` | `FLOW-03` | NFR-04, NFR-08 |
| **US-12** | Thống kê doanh thu & Đối soát phí | `FR-14` | - | NFR-01, NFR-08 |
| **US-13** | Superadmin Quản trị Toàn quyền | `FR-13` | - | NFR-05, NFR-08 |
| **US-14** | Quản lý Chiến dịch Voucher | `FR-07`, `FR-13` | - | NFR-05, NFR-08 |
| **US-15** | Cấu hình Phí Sàn & Đối soát Dòng tiền | `FR-13`, `FR-14` | - | NFR-06, NFR-08 |

---

## 9. Lịch Sử Cập Nhật Tài Liệu (Changelog)

| Phiên bản | Ngày cập nhật | Tác giả | Nội dung thay đổi chính |
| :---: | :---: | :---: | :--- |
| **v1.0** | Tuần 5 | Sinh viên A | Khởi tạo tài liệu đặc tả ban đầu theo mẫu SRS chuẩn IEEE 830. |
| **v1.1** | Tuần 6 | Sinh viên A | Tiếp thu phiếu review của Tester: Bổ sung 4 NFR hiệu năng đo lường được, làm rõ quy tắc Concurrency BR-02 và mốc hủy vé BR-05. |
| **v1.2** | Tuần 6 | Sinh viên A | **Nâng cấp Hệ thống iTick**: <br>1. Chuẩn hóa thương hiệu sang **iTick**.<br>2. Bổ sung cơ chế **Tự động phê duyệt (Auto-Approval)** cho sự kiện mới.<br>3. Bổ sung tính năng **Thương mại & Phí Dịch vụ Sàn** (5%, phân bổ ví BTC, làm tròn số tiền VND).<br>4. Đặc tả cổng **Superadmin Toàn quyền (iTick Control Center)** với 5 tabs, 37 API endpoints, cơ chế hoàn tiền khẩn cấp và cấu hình phí sàn động.<br>5. Mở rộng bộ kịch bản kiểm thử tự động đạt 20/20 Test Cases PASSED. |

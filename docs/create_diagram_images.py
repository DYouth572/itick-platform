# -*- coding: utf-8 -*-
"""
Tạo các biểu đồ Use Case và Flowchart độ phân giải cao (300 DPI)
cho tài liệu SRS_EventTick.docx và URD_EventTick.docx
Đặc điểm:
- 300 DPI sắc nét, chống vỡ hạt
- Khung viền trang nhã, màu sắc chuẩn phong cách kỹ thuật công nghệ
- Font hỗ trợ Unicode tiếng Việt đầy đủ
- Đồng bộ cú pháp Mermaid / PlantUML
"""

import os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

sys.stdout.reconfigure(encoding='utf-8')

assets_dir = r"D:\SJ_Testing\Project\docs\assets"
os.makedirs(assets_dir, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI', 'Calibri', 'Times New Roman']
plt.rcParams['axes.unicode_minus'] = False

# -----------------------------------------------------------------------------
# 1. BIỂU ĐỒ USE CASE TỔNG QUAN (Hình 2-1) - 300 DPI
# -----------------------------------------------------------------------------
def make_usecase_overview():
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Background subtle border
    bg_rect = patches.Rectangle((0.5, 0.5), 99, 99, linewidth=1, edgecolor="#CBD5E1", facecolor="#FFFFFF")
    ax.add_patch(bg_rect)

    # System Boundary Box
    rect = patches.FancyBboxPatch((22, 6), 56, 88, boxstyle="round,pad=1.2", edgecolor="#1E3A8A", facecolor="#F8FAFC", linewidth=2.2)
    ax.add_patch(rect)
    ax.text(50, 91.5, "HỆ THỐNG iTICK PLATFORM (NỀN TẢNG BÁN VÉ SỰ KIỆN)", fontsize=13, fontweight='bold', ha='center', color="#1E3A8A")

    # Actors
    actors = [
        ("Khách vãng lai\n(Guest)", 11, 76, "#475569"),
        ("Khách mua vé\n(Customer/Attendee)", 11, 48, "#2563EB"),
        ("Ban tổ chức\n(Organizer)", 11, 20, "#0D47A1"),
        ("Quản trị viên\n(Administrator)", 89, 62, "#7E22CE"),
        ("Cổng thanh toán\n(VNPay / PayOS)", 89, 26, "#059669")
    ]
    for name, x, y, col in actors:
        circle = patches.Circle((x, y), 3.6, facecolor="#F1F5F9", edgecolor=col, linewidth=2)
        ax.add_patch(circle)
        ax.plot([x, x], [y-3.6, y-8.5], color=col, linewidth=2.2)
        ax.plot([x-3.2, x+3.2], [y-5.8, y-5.8], color=col, linewidth=2.2)
        ax.plot([x, x-3.2], [y-8.5, y-12.8], color=col, linewidth=2.2)
        ax.plot([x, x+3.2], [y-8.5, y-12.8], color=col, linewidth=2.2)
        ax.text(x, y-16, name, fontsize=8.5, fontweight='bold', ha='center', color=col)

    # Use Cases
    usecases = [
        ("UC-01: Đăng ký & Đăng nhập tài khoản", 50, 83),
        ("UC-02: Tìm kiếm & Khám phá sự kiện", 50, 71),
        ("UC-03: Đặt vé & Khóa giữ chỗ 10 phút", 50, 59),
        ("UC-04: Áp dụng Mã giảm giá (Voucher)", 50, 47),
        ("UC-05: Thanh toán trực tuyến & Cấp vé QR", 50, 35),
        ("UC-06: Quản lý vé của tôi & Tải mã vé", 50, 23),
        ("UC-07: Soát vé tại cổng (Check-in Scanner)", 50, 12),
    ]

    for name, cx, cy in usecases:
        ellipse = patches.Ellipse((cx, cy), 34, 7.5, facecolor="#FFFFFF", edgecolor="#1E40AF", linewidth=1.6, zorder=3)
        ax.add_patch(ellipse)
        ax.text(cx, cy, name, fontsize=8.8, fontweight='bold', ha='center', va='center', color="#0F172A", zorder=4)

    # Connecting lines with elegant styling
    ax.plot([14, 33], [74, 83], color="#64748B", linestyle="--", linewidth=1.2)
    ax.plot([14, 33], [74, 71], color="#64748B", linestyle="--", linewidth=1.2)
    ax.plot([14, 33], [48, 59], color="#2563EB", linewidth=1.4)
    ax.plot([14, 33], [48, 47], color="#2563EB", linewidth=1.4)
    ax.plot([14, 33], [48, 35], color="#2563EB", linewidth=1.4)
    ax.plot([14, 33], [48, 23], color="#2563EB", linewidth=1.4)
    ax.plot([14, 33], [20, 23], color="#0D47A1", linewidth=1.4)
    ax.plot([14, 33], [20, 12], color="#0D47A1", linewidth=1.4)
    ax.plot([86, 67], [26, 35], color="#059669", linewidth=1.5)
    ax.plot([86, 67], [62, 83], color="#7E22CE", linestyle="--", linewidth=1.3)
    ax.plot([86, 67], [62, 23], color="#7E22CE", linestyle="--", linewidth=1.3)

    path = os.path.join(assets_dir, "diagram_usecase_overview.png")
    fig.savefig(path, bbox_inches='tight', dpi=300)
    plt.close(fig)
    print(f"Created: {path} (300 DPI)")

# -----------------------------------------------------------------------------
# 2. BIỂU ĐỒ USE CASE PHÂN RÃ (Hình 2-2) - 300 DPI
# -----------------------------------------------------------------------------
def make_usecase_detail():
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    bg_rect = patches.Rectangle((0.5, 0.5), 99, 99, linewidth=1, edgecolor="#CBD5E1", facecolor="#FFFFFF")
    ax.add_patch(bg_rect)

    # Base usecase
    b_ellipse = patches.Ellipse((25, 50), 32, 13, facecolor="#DBEAFE", edgecolor="#1E3A8A", linewidth=2.2)
    ax.add_patch(b_ellipse)
    ax.text(25, 50, "ĐẶT VÉ TRỰC TUYẾN\n(Core Booking UC-03)", fontsize=10.5, fontweight='bold', ha='center', va='center', color="#1E3A8A")

    # Extended / Included UCs
    sub_ucs = [
        ("<<include>>\nKiểm tra tồn kho vé & Khóa giữ chỗ 10 phút\n(Check Available Tier & Hold Timer)", 75, 84, "#1E40AF"),
        ("<<extend>>\nÁp dụng mã giảm giá có trần chiết khấu\n(Voucher Discount Ceiling Validation)", 75, 63, "#059669"),
        ("<<extend>>\nThanh toán trực tuyến qua Cổng đối tác\n(Online Payment Gateway Callback)", 75, 42, "#D97706"),
        ("<<include>>\nPhát hành vé điện tử & Tạo mã QR/Barcode\n(E-Ticket Issuance & Unique QR Code)", 75, 21, "#7E22CE"),
        ("<<include>>\nTự động trích 5% phí sàn iTick\n(Platform Fee Calculation 5%)", 75, 5, "#DC2626"),
    ]

    for name, sx, sy, col in sub_ucs:
        s_ell = patches.Ellipse((sx, sy), 36, 9.2, facecolor="#F8FAFC", edgecolor=col, linewidth=1.6)
        ax.add_patch(s_ell)
        ax.text(sx, sy, name, fontsize=8.2, ha='center', va='center', color="#0F172A", fontweight='bold')
        ax.annotate('', xy=(sx-18, sy), xytext=(41, 50),
                    arrowprops=dict(arrowstyle="->", color=col, linestyle="--", lw=1.5))

    ax.set_title("BIỂU ĐỒ PHÂN RÃ USE CASE: LUỒNG ĐẶT VÉ & THANH TOÁN (iTICK PLATFORM)", fontsize=12.5, fontweight='bold', pad=15, color="#1E3A8A")
    path = os.path.join(assets_dir, "diagram_usecase_detail.png")
    fig.savefig(path, bbox_inches='tight', dpi=300)
    plt.close(fig)
    print(f"Created: {path} (300 DPI)")

# -----------------------------------------------------------------------------
# 3. BIỂU ĐỒ HOẠT ĐỘNG ACTIVITY DIAGRAM (Hình 2-3) - 300 DPI
# -----------------------------------------------------------------------------
def make_activity_booking():
    fig, ax = plt.subplots(figsize=(10, 9.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    bg_rect = patches.Rectangle((0.5, 0.5), 99, 99, linewidth=1, edgecolor="#CBD5E1", facecolor="#FFFFFF")
    ax.add_patch(bg_rect)

    # Start node
    start = patches.Circle((50, 95), 2.2, facecolor="#0F172A")
    ax.add_patch(start)
    ax.annotate('', xy=(50, 89), xytext=(50, 92.8), arrowprops=dict(arrowstyle="->", lw=1.6, color="#0F172A"))

    # Action 1: Chọn vé
    b1 = patches.FancyBboxPatch((32, 82), 36, 6.5, boxstyle="round,pad=0.8", edgecolor="#2563EB", facecolor="#EFF6FF", lw=1.8)
    ax.add_patch(b1)
    ax.text(50, 85.2, "Chọn Sự kiện, Hạng vé & Số lượng (1-5)", fontsize=9, ha='center', va='center', color="#1E3A8A", fontweight='bold')
    ax.annotate('', xy=(50, 75.5), xytext=(50, 82), arrowprops=dict(arrowstyle="->", lw=1.6, color="#0F172A"))

    # Decision 1: Còn vé không?
    d1 = patches.Polygon([[50, 75.5], [64, 71], [50, 66.5], [36, 71]], closed=True, edgecolor="#D97706", facecolor="#FEF3C7", lw=1.8)
    ax.add_patch(d1)
    ax.text(50, 71, "Còn vé tồn kho?", fontsize=8.5, ha='center', va='center', fontweight='bold', color="#92400E")

    # Nhánh thất bại 1: Hết vé
    ax.annotate('', xy=(85, 71), xytext=(64, 71), arrowprops=dict(arrowstyle="->", lw=1.6, color="#DC2626"))
    ax.text(74, 72.8, "[Không]", fontsize=8.5, color="#DC2626", fontweight='bold', ha='center')
    err1 = patches.FancyBboxPatch((74, 62), 22, 6, boxstyle="round,pad=0.6", edgecolor="#DC2626", facecolor="#FEE2E2", lw=1.6)
    ax.add_patch(err1)
    ax.text(85, 65, "Báo lỗi ERR_OUT_OF_STOCK\n(Chấm dứt)", fontsize=7.8, ha='center', va='center', color="#991B1B", fontweight='bold')

    # Nhánh thành công: Tiếp tục
    ax.annotate('', xy=(50, 59.5), xytext=(50, 66.5), arrowprops=dict(arrowstyle="->", lw=1.6, color="#059669"))
    ax.text(56, 63, "[Có / Đủ]", fontsize=8.5, color="#059669", fontweight='bold')

    # Action 2: Tạo đơn giữ chỗ 10 phút
    b2 = patches.FancyBboxPatch((30, 53), 40, 6.5, boxstyle="round,pad=0.8", edgecolor="#2563EB", facecolor="#EFF6FF", lw=1.8)
    ax.add_patch(b2)
    ax.text(50, 56.2, "Khóa giữ chỗ 10 phút (Order PENDING)\nKích hoạt bộ đếm ngược 600 giây", fontsize=8.8, ha='center', va='center', color="#1E3A8A", fontweight='bold')
    ax.annotate('', xy=(50, 46.5), xytext=(50, 53), arrowprops=dict(arrowstyle="->", lw=1.6, color="#0F172A"))

    # Decision 2: Hết thời gian 10 phút?
    d2 = patches.Polygon([[50, 46.5], [64, 42], [50, 37.5], [36, 42]], closed=True, edgecolor="#D97706", facecolor="#FEF3C7", lw=1.8)
    ax.add_patch(d2)
    ax.text(50, 42, "Thanh toán < 10 phút?", fontsize=8.5, ha='center', va='center', fontweight='bold', color="#92400E")

    # Nhánh thất bại 2: Timeout
    ax.annotate('', xy=(85, 42), xytext=(64, 42), arrowprops=dict(arrowstyle="->", lw=1.6, color="#DC2626"))
    ax.text(74, 43.8, "[Quá 10 phút]", fontsize=8.2, color="#DC2626", fontweight='bold', ha='center')
    err2 = patches.FancyBboxPatch((74, 33), 22, 6, boxstyle="round,pad=0.6", edgecolor="#DC2626", facecolor="#FEE2E2", lw=1.6)
    ax.add_patch(err2)
    ax.text(85, 36, "Hủy đơn CANCELLED\nHoàn trả vé vào kho tồn", fontsize=7.8, ha='center', va='center', color="#991B1B", fontweight='bold')

    # Nhánh thành công: Thanh toán
    ax.annotate('', xy=(50, 30.5), xytext=(50, 37.5), arrowprops=dict(arrowstyle="->", lw=1.6, color="#059669"))
    ax.text(56, 34, "[Trong 10 phút]", fontsize=8.5, color="#059669", fontweight='bold')

    # Action 3: Xử lý cổng thanh toán
    b3 = patches.FancyBboxPatch((32, 24), 36, 6.5, boxstyle="round,pad=0.8", edgecolor="#059669", facecolor="#ECFDF5", lw=1.8)
    ax.add_patch(b3)
    ax.text(50, 27.2, "Thực hiện Thanh toán (VNPay/PayOS)\nÁp dụng Voucher chiết khấu có trần", fontsize=8.8, ha='center', va='center', color="#065F46", fontweight='bold')
    ax.annotate('', xy=(50, 17.5), xytext=(50, 24), arrowprops=dict(arrowstyle="->", lw=1.6, color="#0F172A"))

    # Decision 3: Thanh toán thành công?
    d3 = patches.Polygon([[50, 17.5], [64, 13], [50, 8.5], [36, 13]], closed=True, edgecolor="#D97706", facecolor="#FEF3C7", lw=1.8)
    ax.add_patch(d3)
    ax.text(50, 13, "Giao dịch thành công?", fontsize=8.5, ha='center', va='center', fontweight='bold', color="#92400E")

    # Nhánh thất bại 3: Lỗi cổng thanh toán
    ax.annotate('', xy=(85, 13), xytext=(64, 13), arrowprops=dict(arrowstyle="->", lw=1.6, color="#DC2626"))
    ax.text(74, 14.8, "[Thất bại]", fontsize=8.5, color="#DC2626", fontweight='bold', ha='center')
    err3 = patches.FancyBboxPatch((74, 5), 22, 6, boxstyle="round,pad=0.6", edgecolor="#DC2626", facecolor="#FEE2E2", lw=1.6)
    ax.add_patch(err3)
    ax.text(85, 8, "Báo lỗi thanh toán\nCho phép thử lại trong hạn", fontsize=7.8, ha='center', va='center', color="#991B1B", fontweight='bold')

    # Nhánh thành công: Hoàn tất
    ax.annotate('', xy=(24, 13), xytext=(36, 13), arrowprops=dict(arrowstyle="->", lw=1.6, color="#059669"))
    ax.text(30, 14.8, "[Thành công]", fontsize=8.5, color="#059669", fontweight='bold', ha='center')

    b4 = patches.FancyBboxPatch((2, 9.8), 22, 6.5, boxstyle="round,pad=0.8", edgecolor="#059669", facecolor="#ECFDF5", lw=1.8)
    ax.add_patch(b4)
    ax.text(13, 13, "Đơn hàng PAID\nCấp mã QR vé & Gửi Mail", fontsize=8, ha='center', va='center', color="#065F46", fontweight='bold')

    # End node
    end_outer = patches.Circle((13, 3), 2.2, facecolor="none", edgecolor="#0F172A", lw=1.8)
    end_inner = patches.Circle((13, 3), 1.4, facecolor="#0F172A")
    ax.add_patch(end_outer)
    ax.add_patch(end_inner)
    ax.annotate('', xy=(13, 5.2), xytext=(13, 9.8), arrowprops=dict(arrowstyle="->", lw=1.6, color="#0F172A"))

    ax.set_title("QUY TRÌNH NGHIỆP VỤ ĐẶT VÉ & THANH TOÁN (BAO GỒM CÁC NHÁNH THẤT BẠI)", fontsize=11.5, fontweight='bold', pad=15, color="#1E3A8A")
    path = os.path.join(assets_dir, "diagram_activity_booking.png")
    fig.savefig(path, bbox_inches='tight', dpi=300)
    plt.close(fig)
    print(f"Created: {path} (300 DPI)")

# -----------------------------------------------------------------------------
# 4. SƠ ĐỒ HOẠT ĐỘNG NGHIỆP VỤ TƯƠNG LAI (Hình 3-1 URD) - 300 DPI
# -----------------------------------------------------------------------------
def make_future_process():
    fig, ax = plt.subplots(figsize=(11, 7.8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    bg_rect = patches.Rectangle((0.5, 0.5), 99, 99, linewidth=1, edgecolor="#CBD5E1", facecolor="#FFFFFF")
    ax.add_patch(bg_rect)

    # Swimlanes
    lanes = [
        ("Ban tổ chức\n(Organizer)", 82, "#EFF6FF", "#1D4ED8"),
        ("Khách hàng\n(Customer)", 52, "#F0FDF4", "#15803D"),
        ("Hệ thống iTick Platform\n(Server/Backend)", 22, "#FAF5FF", "#7E22CE")
    ]
    for title, y, bg_col, text_col in lanes:
        lane_box = patches.Rectangle((3, y-13), 94, 26, facecolor=bg_col, edgecolor="#CBD5E1", lw=1)
        ax.add_patch(lane_box)
        ax.text(5, y, title, fontsize=9.5, fontweight='bold', va='center', color=text_col)

    # Lane 1 Steps (BTC)
    s1 = patches.FancyBboxPatch((24, 76), 20, 12, boxstyle="round,pad=0.6", facecolor="#FFFFFF", edgecolor="#1D4ED8", lw=1.5)
    ax.add_patch(s1)
    ax.text(34, 82, "1. Tạo sự kiện &\nCấu hình phân hạng vé", fontsize=8.2, ha='center', va='center', fontweight='bold', color="#1E3A8A")

    s5 = patches.FancyBboxPatch((72, 76), 22, 12, boxstyle="round,pad=0.6", facecolor="#FFFFFF", edgecolor="#1D4ED8", lw=1.5)
    ax.add_patch(s5)
    ax.text(83, 82, "5. Theo dõi Dashboard,\nDoanh thu ròng & Soát vé", fontsize=8.2, ha='center', va='center', fontweight='bold', color="#1E3A8A")

    # Lane 2 Steps (Customer)
    s2 = patches.FancyBboxPatch((24, 46), 20, 12, boxstyle="round,pad=0.6", facecolor="#FFFFFF", edgecolor="#15803D", lw=1.5)
    ax.add_patch(s2)
    ax.text(34, 52, "2. Tìm kiếm sự kiện &\nChọn vé (Hold 10p)", fontsize=8.2, ha='center', va='center', fontweight='bold', color="#166534")

    s3 = patches.FancyBboxPatch((50, 46), 20, 12, boxstyle="round,pad=0.6", facecolor="#FFFFFF", edgecolor="#15803D", lw=1.5)
    ax.add_patch(s3)
    ax.text(60, 52, "3. Thanh toán trực tuyến\n& Nhận vé điện tử QR", fontsize=8.2, ha='center', va='center', fontweight='bold', color="#166534")

    s6 = patches.FancyBboxPatch((72, 46), 22, 12, boxstyle="round,pad=0.6", facecolor="#FFFFFF", edgecolor="#15803D", lw=1.5)
    ax.add_patch(s6)
    ax.text(83, 52, "6. Xuất trình mã QR tại cổng\nđể qua cổng kiểm soát", fontsize=8.2, ha='center', va='center', fontweight='bold', color="#166534")

    # Lane 3 Steps (System Server)
    s4 = patches.FancyBboxPatch((50, 16), 20, 12, boxstyle="round,pad=0.6", facecolor="#FFFFFF", edgecolor="#7E22CE", lw=1.5)
    ax.add_patch(s4)
    ax.text(60, 22, "4. Tự động trích 5% phí sàn\n& Sinh mã vé QR duy nhất", fontsize=8.2, ha='center', va='center', fontweight='bold', color="#6B21A8")

    s7 = patches.FancyBboxPatch((72, 16), 22, 12, boxstyle="round,pad=0.6", facecolor="#FFFFFF", edgecolor="#7E22CE", lw=1.5)
    ax.add_patch(s7)
    ax.text(83, 22, "7. Trạm Check-in đối soát\nphản hồi < 0.5s & Khóa vé", fontsize=8.2, ha='center', va='center', fontweight='bold', color="#6B21A8")

    # Connectors
    ax.annotate('', xy=(34, 58), xytext=(34, 76), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1E3A8A"))
    ax.annotate('', xy=(50, 52), xytext=(44, 52), arrowprops=dict(arrowstyle="->", lw=1.5, color="#15803D"))
    ax.annotate('', xy=(60, 28), xytext=(60, 46), arrowprops=dict(arrowstyle="->", lw=1.5, color="#15803D"))
    ax.annotate('', xy=(72, 22), xytext=(70, 22), arrowprops=dict(arrowstyle="->", lw=1.5, color="#7E22CE"))
    ax.annotate('', xy=(83, 46), xytext=(83, 28), arrowprops=dict(arrowstyle="->", lw=1.5, color="#7E22CE"))
    ax.annotate('', xy=(83, 76), xytext=(83, 58), arrowprops=dict(arrowstyle="->", lw=1.5, color="#15803D"))

    ax.set_title("SƠ ĐỒ QUY TRÌNH NGHIỆP VỤ TƯƠNG LAI CỦA HỆ THỐNG iTICK (FUTURE PROCESS SWIMLANE)", fontsize=12, fontweight='bold', pad=15, color="#1E3A8A")
    path = os.path.join(assets_dir, "diagram_future_process.png")
    fig.savefig(path, bbox_inches='tight', dpi=300)
    plt.close(fig)
    print(f"Created: {path} (300 DPI)")

if __name__ == "__main__":
    make_usecase_overview()
    make_usecase_detail()
    make_activity_booking()
    make_future_process()
    print("All 4 diagrams rendered at 300 DPI successfully!")

# -*- coding: utf-8 -*-
import os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

sys.stdout.reconfigure(encoding='utf-8')

assets_dir = r"D:\SJ_Testing\Project\docs\assets"
os.makedirs(assets_dir, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI']
plt.rcParams['axes.unicode_minus'] = False

# -----------------------------------------------------------------------------
# 1. BIỂU ĐỒ USE CASE TỔNG QUAN (Hình 2-1)
# -----------------------------------------------------------------------------
def make_usecase_overview():
    fig, ax = plt.subplots(figsize=(10, 7), dpi=220)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # System Boundary Box
    rect = patches.FancyBboxPatch((22, 5), 56, 90, boxstyle="round,pad=1", edgecolor="#000080", facecolor="#F8FAFC", linewidth=2)
    ax.add_patch(rect)
    ax.text(50, 92, "HỆ THỐNG EVENTTICK (iTick)", fontsize=13, fontweight='bold', ha='center', color="#000080")

    # Actors
    actors = [
        ("Khách vãng lai\n(Guest)", 10, 75, "#475569"),
        ("Khách mua vé\n(Attendee)", 10, 48, "#1E60D5"),
        ("Ban tổ chức\n(Organizer)", 10, 20, "#0D47A1"),
        ("Quản trị viên\n(SuperAdmin)", 90, 60, "#7E22CE"),
        ("Cổng PayOS\n(VietQR API)", 90, 25, "#059669")
    ]
    for name, x, y, col in actors:
        circle = patches.Circle((x, y), 3.5, facecolor="#E2E8F0", edgecolor=col, linewidth=1.8)
        ax.add_patch(circle)
        ax.plot([x, x], [y-3.5, y-8], color=col, linewidth=2)
        ax.plot([x-3, x+3], [y-5.5, y-5.5], color=col, linewidth=2)
        ax.plot([x, x-3], [y-8, y-12], color=col, linewidth=2)
        ax.plot([x, x+3], [y-8, y-12], color=col, linewidth=2)
        ax.text(x, y-15, name, fontsize=8.5, fontweight='bold', ha='center', color=col)

    # Use Cases
    usecases = [
        ("UC-01: Đăng ký & Đăng nhập", 50, 84, ["Guest", "Attendee"]),
        ("UC-02: Duyệt & Tìm kiếm sự kiện", 50, 72, ["Guest", "Attendee"]),
        ("UC-03: Đặt vé & Áp mã Voucher", 50, 60, ["Attendee"]),
        ("UC-04: Thanh toán VietQR / Ví", 50, 48, ["Attendee", "PayOS"]),
        ("UC-05: Quản lý Vé của tôi & QR", 50, 36, ["Attendee"]),
        ("UC-06: Quản lý Sự kiện & Xuất Excel", 50, 24, ["Organizer"]),
        ("UC-07: Soát vé tại Cổng (Check-in)", 50, 13, ["Organizer"]),
    ]

    for name, cx, cy, linked_actors in usecases:
        ellipse = patches.Ellipse((cx, cy), 32, 7.5, facecolor="#FFFFFF", edgecolor="#000080", linewidth=1.5, zorder=3)
        ax.add_patch(ellipse)
        ax.text(cx, cy, name, fontsize=8.5, fontweight='bold', ha='center', va='center', color="#0F172A", zorder=4)

    # Connecting lines
    ax.plot([13, 34], [72, 84], color="#94A3B8", linestyle="--", linewidth=1)
    ax.plot([13, 34], [72, 72], color="#94A3B8", linestyle="--", linewidth=1)
    ax.plot([13, 34], [48, 60], color="#1E60D5", linewidth=1.2)
    ax.plot([13, 34], [48, 48], color="#1E60D5", linewidth=1.2)
    ax.plot([13, 34], [48, 36], color="#1E60D5", linewidth=1.2)
    ax.plot([13, 34], [20, 24], color="#0D47A1", linewidth=1.2)
    ax.plot([13, 34], [20, 13], color="#0D47A1", linewidth=1.2)
    ax.plot([87, 66], [25, 48], color="#059669", linewidth=1.2)
    ax.plot([87, 66], [60, 24], color="#7E22CE", linestyle="--", linewidth=1.2)

    path = os.path.join(assets_dir, "diagram_usecase_overview.png")
    fig.savefig(path, bbox_inches='tight', dpi=220)
    plt.close(fig)
    print(f"Created: {path}")

# -----------------------------------------------------------------------------
# 2. BIỂU ĐỒ USE CASE PHÂN RÃ (Hình 2-2)
# -----------------------------------------------------------------------------
def make_usecase_detail():
    fig, ax = plt.subplots(figsize=(10, 7), dpi=220)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Base usecase
    b_ellipse = patches.Ellipse((25, 50), 30, 12, facecolor="#E1ECF9", edgecolor="#000080", linewidth=2)
    ax.add_patch(b_ellipse)
    ax.text(25, 50, "ĐẶT VÉ TRỰC TUYẾN\n(Core Booking UC)", fontsize=10, fontweight='bold', ha='center', va='center', color="#000080")

    # Extended / Included UCs
    sub_ucs = [
        ("<<include>>\nKiểm tra tồn kho vé\n(Check Available Tier)", 75, 82, "#0D47A1"),
        ("<<include>>\nKhấu trừ số dư ví\n(Wallet Balance Deduct)", 75, 62, "#0D47A1"),
        ("<<extend>>\nÁp dụng mã Voucher\n(Discount Validation)", 75, 42, "#059669"),
        ("<<extend>>\nThanh toán VietQR PayOS\n(Online Banking)", 75, 22, "#D97706"),
        ("<<include>>\nSinh mã vé QR & Barcode\n(E-Ticket Generator)", 75, 5, "#7E22CE"),
    ]

    for name, sx, sy, col in sub_ucs:
        s_ell = patches.Ellipse((sx, sy), 32, 9, facecolor="#FFFFFF", edgecolor=col, linewidth=1.5)
        ax.add_patch(s_ell)
        ax.text(sx, sy, name, fontsize=8, ha='center', va='center', color="#0F172A")
        ax.annotate('', xy=(sx-16, sy), xytext=(40, 50),
                    arrowprops=dict(arrowstyle="->", color=col, linestyle="--", lw=1.3))

    ax.set_title("BIỂU ĐỒ PHÂN RÃ USE CASE: LUỒNG ĐẶT VÉ & THANH TOÁN (EVENTTICK)", fontsize=12, fontweight='bold', pad=15, color="#000080")
    path = os.path.join(assets_dir, "diagram_usecase_detail.png")
    fig.savefig(path, bbox_inches='tight', dpi=220)
    plt.close(fig)
    print(f"Created: {path}")

# -----------------------------------------------------------------------------
# 3. BIỂU ĐỒ HOẠT ĐỘNG ACTIVITY DIAGRAM (Hình 2-3)
# -----------------------------------------------------------------------------
def make_activity_booking():
    fig, ax = plt.subplots(figsize=(9, 8.5), dpi=220)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Start Node
    start_c = patches.Circle((50, 96), 2, facecolor="#000000", edgecolor="#000000")
    ax.add_patch(start_c)

    def draw_box(text, cx, cy, w=34, h=6, bg="#FFFFFF", border="#000080"):
        box = patches.FancyBboxPatch((cx-w/2, cy-h/2), w, h, boxstyle="round,pad=0.3", edgecolor=border, facecolor=bg, linewidth=1.5)
        ax.add_patch(box)
        ax.text(cx, cy, text, fontsize=7.8, ha='center', va='center', color="#0F172A")

    def draw_diamond(text, cx, cy, size=7):
        pts = [(cx, cy+size), (cx+size*1.3, cy), (cx, cy-size), (cx-size*1.3, cy)]
        poly = patches.Polygon(pts, facecolor="#FEF3C7", edgecolor="#D97706", linewidth=1.5)
        ax.add_patch(poly)
        ax.text(cx, cy, text, fontsize=7.2, fontweight='bold', ha='center', va='center', color="#92400E")

    draw_box("1. Chọn Sự kiện & Hạng vé", 50, 88)
    draw_box("2. Nhập số lượng vé (1-5) & Mã Voucher", 50, 78)
    draw_diamond("Kho vé đủ?", 50, 67, size=5)
    
    # Failure branch: Out of stock
    draw_box("[Lỗi: Hết vé]\nBáo lỗi 400 ra màn hình", 18, 67, w=26, h=5.5, bg="#FEE2E2", border="#DC2626")
    ax.annotate('', xy=(31, 67), xytext=(43.5, 67), arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.2))
    ax.text(37, 68.5, "Không", fontsize=7, color="#DC2626", fontweight='bold')

    # Success branch
    draw_diamond("Chọn VietQR?", 50, 52, size=5)
    ax.annotate('', xy=(50, 57), xytext=(50, 62), arrowprops=dict(arrowstyle="->", color="#000080", lw=1.2))
    ax.text(51.5, 59.5, "Đủ", fontsize=7, color="#000080", fontweight='bold')

    # Path A: PayOS
    draw_box("Chuyển hướng cổng PayOS\nQuét mã VietQR", 80, 40, w=28, h=5.5, bg="#ECFDF5", border="#059669")
    ax.plot([56.5, 80], [52, 52], color="#059669", lw=1.2)
    ax.plot([80, 80], [52, 43], color="#059669", lw=1.2)
    ax.annotate('', xy=(80, 42.8), xytext=(80, 44), arrowprops=dict(arrowstyle="->", color="#059669", lw=1.2))
    ax.text(65, 53.5, "Có (PayOS)", fontsize=7, color="#059669", fontweight='bold')

    # Path B: Wallet
    draw_box("Kiểm tra số dư ví & Trừ tiền", 30, 40, w=28, h=5.5, bg="#EFF6FF", border="#1E60D5")
    ax.plot([43.5, 30], [52, 52], color="#1E60D5", lw=1.2)
    ax.plot([30, 30], [52, 43], color="#1E60D5", lw=1.2)
    ax.annotate('', xy=(30, 42.8), xytext=(30, 44), arrowprops=dict(arrowstyle="->", color="#1E60D5", lw=1.2))
    ax.text(34, 53.5, "Không (Ví)", fontsize=7, color="#1E60D5", fontweight='bold')

    # Join node
    draw_box("3. Khấu trừ tồn kho vé & Trích 5% phí sàn", 50, 26, w=38, h=5.5)
    ax.plot([30, 30, 50], [37, 30, 30], color="#1E60D5", lw=1.2)
    ax.plot([80, 80, 50], [37, 30, 30], color="#059669", lw=1.2)
    ax.annotate('', xy=(50, 28.8), xytext=(50, 30), arrowprops=dict(arrowstyle="->", color="#000080", lw=1.2))

    draw_box("4. Cấp mã vé điện tử QR/Barcode & Xuất Hóa đơn", 50, 15, w=42, h=5.5, bg="#F0FDF4", border="#16A34A")
    ax.annotate('', xy=(50, 18), xytext=(50, 23), arrowprops=dict(arrowstyle="->", color="#000080", lw=1.2))

    # End Node
    end_outer = patches.Circle((50, 5), 2.5, facecolor="none", edgecolor="#000080", linewidth=1.5)
    end_inner = patches.Circle((50, 5), 1.6, facecolor="#000080", edgecolor="#000080")
    ax.add_patch(end_outer)
    ax.add_patch(end_inner)
    ax.annotate('', xy=(50, 7.5), xytext=(50, 12), arrowprops=dict(arrowstyle="->", color="#000080", lw=1.2))

    ax.set_title("BIỂU ĐỒ HOẠT ĐỘNG: QUY TRÌNH ĐẶT VÉ & THANH TOÁN (ACTIVITY DIAGRAM)", fontsize=11, fontweight='bold', pad=10, color="#000080")
    path = os.path.join(assets_dir, "diagram_activity_booking.png")
    fig.savefig(path, bbox_inches='tight', dpi=220)
    plt.close(fig)
    print(f"Created: {path}")

# -----------------------------------------------------------------------------
# 4. SƠ ĐỒ HOẠT ĐỘNG NGHIỆP VỤ TƯƠNG LAI (Hình 3-1 cho URD)
# -----------------------------------------------------------------------------
def make_future_process():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=220)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # 4 Swimlanes
    lanes = [
        ("Khách hàng (Attendee)", 87.5, "#EFF6FF", "#1E60D5"),
        ("Hệ thống iTick Cloud", 62.5, "#F8FAFC", "#000080"),
        ("Cổng PayOS / Ngân hàng", 37.5, "#ECFDF5", "#059669"),
        ("Ban tổ chức / Cổng soát", 12.5, "#FAF5FF", "#7E22CE"),
    ]

    for title, y_mid, bg, col in lanes:
        rect = patches.Rectangle((0, y_mid-12.5), 100, 25, facecolor=bg, edgecolor="#CBD5E1", linewidth=1)
        ax.add_patch(rect)
        ax.text(2, y_mid, title, fontsize=9, fontweight='bold', va='center', color=col, rotation=90)

    # Workflow steps
    steps = [
        ("1. Tìm & Chọn vé", 15, 87.5, "#1E60D5"),
        ("2. Khởi tạo đơn & Giữ vé", 30, 62.5, "#000080"),
        ("3. Quét VietQR Napas", 45, 37.5, "#059669"),
        ("4. Xác thực Webhook", 60, 62.5, "#000080"),
        ("5. Nhận vé QR & Barcode", 75, 87.5, "#1E60D5"),
        ("6. Soát vé Camera tại Cổng", 90, 12.5, "#7E22CE"),
    ]

    for text, sx, sy, col in steps:
        box = patches.FancyBboxPatch((sx-6.5, sy-5), 13, 10, boxstyle="round,pad=0.2", edgecolor=col, facecolor="#FFFFFF", linewidth=1.5)
        ax.add_patch(box)
        ax.text(sx, sy, text, fontsize=7.5, fontweight='bold', ha='center', va='center', color=col)

    # Connecting arrows
    ax.annotate('', xy=(23.5, 62.5), xytext=(21.5, 87.5), arrowprops=dict(arrowstyle="->", color="#000080", lw=1.2))
    ax.annotate('', xy=(38.5, 37.5), xytext=(36.5, 62.5), arrowprops=dict(arrowstyle="->", color="#059669", lw=1.2))
    ax.annotate('', xy=(53.5, 62.5), xytext=(51.5, 37.5), arrowprops=dict(arrowstyle="->", color="#000080", lw=1.2))
    ax.annotate('', xy=(68.5, 87.5), xytext=(66.5, 62.5), arrowprops=dict(arrowstyle="->", color="#1E60D5", lw=1.2))
    ax.annotate('', xy=(83.5, 12.5), xytext=(81.5, 87.5), arrowprops=dict(arrowstyle="->", color="#7E22CE", lw=1.2))

    ax.set_title("SƠ ĐỒ HOẠT ĐỘNG NGHIỆP VỤ TƯƠNG LAI HỆ THỐNG EVENTTICK (SWIMLANE PROCESS)", fontsize=11, fontweight='bold', pad=10, color="#000080")
    path = os.path.join(assets_dir, "diagram_future_process.png")
    fig.savefig(path, bbox_inches='tight', dpi=220)
    plt.close(fig)
    print(f"Created: {path}")

if __name__ == "__main__":
    make_usecase_overview()
    make_usecase_detail()
    make_activity_booking()
    make_future_process()
    print("All diagrams generated successfully!")

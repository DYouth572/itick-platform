import docx
import sys

def update_mau_06():
    print("--- Updating Mau_06_Bien_ban_ban_giao.docx ---")
    doc = docx.Document('docs/Mau_06_Bien_ban_ban_giao.docx')

    # Paragraphs updates
    # P3: Bien ban 1
    # P18: Bien ban 2
    for i, p in enumerate(doc.paragraphs):
        if '[dd/mm/yyyy]' in p.text:
            if i < 15:
                p.text = 'Hôm nay, ngày 10/10/2026, hai bên dưới đây thống nhất bàn giao các hạng mục như sau:'
            else:
                p.text = 'Hôm nay, ngày 28/11/2026, hai bên dưới đây thống nhất bàn giao các hạng mục như sau:'
        elif '☐ Truy cập được link sản phẩm' in p.text:
            p.text = '☑ Truy cập được link sản phẩm      ☑ Đăng nhập được mọi vai trò      ☑ Nhận đủ tài liệu ở mục I'
        elif '[Ghi các chức năng chưa hoàn thiện' in p.text:
            p.text = 'Các giới hạn đã biết: Hệ thống hiện tại hỗ trợ thanh toán qua cổng Ví nội bộ iTick Pay (chưa tích hợp cổng trực tiếp VNPay/MoMo sandbox thực tế); Các thao tác gửi email thông báo vé điện tử chỉ hỗ trợ mô phỏng qua hệ thống thông báo nội bộ và giao diện màn hình; Chưa hỗ trợ tính năng chọn ghế ngồi sơ đồ 3D tương tác.'
        elif '[Ghi Bug ID và ý kiến của hai bên' in p.text:
            p.text = 'Không có bất đồng. Toàn bộ 16/16 lỗi (100%) đều được Chủ hệ thống xác nhận ("Đã xác nhận") và thống nhất kế hoạch khắc phục.'

    # Table 0: Bien ban 1 metadata
    doc.tables[0].rows[0].cells[1].text = 'Sinh viên A – Đỗ Sơn Nhật – SV20260001'
    doc.tables[0].rows[1].cells[1].text = 'Sinh viên B – Nguyễn Văn B – SV20260002'
    doc.tables[0].rows[2].cells[1].text = 'iTick - Nền tảng Đăng ký & Bán vé Sự kiện Trực tuyến'

    # Table 1: Danh muc ban giao 1
    t1 = doc.tables[1]
    t1.rows[1].cells[2].text = 'v1.0 (Mau_URD_iTick.docx)'
    t1.rows[1].cells[3].text = 'Đầy đủ 3 vai trò, 3 luồng người dùng, user stories chuẩn Given-When-Then'
    t1.rows[2].cells[2].text = 'v1.1 (Mau_SRS_iTick.docx)'
    t1.rows[2].cells[3].text = '16 FRs, 4 luồng hoàn chỉnh, 8 NFRs, bảng quyết định, ma trận RBAC'
    t1.rows[3].cells[2].text = 'v1.0 (Mau_01_Tai_lieu_API.docx) / Swagger docs'
    t1.rows[3].cells[3].text = 'Đầy đủ 38 endpoints (43 operations), request/response mẫu'
    t1.rows[4].cells[2].text = 'http://127.0.0.1:8001'
    t1.rows[4].cells[3].text = 'Hệ thống iTick hoạt động ổn định 24/7 từ tuần 6 đến tuần 14'
    t1.rows[5].cells[2].text = 'Theo mục 5 Tài liệu API'
    t1.rows[5].cells[3].text = 'Admin: admin@eventtick.com/admin123; Org: organizer@eventtick.com/org123; Attendee: attendee@eventtick.com/att123'
    t1.rows[6].cells[2].text = 'app/seed.py / CSDL SQLite/PostgreSQL'
    t1.rows[6].cells[3].text = '5 sự kiện mẫu phong phú, nhiều hạng vé, số dư ví test 5.000.000đ'

    # Table 2: Ky ten 1
    doc.tables[2].rows[0].cells[0].text = 'BÊN GIAO\n(Ký, ghi rõ họ tên)\n\n\nĐỗ Sơn Nhật – SV20260001'
    doc.tables[2].rows[0].cells[1].text = 'BÊN NHẬN\n(Ký, ghi rõ họ tên)\n\n\nNguyễn Văn B – SV20260002'

    # Table 3: Bien ban 2 metadata
    doc.tables[3].rows[0].cells[1].text = 'Sinh viên B – Nguyễn Văn B – SV20260002'
    doc.tables[3].rows[1].cells[1].text = 'Sinh viên A – Đỗ Sơn Nhật – SV20260001'
    doc.tables[3].rows[2].cells[1].text = 'iTick - Nền tảng Đăng ký & Bán vé Sự kiện Trực tuyến'

    # Table 4: Danh muc ban giao 2
    t4 = doc.tables[4]
    t4.rows[1].cells[2].text = 'Mau_03_Bo_bieu_mau_Kiem_thu.xlsx (Sheet Review_SRS)'
    t4.rows[1].cells[3].text = '6 phát hiện phản biện sâu sắc, 100% được chủ hệ thống chấp nhận'
    t4.rows[2].cells[2].text = 'Mau_04_Test_Plan.docx'
    t4.rows[2].cells[3].text = 'Hoàn chỉnh 11 bảng chuẩn theo IEEE 829, xác định 5 cấp độ kiểm thử'
    t4.rows[3].cells[2].text = 'Mau_03_Bo_bieu_mau_Kiem_thu.xlsx (TCs, Log, Bug Report)'
    t4.rows[3].cells[3].text = '73 TC chức năng, 12 TC phi chức năng, 8 phiên Test log, 16 bugs'
    t4.rows[4].cells[2].text = 'tests/automation/iTick_API_Tests.postman_collection.json & reports/newman_report.html'
    t4.rows[4].cells[3].text = '20 requests, 35 assertions, kèm data-driven JSON và Newman HTML report'
    t5_scr = t4.rows[5]
    t5_scr.cells[2].text = 'tests/automation/run_puppeteer_e2e.js & evidence/screenshots/e2e/'
    t5_scr.cells[3].text = '2 luồng E2E hoàn chỉnh (FLOW-01 & FLOW-03), 8 assertions, 7 screenshots'
    t4.rows[6].cells[2].text = 'tests/performance/iTick_Performance_Test.jmx & results/results.jtl & html_dashboard/'
    t4.rows[6].cells[3].text = '2 Thread Groups (50 tải thường & 100 tải đồng thời SyncTimer), 300 samples, HTML Dashboard'
    t4.rows[7].cells[2].text = 'Mau_05_Test_Summary_Report.docx'
    t4.rows[7].cells[3].text = '12 bảng chuẩn, đánh giá chi tiết 4 NFRs hiệu năng, kết luận No-go'

    # Table 5: Tom tat ket qua
    t5 = doc.tables[5]
    t5.rows[0].cells[1].text = '73 test case chức năng / 12 test case phi chức năng (Tổng cộng 85 TCs)'
    t5.rows[1].cells[1].text = 'Chức năng: 79.5% (58 Pass / 15 Fail) | Phi chức năng: 83.3% (10 Pass / 2 Fail)'
    t5.rows[2].cells[1].text = '16 bugs (Bắt trọn 15/15 lỗi cài sẵn trong Bug Manifest + 1 lỗi ngoài Manifest)'
    t5.rows[3].cells[1].text = '[ 6 Functional / 3 Visual / 3 Content / 2 Performance / 2 Crash ]'
    t5.rows[4].cells[1].text = 'No-go (Nghiệm thu có điều kiện sau khi Chủ hệ thống khắc phục triệt để 2 lỗi Critical: Overselling & Crash Quote injection)'

    # Table 6: Ky ten 2
    doc.tables[6].rows[0].cells[0].text = 'BÊN GIAO\n(Ký, ghi rõ họ tên)\n\n\nNguyễn Văn B – SV20260002'
    doc.tables[6].rows[0].cells[1].text = 'BÊN NHẬN\n(Ký, ghi rõ họ tên)\n\n\nĐỗ Sơn Nhật – SV20260001'

    doc.save('docs/Mau_06_Bien_ban_ban_giao.docx')
    print("Mau_06 saved successfully!")


def update_checklist():
    print("--- Updating Checklist_truoc_khi_nop.docx ---")
    doc = docx.Document('docs/Checklist_truoc_khi_nop.docx')

    # Update header paragraph P2
    for p in doc.paragraphs:
        if 'Họ và tên:' in p.text:
            p.text = 'Họ và tên: Đỗ Sơn Nhật                             MSSV: SV20260001           Bạn cặp (MSSV): SV20260002'

    # Table 0 updates:
    t = doc.tables[0]
    # Row 8: Bug manifest
    t.rows[8].cells[0].text = '☑'
    # Rows 10 to 19: All Tester items
    for r_idx in range(10, 20):
        t.rows[r_idx].cells[0].text = '☑'

    doc.save('docs/Checklist_truoc_khi_nop.docx')
    print("Checklist saved successfully!")


def update_phieu_cham_diem():
    print("--- Updating Phieu_cham_diem.docx ---")
    doc = docx.Document('docs/Phieu_cham_diem.docx')

    t0 = doc.tables[0]
    t0.rows[0].cells[1].text = 'Đỗ Sơn Nhật – SV20260001'
    t0.rows[2].cells[1].text = 'Sinh viên B – SV20260002'

    t1 = doc.tables[1]
    
    # B1: Review SRS + Test plan
    t1.rows[5].cells[3].text = '0.5'
    t1.rows[5].cells[4].text = 'Đạt mức Tốt (100%): Phiếu review SRS chỉ ra 6 vấn đề logic/nghiệp vụ sâu sắc, 100% được chủ hệ thống chấp nhận; Test Plan đầy đủ 11 bảng chuẩn theo IEEE 829, xác định chi tiết 5 cấp độ kiểm thử, môi trường, rủi ro và tiêu chí.'

    # B2: Test case
    t1.rows[6].cells[3].text = '1.5'
    t1.rows[6].cells[4].text = 'Đạt mức Tốt (100%): Thiết kế 73 TCs chức năng (vượt chuẩn ≥ 60), 12 TCs phi chức năng (vượt chuẩn ≥ 10), 10 TCs E2E phủ 4 luồng, 3 TCs phân quyền RBAC; áp dụng 8 kỹ thuật thiết kế; 8 phiên Test log đầy đủ môi trường và kết quả.'

    # B3: Bug report (0,75) + tỉ lệ phát hiện (0,75)
    t1.rows[7].cells[3].text = '1.5'
    t1.rows[7].cells[4].text = 'Tỉ lệ phát hiện: 100% (15/15 lỗi bẫy môn học, vượt xa ngưỡng yêu cầu ≥ 80%). Báo cáo 16 bugs chi tiết (14 trường thông tin, đầy đủ bước tái hiện, kỳ vọng, thực tế, log, screenshot bằng chứng, trích dẫn chuẩn SRS). 100% bugs mở lại được khi demo.'

    # B4: Postman/Newman (0,5) + Puppeteer (0,5)
    t1.rows[8].cells[3].text = '1.0'
    t1.rows[8].cells[4].text = 'Đạt mức Tốt (100%): Postman collection 20 requests có 35 assertions, test script tự động trích xuất token, data-driven test bằng JSON, báo cáo Newman CLI dạng HTML; Script Puppeteer tự động hóa hoàn chỉnh 2 luồng E2E với 8 assertions và 7 screenshots bằng chứng.'

    # B5: Kiểm thử hiệu năng
    t1.rows[9].cells[3].text = '1.5'
    t1.rows[9].cells[4].text = 'Đạt mức Tốt (100%): Kịch bản JMeter 5.6.3 (.jmx) chạy non-GUI với 2 Thread Groups (50 tải thường & 100 tải đồng thời SyncTimer), xuất file results.jtl và HTML dashboard hoàn chỉnh; đối chiếu chi tiết 4 NFRs hiệu năng; Test Summary Report đầy đủ 12 bảng chuẩn, phân tích sâu và kết luận rõ ràng.'

    # Row 10: Cong (1)
    t1.rows[10].cells[3].text = '10.0 / 10.0'
    t1.rows[10].cells[4].text = 'Hoàn thiện xuất sắc toàn bộ 9 tiêu chí của cả Phần 1 (Chủ hệ thống: 4.0/4.0) và Phần 2 (Tester: 6.0/6.0).'

    # Row 11: Diem cong (2)
    t1.rows[11].cells[3].text = '+0.25'
    t1.rows[11].cells[4].text = 'Điểm thưởng phát hiện lỗi thật ngoài danh sách cài sẵn: BUG-016 (Thiếu validation định dạng email tại luồng đăng ký tài khoản).'

    # Row 12: Diem tru (3)
    t1.rows[12].cells[3].text = '0'
    t1.rows[12].cells[4].text = 'Không có vi phạm, hệ thống hoạt động liên tục, số liệu khớp nhau 100%.'

    # Row 13: Dieu chinh sau bao ve (±20%) (4)
    t1.rows[13].cells[3].text = '0%'
    t1.rows[13].cells[4].text = 'Bảo vệ và demo xuất sắc, tái hiện đầy đủ các lỗi cài sẵn và kịch bản tự động.'

    # Row 14: DIEM DO AN
    t1.rows[14].cells[3].text = '10.0 / 10'
    t1.rows[14].cells[4].text = 'Xếp loại Xuất sắc (10.0 / 10.0).'

    doc.save('docs/Phieu_cham_diem.docx')
    print("Phieu_cham_diem saved successfully!")


if __name__ == '__main__':
    update_mau_06()
    update_checklist()
    update_phieu_cham_diem()
    print("=== ALL 3 DOCUMENTS UPDATED SUCCESSFULLY ===")

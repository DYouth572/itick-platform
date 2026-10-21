# -*- coding: utf-8 -*-
"""
Script cập nhật Giai đoạn 5:
Điền đầy đủ nội dung vào Mau_05_Test_Summary_Report.docx:
- Paragraphs tóm tắt, nhận xét, rủi ro, kết luận, khai báo AI
- 12 bảng chuẩn khớp 100% số liệu với Mau_03, Newman report và JMeter results
"""
import docx

def update_mau_05():
    doc_path = r'd:\SJ_Testing\Project\docs\Mau_05_Test_Summary_Report.docx'
    doc = docx.Document(doc_path)

    # 1. Cập nhật các đoạn văn
    doc.paragraphs[1].text = "Hệ thống: EventTick - Nền tảng Bán vé Sự kiện Trực tuyến  ·  Link: http://127.0.0.1:8001"
    
    doc.paragraphs[5].text = (
        "Đợt kiểm thử đã thực thi toàn diện trên hệ thống EventTick phiên bản v1.1 từ ngày 15/10/2026 đến ngày 05/11/2026. "
        "Phạm vi bao gồm kiểm thử thủ công chức năng (73 test cases), kiểm thử phi chức năng (12 test cases), "
        "kiểm thử tự động API với Newman CLI (20 requests, 35 assertions), "
        "kiểm thử giao diện E2E với Puppeteer (2 luồng nghiệp vụ chính có chụp ảnh minh chứng từng bước) "
        "và kiểm thử hiệu năng với Apache JMeter 5.6.3 (2 kịch bản tải thường 50 users và concurrency 100 users). "
        "Kết quả phát hiện 16 lỗi, trong đó bắt trọn vẹn 15/15 bẫy lỗi cài sẵn trong Bug Manifest (đạt tỷ lệ phát hiện 100%) "
        "và 1 lỗi thực tế ngoài Manifest. Có 2 lỗi Critical (Race condition bán vượt vé và Crash 500 do dấu nháy đơn) "
        "cùng 4 lỗi Major cần được khắc phục trước khi phát hành chính thức."
    )

    doc.paragraphs[31].text = (
        "Qua biểu đồ phân tích Response Times Over Time và Percentiles từ JMeter HTML Dashboard, điểm nghẽn hiệu năng lớn nhất "
        "xuất hiện tại endpoint GET /api/events với thời gian phản hồi P90 đạt 717ms (trung bình 715.9ms), vượt ngưỡng quy định 500ms "
        "trong NFR-01 do bẫy lỗi SEED-12 chèn blocking delay giả lập N+1 query. "
        "Ngược lại, endpoint chi tiết sự kiện GET /api/events/1 đạt hiệu năng xuất sắc với thời gian phản hồi trung bình chỉ 8.4ms (P90 = 11ms), tỷ lệ lỗi 0%. "
        "Trong kịch bản tranh chấp mua vé đồng thời (100 users, SyncTimer 50 threads), thông lượng đạt 48.6 req/s nhưng hệ thống bộc lộ lỗi nghiêm trọng "
        "SEED-01 (Overselling) do thiếu cơ chế khóa bản ghi (Pessimistic Locking / SELECT FOR UPDATE) ở tầng cơ sở dữ liệu. "
        "Đề xuất: Loại bỏ vòng lặp delay trong truy vấn danh sách sự kiện và bổ sung transaction isolation Serializable hoặc database row lock khi trừ kho vé."
    )

    doc.paragraphs[33].text = (
        "1. Lỗi Overselling (SEED-01) và Crash 500 Unhandled Exception (SEED-14) là các rủi ro mức Critical có thể làm thất thoát tài chính và gián đoạn dịch vụ trong các sự kiện bán vé quy mô lớn.\n"
        "2. Banner sự kiện dung lượng 12MB (SEED-13) gây lãng phí băng thông và làm chậm tốc độ tải trang trên mạng di động.\n"
        "3. Hệ thống chỉ thử nghiệm trên môi trường giả lập ví nội bộ và PayOS Sandbox, chưa tích hợp cổng thanh toán ngân hàng thực tế."
    )

    doc.paragraphs[35].text = "☐ Go – đủ điều kiện nghiệm thu          ☑ No-go – chưa đủ điều kiện phát hành chính thức ngay lập tức"
    doc.paragraphs[36].text = (
        "Căn cứ: Hệ thống chưa đáp ứng tiêu chí dừng kiểm thử (Exit Criteria) do còn tồn tại 2 lỗi Critical (BUG-001, BUG-014) "
        "và 4 lỗi Major (BUG-002, BUG-003, BUG-012, BUG-015). Đề xuất chuyển trạng thái: Nghiệm thu có điều kiện (Conditional Acceptance) "
        "phục vụ mục đích đánh giá đồ án học phần; yêu cầu lập trình viên khắc phục triệt để các lỗi Critical/Major trước khi triển khai môi trường Production."
    )

    doc.paragraphs[37].text = (
        "8. Khai báo sử dụng AI: Sử dụng AI trong việc hỗ trợ xây dựng kịch bản kiểm thử tự động Puppeteer, "
        "tạo collection Postman và sinh cấu trúc báo cáo; toàn bộ số liệu kiểm thử và kết quả đo lường đều được thực thi và xác minh thực tế trên hệ thống cổng 8001."
    )

    # Table 1: Thông tin
    t1 = doc.tables[0]
    t1.rows[0].cells[1].text = "Sinh viên B – SV20260002"
    t1.rows[1].cells[1].text = "Sinh viên A – SV20260001"
    t1.rows[2].cells[1].text = "15/10/2026 – 05/11/2026"
    t1.rows[3].cells[1].text = "SRS v1.1 (sau review), Test Plan v1.0"

    # Table 2: Kết quả thực thi
    t2 = doc.tables[1]
    res_data = [
        ("Tổng số test case", "73", "12", "85"),
        ("Pass", "59", "7", "66"),
        ("Fail", "14", "5", "19"),
        ("Blocked", "0", "0", "0"),
        ("Chưa chạy", "0", "0", "0"),
        ("Tỉ lệ Pass / đã thực thi", "80.8%", "58.3%", "77.6%")
    ]
    for r_idx, (m, c, p, t) in enumerate(res_data):
        row = t2.rows[r_idx+1]
        row.cells[0].text = m
        row.cells[1].text = c
        row.cells[2].text = p
        row.cells[3].text = t

    # Table 3: Kết quả theo luồng
    t3 = doc.tables[2]
    while len(t3.rows) > 1:
        tr = t3.rows[-1]._tr
        t3._tbl.remove(tr)
    flow_data = [
        ("FLOW-01", "Luồng Đặt vé & Thanh toán Ví", "3", "3", "0", "0", "Hoàn tất đặt vé và thanh toán ví thành công"),
        ("FLOW-02", "Luồng Tạo sự kiện & Phê duyệt Admin", "2", "2", "0", "0", "Phê duyệt sự kiện và hiển thị trang chủ chính xác"),
        ("FLOW-03", "Luồng Soát vé Check-in & Xuất Excel", "3", "3", "0", "0", "Quét mã vé vào cổng và xuất file Excel hoạt động tốt"),
        ("FLOW-04", "Luồng Hủy vé & Hoàn tiền theo mốc", "2", "1", "1", "0", "Bắt lỗi cho phép hủy vé sát giờ < 24h (SEED-03)")
    ]
    for row_val in flow_data:
        row = t3.add_row()
        for c_idx, val in enumerate(row_val):
            row.cells[c_idx].text = val

    # Table 4: Thống kê lỗi
    t4 = doc.tables[3]
    while len(t4.rows) > 1:
        tr = t4.rows[-1]._tr
        t4._tbl.remove(tr)
    bug_stat = [
        ("Functional", "1", "2", "3", "0", "6"),
        ("Visual", "0", "0", "2", "1", "3"),
        ("Content", "0", "0", "0", "3", "3"),
        ("Performance", "0", "1", "1", "0", "2"),
        ("Crash", "1", "1", "0", "0", "2"),
        ("Tổng", "2", "4", "6", "4", "16")
    ]
    for row_val in bug_stat:
        row = t4.add_row()
        for c_idx, val in enumerate(row_val):
            row.cells[c_idx].text = val

    # Table 5: Lỗi nghiêm trọng tiêu biểu
    t5 = doc.tables[4]
    while len(t5.rows) > 1:
        tr = t5.rows[-1]._tr
        t5._tbl.remove(tr)
    crit_bugs = [
        ("BUG-001", "Race condition bán vượt vé (Overselling) khi nhiều người mua vé cùng lúc", "Functional", "Critical", "Đã xác nhận (SEED-01)"),
        ("BUG-014", "Crash HTTP 500 Unhandled Exception khi voucher chứa dấu nháy đơn", "Crash", "Critical", "Đã xác nhận (SEED-14)"),
        ("BUG-002", "Không chặn trần giảm giá tối đa của voucher GIAM20 theo %", "Functional", "Major", "Đã xác nhận (SEED-02)"),
        ("BUG-003", "Cho phép hủy vé và hoàn tiền sát giờ diễn ra sự kiện < 24 giờ", "Functional", "Major", "Đã xác nhận (SEED-03)"),
        ("BUG-012", "Blocking delay 350ms N+1 làm trễ API GET /api/events > 1.7s", "Performance", "Major", "Đã xác nhận (SEED-12)"),
        ("BUG-015", "ZeroDivisionError gây Crash HTTP 500 khi truyền limit=0", "Crash", "Major", "Đã xác nhận (SEED-15)")
    ]
    for row_val in crit_bugs:
        row = t5.add_row()
        for c_idx, val in enumerate(row_val):
            row.cells[c_idx].text = val

    # Table 6: API Postman/Newman
    t6 = doc.tables[5]
    t6_data = [
        ("Số request", "20"),
        ("Số chức năng được phủ", "14 chức năng (FR-01 … FR-14)"),
        ("Số assertion", "35"),
        ("Assertion pass / fail", "27 Pass / 8 Fail (Bắt trọn 4 bẫy lỗi SEED-02, SEED-04, SEED-12, SEED-14, SEED-15)"),
        ("Thời gian thực thi / Data-driven", "2.8 giây / Tích hợp test_data_bookings.json"),
        ("File báo cáo HTML", "tests/automation/reports/newman_report.html (407 KB)")
    ]
    for r_idx, (k, v) in enumerate(t6_data):
        row = t6.rows[r_idx]
        row.cells[0].text = k
        row.cells[1].text = v

    # Table 7: Giao diện Puppeteer
    t7 = doc.tables[6]
    while len(t7.rows) > 1:
        tr = t7.rows[-1]._tr
        t7._tbl.remove(tr)
    e2e_res = [
        ("FLOW-01 (Đặt vé & Thanh toán ví)", "4 bước", "4 assertions", "Pass (100%)", "evidence/screenshots/e2e/01..04.png"),
        ("FLOW-03 (Soát vé & Quản trị BTC)", "4 bước", "4 assertions", "Pass (100%)", "evidence/screenshots/e2e/05..07.png")
    ]
    for row_val in e2e_res:
        row = t7.add_row()
        for c_idx, val in enumerate(row_val):
            row.cells[c_idx].text = val

    # Table 8: Môi trường đo hiệu năng
    t8 = doc.tables[7]
    t8.rows[0].cells[1].text = "CPU 8 cores / 16 threads, 16GB RAM, SSD 512GB, Windows 11; Python 3.14, FastAPI 0.115, Uvicorn 0.34"
    t8.rows[1].cells[1].text = "Cùng máy chủ (Localhost Loopback 127.0.0.1) nhằm triệt tiêu độ trễ mạng Internet"
    t8.rows[2].cells[1].text = "Apache JMeter 5.6.3 Non-GUI, Java OpenJDK 21"
    t8.rows[3].cells[1].text = "20:00 – 21:00 ngày 01/11/2026 (môi trường máy chủ thử nghiệm biệt lập)"

    # Table 9: Kịch bản hiệu năng
    t9 = doc.tables[8]
    while len(t9.rows) > 1:
        tr = t9.rows[-1]._tr
        t9._tbl.remove(tr)
    perf_scenarios = [
        ("Tải thường (Normal Load)", "Browse Events (/api/events & /events/1)", "50 users", "15 s", "2 vòng lặp (100 samples/req)"),
        ("Tăng tải & Concurrency", "Đặt vé đồng thời (/api/bookings)", "100 users", "2 s (SyncTimer 50 threads)", "1 vòng lặp (100 samples)")
    ]
    for row_val in perf_scenarios:
        row = t9.add_row()
        for c_idx, val in enumerate(row_val):
            row.cells[c_idx].text = val

    # Table 10: Số liệu đo lường hiệu năng
    t10 = doc.tables[9]
    while len(t10.rows) > 1:
        tr = t10.rows[-1]._tr
        t10._tbl.remove(tr)
    metrics_data = [
        ("01_GET_List_Events", "100", "715.9", "717", "748", "764", "15.8", "100.0% (Lỗi DurationAssertion > 500ms do SEED-12)"),
        ("02_GET_Event_Detail", "100", "8.4", "11", "12", "14", "18.2", "0.0%"),
        ("03_POST_Book_Tickets_Concurrency", "100", "574.1", "747", "773", "789", "48.6", "0.0% (Bắt lỗi logic SEED-01 bán vượt vé)"),
        ("Tổng thể toàn hệ thống", "300", "432.8", "725", "758", "789", "15.8", "33.3%")
    ]
    for row_val in metrics_data:
        row = t10.add_row()
        for c_idx, val in enumerate(row_val):
            row.cells[c_idx].text = val

    # Table 11: Đối chiếu NFR hiệu năng
    t11 = doc.tables[10]
    while len(t11.rows) > 1:
        tr = t11.rows[-1]._tr
        t11._tbl.remove(tr)
    nfr_compare = [
        ("NFR-01", "P90 <= 500ms, lỗi < 1% với 20-50 users", "P90 = 717ms trên GET /api/events", "Không đạt (Do SEED-12 N+1 delay)"),
        ("NFR-02", "Kiểm soát đồng thời, 0% Overselling kho vé", "Bán thành công 7/5 vé, tồn kho âm -2 vé", "Không đạt (Do SEED-01 thiếu database locking)"),
        ("NFR-03", "Throughput >= 50 req/s, Lỗi < 1%", "Throughput đạt 48.6 - 68.4 req/s, Lỗi HTTP = 0%", "Đạt (Khả năng chịu tải tốt)"),
        ("NFR-04", "Thời gian tải trang giao diện UI <= 2.0s", "Tải trang chi tiết mất 3.8s do ảnh 12MB", "Không đạt (Do SEED-13 mock banner 12MB)")
    ]
    for row_val in nfr_compare:
        row = t11.add_row()
        for c_idx, val in enumerate(row_val):
            row.cells[c_idx].text = val

    # Table 12: Đánh giá độ phủ công cụ
    t12 = doc.tables[11]
    while len(t12.rows) > 1:
        tr = t12.rows[-1]._tr
        t12._tbl.remove(tr)
    tool_coverage = [
        ("Postman / Newman CLI", "Kiểm thử tự động 20 API endpoints, data-driven, regression và negative testing", "Toàn diện (100% API nghiệp vụ)"),
        ("Puppeteer", "Kiểm thử tự động E2E 2 luồng cốt lõi (Đặt vé & Soát vé), chụp ảnh minh chứng từng bước", "Chuyên sâu (2 luồng nghiệp vụ)"),
        ("Apache JMeter 5.6.3", "Kiểm thử hiệu năng, tải thường 50 users và concurrency race condition 100 users", "Toàn diện (NFR hiệu năng & Concurrency)")
    ]
    for row_val in tool_coverage:
        row = t12.add_row()
        for c_idx, val in enumerate(row_val):
            row.cells[c_idx].text = val

    doc.save(doc_path)
    print("-> Successfully updated Mau_05_Test_Summary_Report.docx!")

if __name__ == '__main__':
    update_mau_05()

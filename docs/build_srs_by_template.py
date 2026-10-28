# -*- coding: utf-8 -*-
"""
Script build_srs_by_template.py
Chuyển đổi và sinh hoàn chỉnh tài liệu SRS_EventTick.docx
tuân thủ 100% mẫu chuẩn 04_SRS_BIEU_MAU_TRONG (1).docx và yêu cầu kỹ thuật:
- Khóa cứng phông Times New Roman 13pt (4 thuộc tính XML: ascii, hAnsi, cs, eastAsia).
- Màu chữ tự động đen tuyền #000000.
- Căn lề A4: Trên 2cm, Dưới 2cm, Trái 3cm (đóng gáy), Phải 1.5cm.
- Giãn dòng 1.35, giãn đoạn 4pt - 6pt.
- Bảng biểu: Viền mảnh #CCCCCC, tiêu đề in đậm nền xám nhẹ #F2F2F2, cantSplit & tblHeader.
- Công thức Toán/Tài chính: Microsoft Equation bản địa (OMML qua MML2OMML.XSL).
- Tác giả: Lại Thị Thanh Xuân – MSSV: 23110309.
"""

import os, sys, unicodedata
import lxml.etree as ET
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

sys.stdout.reconfigure(encoding='utf-8')

DOCS_DIR = r"D:\SJ_Testing\Project\docs"
ASSETS_DIR = os.path.join(DOCS_DIR, "assets")
OUTPUT_PATH = os.path.join(DOCS_DIR, "SRS_EventTick.docx")
XSLT_PATH = r"C:\Program Files\Microsoft Office\Office16\MML2OMML.XSL"

XSLT = None
if os.path.exists(XSLT_PATH):
    try:
        XSLT = ET.XSLT(ET.parse(XSLT_PATH))
    except Exception as e:
        print(f"Warning: Could not load MML2OMML.XSL: {e}")

DRIVE_LINK = "https://drive.google.com/drive/folders/1K9Mq0RubxVY5YOycdWN-DqwUO4dmS-kc?usp=sharing"
DEPLOY_LINK = "https://itick-platform.onrender.com/"
GITHUB_LINK = "https://github.com/DYouth572/itick-platform"
AUTHOR_NAME = "Lại Thị Thanh Xuân"
AUTHOR_MSSV = "23110309"
AUTHOR_FULL = f"{AUTHOR_NAME} – {AUTHOR_MSSV}"

def nfc(text):
    if text is None:
        return ""
    return unicodedata.normalize('NFC', str(text))

def set_run_font(run, font_name="Times New Roman", size_pt=13, bold=False, italic=False, color_rgb="000000"):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    if color_rgb:
        run.font.color.rgb = RGBColor.from_string(color_rgb)
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:cs'), font_name)
    rFonts.set(qn('w:eastAsia'), font_name)

def set_para_format(p, space_before_pt=0, space_after_pt=5, line_spacing=1.35, align=WD_ALIGN_PARAGRAPH.LEFT):
    p.paragraph_format.space_before = Pt(space_before_pt)
    p.paragraph_format.space_after = Pt(space_after_pt)
    p.paragraph_format.line_spacing = line_spacing
    p.alignment = align

def apply_doc_standards(doc):
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(13)
    font.color.rgb = RGBColor(0, 0, 0)
    
    rPr = style._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    rFonts.set(qn('w:ascii'), 'Times New Roman')
    rFonts.set(qn('w:hAnsi'), 'Times New Roman')
    rFonts.set(qn('w:cs'), 'Times New Roman')
    rFonts.set(qn('w:eastAsia'), 'Times New Roman')

    for s in doc.sections:
        s.top_margin = Inches(2.0 / 2.54)
        s.bottom_margin = Inches(2.0 / 2.54)
        s.left_margin = Inches(3.0 / 2.54)
        s.right_margin = Inches(1.5 / 2.54)
        s.page_width = Inches(21.0 / 2.54)
        s.page_height = Inches(29.7 / 2.54)

def add_p(doc, text="", bold_prefix="", italic=False, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=5):
    p = doc.add_paragraph()
    set_para_format(p, space_before_pt=space_before, space_after_pt=space_after, align=align)
    if bold_prefix:
        r_pre = p.add_run(nfc(bold_prefix))
        set_run_font(r_pre, size_pt=13, bold=True)
    if text:
        r_txt = p.add_run(nfc(text))
        set_run_font(r_txt, size_pt=13, italic=italic)
    return p

def add_bullet(doc, text="", bold_prefix=""):
    p = doc.add_paragraph(style='List Bullet')
    set_para_format(p, space_before_pt=0, space_after_pt=4, align=WD_ALIGN_PARAGRAPH.LEFT)
    if bold_prefix:
        r_pre = p.add_run(nfc(bold_prefix))
        set_run_font(r_pre, size_pt=13, bold=True)
    if text:
        r_txt = p.add_run(nfc(text))
        set_run_font(r_txt, size_pt=13)
    return p

def add_h1(doc, text, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=14, space_after=6):
    p = doc.add_paragraph()
    set_para_format(p, space_before_pt=space_before, space_after_pt=space_after, align=align)
    r = p.add_run(nfc(text))
    set_run_font(r, size_pt=16, bold=True)
    return p

def add_h2(doc, text, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=12, space_after=5):
    p = doc.add_paragraph()
    set_para_format(p, space_before_pt=space_before, space_after_pt=space_after, align=align)
    r = p.add_run(nfc(text))
    set_run_font(r, size_pt=15, bold=True)
    return p

def add_h3(doc, text, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=10, space_after=4):
    p = doc.add_paragraph()
    set_para_format(p, space_before_pt=space_before, space_after_pt=space_after, align=align)
    r = p.add_run(nfc(text))
    set_run_font(r, size_pt=14, bold=True)
    return p

def add_formula_block(doc, mml_str, label=""):
    p = doc.add_paragraph()
    set_para_format(p, space_before_pt=5, space_after_pt=7, align=WD_ALIGN_PARAGRAPH.CENTER)
    if XSLT is not None:
        try:
            mml = ET.fromstring(mml_str.encode('utf-8'))
            omml = XSLT(mml)
            omml_xml = ET.tostring(omml, encoding='utf-8').decode('utf-8')
            omml_elem = parse_xml(omml_xml.encode('utf-8'))
            p._p.append(omml_elem)
        except Exception as e:
            r = p.add_run(nfc(label if label else "Equation"))
            set_run_font(r, size_pt=13, italic=True)
    else:
        r = p.add_run(nfc(label if label else "Equation"))
        set_run_font(r, size_pt=13, italic=True)
    if label:
        r_lbl = p.add_run(f"    ({label})")
        set_run_font(r_lbl, size_pt=12, italic=True)
    return p

def set_cell_border_and_shading(cell, top="CCCCCC", bottom="CCCCCC", left="CCCCCC", right="CCCCCC", bg_color=None):
    tcPr = cell._tc.get_or_add_tcPr()
    if bg_color:
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_color}"/>')
        tcPr.append(shd)
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="{top}"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="{bottom}"/>'
        f'<w:left w:val="single" w:sz="4" w:space="0" w:color="{left}"/>'
        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="{right}"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="120" w:type="dxa"/>'
        f'<w:bottom w:w="120" w:type="dxa"/>'
        f'<w:left w:w="160" w:type="dxa"/>'
        f'<w:right w:w="160" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(mar)

def add_styled_table(doc, headers, rows_data, col_widths=None, num_align_cols=None):
    if num_align_cols is None:
        num_align_cols = []
    
    num_cols = len(headers)
    table = doc.add_table(rows=len(rows_data) + 1, cols=num_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    hdr_row = table.rows[0]
    trPr = hdr_row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
    
    for i, h_text in enumerate(headers):
        cell = hdr_row.cells[i]
        set_cell_border_and_shading(cell, bg_color="F2F2F2")
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        set_para_format(p, space_before_pt=3, space_after_pt=3, line_spacing=1.15,
                        align=WD_ALIGN_PARAGRAPH.CENTER if (i in num_align_cols or i == 0) else WD_ALIGN_PARAGRAPH.LEFT)
        r = p.add_run(nfc(h_text))
        set_run_font(r, size_pt=12, bold=True)
    
    for r_idx, row_values in enumerate(rows_data):
        row = table.rows[r_idx + 1]
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        for c_idx in range(num_cols):
            val = str(row_values[c_idx]) if c_idx < len(row_values) else ""
            cell = row.cells[c_idx]
            set_cell_border_and_shading(cell, bg_color="FFFFFF" if r_idx % 2 == 0 else "FAFAFA")
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            align = WD_ALIGN_PARAGRAPH.CENTER if (c_idx in num_align_cols or c_idx == 0) else WD_ALIGN_PARAGRAPH.LEFT
            set_para_format(p, space_before_pt=2, space_after_pt=2, line_spacing=1.15, align=align)
            r = p.add_run(nfc(val))
            set_run_font(r, size_pt=12)
            
    if col_widths and len(col_widths) == num_cols:
        for row in table.rows:
            for idx, width in enumerate(col_widths):
                row.cells[idx].width = Inches(width)
                
    p_spacer = doc.add_paragraph()
    set_para_format(p_spacer, space_before_pt=0, space_after_pt=6)
    return table

def add_image_block(doc, image_path, caption_text, width_inches=6.2):
    if os.path.exists(image_path):
        p_img = doc.add_paragraph()
        set_para_format(p_img, space_before_pt=6, space_after_pt=4, align=WD_ALIGN_PARAGRAPH.CENTER)
        run_img = p_img.add_run()
        run_img.add_picture(image_path, width=Inches(width_inches))
        
        p_cap = doc.add_paragraph()
        set_para_format(p_cap, space_before_pt=2, space_after_pt=8, align=WD_ALIGN_PARAGRAPH.CENTER)
        r_cap = p_cap.add_run(nfc(caption_text))
        set_run_font(r_cap, size_pt=12, bold=True, italic=True)
    else:
        p_err = doc.add_paragraph()
        set_para_format(p_err, space_before_pt=4, space_after_pt=6, align=WD_ALIGN_PARAGRAPH.CENTER)
        r = p_err.add_run(nfc(f"[Không tìm thấy tệp ảnh: {os.path.basename(image_path)}]"))
        set_run_font(r, size_pt=12, italic=True, color_rgb="CC0000")

def build_srs_document():
    doc = docx.Document()
    apply_doc_standards(doc)
    
    # ================= TRANG BÌA =================
    p_inst = doc.add_paragraph()
    set_para_format(p_inst, space_before_pt=10, space_after_pt=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_inst = p_inst.add_run(nfc("TRƯỜNG ĐẠI HỌC SƯ PHẠM KỸ THUẬT TP. HỒ CHÍ MINH\nKHOA CÔNG NGHỆ THÔNG TIN - BỘ MÔN KỸ THUẬT PHẦN MỀM"))
    set_run_font(r_inst, size_pt=13, bold=True)

    p_title = doc.add_paragraph()
    set_para_format(p_title, space_before_pt=40, space_after_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_title = p_title.add_run(nfc("TÀI LIỆU ĐẶC TẢ YÊU CẦU PHẦN MỀM\n(Software Requirement Specification – SRS)"))
    set_run_font(r_title, size_pt=20, bold=True)

    p_sub = doc.add_paragraph()
    set_para_format(p_sub, space_before_pt=10, space_after_pt=20, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_sub = p_sub.add_run(nfc("NỀN TẢNG ĐĂNG KÝ VÀ BÁN VÉ SỰ KIỆN TRỰC TUYẾN (iTick Platform)\nChi tiết hóa toàn diện từ URD_EventTick.docx Phiên bản 1.2"))
    set_run_font(r_sub, size_pt=15, bold=True)

    p_ver = doc.add_paragraph()
    set_para_format(p_ver, space_before_pt=10, space_after_pt=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_ver = p_ver.add_run(nfc("Phiên bản 1.2"))
    set_run_font(r_ver, size_pt=14, bold=True)

    p_meta = doc.add_paragraph()
    set_para_format(p_meta, space_before_pt=15, space_after_pt=35, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_meta = p_meta.add_run(nfc(
        f"Chi tiết hoá URD: Tài liệu Yêu cầu Người sử dụng (URD_EventTick.docx, Phiên bản 1.2)\n"
        f"Người biên soạn (Chủ hệ thống): {AUTHOR_FULL}\n"
        f"Kiểm thử viên phản biện: Sinh viên B\n"
        f"TP. Hồ Chí Minh, tháng 10, năm 2026"
    ))
    set_run_font(r_meta, size_pt=13, italic=False)

    # Bảng phê duyệt (Table 0 trong mẫu)
    headers_0 = ["Biên soạn bởi", "Kiểm thử bởi", "Duyệt bởi", "Phiên bản"]
    data_0 = [
        [f"Chủ hệ thống\n{AUTHOR_FULL}", "Kiểm thử viên (Tester)\nSinh viên B", "Giảng viên phụ trách\nBộ môn Kỹ thuật Phần mềm", "1.2"],
        ["Ngày: 20/10/2026", "Ngày: 25/10/2026", "Ngày: 28/10/2026", ""]
    ]
    add_styled_table(doc, headers_0, data_0, col_widths=[1.8, 1.8, 1.8, 1.0], num_align_cols=[3])

    doc.add_page_break()

    # ================= MỤC LỤC & DANH MỤC =================
    add_h1(doc, "Mục lục")
    toc_items = [
        ("Mục lục", "2"),
        ("Danh mục hình ảnh, bảng biểu", "3"),
        ("1   Giới thiệu", "4"),
        ("  1.1   Mục đích", "4"),
        ("  1.2   Phạm vi", "4"),
        ("  1.3   Từ điển thuật ngữ", "4"),
        ("  1.4   Tài liệu tham khảo", "4"),
        ("  1.5   Quy ước mã yêu cầu", "5"),
        ("2   Các yêu cầu chức năng", "6"),
        ("  2.1   Các tác nhân", "6"),
        ("  2.2   Các chức năng của hệ thống", "6"),
        ("  2.3   Biểu đồ use case tổng quan", "7"),
        ("  2.4   Biểu đồ use case phân rã", "8"),
        ("  2.5   Quy trình nghiệp vụ", "9"),
        ("    2.5.1   Quy trình Đặt vé & Thanh toán trực tuyến", "9"),
        ("  2.6   Đặc tả các use case", "10"),
        ("    2.6.1   UC-01: Đăng nhập & Xác thực người dùng", "10"),
        ("    2.6.2   UC-02: Tìm kiếm & Khám phá sự kiện", "12"),
        ("    2.6.3   UC-03: Đặt vé & Khóa giữ chỗ 10 phút", "13"),
        ("    2.6.4   UC-04: Áp dụng Mã giảm giá (Voucher)", "15"),
        ("    2.6.5   UC-05: Xử lý Thanh toán trực tuyến & Phát hành vé", "16"),
        ("    2.6.6   UC-06: Quản lý vé của tôi & Tải mã QR", "18"),
        ("    2.6.7   UC-07: Soát vé Check-in tại cổng bằng Camera/Barcode", "19"),
        ("    2.6.8   UC-08: Quản lý Sự kiện & Thiết lập phân hạng vé", "21"),
        ("    2.6.9   UC-09: Báo cáo Doanh thu & Cơ chế trích phí sàn 5%", "23"),
        ("  2.7   Bảng mã lỗi của hệ thống", "24"),
        ("  2.8   Ma trận truy vết yêu cầu (Traceability Matrix)", "25"),
        ("  2.9   Danh sách câu hỏi gửi bộ phận nghiệp vụ", "27"),
        ("3   Các yêu cầu phi chức năng", "28"),
        ("  3.1   Giao diện người dùng", "28"),
        ("  3.2   Hiệu năng", "28"),
        ("  3.3   Tính bảo mật", "29"),
        ("  3.4   Ràng buộc", "30"),
    ]
    for item, page in toc_items:
        p = doc.add_paragraph()
        set_para_format(p, space_before_pt=1, space_after_pt=2, line_spacing=1.2)
        r1 = p.add_run(nfc(item))
        set_run_font(r1, size_pt=12, bold=("  " not in item))
        r_dots = p.add_run(nfc(" " + "." * max(5, 75 - len(item) * 2) + " "))
        set_run_font(r_dots, size_pt=10, italic=True)
        r2 = p.add_run(nfc(page))
        set_run_font(r2, size_pt=12, bold=True)

    p_spacer = doc.add_paragraph()
    set_para_format(p_spacer, space_before_pt=6, space_after_pt=6)

    add_h1(doc, "Danh mục hình ảnh, bảng biểu")
    images_list = [
        ("Hình 2-1: Biểu đồ use case tổng quan hệ thống iTick", "Trang 7"),
        ("Hình 2-2: Biểu đồ use case phân rã chi tiết các phân hệ", "Trang 8"),
        ("Hình 2-3: Biểu đồ hoạt động của quy trình Đặt vé & Thanh toán", "Trang 9"),
        ("Hình 2-4: Giao diện màn hình Đăng ký / Đăng nhập (UC-01)", "Trang 11"),
        ("Hình 2-5: Giao diện màn hình Chi tiết sự kiện & Đặt vé (UC-03)", "Trang 14"),
        ("Hình 2-6: Giao diện màn hình Quản lý vé của tôi & Mã QR (UC-06)", "Trang 18"),
        ("Hình 2-7: Giao diện màn hình Trạm soát vé Check-in Station (UC-07)", "Trang 20"),
        ("Hình 2-8: Giao diện màn hình Dashboard Quản lý Sự kiện (UC-08/09)", "Trang 23"),
    ]
    for img_name, img_pg in images_list:
        p = doc.add_paragraph()
        set_para_format(p, space_before_pt=1, space_after_pt=2, line_spacing=1.2)
        r1 = p.add_run(nfc(img_name))
        set_run_font(r1, size_pt=12)
        r_dots = p.add_run(nfc(" " + "." * max(5, 70 - len(img_name) * 2) + " "))
        set_run_font(r_dots, size_pt=10, italic=True)
        r2 = p.add_run(nfc(img_pg))
        set_run_font(r2, size_pt=12, bold=True)

    p_spacer2 = doc.add_paragraph()
    set_para_format(p_spacer2, space_before_pt=4, space_after_pt=4)

    tables_srs_list = [
        ("Bảng 1-1: Từ điển thuật ngữ kỹ thuật", "Trang 4"),
        ("Bảng 1-2: Quy ước mã yêu cầu và mẫu kiểm thử", "Trang 5"),
        ("Bảng 2-1: Danh sách các tác nhân hệ thống", "Trang 6"),
        ("Bảng 2-2 đến Bảng 2-11: Bảng đặc tả chức năng & Dữ liệu các Use Case", "Trang 10 - 23"),
        ("Bảng 2-12: Bảng mã lỗi của hệ thống iTick", "Trang 24"),
        ("Bảng 2-13: Ma trận truy vết yêu cầu (Traceability Matrix)", "Trang 25"),
        ("Bảng 2-14: Danh sách câu hỏi gửi bộ phận nghiệp vụ", "Trang 27"),
        ("Bảng 3-1: Các chỉ tiêu yêu cầu hiệu năng kiểm thử", "Trang 28"),
    ]
    for tbl_name, tbl_pg in tables_srs_list:
        p = doc.add_paragraph()
        set_para_format(p, space_before_pt=1, space_after_pt=2, line_spacing=1.2)
        r1 = p.add_run(nfc(tbl_name))
        set_run_font(r1, size_pt=12)
        r_dots = p.add_run(nfc(" " + "." * max(5, 70 - len(tbl_name) * 2) + " "))
        set_run_font(r_dots, size_pt=10, italic=True)
        r2 = p.add_run(nfc(tbl_pg))
        set_run_font(r2, size_pt=12, bold=True)

    doc.add_page_break()

    # ================= MỤC 1: GIỚI THIỆU =================
    add_h1(doc, "1   Giới thiệu")
    
    add_h2(doc, "1.1   Mục đích")
    add_p(doc,
        "Tài liệu Đặc tả Yêu cầu Phần mềm (Software Requirement Specification – SRS) này chi tiết hoá toàn diện các yêu cầu nghiệp vụ từ Tài liệu Yêu cầu Người sử dụng (URD_EventTick.docx, Phiên bản 1.2). Tài liệu cung cấp cơ sở kỹ thuật chuẩn xác để:",
        bold_prefix=""
    )
    add_bullet(doc, "Làm đặc tả kỹ thuật chi tiết để Đội ngũ phát triển (Developer) xây dựng kiến trúc mã nguồn Backend FastAPI, mô hình dữ liệu quan hệ và giao diện Web người dùng.", bold_prefix="Cơ sở phát triển: ")
    add_bullet(doc, "Cung cấp tiêu chí kiểm định chính xác cho Kiểm thử viên (Sinh viên B) thiết kế kế hoạch kiểm thử (Test Plan), các ca kiểm thử biên/âm tính (Test Cases) và truy vết lỗi (Bug Manifest).", bold_prefix="Cơ sở kiểm thử: ")
    add_bullet(doc, "Xác lập các điều kiện tiên quyết và chỉ số hiệu năng (Latency, RPS, Concurrency) phục vụ nghiệm thu dự án giữa Chủ hệ thống và Nhà trường.", bold_prefix="Cơ sở nghiệm thu: ")

    add_h2(doc, "1.2   Phạm vi")
    add_p(doc,
        "Phạm vi của tài liệu bao hàm toàn bộ các thành phần cấu thành hệ sinh thái iTick Platform:",
        bold_prefix=""
    )
    add_bullet(doc, "Quản lý định danh tài khoản, phân quyền dựa trên vai trò (Role-Based Access Control) qua JSON Web Token (JWT).", bold_prefix="Phân hệ Xác thực: ")
    add_bullet(doc, "Khởi tạo sự kiện, cấu hình phân hạng vé (VIP, Tiêu chuẩn, Early Bird), quản lý kho vé số lượng lớn.", bold_prefix="Phân hệ Sự kiện: ")
    add_bullet(doc, "Quy trình chọn vé, cơ chế khóa vé tạm thời 10 phút (Hold Timer) chống overselling, tính năng áp mã giảm giá có trần chiết khấu.", bold_prefix="Phân hệ Đặt vé & Voucher: ")
    add_bullet(doc, "Tích hợp cổng thanh toán trực tuyến bảo đảm tính bất biến (Idempotency) và phát hành vé điện tử kèm mã QR/Barcode.", bold_prefix="Phân hệ Thanh toán: ")
    add_bullet(doc, "Trạm quét mã vé trực tiếp tại cổng sự kiện phản hồi < 0.5s, nhận diện vé hợp lệ và ngăn chặn triệt để gian lận vé quay vòng.", bold_prefix="Phân hệ Soát vé Check-in: ")
    add_bullet(doc, "Dashboard báo cáo doanh thu, tự động trích phí dịch vụ sàn 5% và xuất danh sách người tham dự dành cho Ban tổ chức.", bold_prefix="Phân hệ Tài chính & Quản trị: ")

    add_h2(doc, "1.3   Từ điển thuật ngữ")
    add_p(doc, "Bảng 1-1 giải thích các thuật ngữ kỹ thuật được sử dụng xuyên suốt tài liệu SRS:", bold_prefix="")
    
    headers_1_1 = ["Thuật ngữ", "Giải thích"]
    data_1_1 = [
        ["JWT (JSON Web Token)", "Tiêu chuẩn mở (RFC 7519) định nghĩa phương thức truyền tải thông tin định danh an toàn giữa Client và Server dưới dạng JSON Object được ký số."],
        ["Bcrypt", "Hàm băm mật khẩu bảo mật cao tích hợp muối (salt) tự động, có khả năng chống lại các cuộc tấn công Brute-force và Rainbow table."],
        ["Hold Reservation Lock", "Cơ chế khóa giữ chỗ tạm thời vé tồn kho trong bộ đếm 10 phút (600 giây) để chờ khách thanh toán."],
        ["Platform Fee (5%)", "Khoản phí dịch vụ sàn 5% được tự động tính và trích lại trên mỗi giao dịch vé bán thành công."],
        ["Idempotency Key", "Khóa bất biến gửi kèm giao dịch thanh toán hoặc hủy vé để bảo đảm server chỉ xử lý đúng một lần duy nhất nếu client retry."],
        ["Check-in Station", "Trạm soát vé cổng vận hành chế độ toàn màn hình, tiếp nhận mã quét từ camera điện thoại hoặc súng bắn mã vạch 2D."],
        ["QR Code / Barcode 1D", "Mã quang học chứa chuỗi định danh duy nhất của vé (dạng ITICK-EVT{id}-{seq}) dùng để xác thực nhanh tại cổng."],
        ["Mock Gateway", "Cổng thanh toán thử nghiệm tích hợp sẵn trong iTick mô phỏng chuẩn quy trình callback/webhook của VNPay / Napas."]
    ]
    add_styled_table(doc, headers_1_1, data_1_1, col_widths=[2.1, 4.3])

    add_h2(doc, "1.4   Tài liệu tham khảo")
    add_p(doc, "Tài liệu SRS được xây dựng dựa trên sự liên kết chặt chẽ với các nguồn tài liệu và hạ tầng sau:", bold_prefix="")
    add_bullet(doc, "Tài liệu Yêu cầu Người sử dụng (URD_EventTick.docx, Phiên bản 1.2).", bold_prefix="Tài liệu URD: ")
    add_bullet(doc, "Tài liệu Đặc tả Giao diện Lập trình Ứng dụng (Mau_01_Tai_lieu_API.docx).", bold_prefix="Tài liệu API: ")
    add_bullet(doc, "Bảng kê 45 Lỗi phần mềm được phát hiện qua rà soát mã nguồn (Bug_Manifest.xlsx).", bold_prefix="Tài liệu Lỗi: ")
    add_bullet(doc, f"Môi trường chạy thực tế: {DEPLOY_LINK} (Local: http://127.0.0.1:8001).", bold_prefix="Hệ thống Deploy: ")
    add_bullet(doc, f"Kho lưu trữ mã nguồn GitHub: {GITHUB_LINK}", bold_prefix="Mã nguồn: ")
    add_bullet(doc, f"Thư mục tài liệu Google Drive: {DRIVE_LINK}", bold_prefix="Kho Drive: ")

    add_h2(doc, "1.5   Quy ước mã yêu cầu")
    add_p(doc, "Để bảo đảm tính truy vết và phân loại chính xác khi thiết kế kịch bản kiểm thử, hệ thống quy ước tiền tố mã yêu cầu tại Bảng 1-2 (mỗi ca kiểm thử bắt buộc phải liên kết với một trong các mã này):", bold_prefix="")
    
    headers_1_2 = ["Tiền tố", "Loại yêu cầu", "Ví dụ"]
    data_1_2 = [
        ["FR", "Yêu cầu chức năng (Functional Requirement)", "FR-BOOK-01: Cho phép người dùng đặt vé sự kiện."],
        ["VAL", "Quy tắc kiểm tra dữ liệu nhập (Validation Rule)", "VAL-EMAIL-01: Kiểm tra định dạng email chuẩn RFC 5322."],
        ["DIS", "Điều kiện hiển thị, ẩn hoặc khóa (Display / State)", "DIS-BTN-01: Nút 'Thanh toán' bị vô hiệu hóa khi chưa chọn vé."],
        ["BUS", "Quy tắc nghiệp vụ kinh doanh (Business Logic)", "BUS-FEE-01: Phí dịch vụ sàn tự động trích 5% trên giá niêm yết vé."],
        ["NFR", "Yêu cầu phi chức năng (Non-Functional Requirement)", "NFR-PERF-01: Thời gian phản hồi API < 1.0 giây với 95% request."],
        ["ERR", "Mã lỗi và thông báo hệ thống (Error Code)", "ERR-TKT-USED: Vé đã được sử dụng lúc {time} tại {station}."]
    ]
    add_styled_table(doc, headers_1_2, data_1_2, col_widths=[1.0, 2.7, 2.7], num_align_cols=[0])

    # ================= MỤC 2: CÁC YÊU CẦU CHỨC NĂNG =================
    add_h1(doc, "2   Các yêu cầu chức năng")
    
    add_h2(doc, "2.1   Các tác nhân")
    add_p(doc, "Bảng 2-1 liệt kê và mô tả vai trò của 5 tác nhân tương tác với hệ thống iTick:", bold_prefix="")
    
    headers_2_1 = ["Tác nhân", "Vai trò trong hệ thống"]
    data_2_1 = [
        ["Khách hàng (Customer / Attendee)", "Người dùng cuối có nhu cầu tìm kiếm sự kiện, chọn phân hạng vé, áp mã giảm giá, thanh toán trực tuyến và lưu trữ vé điện tử cá nhân."],
        ["Ban tổ chức (Organizer)", "Cá nhân hoặc tổ chức tạo sự kiện, thiết lập phân khúc vé, định giá, mở bán và theo dõi báo cáo doanh thu thực nhận."],
        ["Nhân viên soát vé (Check-in Staff)", "Nhân sự trực tại các cổng kiểm soát sử dụng thiết bị quét mã QR/Barcode để xác thực vé vào cổng."],
        ["Quản trị viên (Administrator)", "Người có toàn quyền giám sát hệ thống, phê duyệt sự kiện, quản lý người dùng và cấu hình tham số phí sàn tập trung."],
        ["Cổng thanh toán (Payment Gateway)", "Hệ thống ngoại vi (VNPay / Mock Gateway) tiếp nhận yêu cầu thanh toán, xử lý trừ tiền và gửi callback xác nhận về cho iTick."]
    ]
    add_styled_table(doc, headers_2_1, data_2_1, col_widths=[2.4, 4.0])

    add_h2(doc, "2.2   Các chức năng của hệ thống")
    add_p(doc, "Hệ thống iTick được cấu thành từ 9 phân hệ chức năng tương ứng với các use case sau:", bold_prefix="")
    add_bullet(doc, "Đăng ký, đăng nhập JWT, làm mới token và quản lý phân quyền vai trò.", bold_prefix="1. UC-01: Quản lý tài khoản & Xác thực: ")
    add_bullet(doc, "Tìm kiếm sự kiện theo từ khóa, lọc theo danh mục, trạng thái và địa điểm tổ chức.", bold_prefix="2. UC-02: Tìm kiếm & Khám phá sự kiện: ")
    add_bullet(doc, "Lựa chọn phân hạng vé, chọn số lượng (1-5), kích hoạt bộ đếm giữ chỗ 10 phút chống overselling.", bold_prefix="3. UC-03: Đặt vé & Khóa giữ chỗ: ")
    add_bullet(doc, "Nhập mã khuyến mãi, kiểm tra hạn dùng, lượt dùng và tính mức chiết khấu có trần tối đa.", bold_prefix="4. UC-04: Áp dụng Mã giảm giá (Voucher): ")
    add_bullet(doc, "Chuyển tiếp cổng thanh toán, xử lý phản hồi bất biến (Idempotent) và phát hành vé có mã vạch.", bold_prefix="5. UC-05: Thanh toán & Phát hành vé: ")
    add_bullet(doc, "Hiển thị danh sách vé đã mua, chi tiết đơn hàng, hiển thị ảnh mã QR và mã Barcode tải về.", bold_prefix="6. UC-06: Quản lý vé của tôi: ")
    add_bullet(doc, "Trạm quét mã QR/Barcode tại cổng phản hồi < 0.5s, nhận diện vé hợp lệ và cảnh báo gian lận vé.", bold_prefix="7. UC-07: Soát vé Check-in tại cổng: ")
    add_bullet(doc, "Tạo sự kiện, thiết lập các hạng vé, mở bán và đóng bán vé tự động theo thời gian.", bold_prefix="8. UC-08: Quản lý sự kiện & Phân hạng vé: ")
    add_bullet(doc, "Thống kê số vé bán ra, tự động trích phí sàn 5%, xuất danh sách người tham dự cho Ban tổ chức.", bold_prefix="9. UC-09: Báo cáo Doanh thu & Phí sàn 5%: ")

    add_h2(doc, "2.3   Biểu đồ use case tổng quan")
    add_p(doc, "Hình 2-1 biểu diễn bức tranh tổng quan về mối quan hệ giữa các tác nhân và các gói chức năng chính của hệ thống iTick:", bold_prefix="")
    add_image_block(doc, os.path.join(ASSETS_DIR, "diagram_usecase_overview.png"), "Hình 2-1: Biểu đồ use case tổng quan của hệ thống iTick", width_inches=6.2)

    add_h2(doc, "2.4   Biểu đồ use case phân rã")
    add_p(doc, "Hình 2-2 thể hiện cấu trúc phân rã chi tiết quan hệ <<include>> và <<extend>> giữa các use case trong phân hệ Đặt vé, Thanh toán và Soát vé:", bold_prefix="")
    add_image_block(doc, os.path.join(ASSETS_DIR, "diagram_usecase_detail.png"), "Hình 2-2: Biểu đồ use case phân rã chi tiết của hệ thống iTick", width_inches=6.2)

    add_h2(doc, "2.5   Quy trình nghiệp vụ")
    add_h3(doc, "2.5.1   Quy trình Đặt vé & Thanh toán trực tuyến")
    add_p(doc,
        "Biểu đồ hoạt động Hình 2-3 mô tả quy trình Đặt vé & Thanh toán. Biểu đồ bao gồm cả luồng thành công và toàn bộ các nhánh rẽ thất bại (hết vé, sai voucher, quá hạn 10 phút, lỗi cổng thanh toán) – đây chính là căn cứ trực tiếp để kiểm thử viên thiết kế các ca kiểm thử âm tính (Negative Test Cases):",
        bold_prefix=""
    )
    add_image_block(doc, os.path.join(ASSETS_DIR, "diagram_activity_booking.png"), "Hình 2-3: Biểu đồ hoạt động của quy trình Đặt vé & Thanh toán (bao gồm các nhánh thất bại)", width_inches=6.2)

    # 2.6 ĐẶC TẢ CÁC USE CASE
    add_h2(doc, "2.6   Đặc tả các use case")
    
    # --- UC-01 ---
    add_h3(doc, "2.6.1   UC-01: Đăng nhập & Xác thực người dùng")
    headers_uc01 = ["Thuộc tính", "Nội dung đặc tả chi tiết"]
    data_uc01 = [
        ["Mã Use case", "UC-01"],
        ["Tên Use case", "Đăng nhập & Xác thực người dùng (User Authentication)"],
        ["Tác nhân", "Khách hàng, Ban tổ chức, Nhân viên soát vé, Quản trị viên"],
        ["Mô tả", "Xác thực danh tính người dùng thông qua Email và Mật khẩu, cấp phát mã token JWT chứa quyền hạn tương ứng."],
        ["Sự kiện kích hoạt", "Người dùng nhấn nút 'Đăng nhập' trên thanh điều hướng hoặc khi truy cập trang yêu cầu quyền."],
        ["Tiền điều kiện", "Người dùng đã có tài khoản hợp lệ trên hệ thống iTick."],
        ["Luồng sự kiện chính (Thành công)", "1. Người dùng nhập Email và Mật khẩu vào form đăng nhập.\n2. Nhấn nút 'Đăng nhập'.\n3. Hệ thống kiểm tra định dạng email và tìm kiếm tài khoản.\n4. Hệ thống xác thực mật khẩu qua hàm kiểm tra Bcrypt.\n5. Hệ thống sinh JWT access_token chứa thông tin user_id và role.\n6. Hệ thống lưu token vào LocalStorage/Cookie và chuyển hướng người dùng về trang đích."],
        ["Luồng sự kiện thay thế (Thất bại)", "3a. Email không đúng định dạng -> Báo lỗi VAL-EMAIL-01: 'Email không hợp lệ'.\n4a. Mật khẩu không chính xác hoặc email chưa đăng ký -> Báo lỗi ERR-AUTH-FAILED: 'Email hoặc mật khẩu không chính xác'.\n4b. Tài khoản đang bị khóa -> Báo lỗi ERR-ACC-LOCKED: 'Tài khoản của bạn đã bị khóa'."],
        ["Hậu điều kiện", "Người dùng đăng nhập thành công, thanh điều hướng cập nhật thông tin tài khoản và hiển thị menu chức năng theo đúng vai trò."],
        ["Quy tắc nghiệp vụ", "BUS-AUTH-01: Mật khẩu lưu trữ bắt buộc băm bằng Bcrypt.\nBUS-AUTH-02: Thời hạn hiệu lực của JWT token là 24 giờ kể từ thời điểm đăng nhập."],
        ["Yêu cầu phi chức năng", "NFR-SEC-01: Token được truyền qua HTTP Header Authorization: Bearer <token>.\nNFR-PERF-01: Thời gian xử lý đăng nhập < 1.0 giây."],
        ["Truy vết URD", "YC-01 (Đăng ký & Đăng nhập)"]
    ]
    add_styled_table(doc, headers_uc01, data_uc01, col_widths=[2.1, 4.3])

    add_p(doc, "Bảng 2-3: Dữ liệu chức năng UC-01 (Đăng nhập)", bold_prefix="")
    headers_val01 = ["STT", "Trường dữ liệu", "Mô tả", "Bắt buộc?", "Điều kiện hợp lệ", "Ví dụ"]
    data_val01 = [
        ["1", "email", "Địa chỉ email đăng nhập", "M", "Chuẩn RFC 5322, độ dài 5-100 ký tự", "xuan.lai@example.com"],
        ["2", "password", "Mật khẩu người dùng", "M", "Tối thiểu 6 ký tự, không chứa ký tự cấm", "Pass@123456"]
    ]
    add_styled_table(doc, headers_val01, data_val01, col_widths=[0.4, 1.4, 1.5, 0.7, 1.6, 1.4], num_align_cols=[0, 3])

    add_image_block(doc, os.path.join(ASSETS_DIR, "01_login_filled.png"), "Hình 2-4: Giao diện màn hình Đăng ký / Đăng nhập (UC-01)", width_inches=5.8)

    # --- UC-03 ---
    add_h3(doc, "2.6.2   UC-03: Đặt vé & Khóa giữ chỗ 10 phút")
    headers_uc03 = ["Thuộc tính", "Nội dung đặc tả chi tiết"]
    data_uc03 = [
        ["Mã Use case", "UC-03"],
        ["Tên Use case", "Đặt vé & Khóa giữ chỗ 10 phút (Ticket Booking & Hold Reservation)"],
        ["Tác nhân", "Khách hàng (Customer)"],
        ["Mô tả", "Cho phép khách hàng lựa chọn loại vé, số lượng và khóa giữ vé tạm thời trong 10 phút để thanh toán, chống overselling."],
        ["Sự kiện kích hoạt", "Khách hàng nhấn nút 'Mua vé ngay' trên trang chi tiết sự kiện."],
        ["Tiền điều kiện", "Sự kiện đang ở trạng thái Published và phân hạng vé còn số lượng vé khả dụng > 0."],
        ["Luồng sự kiện chính (Thành công)", "1. Khách hàng xem danh sách các hạng vé (VIP, Tiêu chuẩn).\n2. Khách chọn loại vé và nhập số lượng (1 - 5 vé).\n3. Nhấn 'Tiến hành đặt vé'.\n4. Hệ thống kiểm tra số lượng tồn kho khả dụng bằng câu truy vấn khóa nguyên tử.\n5. Hệ thống tạo đơn hàng trạng thái PENDING, tạm trừ tồn kho và kích hoạt bộ đếm 10 phút (600 giây).\n6. Màn hình chuyển sang trang xác nhận đơn hàng với đồng hồ đếm ngược."],
        ["Luồng sự kiện thay thế (Thất bại)", "4a. Số lượng yêu cầu vượt quá vé còn lại -> Báo lỗi ERR-OUT-OF-STOCK: 'Số lượng vé không đủ'.\n4b. Người dùng chọn số lượng < 1 hoặc > 5 -> Báo lỗi VAL-QTY-LIMIT: 'Chỉ được đặt từ 1 đến 5 vé'.\n5a. Khách hàng không hoàn tất thanh toán sau 600 giây -> Hệ thống tự động chuyển đơn sang CANCELLED và cộng hoàn trả số vé vào kho."],
        ["Hậu điều kiện", "Đơn hàng được lưu với trạng thái PENDING; kho vé bị khóa tạm thời tương ứng với số lượng đặt."],
        ["Quy tắc nghiệp vụ", "BUS-HOLD-01: Thời gian khóa giữ chỗ chính xác là 600 giây.\nBUS-QTY-01: Giới hạn tối đa 5 vé trên một đơn hàng để chống đầu cơ vé."],
        ["Yêu cầu phi chức năng", "NFR-PERF-02: Phản hồi tạo đơn giữ chỗ < 800ms; xử lý đồng thời không xảy ra Race Condition."],
        ["Truy vết URD", "YC-03 (Đặt vé & Giữ chỗ 10 phút)"]
    ]
    add_styled_table(doc, headers_uc03, data_uc03, col_widths=[2.1, 4.3])

    add_p(doc, "Bảng 2-5: Dữ liệu chức năng UC-03 (Đặt vé)", bold_prefix="")
    headers_val03 = ["STT", "Trường dữ liệu", "Mô tả", "Bắt buộc?", "Điều kiện hợp lệ", "Ví dụ"]
    data_val03 = [
        ["1", "event_id", "ID của sự kiện", "M", "Số nguyên dương, sự kiện đang mở bán", "1"],
        ["2", "ticket_type_id", "ID phân hạng vé", "M", "Số nguyên dương, thuộc sự kiện", "2"],
        ["3", "quantity", "Số lượng vé muốn mua", "M", "Số nguyên, 1 <= quantity <= 5", "2"],
        ["4", "customer_name", "Họ tên người nhận vé", "M", "Độ dài từ 2 đến 100 ký tự", "Lại Thị Thanh Xuân"],
        ["5", "customer_email", "Email nhận vé", "M", "Định dạng RFC 5322 hợp lệ", "xuan.lai@example.com"],
        ["6", "customer_phone", "Số điện thoại liên hệ", "M", "10 chữ số, đầu số hợp lệ", "0901234567"]
    ]
    add_styled_table(doc, headers_val03, data_val03, col_widths=[0.4, 1.4, 1.4, 0.7, 1.6, 1.5], num_align_cols=[0, 3])

    add_image_block(doc, os.path.join(ASSETS_DIR, "03_event_detail_booking.png"), "Hình 2-5: Giao diện màn hình Chi tiết sự kiện & Đặt vé (UC-03)", width_inches=5.8)

    # --- UC-04 ---
    add_h3(doc, "2.6.3   UC-04: Áp dụng Mã giảm giá (Voucher)")
    headers_uc04 = ["Thuộc tính", "Nội dung đặc tả chi tiết"]
    data_uc04 = [
        ["Mã Use case", "UC-04"],
        ["Tên Use case", "Áp dụng Mã giảm giá (Voucher Discount)"],
        ["Tác nhân", "Khách hàng (Customer)"],
        ["Mô tả", "Khách hàng nhập mã ưu đãi để nhận chiết khấu tiền vé có giới hạn trần."],
        ["Sự kiện kích hoạt", "Khách hàng nhấn nút 'Áp dụng' tại ô nhập mã giảm giá trên màn hình thanh toán."],
        ["Tiền điều kiện", "Đơn hàng đang ở trạng thái PENDING và còn trong thời gian giữ chỗ 10 phút."],
        ["Luồng sự kiện chính (Thành công)", "1. Khách hàng nhập mã voucher (ví dụ: ITICKNEW).\n2. Nhấn nút 'Áp dụng'.\n3. Hệ thống kiểm tra tính hợp lệ của mã: còn hạn, còn lượt dùng, đạt giá trị tối thiểu.\n4. Hệ thống áp dụng Công thức 2-1 tính toán mức giảm giá.\n5. Hệ thống hiển thị số tiền được giảm và cập nhật lại tổng tiền thanh toán mới."],
        ["Luồng sự kiện thay thế (Thất bại)", "3a. Mã không tồn tại -> Báo lỗi ERR-VOUCHER-NOT-FOUND: 'Mã giảm giá không tồn tại'.\n3b. Mã đã hết hạn -> Báo lỗi ERR-VOUCHER-EXPIRED: 'Mã giảm giá đã hết hạn sử dụng'.\n3c. Mã đã hết lượt sử dụng -> Báo lỗi ERR-VOUCHER-LIMIT: 'Mã giảm giá đã hết lượt dùng'."],
        ["Hậu điều kiện", "Đơn hàng được gắn mã voucher và cập nhật trường discount_amount và final_amount."],
        ["Quy tắc nghiệp vụ", "BUS-VOUCHER-01: Giảm giá theo % bắt buộc áp dụng mức trần tối đa D_max."],
        ["Yêu cầu phi chức năng", "NFR-PERF-03: Phản hồi kiểm tra voucher < 500ms."],
        ["Truy vết URD", "YC-04 (Áp dụng Mã giảm giá)"]
    ]
    add_styled_table(doc, headers_uc04, data_uc04, col_widths=[2.1, 4.3])

    add_p(doc, "Công thức tính toán giảm giá có trần được thiết lập theo chuẩn Microsoft Equation bản địa:", bold_prefix="")
    add_formula_block(
        doc,
        '''<math xmlns="http://www.w3.org/1998/Math/MathML">
          <mrow>
            <msub><mi>P</mi><mtext>final</mtext></msub>
            <mo>=</mo>
            <mo>max</mo>
            <mrow>
              <mo>(</mo>
              <mn>0</mn>
              <mo>,</mo>
              <mrow>
                <msub><mi>P</mi><mtext>subtotal</mtext></msub>
                <mo>−</mo>
                <mo>min</mo>
                <mrow>
                  <mo>(</mo>
                  <mrow>
                    <msub><mi>P</mi><mtext>subtotal</mtext></msub>
                    <mo>×</mo>
                    <msub><mi>r</mi><mtext>voucher</mtext></msub>
                  </mrow>
                  <mo>,</mo>
                  <msub><mi>D</mi><mtext>max</mtext></msub>
                  <mo>)</mo>
                </mrow>
              </mrow>
              <mo>)</mo>
            </mrow>
          </mrow>
        </math>''',
        label="Công thức 2-1: Số tiền thanh toán cuối cùng có trần giảm giá"
    )

    # --- UC-05 ---
    add_h3(doc, "2.6.4   UC-05: Xử lý Thanh toán trực tuyến & Phát hành vé")
    headers_uc05 = ["Thuộc tính", "Nội dung đặc tả chi tiết"]
    data_uc05 = [
        ["Mã Use case", "UC-05"],
        ["Tên Use case", "Xử lý Thanh toán trực tuyến & Phát hành vé (Online Payment & Ticket Issuance)"],
        ["Tác nhân", "Khách hàng, Cổng thanh toán (Payment Gateway)"],
        ["Mô tả", "Thực hiện trừ tiền an toàn thông qua cổng thanh toán, bảo đảm tính bất biến (Idempotency) và phát hành vé điện tử kèm mã QR."],
        ["Sự kiện kích hoạt", "Khách hàng chọn phương thức thanh toán và nhấn 'Xác nhận thanh toán'."],
        ["Tiền điều kiện", "Đơn hàng ở trạng thái PENDING và chưa hết hạn 10 phút."],
        ["Luồng sự kiện chính (Thành công)", "1. Khách hàng nhấn 'Xác nhận thanh toán'.\n2. Hệ thống gọi cổng thanh toán tạo URL giao dịch.\n3. Khách hàng xác nhận trừ tiền thành công tại cổng.\n4. Cổng thanh toán gửi webhook/callback xác nhận kết quả.\n5. Hệ thống cập nhật trạng thái đơn hàng thành PAID.\n6. Hệ thống tự động phát hành vé tương ứng, sinh chuỗi Barcode và mã QR duy nhất.\n7. Hệ thống gửi email xác nhận kèm vé điện tử cho khách hàng."],
        ["Luồng sự kiện thay thế (Thất bại)", "3a. Khách hàng hủy giao dịch tại cổng -> Đơn hàng vẫn PENDING cho tới khi hết hạn.\n4a. Cổng thanh toán báo giao dịch thất bại -> Báo lỗi ERR-PAYMENT-FAILED.\n4b. Callback bị gửi trùng -> Hệ thống kiểm tra Idempotency Key, nếu đơn hàng đã PAID thì bỏ qua không tạo vé trùng."],
        ["Hậu điều kiện", "Đơn hàng chuyển thành PAID; các vé điện tử được kích hoạt ở trạng thái ACTIVE."],
        ["Quy tắc nghiệp vụ", "BUS-PAY-01: Đảm bảo Idempotency tuyệt đối; không phát hành trùng vé."],
        ["Yêu cầu phi chức năng", "NFR-SEC-02: Toàn bộ dữ liệu callback được ký số HMAC SHA256 để chống giả mạo."],
        ["Truy vết URD", "YC-05 (Thanh toán trực tuyến)"]
    ]
    add_styled_table(doc, headers_uc05, data_uc05, col_widths=[2.1, 4.3])

    # --- UC-06 ---
    add_h3(doc, "2.6.5   UC-06: Quản lý vé của tôi & Tải mã QR")
    add_p(doc, "Cho phép khách hàng truy cập kho vé cá nhân, kiểm tra trạng thái vé (ACTIVE, CHECKED_IN, CANCELLED) và hiển thị mã QR/Barcode trên màn hình để quét vào cổng.", bold_prefix="")
    add_image_block(doc, os.path.join(ASSETS_DIR, "04_my_tickets_success.png"), "Hình 2-6: Giao diện màn hình Quản lý vé của tôi & Mã QR (UC-06)", width_inches=5.8)

    # --- UC-07 ---
    add_h3(doc, "2.6.6   UC-07: Soát vé Check-in tại cổng bằng Camera/Barcode")
    headers_uc07 = ["Thuộc tính", "Nội dung đặc tả chi tiết"]
    data_uc07 = [
        ["Mã Use case", "UC-07"],
        ["Tên Use case", "Soát vé Check-in tại cổng (Check-in Scanner Station)"],
        ["Tác nhân", "Nhân viên soát vé (Check-in Staff)"],
        ["Mô tả", "Trạm kiểm soát quét mã QR hoặc mã Barcode trên vé của người tham dự, đối soát tính hợp lệ và cho phép vào cổng trong thời gian < 0.5s."],
        ["Sự kiện kích hoạt", "Nhân viên hướng camera hoặc đầu đọc laser vào mã vé của khách."],
        ["Tiền điều kiện", "Nhân viên đã đăng nhập trạm soát vé và chọn đúng sự kiện đang diễn ra."],
        ["Luồng sự kiện chính (Thành công)", "1. Đầu đọc quét được chuỗi mã vé (ví dụ: ITICK-EVT01-0001).\n2. Giao diện gửi request lên API `/api/checkin`.\n3. Hệ thống tìm kiếm bản ghi vé và kiểm tra: Trạng thái = PAID, chưa check-in, đúng event_id.\n4. Hệ thống cập nhật vé thành CHECKED_IN, lưu checked_in_at và trạm soát.\n5. Màn hình trạm chuyển sang màu xanh lá rực rỡ, phát âm thanh 'Bíp' thành công và hiển thị tên khách hàng."],
        ["Luồng sự kiện thay thế (Thất bại)", "3a. Vé đã được quét trước đó -> Báo động đỏ ERR-TKT-USED: 'Vé đã sử dụng lúc {time} tại {station}!'.\n3b. Mã vé không tồn tại -> Báo lỗi ERR-TKT-NOT-FOUND: 'Vé không hợp lệ!'.\n3c. Vé của sự kiện khác -> Báo lỗi ERR-EVENT-MISMATCH: 'Vé sai sự kiện!'."],
        ["Hậu điều kiện", "Vé được chuyển trạng thái thành CHECKED_IN, số lượng khách check-in trên Dashboard tự động tăng thêm 1."],
        ["Quy tắc nghiệp vụ", "BUS-CHK-01: Mỗi vé chỉ được phép quét thành công đúng một lần duy nhất trong toàn bộ vòng đời sự kiện."],
        ["Yêu cầu phi chức năng", "NFR-PERF-04: Thời gian phản hồi xác thực check-in bắt buộc < 0.5 giây."],
        ["Truy vết URD", "YC-07 (Soát vé Check-in tại cổng)"]
    ]
    add_styled_table(doc, headers_uc07, data_uc07, col_widths=[2.1, 4.3])

    add_image_block(doc, os.path.join(ASSETS_DIR, "05_checkin_scanner_station.png"), "Hình 2-7: Giao diện màn hình Trạm soát vé Check-in Station (UC-07)", width_inches=5.8)

    # --- UC-08 & UC-09 ---
    add_h3(doc, "2.6.7   UC-08 & UC-09: Quản lý Sự kiện & Doanh thu trích phí sàn 5%")
    add_p(doc,
        "Phân hệ dành riêng cho Ban tổ chức và Quản trị viên để theo dõi số lượng vé bán, danh sách người tham dự và báo cáo phân chia doanh thu ròng. Hệ thống tự động áp dụng công thức trích 5% phí sàn như sau:",
        bold_prefix=""
    )
    add_formula_block(
        doc,
        '''<math xmlns="http://www.w3.org/1998/Math/MathML">
          <mrow>
            <msub><mi>R</mi><mtext>net</mtext></msub>
            <mo>=</mo>
            <munderover>
              <mo>∑</mo>
              <mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow>
              <mi>N</mi>
            </munderover>
            <mrow>
              <mo>(</mo>
              <mrow>
                <msub><mi>P</mi><mi>i</mi></msub>
                <mo>×</mo>
                <mn>0.95</mn>
              </mrow>
              <mo>)</mo>
            </mrow>
          </mrow>
        </math>''',
        label="Công thức 2-2: Doanh thu thực nhận ròng của Ban tổ chức (trừ 5% phí sàn iTick)"
    )

    add_image_block(doc, os.path.join(ASSETS_DIR, "07_organizer_attendees_dashboard.png"), "Hình 2-8: Giao diện màn hình Dashboard Quản lý Sự kiện & Người tham dự (UC-08/09)", width_inches=5.8)

    # ================= MỤC 2.7: BẢNG MÃ LỖI HỆ THỐNG =================
    add_h2(doc, "2.7   Bảng mã lỗi")
    add_p(doc, "Bảng 2-12 quy định 12 mã lỗi hệ thống chuẩn hóa, đóng vai trò là chuẩn đối soát với Bảng kê lỗi Bug Manifest và kịch bản kiểm thử:", bold_prefix="")
    
    headers_err = ["Mã lỗi", "Trường hợp phát sinh", "Thông báo hiển thị cho người dùng"]
    data_err = [
        ["ERR_AUTH_FAILED", "Email hoặc mật khẩu nhập không khớp trong cơ sở dữ liệu", "Email hoặc mật khẩu không chính xác."],
        ["ERR_OUT_OF_STOCK", "Số lượng vé yêu cầu vượt quá tồn kho khả dụng của hạng vé", "Rất tiếc, số lượng vé bạn chọn hiện đã hết."],
        ["ERR_QTY_LIMIT", "Người mua đặt số lượng ngoài khoảng cho phép (1 - 5 vé)", "Số lượng vé cho mỗi đơn hàng phải từ 1 đến 5 vé."],
        ["ERR_HOLD_TIMEOUT", "Quá 10 phút (600 giây) mà khách hàng chưa hoàn tất thanh toán", "Giao dịch đã hết hạn giữ vé (10 phút). Vui lòng đặt lại vé."],
        ["ERR_VOUCHER_NOT_FOUND", "Mã giảm giá nhập vào không tồn tại", "Mã giảm giá không tồn tại trên hệ thống."],
        ["ERR_VOUCHER_EXPIRED", "Mã ưu đãi đã hết thời gian sử dụng", "Mã giảm giá đã hết hạn sử dụng."],
        ["ERR_VOUCHER_LIMIT", "Mã ưu đãi đã hết lượt dùng tối đa", "Mã giảm giá đã hết lượt sử dụng."],
        ["ERR_PAYMENT_FAILED", "Cổng thanh toán phản hồi giao dịch không thành công", "Thanh toán không thành công. Vui lòng thử lại."],
        ["ERR_TKT_NOT_FOUND", "Mã quét tại trạm check-in không tồn tại", "Vé không hợp lệ! Không tìm thấy dữ liệu vé trên hệ thống."],
        ["ERR_TKT_USED", "Vé đã được quét thành công trước đó tại cổng", "CẢNH BÁO: Vé đã được sử dụng lúc {time} tại {station}!"],
        ["ERR_EVENT_MISMATCH", "Mã vé thuộc sự kiện khác", "Vé này không thuộc sự kiện hiện tại!"],
        ["ERR_ACCESS_DENIED", "Người dùng truy cập vào trang không có quyền hạn", "Bạn không có quyền truy cập vào chức năng này."]
    ]
    add_styled_table(doc, headers_err, data_err, col_widths=[2.0, 2.3, 2.1])

    # ================= MỤC 2.8: MA TRẬN TRUY VẾT YÊU CẦU =================
    add_h2(doc, "2.8   Ma trận truy vết yêu cầu")
    add_p(doc, "Bảng 2-13 thiết lập ma trận truy vết hai chiều (Traceability Matrix) từ mã yêu cầu người dùng URD sang các mã đặc tả SRS, màn hình và gợi ý điểm kiểm thử biên/âm tính cho Sinh viên B:", bold_prefix="")
    
    headers_trace = ["Mã URD", "Mã yêu cầu SRS", "Màn hình", "Gợi ý điểm kiểm thử"]
    data_trace = [
        ["YC-01", "FR-AUTH-01, VAL-EMAIL-01", "Màn hình Đăng nhập / Đăng ký", "Kiểm tra nhập email sai định dạng, mật khẩu < 6 ký tự, SQL Injection trong ô email, đăng nhập thành công cấp JWT token."],
        ["YC-02", "FR-DISC-01, DIS-EVT-01", "Trang chủ & Danh sách sự kiện", "Kiểm tra tìm kiếm từ khóa có dấu tiếng Việt, lọc thể loại không có sự kiện, hiển thị badge trạng thái 'Đang mở bán'."],
        ["YC-03", "FR-BOOK-01, BUS-HOLD-01", "Chi tiết sự kiện & Đặt vé", "Kiểm tra đặt 0 vé, 6 vé (vượt trần 5 vé), 2 người dùng cùng đặt 1 vé cuối cùng (Race Condition), đếm ngược đúng 600 giây."],
        ["YC-04", "FR-VOUCH-01, BUS-CEIL-01", "Màn hình Thanh toán", "Kiểm tra mã hết hạn, mã hết lượt dùng, kiểm tra công thức tính trần giảm giá D_max không bao giờ vượt mức trần quy định."],
        ["YC-05", "FR-PAY-01, BUS-IDEMP-01", "Cổng thanh toán tích hợp", "Kiểm tra Idempotency khi người dùng bấm đôi nút 'Thanh toán', kiểm tra xử lý callback giả mạo chữ ký HMAC."],
        ["YC-06", "FR-MYTKT-01, DIS-QR-01", "Trang Vé của tôi", "Kiểm tra tải ảnh QR code vé về máy, kiểm tra hiển thị đúng phân hạng vé và trạng thái ACTIVE."],
        ["YC-07", "FR-CHK-01, BUS-CHK-01", "Trạm Soát vé Check-in Station", "Kiểm tra quét vé hợp lệ (< 0.5s), quét lại vé đã dùng (báo động đỏ), quét vé sai sự kiện, mất kết nối mạng trạm."],
        ["YC-08", "FR-ORG-01, VAL-PRICE-01", "Dashboard Ban tổ chức", "Kiểm tra tạo sự kiện thời gian kết thúc trước thời gian bắt đầu, giá vé âm, chỉnh sửa hạng vé khi đã có người đặt mua."],
        ["YC-09", "FR-REP-01, BUS-FEE-01", "Dashboard Báo cáo Doanh thu", "Kiểm tra tính toán chính xác 5% phí dịch vụ sàn, đối soát doanh thu thực nhận ròng của BTC với số vé bán thực tế."]
    ]
    add_styled_table(doc, headers_trace, data_trace, col_widths=[0.9, 1.8, 1.7, 2.0], num_align_cols=[0])

    # ================= MỤC 2.9: CÂU HỎI GỬI BỘ PHẬN NGHIỆP VỤ =================
    add_h2(doc, "2.9   Câu hỏi gửi bộ phận nghiệp vụ")
    add_p(doc, "Bảng 2-14 ghi nhận các câu hỏi nghiệp vụ và biên bản thống nhất giữa Chủ hệ thống và bên thụ hưởng (làm căn cứ pháp lý khi hai bên đối soát):", bold_prefix="")
    
    headers_qa = ["TT", "Câu hỏi", "Người trả lời", "Câu trả lời / ngày"]
    data_qa = [
        ["1", "Nếu sự kiện bị hủy bỏ đột xuất do thời tiết hoặc quyết định của BTC thì chính sách hoàn tiền vé và phí sàn 5% sẽ xử lý thế nào?", "Đại diện Ban tổ chức", "Hoàn trả 100% tiền vé cho khách hàng; iTick không thu 5% phí sàn đối với các sự kiện bị hủy bất khả kháng (Thống nhất: 20/10/2026)."],
        ["2", "Khi trạm soát vé Check-in tại cổng bị mất kết nối Internet tạm thời thì trạm có được phép hoạt động ở chế độ Offline Cache không?", "Kỹ sư Trưởng hệ thống", "Có. Trạm được cache cục bộ danh sách vé mã băm trong trình duyệt và đồng bộ ngược lên máy chủ ngay khi có mạng trở lại (Thống nhất: 22/10/2026)."],
        ["3", "Thời gian giữ vé 10 phút có được phép gia hạn thêm nếu khách hàng đang nhập thông tin thẻ ngân hàng tại cổng thanh toán không?", "Chuyên viên Nghiệp vụ", "Không gia hạn cứng. Sau đúng 600 giây đơn hàng tự hủy để trả vé cho người khác, bảo đảm công bằng trong giờ cao điểm (Thống nhất: 23/10/2026)."],
        ["4", "Một tài khoản khách hàng có được phép mua vé nhiều lần cho cùng một sự kiện nếu mỗi lần mua tối đa 5 vé không?", "Đại diện Khách hàng", "Được phép, nhưng tổng số vé mua trên một tài khoản không vượt quá 10 vé/sự kiện để hạn chế phe vé (Thống nhất: 24/10/2026)."],
        ["5", "Phân hạng vé VIP có bao gồm dịch vụ đính kèm (nước uống, quà tặng) cần hiển thị trên trạm soát vé không?", "Đại diện Ban tổ chức", "Có hiển thị ký hiệu 'VIP + Gift' trên màn hình trạm soát vé để nhân viên cổng phát quà kèm theo vé (Thống nhất: 25/10/2026)."],
        ["6", "Mã QR của vé có thể bị chụp ảnh gửi qua mạng xã hội, làm sao để nhân viên phát hiện vé bị lộ?", "Bộ phận Kiểm thử", "Hệ thống kiểm soát theo nguyên tắc 'First come, First served': người đến trước quét thành công thì vé bị khóa ngay lập tức (Thống nhất: 26/10/2026)."]
    ]
    add_styled_table(doc, headers_qa, data_qa, col_widths=[0.4, 2.7, 1.4, 1.9], num_align_cols=[0])

    # ================= MỤC 3: CÁC YÊU CẦU PHI CHỨC NĂNG =================
    add_h1(doc, "3   Các yêu cầu phi chức năng")
    
    add_h2(doc, "3.1   Giao diện người dùng")
    add_p(doc,
        "Giao diện người dùng của iTick phải tuân thủ nghiêm ngặt các nguyên tắc thiết kế hiện đại:",
        bold_prefix=""
    )
    add_bullet(doc, "Bảo đảm hiển thị hoàn hảo và không vỡ layout trên mọi kích thước màn hình từ 375px (Mobile) đến 1920px (Desktop Full HD).", bold_prefix="Chuẩn Responsive Web: ")
    add_bullet(doc, "Độ tương phản màu sắc đạt chuẩn WCAG 2.1 AA (tỷ lệ tương phản tối thiểu 4.5:1 đối với văn bản thông thường).", bold_prefix="Khả năng tiếp cận: ")
    add_bullet(doc, "Giao diện trạm soát vé Check-in được thiết kế tối giản, loại bỏ mọi chi tiết thừa, nút quét lớn và có phản hồi màu sắc toàn màn hình.", bold_prefix="Trải nghiệm cổng soát vé: ")

    add_h2(doc, "3.2   Hiệu năng")
    add_p(doc, "Bảng 3-1 quy định các chỉ tiêu hiệu năng bắt buộc được kiểm chứng bằng công cụ Locust hoặc Apache JMeter:", bold_prefix="")
    
    headers_perf = ["Mã chỉ tiêu", "Nội dung yêu cầu hiệu năng kiểm thử"]
    data_perf = [
        ["NFR-PERF-01", "Thời gian phản hồi (Response Time) đối với 95% số request truy vấn danh sách sự kiện < 1.0 giây."],
        ["NFR-PERF-02", "Thời gian phản hồi API tạo đơn hàng giữ chỗ và khóa kho vé < 800 mili-giây."],
        ["NFR-PERF-03", "Thời gian phản hồi API xác thực mã vé Check-in tại cổng bắt buộc < 500 mili-giây (0.5 giây)."],
        ["NFR-PERF-04", "Hệ thống đáp ứng thông lượng tối thiểu 50 requests/giây (RPS) đối với các giao dịch đọc và ghi hỗn hợp."],
        ["NFR-PERF-05", "Hệ thống chịu tải ổn định ở mức 1.000 người dùng đồng thời (CCU) trong kịch bản cao điểm mở bán vé."],
        ["NFR-PERF-06", "Mức tiêu thụ tài nguyên máy chủ: CPU không vượt quá 70%, RAM không vượt quá 1GB trong điều kiện tải cao điểm."]
    ]
    add_styled_table(doc, headers_perf, data_perf, col_widths=[1.6, 4.8], num_align_cols=[0])

    add_h2(doc, "3.3   Tính bảo mật")
    add_p(doc, "Hệ thống được thiết kế theo nguyên tắc bảo mật đa tầng (Defense in Depth):", bold_prefix="")
    add_bullet(doc, "Bắt buộc băm mật khẩu bằng thuật toán Bcrypt với hệ số độ khó (work factor) phù hợp; tuyệt đối không lưu trữ mật khẩu dạng rõ (plaintext).", bold_prefix="Mật khẩu người dùng: ")
    add_bullet(doc, "Sử dụng token JWT có chữ ký điện tử an toàn, thiết lập thời gian hết hạn (expiration) và cơ chế thu hồi token khi đăng xuất.", bold_prefix="Xác thực phiên làm việc: ")
    add_bullet(doc, "Sử dụng ORM (SQLAlchemy / Pydantic) với cơ chế tham số hóa câu truy vấn (Parameterized queries), loại bỏ 100% nguy cơ SQL Injection.", bold_prefix="Chống tấn công cơ sở dữ liệu: ")
    add_bullet(doc, "Mã hóa toàn bộ chuỗi ký tự vé QR và Barcode, chỉ máy chủ iTick mới có khóa giải mã và kiểm tra tính hợp lệ.", bold_prefix="Bảo mật vé điện tử: ")

    add_h2(doc, "3.4   Ràng buộc")
    add_p(doc, "Các ràng buộc về mặt công nghệ, hạ tầng và môi trường vận hành của dự án:", bold_prefix="")
    add_bullet(doc, "Python 3.10+, Web Framework FastAPI, kiến trúc bất đồng bộ (Asynchronous ASGI). Cơ sở dữ liệu SQLite trong môi trường Dev/Test và PostgreSQL trên Cloud.", bold_prefix="Công nghệ Backend: ")
    add_bullet(doc, "HTML5 chuẩn ngữ nghĩa, Tailwind CSS / Vanilla CSS, JavaScript ES6+, thư viện xử lý camera quét mã html5-qrcode.", bold_prefix="Công nghệ Frontend: ")
    add_bullet(doc, "Hệ thống được đóng gói container và triển khai tự động trên hạ tầng Render Cloud (Web Service chạy 24/7).", bold_prefix="Môi trường Triển khai: ")
    add_bullet(doc, "Hỗ trợ 100% các phiên bản trình duyệt hiện đại: Google Chrome 90+, Microsoft Edge 90+, Mozilla Firefox 88+, Safari 14+.", bold_prefix="Trình duyệt hỗ trợ: ")

    # Lưu tài liệu
    doc.save(OUTPUT_PATH)
    print(f"Build SRS successfully saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    build_srs_document()

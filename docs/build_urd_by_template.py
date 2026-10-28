# -*- coding: utf-8 -*-
"""
Script build_urd_by_template.py
Chuyển đổi và sinh hoàn chỉnh tài liệu URD_EventTick.docx
tuân thủ 100% mẫu chuẩn 03_URD_BIEU_MAU_TRONG (1).docx và yêu cầu kỹ thuật:
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

# Đường dẫn tài nguyên
DOCS_DIR = r"D:\SJ_Testing\Project\docs"
ASSETS_DIR = os.path.join(DOCS_DIR, "assets")
OUTPUT_PATH = os.path.join(DOCS_DIR, "URD_EventTick.docx")
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

def build_urd_document():
    doc = docx.Document()
    apply_doc_standards(doc)
    
    # ================= TRANG BÌA =================
    p_inst = doc.add_paragraph()
    set_para_format(p_inst, space_before_pt=10, space_after_pt=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_inst = p_inst.add_run(nfc("TRƯỜNG ĐẠI HỌC SƯ PHẠM KỸ THUẬT TP. HỒ CHÍ MINH\nKHOA CÔNG NGHỆ THÔNG TIN - BỘ MÔN KỸ THUẬT PHẦN MỀM"))
    set_run_font(r_inst, size_pt=13, bold=True)

    p_title = doc.add_paragraph()
    set_para_format(p_title, space_before_pt=45, space_after_pt=10, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_title = p_title.add_run(nfc("TÀI LIỆU YÊU CẦU NGƯỜI SỬ DỤNG\n(User Requirements Document – URD)"))
    set_run_font(r_title, size_pt=20, bold=True)

    p_sub = doc.add_paragraph()
    set_para_format(p_sub, space_before_pt=10, space_after_pt=25, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_sub = p_sub.add_run(nfc("NỀN TẢNG ĐĂNG KÝ VÀ BÁN VÉ SỰ KIỆN TRỰC TUYẾN (iTick Platform)\nPhân hệ: Quản lý Sự kiện, Bán vé, Thanh toán, Voucher & Soát vé Check-in"))
    set_run_font(r_sub, size_pt=15, bold=True)

    p_ver = doc.add_paragraph()
    set_para_format(p_ver, space_before_pt=10, space_after_pt=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_ver = p_ver.add_run(nfc("Phiên bản 1.2"))
    set_run_font(r_ver, size_pt=14, bold=True)

    p_meta = doc.add_paragraph()
    set_para_format(p_meta, space_before_pt=15, space_after_pt=35, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_meta = p_meta.add_run(nfc(
        f"Đơn vị chủ trì: Bộ môn Kỹ thuật Phần mềm (Học phần Đánh giá hiệu năng / Kiểm thử)\n"
        f"Người biên soạn (Chủ hệ thống): {AUTHOR_FULL}\n"
        f"Đối tượng bàn giao kiểm thử: Sinh viên B (Kiểm thử viên độc lập)\n"
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
        ("  1.1   Mục đích tài liệu", "4"),
        ("  1.2   Phạm vi và đối tượng sử dụng", "4"),
        ("  1.3   Từ điển thuật ngữ", "4"),
        ("  1.4   Ký hiệu sử dụng", "4"),
        ("  1.5   Căn cứ và tài liệu tham khảo", "4"),
        ("2   Mô tả chung về hệ thống", "5"),
        ("  2.1   Mô tả hệ thống hiện tại", "5"),
        ("  2.2   Hạn chế của hệ thống hiện tại", "5"),
        ("  2.3   Mức độ sử dụng và tăng trưởng giao dịch", "5"),
        ("  2.4   Mục tiêu của hệ thống cần xây dựng", "5"),
        ("  2.5   Khung cảnh dự án", "5"),
        ("  2.6   Ngữ cảnh hệ thống", "6"),
        ("  2.7   Hiệu quả mong đợi", "6"),
        ("3   Yêu cầu nghiệp vụ chi tiết", "7"),
        ("  3.1   Sơ đồ hoạt động nghiệp vụ tương lai", "7"),
        ("  3.2   Luồng Đặt vé & Thanh toán trực tuyến", "7"),
        ("    3.2.1   Yêu cầu thông tin (các trường dữ liệu)", "7"),
        ("    3.2.2   Trạng thái của đối tượng", "8"),
        ("    3.2.3   Mô tả các chức năng", "8"),
        ("    3.2.4   Bảng mã lỗi", "9"),
        ("  3.3   Luồng Soát vé tại cổng (Check-in Scanner Station)", "9"),
        ("    3.3.1   Yêu cầu thông tin", "9"),
        ("    3.3.2   Trạng thái soát vé", "10"),
        ("    3.3.3   Mô tả chức năng soát vé", "10"),
        ("    3.3.4   Bảng mã lỗi soát vé", "10"),
        ("  3.4   Luồng Quản lý Sự kiện & Doanh thu (Ban tổ chức)", "11"),
        ("    3.4.1   Yêu cầu thông tin sự kiện & phân hạng vé", "11"),
        ("    3.4.2   Quy tắc tài chính & Cơ chế trích phí sàn 5%", "11"),
        ("    3.4.3   Bảng mã lỗi quản lý sự kiện", "12"),
        ("4   Yêu cầu giao diện và dữ liệu", "12"),
        ("5   Yêu cầu phi chức năng", "13"),
        ("6   Bảng tổng hợp các yêu cầu chức năng", "14"),
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
    add_p(doc, "Hình 3-1: Sơ đồ hoạt động nghiệp vụ tương lai ..................................................................... Trang 7", bold_prefix="")
    
    tables_list = [
        ("Bảng 1-1: Từ điển thuật ngữ", "Trang 4"),
        ("Bảng 1-2: Các ký hiệu sử dụng trong tài liệu", "Trang 4"),
        ("Bảng 2-1: Mức độ sử dụng và tăng trưởng giao dịch", "Trang 5"),
        ("Bảng 2-2: Khung cảnh dự án", "Trang 5"),
        ("Bảng 2-3: Ngữ cảnh hệ thống — các hệ thống liên quan", "Trang 6"),
        ("Bảng 3-1: Yêu cầu thông tin của luồng Đặt vé & Thanh toán", "Trang 7"),
        ("Bảng 3-2: Các trạng thái của đơn hàng và vé", "Trang 8"),
        ("Bảng 3-3: Bảng mã lỗi của luồng Đặt vé & Thanh toán", "Trang 9"),
        ("Bảng 3-4: Yêu cầu thông tin của luồng Soát vé tại cổng", "Trang 9"),
        ("Bảng 3-5: Trạng thái và phản hồi tại trạm Soát vé", "Trang 10"),
        ("Bảng 3-6: Bảng mã lỗi của trạm Soát vé Check-in", "Trang 10"),
        ("Bảng 3-7: Yêu cầu thông tin luồng Quản lý Sự kiện", "Trang 11"),
        ("Bảng 3-8: Bảng mã lỗi luồng Quản lý Sự kiện", "Trang 12"),
        ("Bảng 5-1: Các yêu cầu phi chức năng", "Trang 13"),
        ("Bảng 6-1: Bảng tổng hợp các yêu cầu chức năng", "Trang 14"),
    ]
    for tbl_name, tbl_pg in tables_list:
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
    
    add_h2(doc, "1.1   Mục đích tài liệu")
    add_p(doc, 
        "Tài liệu Yêu cầu Người sử dụng (User Requirements Document – URD) này xác định và hệ thống hóa toàn diện các yêu cầu nghiệp vụ, luồng hoạt động chức năng, các quy tắc vận hành và chỉ tiêu chất lượng cho Nền tảng Đăng ký và Bán vé Sự kiện Trực tuyến (iTick Platform). Tài liệu đóng vai trò là căn cứ pháp lý và kỹ thuật ràng buộc giữa Chủ hệ thống (Sinh viên A – Lại Thị Thanh Xuân) và Bộ phận Kiểm thử độc lập (Sinh viên B – Tester) nhằm:",
        bold_prefix=""
    )
    add_bullet(doc, "Làm cơ sở để xây dựng Tài liệu Đặc tả Yêu cầu Phần mềm (SRS_EventTick.docx) ở mức kỹ thuật chi tiết.", bold_prefix="Căn cứ thiết kế:")
    add_bullet(doc, "Làm chuẩn mực đối chiếu để lập Kế hoạch Kiểm thử (Test Plan), Bảng thiết kế Kịch bản kiểm thử (Test Cases) và Bảng kê lỗi (Bug Manifest).", bold_prefix="Căn cứ kiểm thử:")
    add_bullet(doc, "Xác lập tiêu chí đánh giá hiệu năng (chịu tải, thông lượng, độ trễ) và tiêu chuẩn nghiệm thu bàn giao sản phẩm trước hội đồng học phần.", bold_prefix="Căn cứ nghiệm thu:")

    add_h2(doc, "1.2   Phạm vi và đối tượng sử dụng")
    add_p(doc,
        "Phạm vi tài liệu bao phủ trọn vẹn vòng đời nghiệp vụ của hệ thống iTick, bao gồm: Quản lý danh mục sự kiện & phân hạng vé; Quy trình đăng ký, giữ chỗ tạm thời (Hold timer) và thanh toán trực tuyến; Áp dụng mã giảm giá (Voucher) có trần chiết khấu; Trạm soát vé điện tử (Check-in Scanner Station) tại cổng sự kiện bằng mã QR/Barcode; và Dashboard quản trị, báo cáo tài chính trích phí sàn 5% dành cho Ban tổ chức (Organizer) và Quản trị viên (Admin).",
        bold_prefix=""
    )
    add_p(doc, "Đối tượng sử dụng tài liệu bao gồm:", bold_prefix="")
    add_bullet(doc, "Tìm kiếm sự kiện, chọn vé, thanh toán vé và tải vé điện tử cá nhân.", bold_prefix="Khách hàng (Customer / Attendee): ")
    add_bullet(doc, "Tạo sự kiện, phát hành hạng vé, cài đặt mã giảm giá và theo dõi doanh thu thực nhận.", bold_prefix="Ban tổ chức (Organizer): ")
    add_bullet(doc, "Vận hành thiết bị quét mã QR/Barcode tại cổng ra vào để xác thực vé vào cổng tức thì.", bold_prefix="Nhân viên Soát vé (Check-in Staff): ")
    add_bullet(doc, "Giám sát toàn bộ hệ thống, kiểm duyệt sự kiện và quản trị danh mục dữ liệu tập trung.", bold_prefix="Quản trị viên hệ thống (Administrator): ")
    add_bullet(doc, "Sinh viên B – Kiểm thử viên độc lập sử dụng tài liệu để phát hiện lỗi, đánh giá sai lệch giữa tài liệu và mã nguồn thực tế.", bold_prefix="Đội ngũ Kiểm thử (Tester): ")

    add_h2(doc, "1.3   Từ điển thuật ngữ")
    add_p(doc, "Các thuật ngữ cốt lõi sử dụng trong tài liệu được định nghĩa thống nhất tại Bảng 1-1 nhằm tránh mọi hiểu lầm trong quá trình phát triển và kiểm thử:", bold_prefix="")
    
    headers_1_1 = ["Thuật ngữ", "Giải thích"]
    data_1_1 = [
        ["iTick Platform", "Nền tảng trực tuyến phục vụ quản lý sự kiện, phân phối vé điện tử và kiểm soát cổng vào."],
        ["Ticket / Vé điện tử", "Chứng từ xác nhận quyền tham dự sự kiện dưới dạng mã vạch số (QR Code và Barcode 1D)."],
        ["Ticket Type / Hạng vé", "Phân khúc vé trong một sự kiện (ví dụ: Early Bird, Vé Tiêu chuẩn Regular, Vé VIP)."],
        ["Hold Timer / Khóa giữ chỗ", "Cơ chế tạm giữ vé tồn kho trong 10 phút kể từ lúc tạo đơn hàng để chờ thanh toán, chống bán vượt."],
        ["Platform Fee / Phí sàn", "Khoản phí dịch vụ 5% tính trên tổng giá trị vé bán ra mà iTick trích lại từ doanh thu của Ban tổ chức."],
        ["Check-in Station", "Trạm làm việc tại cổng kiểm soát thực tế, sử dụng camera hoặc đầu đọc laser để xác thực vé."],
        ["Voucher Ceiling / Trần giảm giá", "Mức giảm giá tối đa bằng tiền mặt được áp dụng cho một mã giảm giá tính theo tỷ lệ phần trăm."],
        ["Idempotency / Tính bất biến", "Đặc tính kỹ thuật đảm bảo khi người dùng gửi trùng một yêu cầu thanh toán/hủy vé thì kết quả không bị lặp lại."]
    ]
    add_styled_table(doc, headers_1_1, data_1_1, col_widths=[2.0, 4.4])

    add_h2(doc, "1.4   Ký hiệu sử dụng")
    add_p(doc, "Các quy ước ký hiệu về thuộc tính trường dữ liệu được chuẩn hóa trong Bảng 1-2:", bold_prefix="")
    headers_1_2 = ["Ký hiệu", "Ý nghĩa"]
    data_1_2 = [
        ["M", "Mandatory — Trường dữ liệu bắt buộc phải nhập; hệ thống sẽ từ chối nếu để trống."],
        ["O", "Optional — Trường dữ liệu tùy chọn; người dùng có thể nhập hoặc bỏ qua."],
        ["C", "Conditional — Bắt buộc nhập khi thỏa mãn điều kiện logic kinh doanh cụ thể được ghi chú."],
        ["R", "Read-only — Trường dữ liệu do hệ thống tự sinh và hiển thị; người dùng không thể tự ý sửa đổi."]
    ]
    add_styled_table(doc, headers_1_2, data_1_2, col_widths=[1.5, 4.9], num_align_cols=[0])

    add_h2(doc, "1.5   Căn cứ và tài liệu tham khảo")
    add_p(doc, "Tài liệu này được biên soạn dựa trên các cơ sở thực tế và tài liệu dự án sau:", bold_prefix="")
    add_bullet(doc, "Đề cương chi tiết học phần Đánh giá hiệu năng và Kiểm thử phần mềm, Khoa CNTT - HCMUTE.", bold_prefix="Cơ sở môn học: ")
    add_bullet(doc, f"Mã nguồn Backend (FastAPI Python) và Frontend Web Client tại GitHub: {GITHUB_LINK}", bold_prefix="Mã nguồn dự án: ")
    add_bullet(doc, f"Môi trường Cloud hoạt động 24/7 tại: {DEPLOY_LINK} (Localhost: http://127.0.0.1:8001).", bold_prefix="Triển khai thực tế: ")
    add_bullet(doc, f"Toàn bộ tài liệu phân tích, biên bản và dữ liệu kiểm thử lưu trữ tại Google Drive: {DRIVE_LINK}", bold_prefix="Kho tài liệu số: ")
    add_bullet(doc, "Tài liệu Đặc tả API (Mau_01_Tai_lieu_API.docx) và Bảng phân loại 45 lỗi (Bug_Manifest.xlsx).", bold_prefix="Tài liệu liên quan: ")

    # ================= MỤC 2: MÔ TẢ CHUNG VỀ HỆ THỐNG =================
    add_h1(doc, "2   Mô tả chung về hệ thống")
    
    add_h2(doc, "2.1   Mô tả hệ thống hiện tại")
    add_p(doc,
        "Hiện nay, công tác bán vé và quản lý người tham dự tại phần lớn các sự kiện quy mô vừa và nhỏ (hội thảo học thuật, workshop kỹ năng, đêm nhạc sinh viên) vẫn phụ thuộc chủ yếu vào các công cụ thủ công hoặc chắp vá: Ban tổ chức thu thập thông tin qua Google Forms, hướng dẫn người tham dự chuyển khoản ngân hàng rồi đối soát từng giao dịch trên bảng tính Google Sheets. Khi đến ngày diễn ra sự kiện, tình nguyện viên tại cổng in danh sách giấy hoặc dùng file Excel trên laptop để gạch tên từng người tham dự.",
        bold_prefix=""
    )

    add_h2(doc, "2.2   Hạn chế của hệ thống hiện tại")
    add_p(doc, "Phương thức vận hành thủ công hiện tại bộc lộ nhiều hạn chế nghiêm trọng có thể đo lường được:", bold_prefix="")
    add_bullet(doc, "Tỷ lệ sai sót khi đối soát nội dung chuyển khoản thủ công lên tới 12% - 15%, dễ gây tranh chấp và mất vé của khách.", bold_prefix="Sai sót thanh toán: ")
    add_bullet(doc, "Thời gian tìm tên và đối chiếu thủ công tại cổng mất từ 45 đến 90 giây cho mỗi lượt khách, dẫn đến ùn tắc kéo dài tại cửa vào.", bold_prefix="Ùn tắc cổng soát vé: ")
    add_bullet(doc, "Không có cơ chế ngăn chặn gian lận vé quay vòng (khách chia sẻ chụp màn hình mã vé cho nhiều người cùng vào cổng).", bold_prefix="Lỗ hổng gian lận vé: ")
    add_bullet(doc, "Thiếu cơ chế khóa giữ vé thời gian thực (Reservation Lock), dẫn đến tình trạng bán vượt số lượng vé thực tế (Overselling).", bold_prefix="Bán vượt số lượng: ")
    add_bullet(doc, "Ban tổ chức hoàn toàn không có số liệu tức thời về số người đã check-in hay doanh thu thực tế để đưa ra quyết định điều phối.", bold_prefix="Mù thông tin thời gian thực: ")

    add_h2(doc, "2.3   Mức độ sử dụng và tăng trưởng giao dịch")
    add_p(doc, "Bảng 2-1 tổng hợp các chỉ số giao dịch hiện tại và dự kiến tăng trưởng, đóng vai trò là tham số đầu vào trực tiếp để thiết kế kịch bản kiểm thử hiệu năng (Stress test & Spike test):", bold_prefix="")
    
    headers_2_1 = ["Chỉ số", "Giá trị định lượng nghiệp vụ"]
    data_2_1 = [
        ["Số giao dịch hiện tại", "500 - 1.500 giao dịch đặt vé mỗi tháng cho các sự kiện thử nghiệm."],
        ["Tăng trưởng dự kiến", "Tăng trưởng 200% mỗi quý khi mở rộng phục vụ toàn bộ các câu lạc bộ và khoa viện."],
        ["Cao điểm (Peak load)", "10.000 lượt truy cập/giờ trong 15 phút đầu mở bán vé Flash Sale/VIP; tốc độ đặt vé đạt 120 đơn/phút. Tốc độ check-in tại cổng đạt 30 vé/phút/cổng."],
        ["Số người dùng đồng thời tối đa (CCU)", "1.000 người dùng đồng thời truy cập xem sự kiện và thanh toán tại thời điểm cao điểm mở bán."]
    ]
    add_styled_table(doc, headers_2_1, data_2_1, col_widths=[2.5, 3.9])

    add_h2(doc, "2.4   Mục tiêu của hệ thống cần xây dựng")
    add_p(doc, "Hệ thống iTick được xây dựng nhằm đạt được 4 mục tiêu trọng tâm sau:", bold_prefix="")
    add_bullet(doc, "Tự động hóa 100% quy trình chọn vé, áp mã giảm giá, tính toán phí sàn và xử lý thanh toán trực tuyến bảo đảm không bán vượt vé.", bold_prefix="1. Tự động hóa bán vé: ")
    add_bullet(doc, "Cung cấp trạm soát vé điện tử (Check-in Scanner Station) có khả năng đọc mã QR/Barcode và phản hồi kết quả < 0.5 giây.", bold_prefix="2. Kiểm soát vé thông minh: ")
    add_bullet(doc, "Bảo đảm tính minh bạch tài chính bằng việc tự động trích 5% phí dịch vụ sàn và cung cấp báo cáo doanh thu trực quan cho Ban tổ chức.", bold_prefix="3. Minh bạch tài chính: ")
    add_bullet(doc, "Hệ thống vận hành ổn định, sẵn sàng chịu tải 1.000 CCU và đạt độ tin cậy cao trên nền tảng điện toán đám mây.", bold_prefix="4. Sẵn sàng chịu tải cao: ")

    add_h2(doc, "2.5   Khung cảnh dự án")
    add_p(doc, "Lộ trình triển khai dự án được phân chia thành 4 giai đoạn cụ thể tại Bảng 2-2:", bold_prefix="")
    headers_2_2 = ["Giai đoạn", "Thời gian", "Nội dung chính"]
    data_2_2 = [
        ["Giai đoạn 1: Khảo sát & Đặc tả", "01/09/2026 – 20/09/2026", "Khảo sát thực tế, thiết lập tài liệu URD, SRS, thiết kế kiến trúc cơ sở dữ liệu và giao diện mẫu."],
        ["Giai đoạn 2: Phát triển & Tích hợp", "21/09/2026 – 15/10/2026", "Lập trình Backend FastAPI, tích hợp cổng thanh toán giả lập, hoàn thiện giao diện Web và trạm quét Check-in."],
        ["Giai đoạn 3: Kiểm thử & Đánh giá tải", "16/10/2026 – 25/10/2026", "Thực hiện kiểm thử chức năng, đối soát bảng 45 lỗi Bug Manifest, kiểm thử tải Locust/JMeter và tối ưu hóa hệ thống."],
        ["Giai đoạn 4: Đóng gói & Bàn giao", "26/10/2026 – 31/10/2026", "Triển khai lên Cloud Render, hoàn tất hồ sơ bàn giao kiểm thử (Bien_ban_ban_giao.docx) và báo cáo nghiệm thu."]
    ]
    add_styled_table(doc, headers_2_2, data_2_2, col_widths=[1.8, 1.6, 3.0])

    add_h2(doc, "2.6   Ngữ cảnh hệ thống")
    add_p(doc, "Ngữ cảnh kết nối giữa iTick và các hệ thống phụ trợ liên quan được mô tả tại Bảng 2-3 (mỗi kết nối là một đối tượng của kiểm thử tích hợp):", bold_prefix="")
    headers_2_3 = ["Hệ thống liên quan", "Chiều kết nối", "Nội dung trao đổi"]
    data_2_3 = [
        ["Cổng thanh toán trực tuyến (VNPay / Mock Gateway)", "Hai chiều (Bi-directional)", "iTick gửi yêu cầu tạo giao dịch thanh toán kèm OrderId và số tiền; Cổng thanh toán trả về trạng thái giao dịch (thành công/thất bại)."],
        ["Hệ thống Gửi Mail thông báo (SMTP / SendGrid)", "Một chiều (Outgoing)", "iTick gửi thông tin xác nhận đặt vé, biên lai thanh toán và đính kèm file ảnh mã QR vé đến email khách hàng."],
        ["Thiết bị Quét mã vạch (Barcode / 2D Scanner)", "Một chiều (Incoming)", "Trạm Check-in tiếp nhận chuỗi ký tự mã vé đọc được từ máy quét laser hoặc camera điện thoại."],
        ["Dịch vụ Lưu trữ Tĩnh (CDN / Cloud Storage)", "Hai chiều (Bi-directional)", "Lưu trữ và phân phối hình ảnh poster sự kiện, ảnh đại diện và các tệp mã nguồn giao diện người dùng."]
    ]
    add_styled_table(doc, headers_2_3, data_2_3, col_widths=[2.1, 1.5, 2.8])

    add_h2(doc, "2.7   Hiệu quả mong đợi")
    add_p(doc, "Khi đưa vào vận hành, hệ thống iTick cam kết mang lại các hiệu quả định lượng rõ rệt:", bold_prefix="")
    add_bullet(doc, "Giảm 95% thời gian xử lý check-in tại cổng (từ 60 giây xuống dưới 0.5 giây cho mỗi lượt khách).", bold_prefix="Tối ưu cổng vào: ")
    add_bullet(doc, "Triệt tiêu 100% tình trạng bán vượt vé (overselling) nhờ cơ chế khóa vé tạm thời 10 phút.", bold_prefix="Loại trừ sai sót: ")
    add_bullet(doc, "Tiết kiệm 80% nhân sự trực cổng soát vé và loại bỏ hoàn toàn chi phí in ấn vé giấy truyền thống.", bold_prefix="Tiết kiệm chi phí: ")
    add_bullet(doc, "Bảo đảm tính chính xác tuyệt đối trong phân chia tài chính nhờ cơ chế tự động trích 5% phí sàn.", bold_prefix="Minh bạch tài chính: ")

    # ================= MỤC 3: YÊU CẦU NGHIỆP VỤ CHI TIẾT =================
    add_h1(doc, "3   Yêu cầu nghiệp vụ chi tiết")
    
    add_h2(doc, "3.1   Sơ đồ hoạt động nghiệp vụ tương lai")
    add_p(doc,
        "Sơ đồ Hình 3-1 thể hiện tổng quan luồng hoạt động nghiệp vụ tương lai của hệ thống iTick: từ lúc Ban tổ chức tạo sự kiện, người mua chọn vé & thanh toán trực tuyến, hệ thống cấp phát vé QR, đến bước nhân viên quét mã kiểm soát tại cổng sự kiện:",
        bold_prefix=""
    )
    add_image_block(doc, os.path.join(ASSETS_DIR, "diagram_future_process.png"), "Hình 3-1: Sơ đồ hoạt động nghiệp vụ tương lai của hệ thống iTick", width_inches=6.2)

    # 3.2 Luồng Đặt vé & Thanh toán
    add_h2(doc, "3.2   Luồng Đặt vé & Thanh toán trực tuyến")
    add_p(doc, "Luồng nghiệp vụ cho phép khách hàng tìm kiếm sự kiện, chọn phân hạng vé, nhập thông tin liên lạc, áp dụng mã ưu đãi và thanh toán trực tuyến an toàn.", bold_prefix="")
    
    add_h3(doc, "3.2.1   Yêu cầu thông tin (các trường dữ liệu)")
    add_p(doc, "Bảng 3-1 quy định chi tiết các trường dữ liệu của đơn hàng đặt vé (mỗi quy tắc là căn cứ sinh ra ít nhất 3 kịch bản kiểm thử: hợp lệ, giá trị biên, và không hợp lệ):", bold_prefix="")
    
    headers_3_1 = ["TT", "Tên trường (VIE)", "Tên trường (ENG)", "Định dạng", "Bắt buộc", "Ghi chú / quy tắc kiểm tra"]
    data_3_1 = [
        ["1", "Mã đơn hàng", "order_id", "Chuỗi ký tự", "M", "Tự sinh, định dạng UUID hoặc chuỗi ngẫu nhiên duy nhất."],
        ["2", "Mã sự kiện", "event_id", "Số nguyên", "M", "ID sự kiện hợp lệ và đang mở bán trong hệ thống."],
        ["3", "Hạng vé", "ticket_type_id", "Số nguyên", "M", "ID hạng vé được chọn, còn số lượng tồn kho > 0."],
        ["4", "Số lượng vé", "quantity", "Số nguyên", "M", "Tối thiểu 1 vé, tối đa 5 vé trên một giao dịch."],
        ["5", "Họ tên người mua", "customer_name", "Chuỗi ký tự", "M", "Độ dài từ 2 đến 100 ký tự; không chứa mã HTML/Script độc hại."],
        ["6", "Email nhận vé", "customer_email", "Email", "M", "Đúng định dạng chuẩn RFC 5322; dùng để gửi mã vé điện tử."],
        ["7", "Số điện thoại", "customer_phone", "Chuỗi ký tự", "M", "Số điện thoại Việt Nam (10 chữ số, bắt đầu bằng 03, 05, 07, 08, 09)."],
        ["8", "Mã giảm giá", "voucher_code", "Chuỗi ký tự", "O", "Tối đa 20 ký tự in hoa; phải còn hạn sử dụng và còn lượt dùng."]
    ]
    add_styled_table(doc, headers_3_1, data_3_1, col_widths=[0.4, 1.4, 1.3, 0.9, 0.7, 1.7], num_align_cols=[0, 4])

    add_h3(doc, "3.2.2   Trạng thái của đối tượng")
    add_p(doc, "Vòng đời trạng thái của đơn hàng và vé được quy định tại Bảng 3-2:", bold_prefix="")
    headers_3_2 = ["Trạng thái", "Mô tả và điều kiện chuyển trạng thái"]
    data_3_2 = [
        ["PENDING (Chờ thanh toán)", "Đơn hàng vừa khởi tạo thành công; hệ thống tạm giữ vé trong kho trong đúng 10 phút. Nếu quá 10 phút chưa thanh toán, tự động chuyển sang CANCELLED."],
        ["CONFIRMED / PAID (Đã thanh toán)", "Cổng thanh toán phản hồi giao dịch thành công; hệ thống cấp mã QR/Barcode duy nhất cho từng vé và chuyển trạng thái vé thành ACTIVE."],
        ["CANCELLED (Đã hủy)", "Đơn hàng bị hủy do hết thời gian giữ chỗ 10 phút hoặc do người mua chủ động hủy; số lượng vé được hoàn trả lại kho bán."],
        ["CHECKED_IN (Đã soát vé)", "Vé đã được quét hợp lệ tại trạm kiểm soát cổng; không thể sử dụng lại để vào cổng lần thứ hai."],
        ["REFUNDED (Đã hoàn tiền)", "Ban tổ chức hoặc Quản trị viên thực hiện hoàn tiền theo quy định hủy vé; vé bị vô hiệu hóa lập tức."]
    ]
    add_styled_table(doc, headers_3_2, data_3_2, col_widths=[2.1, 4.3])

    add_h3(doc, "3.2.3   Mô tả các chức năng")
    add_p(doc, "Chức năng 1: Chọn vé & Khóa giữ chỗ tạm thời (Hold Reservation)", bold_prefix="")
    add_bullet(doc, "Cho phép khách hàng lựa chọn loại vé và số lượng mong muốn trên giao diện chi tiết sự kiện.", bold_prefix="Mô tả: ")
    add_bullet(doc, "Khách hàng chọn hạng vé -> Chọn số lượng (1 - 5) -> Nhấn 'Tiến hành đặt vé' -> Hệ thống kiểm tra số lượng tồn kho khả dụng -> Nếu đủ, tạo đơn hàng trạng thái PENDING, tạm trừ tồn kho và kích hoạt bộ đếm ngược 10 phút (600 giây) trên màn hình.", bold_prefix="Luồng xử lý: ")
    add_bullet(doc, "Số lượng vé mua trên 1 đơn hàng không vượt quá 5 vé. Nếu sau 600 giây khách hàng không hoàn tất thanh toán, hệ thống tự động hủy đơn và hoàn trả vé vào kho tồn.", bold_prefix="Quy tắc nghiệp vụ: ")

    add_p(doc, "Chức năng 2: Áp dụng Mã giảm giá (Voucher Discount)", bold_prefix="")
    add_bullet(doc, "Cho phép khách hàng nhập mã ưu đãi để được chiết khấu trực tiếp vào tổng tiền đơn hàng.", bold_prefix="Mô tả: ")
    add_bullet(doc, "Khách hàng nhập mã voucher -> Nhấn 'Áp dụng' -> Hệ thống gọi API kiểm tra: mã có tồn tại, còn trong khoảng thời gian hiệu lực, chưa vượt quá số lượt dùng tối đa, và tổng tiền đạt giá trị tối thiểu -> Tính toán mức giảm giá và cập nhật lại số tiền phải thanh toán.", bold_prefix="Luồng xử lý: ")
    add_bullet(doc, "Mức giảm giá theo tỷ lệ phần trăm bắt buộc phải áp dụng mức trần giảm giá tối đa (Voucher Ceiling). Công thức tính toán được bảo đảm chuẩn xác theo công thức toán học dưới đây:", bold_prefix="Quy tắc nghiệp vụ: ")

    # Chèn công thức OMML cho Voucher
    add_formula_block(
        doc,
        '''<math xmlns="http://www.w3.org/1998/Math/MathML">
          <mrow>
            <msub><mi>D</mi><mtext>voucher</mtext></msub>
            <mo>=</mo>
            <mo>min</mo>
            <mrow>
              <mo>(</mo>
              <mrow>
                <msub><mi>P</mi><mtext>subtotal</mtext></msub>
                <mo>×</mo>
                <msub><mi>r</mi><mtext>pct</mtext></msub>
              </mrow>
              <mo>,</mo>
              <msub><mi>D</mi><mtext>max</mtext></msub>
              <mo>)</mo>
            </mrow>
          </mrow>
        </math>''',
        label="Công thức 3-1: Mức giảm giá Voucher có trần"
    )

    add_p(doc, "Chức năng 3: Xử lý Thanh toán trực tuyến & Phát hành vé", bold_prefix="")
    add_bullet(doc, "Xử lý giao dịch thanh toán thông qua cổng thanh toán tích hợp và phát hành vé điện tử tức thì.", bold_prefix="Mô tả: ")
    add_bullet(doc, "Khách hàng chọn phương thức thanh toán (VNPay / Thẻ ngân hàng / QR Mock) -> Nhấn 'Xác nhận thanh toán' -> Hệ thống chuyển hướng sang cổng thanh toán -> Cổng thanh toán trả về kết quả -> Hệ thống xác thực tính hợp lệ -> Cập nhật đơn hàng thành PAID, kích hoạt vé và gửi thông báo email.", bold_prefix="Luồng xử lý: ")
    add_bullet(doc, "Bảo đảm tính bất biến (Idempotency): mỗi giao dịch chỉ xử lý trừ tiền và phát hành vé một lần duy nhất. Mỗi vé được gán một chuỗi mã Barcode và mã QR duy nhất toàn hệ thống.", bold_prefix="Quy tắc nghiệp vụ: ")

    add_h3(doc, "3.2.4   Bảng mã lỗi")
    add_p(doc, "Bảng 3-3 quy định các mã lỗi chuẩn của luồng Đặt vé & Thanh toán:", bold_prefix="")
    headers_3_3 = ["TT", "Mã lỗi", "Trường hợp phát sinh", "Thông báo hiển thị cho người dùng"]
    data_3_3 = [
        ["1", "ERR_OUT_OF_STOCK", "Số lượng vé yêu cầu vượt quá số lượng vé tồn kho khả dụng", "Rất tiếc, số lượng vé bạn chọn hiện đã hết hoặc không đủ."],
        ["2", "ERR_VOUCHER_EXPIRED", "Mã giảm giá đã quá thời hạn sử dụng quy định", "Mã giảm giá đã hết hạn sử dụng. Vui lòng kiểm tra lại."],
        ["3", "ERR_VOUCHER_LIMIT", "Mã giảm giá đã đạt giới hạn số lượt sử dụng tối đa", "Mã giảm giá đã hết lượt sử dụng."],
        ["4", "ERR_INVALID_EMAIL", "Người mua nhập sai định dạng email", "Địa chỉ email không hợp lệ. Vui lòng nhập đúng định dạng."],
        ["5", "ERR_INVALID_PHONE", "Số điện thoại không đúng quy chuẩn Việt Nam", "Số điện thoại không hợp lệ. Vui lòng nhập 10 chữ số."],
        ["6", "ERR_PAYMENT_TIMEOUT", "Quá 10 phút giữ chỗ mà khách hàng chưa hoàn tất thanh toán", "Giao dịch đã hết hạn giữ vé (10 phút). Vui lòng đặt lại vé mới."],
        ["7", "ERR_PAYMENT_FAILED", "Cổng thanh toán báo trừ tiền không thành công", "Thanh toán thất bại hoặc bị hủy bởi người dùng."]
    ]
    add_styled_table(doc, headers_3_3, data_3_3, col_widths=[0.4, 1.8, 2.2, 2.0], num_align_cols=[0])

    # 3.3 Luồng Soát vé tại cổng
    add_h2(doc, "3.3   Luồng Soát vé tại cổng (Check-in Scanner Station)")
    add_p(doc, "Luồng nghiệp vụ phục vụ nhân viên trực cổng sử dụng máy quét mã vạch hoặc camera để xác thực quyền vào cổng của người tham dự trong thời gian thực.", bold_prefix="")

    add_h3(doc, "3.3.1   Yêu cầu thông tin")
    add_p(doc, "Bảng 3-4 định nghĩa các trường dữ liệu xử lý tại trạm soát vé:", bold_prefix="")
    headers_3_4 = ["TT", "Tên trường (VIE)", "Tên trường (ENG)", "Định dạng", "Bắt buộc", "Ghi chú / quy tắc kiểm tra"]
    data_3_4 = [
        ["1", "Mã vé (Barcode/QR)", "ticket_code", "Chuỗi ký tự", "M", "Chuỗi định danh duy nhất của vé (ví dụ: ITICK-EVT01-0001)."],
        ["2", "Mã sự kiện", "event_id", "Số nguyên", "M", "Khóa ngoại liên kết tới sự kiện đang mở cổng soát vé."],
        ["3", "Thời gian soát", "checked_in_at", "Ngày giờ", "R", "Thời gian máy chủ ghi nhận tại thời điểm quét mã thành công."],
        ["4", "Mã trạm kiểm soát", "station_id", "Chuỗi ký tự", "M", "Mã định danh cổng (ví dụ: GATE_A_01, GATE_B_02)."],
        ["5", "Nhân viên trực cổng", "staff_name", "Chuỗi ký tự", "M", "Tên tài khoản hoặc họ tên nhân viên vận hành trạm."]
    ]
    add_styled_table(doc, headers_3_4, data_3_4, col_widths=[0.4, 1.6, 1.3, 0.9, 0.7, 1.5], num_align_cols=[0, 4])

    add_h3(doc, "3.3.2   Trạng thái soát vé")
    add_p(doc, "Bảng 3-5 quy định các trạng thái phản hồi tại trạm soát vé cổng:", bold_prefix="")
    headers_3_5 = ["Trạng thái phản hồi", "Mô tả và quy định xử lý"]
    data_3_5 = [
        ["HỢP LỆ (VALID / SUCCESS)", "Vé hợp lệ, thuộc sự kiện hiện tại và chưa từng qua cổng. Màn hình trạm chuyển xanh lá, phát tín hiệu âm thanh thành công và mở cổng."],
        ["VÉ ĐÃ SỬ DỤNG (ALREADY_CHECKED_IN)", "Vé đã được quét thành công trước đó. Màn hình cảnh báo đỏ, hiển thị chính xác thời gian và cổng đã quét trước đó để chống gian lận."],
        ["SAI SỰ KIỆN (EVENT_MISMATCH)", "Vé hợp lệ nhưng thuộc sự kiện khác, không được phép vào cổng sự kiện này."],
        ["VÉ KHÔNG HỢP LỆ (INVALID / NOT_FOUND)", "Mã quét không tồn tại trên hệ thống dữ liệu iTick; từ chối vào cổng."]
    ]
    add_styled_table(doc, headers_3_5, data_3_5, col_widths=[2.4, 4.0])

    add_h3(doc, "3.3.3   Mô tả chức năng soát vé")
    add_p(doc, "Chức năng: Quét mã QR/Barcode và Xác thực cổng tức thì", bold_prefix="")
    add_bullet(doc, "Xác thực tính hợp lệ của vé và ghi nhận lịch sử vào cổng trong thời gian dưới 0.5 giây.", bold_prefix="Mô tả: ")
    add_bullet(doc, "Nhân viên hướng đầu đọc vào mã QR/Barcode trên vé -> Thiết bị gửi chuỗi mã lên API `/api/checkin` -> Hệ thống truy vấn bản ghi vé -> Kiểm tra: Trạng thái có phải là PAID không? Đã check-in chưa? Có đúng sự kiện không? -> Cập nhật trạng thái thành CHECKED_IN và ghi nhận thời gian, nhân viên soát -> Phản hồi kết quả về màn hình trạm.", bold_prefix="Luồng xử lý: ")
    add_bullet(doc, "Mỗi mã vé chỉ được check-in thành công đúng 1 lần duy nhất trong toàn bộ thời gian diễn ra sự kiện. Giao diện trạm phải phản hồi màu sắc trực quan (Xanh lá / Đỏ) và chuông âm thanh để nhân viên không cần nhìn bàn phím.", bold_prefix="Quy tắc nghiệp vụ: ")

    add_h3(doc, "3.3.4   Bảng mã lỗi soát vé")
    add_p(doc, "Bảng 3-6 quy định bảng mã lỗi tại trạm soát vé:", bold_prefix="")
    headers_3_6 = ["TT", "Mã lỗi", "Trường hợp phát sinh", "Thông báo hiển thị cho người dùng"]
    data_3_6 = [
        ["1", "ERR_TKT_NOT_FOUND", "Mã quét không tồn tại trong cơ sở dữ liệu vé", "Vé không hợp lệ! Không tìm thấy dữ liệu vé trên hệ thống."],
        ["2", "ERR_TKT_USED", "Vé đã được quét vào cổng trước đó", "CẢNH BÁO: Vé đã được sử dụng lúc {time} tại {station}!"],
        ["3", "ERR_EVENT_MISMATCH", "Vé thuộc sự kiện khác", "Vé này không thuộc sự kiện đang diễn ra tại cổng này!"],
        ["4", "ERR_TKT_NOT_PAID", "Vé chưa hoàn tất thanh toán (trạng thái PENDING)", "Vé chưa được thanh toán. Không có giá trị vào cổng."]
    ]
    add_styled_table(doc, headers_3_6, data_3_6, col_widths=[0.4, 1.8, 2.2, 2.0], num_align_cols=[0])

    # 3.4 Luồng Quản lý Sự kiện & Doanh thu
    add_h2(doc, "3.4   Luồng Quản lý Sự kiện & Doanh thu (Ban tổ chức)")
    add_p(doc, "Luồng nghiệp vụ dành cho Ban tổ chức khởi tạo sự kiện, thiết lập phân hạng vé, mở bán và theo dõi doanh thu thực tế được tự động tính toán minh bạch.", bold_prefix="")

    add_h3(doc, "3.4.1   Yêu cầu thông tin sự kiện & phân hạng vé")
    add_p(doc, "Bảng 3-7 quy định thông tin khởi tạo sự kiện và phân hạng vé:", bold_prefix="")
    headers_3_7 = ["TT", "Tên trường (VIE)", "Tên trường (ENG)", "Định dạng", "Bắt buộc", "Ghi chú / quy tắc kiểm tra"]
    data_3_7 = [
        ["1", "Tên sự kiện", "title", "Chuỗi ký tự", "M", "Độ dài từ 5 đến 200 ký tự; không để trống."],
        ["2", "Thời gian bắt đầu", "start_time", "Ngày giờ", "M", "Thời gian bắt đầu phải lớn hơn thời điểm hiện tại."],
        ["3", "Thời gian kết thúc", "end_time", "Ngày giờ", "M", "Thời gian kết thúc phải sau thời gian bắt đầu ít nhất 30 phút."],
        ["4", "Địa điểm tổ chức", "location", "Chuỗi ký tự", "M", "Địa chỉ cụ thể hoặc đường link tham dự trực tuyến."],
        ["5", "Tên hạng vé", "type_name", "Chuỗi ký tự", "M", "Ví dụ: VIP, Tiêu chuẩn, Early Bird."],
        ["6", "Giá vé niêm yết", "price", "Số thập phân", "M", "Giá vé >= 0 VNĐ (nếu bằng 0 là vé miễn phí)."],
        ["7", "Tổng số vé phát hành", "total_quantity", "Số nguyên", "M", "Tổng vé mỗi hạng >= 10 vé, tối đa 50.000 vé."]
    ]
    add_styled_table(doc, headers_3_7, data_3_7, col_widths=[0.4, 1.6, 1.3, 0.9, 0.7, 1.5], num_align_cols=[0, 4])

    add_h3(doc, "3.4.2   Quy tắc tài chính & Cơ chế trích phí sàn 5%")
    add_p(doc, "iTick áp dụng cơ chế tự động trích phí dịch vụ sàn 5% trên mỗi vé bán ra để duy trì hạ tầng vận hành. Các công thức tài chính được thiết lập bản địa như sau:", bold_prefix="")
    
    # Công thức phí sàn OMML
    add_formula_block(
        doc,
        '''<math xmlns="http://www.w3.org/1998/Math/MathML">
          <mrow>
            <msub><mi>P</mi><mtext>fee</mtext></msub>
            <mo>=</mo>
            <msub><mi>P</mi><mtext>ticket</mtext></msub>
            <mo>×</mo>
            <mn>0.05</mn>
          </mrow>
        </math>''',
        label="Công thức 3-2: Phí dịch vụ sàn iTick 5%"
    )

    # Công thức doanh thu thực nhận OMML
    add_formula_block(
        doc,
        '''<math xmlns="http://www.w3.org/1998/Math/MathML">
          <mrow>
            <msub><mi>R</mi><mtext>organizer_net</mtext></msub>
            <mo>=</mo>
            <munderover>
              <mo>∑</mo>
              <mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow>
              <mi>n</mi>
            </munderover>
            <mrow>
              <mo>(</mo>
              <msub><mi>P</mi><mi>i</mi></msub>
              <mo>×</mo>
              <mn>0.95</mn>
              <mo>)</mo>
            </mrow>
          </mrow>
        </math>''',
        label="Công thức 3-3: Doanh thu thực nhận ròng của Ban tổ chức"
    )

    add_h3(doc, "3.4.3   Bảng mã lỗi quản lý sự kiện")
    add_p(doc, "Bảng 3-8 quy định các lỗi trong quản lý sự kiện:", bold_prefix="")
    headers_3_8 = ["TT", "Mã lỗi", "Trường hợp phát sinh", "Thông báo hiển thị cho người dùng"]
    data_3_8 = [
        ["1", "ERR_INVALID_DATE", "Thời gian kết thúc trước hoặc bằng thời gian bắt đầu", "Thời gian kết thúc sự kiện phải diễn ra sau thời gian bắt đầu."],
        ["2", "ERR_INVALID_PRICE", "Giá vé nhập số âm", "Giá vé không hợp lệ! Giá vé phải lớn hơn hoặc bằng 0 VNĐ."],
        ["3", "ERR_DUPLICATE_TYPE", "Trùng tên hạng vé trong cùng một sự kiện", "Hạng vé này đã tồn tại trong sự kiện."],
        ["4", "ERR_EVENT_LOCKED", "Sửa đổi hạng vé khi sự kiện đã bắt đầu mở bán có người mua", "Không thể chỉnh sửa hạng vé đã có giao dịch phát sinh."]
    ]
    add_styled_table(doc, headers_3_8, data_3_8, col_widths=[0.4, 1.8, 2.2, 2.0], num_align_cols=[0])

    # ================= MỤC 4: YÊU CẦU GIAO DIỆN VÀ DỮ LIỆU =================
    add_h1(doc, "4   Yêu cầu giao diện và dữ liệu")
    add_p(doc, "4.1 Yêu cầu giao diện người dùng (UI/UX):", bold_prefix="")
    add_bullet(doc, "Thiết kế Responsive hoàn toàn trên màn hình Desktop (>= 1200px), Tablet (768px - 1024px) và Smartphone (>= 375px).", bold_prefix="Tương thích đa màn hình: ")
    add_bullet(doc, "Giao diện sử dụng phong cách hiện đại, màu sắc chủ đạo là Xanh công nghệ (#2563EB) kết hợp nền trắng sáng; thông tin vé hiển thị rõ ràng, dễ đọc.", bold_prefix="Tính thẩm mỹ: ")
    add_bullet(doc, "Giao diện trạm soát vé (Check-in Station) tối ưu hóa thao tác chạm, nút bấm kích thước lớn, phản hồi kết quả bằng màu sắc toàn màn hình (Xanh lá = Cho phép qua cổng, Đỏ = Cảnh báo gian lận) giúp nhân viên vận hành liên tục không mỏi mắt.", bold_prefix="Tối ưu cổng kiểm soát: ")
    
    add_p(doc, "4.2 Yêu cầu cơ sở dữ liệu và bảo toàn thông tin:", bold_prefix="")
    add_bullet(doc, "Tuân thủ chặt chẽ các ràng buộc toàn vẹn tham chiếu ACID trong cơ sở dữ liệu quan hệ (SQLite cho môi trường Dev/Test và PostgreSQL cho Production).", bold_prefix="Toàn vẹn dữ liệu: ")
    add_bullet(doc, "Áp dụng cơ chế khóa bi quan (Pessimistic Lock) hoặc cập nhật có điều kiện (Atomic Update) khi trừ số lượng vé tồn kho nhằm ngăn chặn triệt để xung đột Race Condition khi hàng trăm người cùng đặt vé một lúc.", bold_prefix="Kiểm soát đồng thời: ")

    # ================= MỤC 5: YÊU CẦU PHI CHỨC NĂNG =================
    add_h1(doc, "5   Yêu cầu phi chức năng")
    add_p(doc, "Các chỉ tiêu phi chức năng định lượng bắt buộc được quy định tại Bảng 5-1 (mọi chỉ tiêu đều có thể kiểm chứng được bằng công cụ kiểm thử hiệu năng chuyên dụng):", bold_prefix="")
    
    headers_5_1 = ["Nhóm yêu cầu", "Nội dung chỉ tiêu định lượng kiểm thử"]
    data_5_1 = [
        ["Hiệu năng (Performance)", "Thời gian phản hồi (Response Time) đối với 95% số request API thông thường < 1.0 giây; thời gian tải trang chủ < 2.0 giây. API soát vé Check-in phản hồi < 0.5 giây. Hệ thống đáp ứng thông lượng tối thiểu 50 requests/giây (RPS) và chịu tải ổn định ở mức 1.000 người dùng đồng thời (CCU)."],
        ["Khả dụng (Availability)", "Hệ thống bảo đảm mức độ sẵn sàng hoạt động đạt tối thiểu 99.5% thời gian trong tháng. Có cơ chế tự khởi động lại dịch vụ và endpoint `/health` phục vụ kiểm tra sức khỏe hệ thống tự động."],
        ["Bảo mật (Security)", "Mật khẩu người dùng bắt buộc được băm bằng thuật toán Bcrypt an toàn. Cơ chế xác thực phân quyền qua JWT (JSON Web Token). Mã QR của vé được ký số hoặc gán chuỗi hash bảo mật chống làm giả. Hệ thống ngăn chặn 100% các lỗ hổng cơ bản: SQL Injection, XSS, CSRF."],
        ["Tương thích (Compatibility)", "Hoạt động mượt mà không lỗi giao diện trên tất cả trình duyệt hiện đại: Google Chrome, Microsoft Edge, Mozilla Firefox, Apple Safari. Tương thích chuẩn với các thiết bị đầu đọc mã vạch 2D cầm tay cắm qua cổng USB hoặc kết nối Bluetooth."],
        ["Sao lưu & Phục hồi (Backup & Recovery)", "Dữ liệu cơ sở dữ liệu được thiết lập sao lưu định kỳ hàng ngày (Daily Backup). Thời gian phục hồi thảm họa mục tiêu (RTO - Recovery Time Objective) < 30 phút; Mức mất mát dữ liệu tối đa chấp nhận được (RPO - Recovery Point Objective) < 1 giờ."]
    ]
    add_styled_table(doc, headers_5_1, data_5_1, col_widths=[2.1, 4.3])

    # ================= MỤC 6: BẢNG TỔNG HỢP CÁC YÊU CẦU CHỨC NĂNG =================
    add_h1(doc, "6   Bảng tổng hợp các yêu cầu chức năng")
    add_p(doc, "Bảng 6-1 tổng hợp toàn bộ các yêu cầu chức năng của hệ thống iTick, đóng vai trò là danh mục kiểm tra (Checklist) để Sinh viên B thiết kế các kịch bản kiểm thử phủ kín 100%:", bold_prefix="")
    
    headers_6_1 = ["Mã YC", "Tên yêu cầu", "Mô tả ngắn", "Ưu tiên"]
    data_6_1 = [
        ["YC-01", "Đăng ký & Đăng nhập", "Xác thực người dùng qua Email/Mật khẩu; phân quyền theo vai trò (Customer, Organizer, Admin, Staff).", "High (Bắt buộc)"],
        ["YC-02", "Khám phá sự kiện", "Xem danh sách sự kiện, tìm kiếm theo tên, lọc theo thể loại và địa điểm tổ chức.", "High (Bắt buộc)"],
        ["YC-03", "Đặt vé & Giữ chỗ 10 phút", "Cho phép chọn loại vé, số lượng (1-5 vé), tạm giữ chỗ trong 10 phút chống overselling.", "High (Bắt buộc)"],
        ["YC-04", "Áp dụng Mã giảm giá (Voucher)", "Nhập mã ưu đãi, kiểm tra điều kiện hiệu lực và áp dụng trần chiết khấu tối đa.", "Medium (Trung bình)"],
        ["YC-05", "Thanh toán trực tuyến", "Tích hợp cổng thanh toán trực tuyến bảo đảm tính bất biến (Idempotency) và phát hành vé.", "High (Bắt buộc)"],
        ["YC-06", "Quản lý vé của tôi", "Hiển thị danh sách vé cá nhân đã mua kèm hình ảnh mã QR và Barcode tải về máy.", "High (Bắt buộc)"],
        ["YC-07", "Soát vé Check-in tại cổng", "Trạm quét mã QR/Barcode phản hồi < 0.5s, nhận diện vé hợp lệ và cảnh báo vé đã qua cổng.", "High (Bắt buộc)"],
        ["YC-08", "Quản lý sự kiện (Ban tổ chức)", "Khởi tạo sự kiện mới, tạo các phân hạng vé, mở bán vé và đóng bán vé tự động.", "High (Bắt buộc)"],
        ["YC-09", "Báo cáo doanh thu & Phí sàn 5%", "Thống kê số vé bán, tính toán phí sàn 5%, xuất danh sách người tham dự sự kiện.", "Medium (Trung bình)"]
    ]
    add_styled_table(doc, headers_6_1, data_6_1, col_widths=[1.0, 1.8, 2.7, 0.9], num_align_cols=[0, 3])

    # Lưu tài liệu
    doc.save(OUTPUT_PATH)
    print(f"Build URD successfully saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    build_urd_document()

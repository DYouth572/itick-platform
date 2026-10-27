# -*- coding: utf-8 -*-
import os, sys, unicodedata, shutil
import lxml.etree as ET
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

XSLT_PATH = r'C:\Program Files\Microsoft Office\Office16\MML2OMML.XSL'
XSLT = ET.XSLT(ET.parse(XSLT_PATH))
sys.stdout.reconfigure(encoding='utf-8')

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

def add_h1(doc, text, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=14, space_after=6):
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

def add_math_to_p(p, mml_str):
    mml = ET.fromstring(mml_str.encode('utf-8'))
    omml = XSLT(mml)
    omml_xml = ET.tostring(omml, encoding='utf-8').decode('utf-8')
    omml_elem = parse_xml(omml_xml.encode('utf-8'))
    p._p.append(omml_elem)

def add_formula_block(doc, mml_str, label=""):
    p = doc.add_paragraph()
    set_para_format(p, space_before_pt=5, space_after_pt=7, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_math_to_p(p, mml_str)
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
    
    for idx, heading in enumerate(headers):
        cell = hdr_row.cells[idx]
        set_cell_border_and_shading(cell, bg_color="F2F2F2")
        p = cell.paragraphs[0]
        align = WD_ALIGN_PARAGRAPH.CENTER if (idx in num_align_cols or idx == 0) else WD_ALIGN_PARAGRAPH.LEFT
        set_para_format(p, space_before_pt=2, space_after_pt=2, line_spacing=1.15, align=align)
        r = p.add_run(nfc(heading))
        set_run_font(r, size_pt=12, bold=True)
        if col_widths and idx < len(col_widths):
            cell.width = Inches(col_widths[idx])
            
    for r_idx, row_values in enumerate(rows_data):
        row = table.rows[r_idx + 1]
        r_trPr = row._tr.get_or_add_trPr()
        r_trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        for c_idx, val in enumerate(row_values):
            cell = row.cells[c_idx]
            set_cell_border_and_shading(cell)
            p = cell.paragraphs[0]
            align = WD_ALIGN_PARAGRAPH.CENTER if (c_idx in num_align_cols or (num_cols <= 4 and c_idx == 0)) else WD_ALIGN_PARAGRAPH.LEFT
            set_para_format(p, space_before_pt=2, space_after_pt=2, line_spacing=1.15, align=align)
            r = p.add_run(nfc(str(val)))
            set_run_font(r, size_pt=12)
            if col_widths and c_idx < len(col_widths):
                cell.width = Inches(col_widths[c_idx])
                
    p_after = doc.add_paragraph()
    set_para_format(p_after, space_before_pt=0, space_after_pt=6)
    return table

# Định nghĩa các chuỗi MathML chuẩn
MML_PLATFORM_FEE = '''<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mrow>
    <mtext>platform_fee</mtext>
    <mo>=</mo>
    <mtext>round</mtext>
    <mo>(</mo>
    <mfrac>
      <mrow><mtext>final_amount</mtext><mo>×</mo><mtext>platform_fee_rate</mtext></mrow>
      <mn>100</mn>
    </mfrac>
    <mo>)</mo>
  </mrow>
</math>'''

MML_ORGANIZER_AMOUNT = '''<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mrow>
    <mtext>organizer_amount</mtext>
    <mo>=</mo>
    <mtext>final_amount</mtext>
    <mo>−</mo>
    <mtext>platform_fee</mtext>
  </mrow>
</math>'''

MML_FEE_EXAMPLE = '''<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mrow>
    <mtext>Phí sàn</mtext>
    <mo>=</mo>
    <mtext>round</mtext>
    <mo>(</mo>
    <mn>179,100</mn>
    <mo>×</mo>
    <mn>5%</mn>
    <mo>)</mo>
    <mo>=</mo>
    <mn>8,955</mn>
    <mtext> VNĐ</mtext>
  </mrow>
</math>'''

MML_PIECEWISE_REFUND = '''<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mrow>
    <mtext>Số tiền hoàn</mtext>
    <mo>=</mo>
    <mrow>
      <mo>{</mo>
      <mtable columnalign="left left">
        <mtr>
          <mtd><mrow><mtext>Giá vé</mtext><mo>×</mo><mn>90%</mn></mrow></mtd>
          <mtd><mrow><mtext>nếu thời gian đến sự kiện </mtext><mo>≥</mo><mn>48</mn><mtext> giờ</mtext></mrow></mtd>
        </mtr>
        <mtr>
          <mtd><mrow><mtext>Giá vé</mtext><mo>×</mo><mn>70%</mn></mrow></mtd>
          <mtd><mrow><mtext>nếu </mtext><mn>24</mn><mtext> giờ </mtext><mo>≤</mo><mtext> thời gian </mtext><mo>&lt;</mo><mn>48</mn><mtext> giờ</mtext></mrow></mtd>
        </mtr>
        <mtr>
          <mtd><mrow><mn>0</mn><mtext> (Từ chối hủy)</mtext></mrow></mtd>
          <mtd><mrow><mtext>nếu thời gian đến sự kiện </mtext><mo>&lt;</mo><mn>24</mn><mtext> giờ</mtext></mrow></mtd>
        </mtr>
      </mtable>
    </mrow>
  </mrow>
</math>'''

MML_RECONCILIATION = '''<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mrow>
    <mtext>Doanh thu Gộp</mtext>
    <mo>=</mo>
    <mtext>Phí Sàn iTick</mtext>
    <mo>+</mo>
    <mtext>Chi Trả BTC</mtext>
    <mo>+</mo>
    <mtext>Tiền Hoàn Trả (Refunded)</mtext>
  </mrow>
</math>'''

MML_VARIANCE = '''<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mrow>
    <mtext>Độ lệch đối soát</mtext>
    <mo>=</mo>
    <mn>0</mn>
    <mtext> VNĐ</mtext>
  </mrow>
</math>'''

MML_NFR01 = '''<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mrow>
    <msub><mi>p</mi><mn>95</mn></msub>
    <mo>≤</mo>
    <mn>500</mn>
    <mtext> ms</mtext>
    <mo>,</mo>
    <mtext> trung bình </mtext>
    <mo>≤</mo>
    <mn>300</mn>
    <mtext> ms</mtext>
  </mrow>
</math>'''

MML_NFR02 = '''<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mrow>
    <msub><mi>p</mi><mn>90</mn></msub>
    <mo>≤</mo>
    <mn>1,500</mn>
    <mtext> ms</mtext>
    <mo>,</mo>
    <mtext> Overselling Rate </mtext>
    <mo>=</mo>
    <mn>0%</mn>
  </mrow>
</math>'''

MML_NPV = '''<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mrow>
    <mtext>NPV</mtext>
    <mo>=</mo>
    <munderover>
      <mo>∑</mo>
      <mrow><mi>t</mi><mo>=</mo><mn>0</mn></mrow>
      <mi>n</mi>
    </munderover>
    <mfrac>
      <mrow><msub><mrow><mi>CF</mi></mrow><mi>t</mi></msub></mrow>
      <mrow>
        <msup>
          <mrow><mo>(</mo><mn>1</mn><mo>+</mo><mi>r</mi><mo>)</mo></mrow>
          <mi>t</mi>
        </msup>
      </mrow>
    </mfrac>
  </mrow>
</math>'''

MML_WACC = '''<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mrow>
    <mtext>WACC</mtext>
    <mo>=</mo>
    <mrow>
      <mo>(</mo>
      <mfrac><mi>E</mi><mi>V</mi></mfrac>
      <mo>×</mo>
      <msub><mi>R</mi><mi>e</mi></msub>
      <mo>)</mo>
    </mrow>
    <mo>+</mo>
    <mrow>
      <mo>(</mo>
      <mfrac><mi>D</mi><mi>V</mi></mfrac>
      <mo>×</mo>
      <msub><mi>R</mi><mi>d</mi></msub>
      <mo>×</mo>
      <mo>(</mo><mn>1</mn><mo>−</mo><msub><mi>T</mi><mi>c</mi></msub><mo>)</mo>
      <mo>)</mo>
    </mrow>
  </mrow>
</math>'''

print("MathML definitions loaded!")

# ==============================================================================
# PHẦN 1: TÀI LIỆU YÊU CẦU NGƯỜI DÙNG (URD)
# ==============================================================================
def build_urd_content(doc):
    add_h1(doc, "TÀI LIỆU YÊU CẦU NGƯỜI DÙNG (URD - USER REQUIREMENTS DOCUMENT)")
    add_h2(doc, "DỰ ÁN: NỀN TẢNG ĐĂNG KÝ & BÁN VÉ SỰ KIỆN TRỰC TUYẾN (iTick)", align=WD_ALIGN_PARAGRAPH.CENTER)
    
    add_p(doc, "Đánh giá hiệu năng / Kiểm thử phần mềm", bold_prefix="Môn học: ")
    add_p(doc, "URD-ITICK-V1.2", bold_prefix="Mã tài liệu: ")
    add_p(doc, "1.2 (Đồng bộ Thương hiệu iTick, Cơ chế Thương mại Phí sàn 5%, Phê duyệt Tự động & Cổng Superadmin Toàn quyền)", bold_prefix="Phiên bản: ")
    add_p(doc, AUTHOR_FULL, bold_prefix="Tác giả (Chủ hệ thống): ")
    add_p(doc, "iTick - Modern Event & Conference Ticketing Platform", bold_prefix="Hệ thống: ")
    add_p(doc, f"{DEPLOY_LINK} | Mã nguồn GitHub: {GITHUB_LINK}", bold_prefix="Link Triển khai Cloud (Deploy): ")
    add_p(doc, DRIVE_LINK, bold_prefix="Thư mục tài liệu Google Drive: ")
    add_p(doc, "Sinh viên B (Tester)", bold_prefix="Đối tượng bàn giao kiểm thử: ")
    add_p(doc, "—" * 55, align=WD_ALIGN_PARAGRAPH.CENTER)

    # 1. Bối cảnh
    add_h2(doc, "1. Bối cảnh, Mục tiêu & Phạm vi (Context, Objectives & Scope)")
    add_h3(doc, "1.1. Bối cảnh dự án (Context)")
    add_p(doc, "Trong thời đại chuyển đổi số, nhu cầu tham dự các hội thảo công nghệ, sự kiện âm nhạc, workshop kỹ năng và hội nghị chuyên môn tăng trưởng mạnh mẽ. Nền tảng iTick được phát triển nhằm cung cấp một giải pháp web hiện đại, chuẩn RESTful API, cho phép:")
    add_bullet(doc, "Ban tổ chức dễ dàng khởi tạo sự kiện, mở bán vé nhiều phân hạng và tự động kích hoạt công khai mở bán (Auto-Approval).", bold_prefix="1. ")
    add_bullet(doc, "Tích hợp cơ chế thương mại dịch vụ nền tảng minh bạch: Trích thu phí dịch vụ sàn hợp lý (mặc định 5%) để duy trì hạ tầng, đồng thời tự động phân bổ doanh thu thuần vào ví Ban tổ chức.", bold_prefix="2. ")
    add_bullet(doc, "Cung cấp cổng Quản trị Tối cao (Superadmin Control Center) toàn quyền giám sát người dùng, sự kiện, đơn hàng, kiểm soát đối soát dòng tiền và xử lý hoàn tiền khẩn cấp.", bold_prefix="3. ")
    add_bullet(doc, "Đảm bảo môi trường hoàn hảo cho môn học Kiểm thử phần mềm: Cài cắm các bài toán bẫy lỗi kinh điển (Làm tròn số tiền VND, Cạnh tranh tài nguyên Race Condition, Boundary Testing vé 0đ, Voucher đối soát).", bold_prefix="4. ")

    add_h3(doc, "1.2. Mục tiêu dự án (Objectives)")
    add_bullet(doc, "Tra cứu sự kiện dễ dàng, đặt mua vé an toàn, nhận mã vé điện tử tức thì và hỗ trợ hủy vé minh bạch theo chính sách thời gian.", bold_prefix="1. Đối với người tham dự: ")
    add_bullet(doc, "Tự chủ khởi tạo sự kiện mở bán ngay lập tức (không bị ách tắc chờ duyệt), theo dõi doanh thu thực nhận vào ví điện tử sau khi trừ phí sàn minh bạch.", bold_prefix="2. Đối với ban tổ chức: ")
    add_bullet(doc, "Nắm toàn quyền quản trị người dùng, phân quyền (RBAC), kiểm duyệt sự kiện, hủy đơn hoàn tiền khẩn cấp và cấu hình tỷ lệ phí sàn linh hoạt.", bold_prefix="3. Đối với Quản trị viên (Superadmin): ")
    add_bullet(doc, "Cung cấp ứng dụng có 39 API Endpoints (44 Operations) chuẩn mực, hỗ trợ đo kiểm tải cao điểm (JMeter) và kiểm thử tự động toàn diện.", bold_prefix="4. Đối với môn học Kiểm thử & Đánh giá hiệu năng: ")

    add_h3(doc, "1.3. Phạm vi hệ thống (Scope)")
    add_p(doc, "Trong phạm vi (In-Scope):", bold_prefix="• ")
    add_bullet(doc, "Quản trị tài khoản và phân quyền người dùng (Khách vãng lai, Người tham dự, Ban tổ chức, Quản trị viên).")
    add_bullet(doc, "Khám phá, tìm kiếm và lọc sự kiện theo từ khóa, danh mục.")
    add_bullet(doc, "Đặt vé, kiểm tra tồn kho theo thời gian thực, áp dụng mã voucher giảm giá, tích hợp kép thanh toán Ví nội bộ và PayOS VietQR.")
    add_bullet(doc, "Cơ chế thương mại & phí sàn: Tự động trích 5% phí dịch vụ, tính toán làm tròn chuẩn tiền tệ VND, chuyển doanh thu thuần về ví BTC.")
    add_bullet(doc, "Quản lý vé cá nhân, xuất mã vé điện tử QR/Alpha-code để check-in tại cổng.")
    add_bullet(doc, "Cổng Quản trị Superadmin Toàn quyền (5 Tab): Thống kê & Phí sàn, Người dùng & Phân quyền, Sự kiện, Đơn hàng & Vé, Cấu hình Hệ thống.")
    
    add_p(doc, "Ngoài phạm vi (Out-of-Scope):", bold_prefix="• ")
    add_bullet(doc, "Tích hợp cổng thanh toán quốc tế Visa/Mastercard trực tiếp (sử dụng VietQR PayOS nội địa và ví nội bộ để kiểm thử cô lập).")
    add_bullet(doc, "Gửi SMS Brandname vật lý – hiển thị trực tiếp mã xác thực trên giao diện web.")

    # 2. Vai trò
    add_h2(doc, "2. Các Vai trò Người dùng & Nhu cầu (User Roles & Needs)")
    add_p(doc, "Hệ thống định nghĩa 3 vai trò người dùng chính và 1 vai trò khách vãng lai:")
    
    headers_roles = ["Vai trò", "Mô tả đặc điểm", "Nhu cầu chính (Core Needs)"]
    data_roles = [
        [
            "1. Khách tham dự (Attendee)",
            "Cá nhân tìm kiếm, đăng ký và tham gia các sự kiện, hội thảo.",
            "• Tìm kiếm nhanh sự kiện theo sở thích, địa điểm.\n• Mua vé nhanh chóng, chọn thanh toán Ví hoặc quét VietQR PayOS.\n• Áp dụng mã voucher giảm giá hợp lệ.\n• Nhận mã vé điện tử tức thì để check-in.\n• Hủy vé nhận hoàn tiền minh bạch theo chính sách thời gian."
        ],
        [
            "2. Ban tổ chức (Organizer)",
            "Đơn vị, cá nhân tổ chức hội thảo, sự kiện.",
            "• Tạo sự kiện và mở bán tức thì nhờ cơ chế Tự động phê duyệt (Auto-Approval).\n• Phân chia nhiều hạng vé (VIP, Standard, Early Bird) linh hoạt.\n• Tự động nhận doanh thu thuần vào ví điện tử sau khi trích phí sàn 5%.\n• Soát vé tại cổng nhanh chóng, chính xác, phát hiện ngay vé giả/vé đã dùng.\n• Theo dõi báo cáo tài chính đối soát minh bạch."
        ],
        [
            "3. Quản trị viên (Superadmin)",
            "Người quản trị tối cao, nắm toàn quyền điều hành hệ thống iTick.",
            "• Toàn quyền quản trị tài khoản người dùng và nâng/hạ vai trò (RBAC).\n• Giám sát toàn bộ sự kiện toàn sàn, ẩn/hiện hoặc xóa sự kiện vi phạm.\n• Quản trị đơn hàng toàn sàn, thực hiện Hủy đơn khẩn cấp & Hoàn 100% tiền cho khách khi có tranh chấp (tự động thu hồi số dư từ ví BTC).\n• Cấu hình tỷ lệ phần trăm phí sàn linh hoạt (platform_fee_rate).\n• Báo cáo tổng thể doanh thu, phí sàn, chi trả BTC với độ lệch đối soát bằng 0đ."
        ],
        [
            "Khách vãng lai (Guest)",
            "Người dùng chưa đăng nhập vào hệ thống.",
            "• Xem danh sách sự kiện công khai, đọc chi tiết chương trình, xem bảng giá vé trước khi đăng ký tài khoản."
        ]
    ]
    add_styled_table(doc, headers_roles, data_roles, col_widths=[1.5, 2.0, 3.2])

    # 3. Luồng nghiệp vụ
    add_h2(doc, "3. Các Luồng Nghiệp vụ Trọng Yếu (User Business Flows)")
    add_h3(doc, "FLOW-01: Khám phá Sự kiện, Đặt mua Vé, Tính Phí Sàn & Phân Bổ Doanh Thu")
    add_p(doc, "Điểm bắt đầu: Người dùng mở trang chủ iTick, tìm kiếm và chọn sự kiện yêu thích.", bold_prefix="• ")
    add_p(doc, "Bước 1 - Chọn vé & Số lượng: Người dùng chọn hạng vé và số lượng (1 - 5 vé).", bold_prefix="• ")
    add_p(doc, "Bước 2 - Áp dụng Voucher (nếu có): Nhập mã giảm giá. Hệ thống thẩm định điều kiện và tính chiết khấu hợp lệ.", bold_prefix="• ")
    add_p(doc, "Bước 3 - Xác nhận Thanh toán & Phân bổ Dòng tiền:", bold_prefix="• ")
    add_bullet(doc, "Người dùng chọn phương thức thanh toán: Ví nội bộ hoặc Quét mã VietQR qua PayOS.")
    add_bullet(doc, "Khi đơn hàng hoàn tất, hệ thống kích hoạt tự động cơ chế thương mại:")
    add_p(doc, "Phí dịch vụ nền tảng iTick (5%):", bold_prefix="+ ")
    add_formula_block(doc, MML_PLATFORM_FEE, "Công thức Phí sàn")
    add_p(doc, "Doanh thu thuần của Ban tổ chức:", bold_prefix="+ ")
    add_formula_block(doc, MML_ORGANIZER_AMOUNT, "Công thức Doanh thu BTC")
    add_bullet(doc, "Trừ tồn kho vé tức thì, cấp mã vé điện tử định danh cho khách hàng.")

    add_h3(doc, "FLOW-02: Ban tổ chức Tạo sự kiện & Tự động Phê duyệt Mở bán (Auto-Approval Flow)")
    add_p(doc, "Ban tổ chức đăng nhập, vào mục 'Quản lý sự kiện' -> 'Tạo sự kiện mới'. Nhập thông tin: Tiêu đề, danh mục, thời gian tổ chức, địa điểm, sức chứa và ảnh banner.")
    add_p(doc, "Cơ chế Tự động Phê duyệt (Auto-Approval): Hệ thống tự động kiểm tra các ràng buộc dữ liệu. Nếu hợp lệ, sự kiện lập tức nhận trạng thái PUBLISHED và kích hoạt hiển thị is_visible = True để mở bán ngay cho khách hàng, không còn cảnh chờ duyệt thủ công.")

    add_h3(doc, "FLOW-03: Soát vé tại Cổng Sự kiện & Xuất Báo Cáo Đối Soát Timeline")
    add_p(doc, "Nghiệp vụ Soát vé tại Cổng: Nhân viên soát vé mở giao diện Check-in, quét mã QR qua webcam/camera điện thoại hoặc bắn mã vạch USB/gõ mã vé điện tử. Hệ thống chuyển trạng thái CONFIRMED -> CHECKED_IN, lưu giờ check-in thực tế.")
    add_p(doc, "Nghiệp vụ Xuất File Excel Đối Soát: Ban tổ chức bấm nút 'Xuất Excel Soát Vé' trong Tab Quản lý người đăng ký. File Excel (.xlsx) xuất chuẩn với Data Validation Dropdown ở cột Trạng thái soát vé và đối chiếu timeline: ĐÃ THAM DỰ, VẮNG MẶT, CHƯA CHECK-IN, ĐÃ HỦY VÉ.")

    add_h3(doc, "FLOW-04: Yêu cầu Hủy vé Cá nhân & Hoàn tiền theo Chính sách")
    add_p(doc, "Chính sách hoàn hủy vé cá nhân trên giao diện 'Vé của tôi':")
    add_bullet(doc, ">= 48 giờ trước sự kiện: Phí hủy 10%, hoàn lại 90% giá vé vào ví.")
    add_bullet(doc, "24 đến < 48 giờ trước sự kiện: Phí hủy 30%, hoàn lại 70% giá vé vào ví.")
    add_bullet(doc, "< 24 giờ trước sự kiện: Từ chối hủy sát giờ để bảo vệ quyền lợi Ban tổ chức.")

    # 4. User Stories
    add_h2(doc, "4. Danh sách 16 User Stories & Tiêu chí Nghiệm thu Chi tiết (Given - When - Then)")
    
    add_h3(doc, "Nhóm 1: Tài khoản & Xác thực (Authentication)")
    add_p(doc, "Là khách vãng lai, tôi muốn đăng ký tài khoản bằng email và mật khẩu, để tôi có thể đăng nhập để mua vé hoặc tạo sự kiện.", bold_prefix="US-01: Đăng ký Tài khoản mới | ")
    add_bullet(doc, "Given: Khách vãng lai ở màn hình Đăng ký tài khoản.")
    add_bullet(doc, "When: Nhập họ tên hợp lệ, email chưa tồn tại, mật khẩu từ 6 ký tự gồm chữ và số, chọn vai trò và bấm 'Đăng ký'.")
    add_bullet(doc, "Then: Hệ thống tạo tài khoản thành công, thông báo đăng ký thành công và chuyển sang màn hình Đăng nhập.")

    add_p(doc, "Là người dùng đã có tài khoản, tôi muốn đăng nhập bằng email và mật khẩu, để tôi được xác thực phiên làm việc JWT và thao tác theo vai trò.", bold_prefix="US-02: Đăng nhập Hệ thống & Cấp phiên làm việc | ")
    add_bullet(doc, "Given: Người dùng ở màn hình Đăng nhập.")
    add_bullet(doc, "When: Nhập đúng email và mật khẩu đã đăng ký, bấm 'Đăng nhập'.")
    add_bullet(doc, "Then: Hệ thống cấp JWT Bearer Token (60 phút), lưu cookie phiên và chuyển hướng về trang chủ theo đúng quyền hạn.")

    add_h3(doc, "Nhóm 2: Khám phá & Đặt vé (Booking & Platform Fee)")
    add_p(doc, "Là người tham dự, tôi muốn tìm kiếm sự kiện theo từ khóa (tiêu đề, địa điểm) và lọc theo danh mục hoặc khoảng thời gian để nhanh chóng tìm thấy sự kiện mong muốn.", bold_prefix="US-03: Tìm kiếm & Lọc Danh sách Sự kiện | ")
    add_bullet(doc, "Given: Người tham dự ở trang chủ hoặc trang danh sách sự kiện.")
    add_bullet(doc, "When: Nhập từ khóa tìm kiếm (tiêu đề hoặc địa điểm) và chọn danh mục sự kiện.")
    add_bullet(doc, "Then: Hệ thống trả về danh sách các sự kiện đang mở bán (trạng thái APPROVED/PUBLISHED) khớp với tiêu chí, hỗ trợ phân trang chuẩn page và limit.")

    add_p(doc, "Là người tham dự, tôi muốn xem trang chi tiết sự kiện bao gồm banner, lịch trình, địa điểm và danh sách các hạng vé kèm số lượng vé còn lại để quyết định đặt vé.", bold_prefix="US-04: Xem Chi tiết Sự kiện & Tồn kho Hạng vé | ")
    add_bullet(doc, "Given: Người tham dự bấm chọn một sự kiện từ danh sách.")
    add_bullet(doc, "When: Trang chi tiết sự kiện tải thành công (GET /events/{id}).")
    add_bullet(doc, "Then: Hiển thị đầy đủ thông tin sự kiện; các hạng vé (Standard, VIP) hiển thị rõ giá bán và số lượng vé còn lại; hạng vé hết chỗ hiển thị nhãn 'Hết vé' và vô hiệu hóa nút đặt vé.")

    add_p(doc, "Là người tham dự, tôi muốn đặt mua vé trực tuyến và chọn thanh toán linh hoạt, đồng thời hệ thống tự động trích 5% phí sàn và chuyển doanh thu thuần cho Ban tổ chức.", bold_prefix="US-05: Đặt mua Vé, Tính Phí Sàn 5% & Tự động Phân bổ Doanh thu | ")
    add_bullet(doc, "Kịch bản 5.1 (Đặt vé thành công): Đơn hàng 600,000đ -> Phí sàn 5% = 30,000đ, Doanh thu thuần BTC = 570,000đ. Ví Ban tổ chức tự động cộng +570,000đ ngay lập tức; cấp 2 mã vé điện tử CONFIRMED.")
    add_bullet(doc, "Kịch bản 5.2 (Vé miễn phí 0đ): Sự kiện vé 0đ -> Tổng tiền = 0đ, Phí sàn = 0đ, Tiền chuyển BTC = 0đ. Cấp vé thành công không lỗi chia cho 0.")
    add_bullet(doc, "Kịch bản 5.3 (Làm tròn tiền tệ khi áp Voucher): Vé 199,000đ giảm 10% còn 179,100đ -> Tính phí sàn:")
    add_formula_block(doc, MML_FEE_EXAMPLE)

    add_p(doc, "Là người tham dự, tôi muốn nhập mã voucher giảm giá tại bước thanh toán để được giảm trừ trực tiếp vào tổng tiền đơn hàng.", bold_prefix="US-06: Áp dụng Mã Giảm Giá (Voucher) | ")
    add_bullet(doc, "Given: Người tham dự ở màn hình đặt vé với đơn hàng đạt giá trị tối thiểu của voucher (min_order_value).")
    add_bullet(doc, "When: Nhập mã voucher hợp lệ (ví dụ: SUMMER2026) và bấm 'Áp dụng'.")
    add_bullet(doc, "Then: Hệ thống tính toán số tiền giảm (theo % hoặc số tiền cố định), áp dụng giới hạn giảm tối đa (max_discount_cap nếu có), trừ số lần sử dụng của voucher và cập nhật lại số tiền thanh toán thực tế.")

    add_p(doc, "Là người tham dự đã mua vé, tôi muốn xem lại danh sách vé của mình kèm mã vé độc nhất và mã QR động để xuất trình khi đến cổng soát vé.", bold_prefix="US-07: Xem Vé Cá Nhân & Lấy Mã QR E-Ticket | ")
    add_bullet(doc, "Given: Người dùng đã đăng nhập và truy cập trang 'Vé của tôi' (/my-tickets).")
    add_bullet(doc, "When: Hệ thống tải danh sách vé cá nhân.")
    add_bullet(doc, "Then: Hiển thị danh sách vé được nhóm theo sự kiện, mỗi vé có mã định danh duy nhất (TCK-XXXX-YYYY), mã QR Code dạng Base64, trạng thái vé (VALID, CHECKED_IN, CANCELLED).")

    add_p(doc, "Là người tham dự, tôi muốn có thể yêu cầu hủy vé đã mua trước khi sự kiện diễn ra theo chính sách hoàn tiền để nhận lại tiền vào ví tài khoản.", bold_prefix="US-08: Yêu cầu Hủy Vé & Hoàn Tiền Ví | ")
    add_bullet(doc, "Given: Người dùng có vé ở trạng thái VALID và thời gian hiện tại cách thời điểm bắt đầu sự kiện >= 24 giờ.")
    add_bullet(doc, "When: Người dùng bấm 'Yêu cầu hủy vé' trên giao diện Vé của tôi.")
    add_bullet(doc, "Then: Xác thực mốc thời gian: Hủy trước >= 48h hoàn 100% (hoặc 90%), hủy từ 24 đến < 48h hoàn 70% vào ví; chuyển trạng thái vé thành CANCELLED, hoàn lại tồn kho (+1 available_quantity), chặn hủy nếu < 24h.")

    add_h3(doc, "Nhóm 3: Ban tổ chức & Quản lý Sự kiện (Organizer)")
    add_p(doc, "Là ban tổ chức, tôi muốn tạo sự kiện mới và hệ thống tự động kiểm duyệt mở bán ngay lập tức, để tôi không phải chờ đợi quản trị viên duyệt thủ công.", bold_prefix="US-09: Khởi tạo Sự kiện & Tự động Phê duyệt Mở bán (Auto-Approval) | ")
    add_bullet(doc, "Given: Ban tổ chức đã đăng nhập vào mục 'Quản lý sự kiện'.")
    add_bullet(doc, "When: Nhập thông tin sự kiện hợp lệ (tiêu đề, thời gian tương lai, địa điểm, sức chứa) và bấm 'Lưu'.")
    add_bullet(doc, "Then: Hệ thống tự động cấp trạng thái PUBLISHED và kích hoạt is_visible = True ngay lập tức, sự kiện xuất hiện ngay trên trang chủ.")

    add_p(doc, "Là ban tổ chức, tôi muốn tạo nhiều hạng vé khác nhau cho sự kiện với mức giá và số lượng tương ứng để đa dạng hóa phân khúc khách hàng.", bold_prefix="US-10: Cấu hình Phân Hạng Vé Sự Kiện | ")
    add_bullet(doc, "Given: Ban tổ chức đang quản lý sự kiện của mình ở trạng thái PENDING hoặc APPROVED (chưa có vé bán ra).")
    add_bullet(doc, "When: Nhập tên hạng vé, số lượng phát hành (total_quantity > 0), giá vé (price >= 0) và bấm 'Thêm hạng vé'.")
    add_bullet(doc, "Then: Hạng vé được lưu vào cơ sở dữ liệu với available_quantity = total_quantity, hiển thị ngay trên trang chi tiết sự kiện.")

    add_p(doc, "Là nhân viên soát vé, tôi muốn quét mã vé hoặc QR để xác thực khách vào cửa, để tôi kiểm soát người tham dự và ngăn chặn vé giả mạo.", bold_prefix="US-11: Soát vé tại Cổng Sự kiện | ")
    add_bullet(doc, "Given: Người soát vé mở cổng check-in (/checkin-gate).")
    add_bullet(doc, "When: Quét mã QR hoặc nhập mã vé TCK-XXXX-YYYY.")
    add_bullet(doc, "Then: Hệ thống chuyển trạng thái sang CHECKED_IN, báo xanh thành công; nếu quét lại báo lỗi 409 Conflict kèm mốc giờ đã quét.")

    add_p(doc, "Là ban tổ chức, tôi muốn xem thống kê số lượng vé đã bán và doanh thu thực nhận sau khi trừ phí dịch vụ nền tảng 5%, để tôi đối soát tài chính minh bạch.", bold_prefix="US-12: Báo cáo Doanh thu & Đối soát Dòng tiền | ")
    add_bullet(doc, "Then: Báo cáo hiển thị rõ: Doanh thu gộp (10,000,000đ), Phí dịch vụ sàn iTick 5% (-500,000đ), Doanh thu thực nhận (+9,500,000đ) đúng bằng số dư đã ghi nhận vào ví.")

    add_p(doc, "Là ban tổ chức sự kiện, tôi muốn xuất file Excel (.xlsx) danh sách người tham dự và mã vé của từng sự kiện có Dropdown thả xuống để đối soát trực tiếp.", bold_prefix="US-12b: Xuất File Excel Danh Sách Soát Vé & Đối Soát Timeline | ")
    add_bullet(doc, "Then: File tải xuống định dạng chuẩn (.xlsx) với Data Validation Dropdown ở cột 'Trạng thái soát vé' (ĐÃ THAM DỰ, VẮNG MẶT, CHƯA CHECK-IN, ĐÃ HỦY VÉ); hỗ trợ format csv và json.")

    add_h3(doc, "Nhóm 4: Quản trị Hệ thống Tối cao (Superadmin)")
    add_p(doc, "Là quản trị viên tối cao, tôi muốn có toàn quyền xem, thêm, sửa, đổi vai trò (Role), đặt lại mật khẩu và khóa/mở khóa mọi tài khoản trên hệ thống.", bold_prefix="US-13: Superadmin Quản trị Toàn quyền Người dùng & Phân quyền (RBAC) | ")
    add_bullet(doc, "Then: Quyền hạn mới có hiệu lực tức thì; tài khoản bị khóa không thể đăng nhập vào hệ thống (HTTP 403 Forbidden).")

    add_p(doc, "Là quản trị viên, tôi muốn có quyền ẩn/hiện hoặc xóa sự kiện vi phạm, đồng thời vô hiệu hóa các vé gian lận, để tôi bảo vệ uy tín nền tảng iTick.", bold_prefix="US-14: Quản trị Sự kiện & Vé Điện tử Toàn sàn | ")
    add_bullet(doc, "Then: Sự kiện vi phạm bị gỡ khỏi trang chủ tức thì; vé gian lận bị hủy qua POST /api/admin/tickets/{id}/void.")

    add_p(doc, "Là quản trị viên tối cao, tôi muốn cấu hình tỷ lệ phí sàn linh hoạt và có quyền hủy đơn khẩn cấp hoàn tiền 100% cho khách, để tôi giải quyết các tranh chấp khiếu nại và đảm bảo đối soát dòng tiền cân bằng tuyệt đối.", bold_prefix="US-15: Cấu hình Tỷ lệ Phí Sàn & Hủy Đơn Hoàn Tiền Khẩn Cấp | ")
    add_bullet(doc, "Kịch bản 15.1: Admin đổi phí sàn thành 6.5% -> Hệ thống lưu cấu hình và áp dụng ngay cho đơn mới.")
    add_bullet(doc, "Kịch bản 15.2: Hủy đơn khẩn cấp 480k -> Khách nhận đủ 480k, ví BTC bị thu hồi lại đúng 456k, phí sàn giảm 24k, hoàn lại vé.")
    add_bullet(doc, "Kịch bản 15.3: Bảo toàn đối soát sàn tuyệt đối:")
    add_formula_block(doc, MML_RECONCILIATION)
    add_formula_block(doc, MML_VARIANCE)

    # 5. Tiêu chí nghiệm thu tổng thể
    add_h2(doc, "5. Tiêu chí Nghiệm thu Tổng thể ở Mức Người dùng (Overall Acceptance Criteria)")
    add_p(doc, "Giao diện Dark Modern Mesh hiện đại, tối ưu cho sự kiện âm nhạc & nghệ thuật sân khấu, hiển thị trực quan và tương thích responsive trên mọi thiết bị. Mọi thông báo hiển thị bằng tiếng Việt thân thiện, rõ ràng.", bold_prefix="1. Khả năng sử dụng & Thẩm mỹ: ")
    add_p(doc, "Tỷ lệ phí sàn, chiết khấu voucher và doanh thu thực nhận hiển thị chi tiết, minh bạch ở mọi khâu. Tuyệt đối không xảy ra hiện tượng thất thoát tiền hay sai lệch số dư ví.", bold_prefix="2. Minh bạch Tài chính & Toàn vẹn Dữ liệu: ")
    add_p(doc, "Mã vé và mã QR sẵn sàng ngay lập tức sau thanh toán, hỗ trợ quét check-in mượt mà tại cổng sự kiện.", bold_prefix="3. Tính sẵn sàng của vé điện tử: ")

print("build_urd_content appended successfully!")

# ==============================================================================
# PHẦN 2: BIÊN BẢN BÀN GIAO SẢN PHẨM & KẾT QUẢ KIỂM THỬ
# ==============================================================================
def build_handover_content(doc):
    add_h1(doc, "TRƯỜNG ĐẠI HỌC VIỆT NHẬT – HỌC PHẦN ĐÁNH GIÁ HIỆU NĂNG")
    add_h2(doc, "BIÊN BẢN BÀN GIAO SỐ 1: BÀN GIAO SẢN PHẨM ĐỂ KIỂM THỬ (TUẦN 6)", align=WD_ALIGN_PARAGRAPH.CENTER)
    add_p(doc, "Hôm nay, ngày 10/10/2026, hai bên dưới đây thống nhất bàn giao các hạng mục như sau:", italic=True)
    
    headers_meta1 = ["Thành phần", "Thông tin chi tiết"]
    rows_meta1 = [
        ["Bên giao (Chủ hệ thống)", f"Sinh viên A – {AUTHOR_FULL}"],
        ["Bên nhận (Tester)", "Sinh viên B – Nguyễn Văn B – SV20260002"],
        ["Tên hệ thống", "iTick - Nền tảng Đăng ký & Bán vé Sự kiện Trực tuyến"]
    ]
    add_styled_table(doc, headers_meta1, rows_meta1, col_widths=[2.5, 4.2])

    add_h3(doc, "I. Danh mục bàn giao")
    headers_deliv1 = ["STT", "Hạng mục", "Phiên bản / link", "Ghi chú"]
    rows_deliv1 = [
        ["1", "Tài liệu URD", "v1.2 (URD_EventTick.docx)", "Đầy đủ 3 vai trò, 3 luồng người dùng, 16 user stories chuẩn Given-When-Then"],
        ["2", "Tài liệu SRS (bản chốt sau review)", "v1.2 (SRS_EventTick.docx)", "16 FRs, 5 luồng hoàn chỉnh, 8 NFRs, bảng quyết định, ma trận RBAC"],
        ["3", "Tài liệu API", "v1.2 (Tai_lieu_API.docx) / Swagger docs", "Đầy đủ 39 endpoints (44 operations), request/response mẫu"],
        ["4", "Link sản phẩm", f"Cloud Deploy: {DEPLOY_LINK} (Local: http://127.0.0.1:8001)", "Hệ thống iTick hoạt động ổn định 24/7 từ tuần 6 đến tuần 14"],
        ["5", "Tài khoản thử cho từng vai trò", "Theo mục 5 Tài liệu API", "Admin: admin@eventtick.com/admin123; Org: organizer@eventtick.com/org123; Attendee: attendee@eventtick.com/att123"],
        ["6", "Dữ liệu mẫu", "app/seed.py / CSDL SQLite/PostgreSQL", "5 sự kiện mẫu phong phú, nhiều hạng vé, số dư ví test 5.000.000đ"],
        ["7", "Thư mục Drive minh chứng Bug & Docs", DRIVE_LINK, "Thư mục Drive dành riêng cho upload tài liệu và minh chứng Bug"]
    ]
    add_styled_table(doc, headers_deliv1, rows_deliv1, col_widths=[0.6, 2.0, 2.4, 1.7], num_align_cols=[0])

    add_h3(doc, "II. Xác nhận của bên nhận")
    add_p(doc, "[X] Truy cập được link sản phẩm        [X] Đăng nhập được mọi vai trò        [X] Nhận đủ tài liệu ở mục I", bold_prefix="Xác nhận: ")

    add_h3(doc, "III. Hạn chế đã biết")
    add_p(doc, "Các giới hạn đã biết: Hệ thống hiện tại hỗ trợ thanh toán qua cổng Ví nội bộ iTick Pay (chưa tích hợp cổng trực tiếp VNPay/MoMo sandbox thực tế); Các thao tác gửi email thông báo vé điện tử chỉ hỗ trợ mô phỏng qua hệ thống thông báo nội bộ và giao diện màn hình; Chưa hỗ trợ tính năng chọn ghế ngồi sơ đồ 3D tương tác.")

    add_h3(doc, "IV. Cam kết")
    add_bullet(doc, "Bên giao giữ nguyên sản phẩm (không sửa các lỗi) và duy trì link hoạt động liên tục từ tuần 6 đến hết buổi demo tuần 14.")
    add_bullet(doc, "Bên giao phản hồi bug report trong vòng 48 giờ.")
    add_bullet(doc, "Bên giao không tiết lộ danh sách lỗi cài sẵn (Bug Manifest) cho bên nhận.")

    headers_sig1 = ["BÊN GIAO (Ký, ghi rõ họ tên)", "BÊN NHẬN (Ký, ghi rõ họ tên)"]
    rows_sig1 = [
        [f"\n\n\n{AUTHOR_FULL}", "\n\n\nNguyễn Văn B – SV20260002"]
    ]
    add_styled_table(doc, headers_sig1, rows_sig1, col_widths=[3.3, 3.4], num_align_cols=[0, 1])

    # Biên bản 2
    add_p(doc, "—" * 55, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_h1(doc, "TRƯỜNG ĐẠI HỌC VIỆT NHẬT – HỌC PHẦN ĐÁNH GIÁ HIỆU NĂNG")
    add_h2(doc, "BIÊN BẢN BÀN GIAO SỐ 2: BÀN GIAO KẾT QUẢ KIỂM THỬ (TUẦN 14)", align=WD_ALIGN_PARAGRAPH.CENTER)
    add_p(doc, "Hôm nay, ngày 28/11/2026, hai bên dưới đây thống nhất bàn giao các hạng mục như sau:", italic=True)

    headers_meta2 = ["Thành phần", "Thông tin chi tiết"]
    rows_meta2 = [
        ["Bên giao (Tester)", "Sinh viên B – Nguyễn Văn B – SV20260002"],
        ["Bên nhận (Chủ hệ thống)", f"Sinh viên A – {AUTHOR_FULL}"],
        ["Tên hệ thống", "iTick - Nền tảng Đăng ký & Bán vé Sự kiện Trực tuyến"]
    ]
    add_styled_table(doc, headers_meta2, rows_meta2, col_widths=[2.5, 4.2])

    add_h3(doc, "I. Danh mục bàn giao kết quả kiểm thử")
    headers_deliv2 = ["STT", "Hạng mục", "Tên file / link", "Ghi chú"]
    rows_deliv2 = [
        ["1", "Phiếu review SRS", "Mau_03_Bo_bieu_mau_Kiem_thu.xlsx (Sheet Review_SRS)", "6 phát hiện phản biện sâu sắc, 100% được chủ hệ thống chấp nhận"],
        ["2", "Test plan", "Mau_04_Test_Plan.docx", "Hoàn chỉnh 11 bảng chuẩn theo IEEE 829, xác định 5 cấp độ kiểm thử"],
        ["3", "Bộ test case, test log, bug report", "Mau_03_Bo_bieu_mau_Kiem_thu.xlsx (TCs, Log, Bug Report)", "73 TC chức năng, 12 TC phi chức năng, 8 phiên Test log, 16 bugs"],
        ["4", "Collection Postman + báo cáo Newman", "tests/automation/iTick_API_Tests.postman_collection.json & reports/newman_report.html", "20 requests, 35 assertions, kèm data-driven JSON và Newman HTML report"],
        ["5", "Script Puppeteer", "tests/automation/run_puppeteer_e2e.js & evidence/screenshots/e2e/", "2 luồng E2E hoàn chỉnh (FLOW-01 & FLOW-03), 8 assertions, 7 screenshots"],
        ["6", "Kịch bản JMeter + kết quả + HTML dashboard", "tests/performance/iTick_Performance_Test.jmx & results/results.jtl", "2 Thread Groups (50 tải thường & 100 tải đồng thời SyncTimer), 300 samples, HTML Dashboard"],
        ["7", "Test summary report", "Mau_05_Test_Summary_Report.docx", "12 bảng chuẩn, đánh giá chi tiết 4 NFRs hiệu năng, kết luận No-go"]
    ]
    add_styled_table(doc, headers_deliv2, rows_deliv2, col_widths=[0.6, 2.0, 2.4, 1.7], num_align_cols=[0])

    add_h3(doc, "II. Tóm tắt kết quả kiểm thử")
    headers_sum = ["Chỉ số", "Giá trị ghi nhận"]
    rows_sum = [
        ["Số test case chức năng / phi chức năng", "73 test case chức năng / 12 test case phi chức năng (Tổng cộng 85 TCs)"],
        ["Tỉ lệ Pass", "Chức năng: 79.5% (58 Pass / 15 Fail) | Phi chức năng: 83.3% (10 Pass / 2 Fail)"],
        ["Tổng số bug", "16 bugs (Bắt trọn 15/15 lỗi cài sẵn trong Bug Manifest + 1 lỗi ngoài Manifest)"],
        ["Phân loại theo danh mục", "[ 6 Functional / 3 Visual / 3 Content / 2 Performance / 2 Crash ]"],
        ["Kết luận kiểm thử", "No-go (Nghiệm thu có điều kiện sau khi Chủ hệ thống khắc phục triệt để 2 lỗi Critical: Overselling & Crash Quote injection)"]
    ]
    add_styled_table(doc, headers_sum, rows_sum, col_widths=[2.7, 4.0])

    add_h3(doc, "III. Các lỗi còn bất đồng (nếu có)")
    add_p(doc, "Không có bất đồng. Toàn bộ 16/16 lỗi (100%) đều được Chủ hệ thống xác nhận ('Đã xác nhận') và thống nhất kế hoạch khắc phục.")

    headers_sig2 = ["BÊN GIAO (Ký, ghi rõ họ tên)", "BÊN NHẬN (Ký, ghi rõ họ tên)"]
    rows_sig2 = [
        ["\n\n\nNguyễn Văn B – SV20260002", f"\n\n\n{AUTHOR_FULL}"]
    ]
    add_styled_table(doc, headers_sig2, rows_sig2, col_widths=[3.3, 3.4], num_align_cols=[0, 1])

print("build_handover_content appended successfully!")

# ==============================================================================
# PHẦN 3: ĐẶC TẢ YÊU CẦU PHẦN MỀM (SRS)
# ==============================================================================
def build_srs_content(doc):
    add_h1(doc, "ĐẶC TẢ YÊU CẦU PHẦN MỀM (SRS - SOFTWARE REQUIREMENTS SPECIFICATION)")
    add_h2(doc, "DỰ ÁN: NỀN TẢNG ĐĂNG KÝ & BÁN VÉ SỰ KIỆN TRỰC TUYẾN (iTick)", align=WD_ALIGN_PARAGRAPH.CENTER)
    
    add_p(doc, "Đánh giá hiệu năng / Kiểm thử phần mềm", bold_prefix="Môn học: ")
    add_p(doc, "ITICK-V1.2", bold_prefix="Mã hệ thống: ")
    add_p(doc, "1.2 (Bổ sung Cơ chế Phí Dịch vụ Sàn 5%, Phê duyệt Tự động & Superadmin Toàn quyền)", bold_prefix="Phiên bản tài liệu: ")
    add_p(doc, AUTHOR_FULL, bold_prefix="Tác giả (Chủ hệ thống): ")
    add_p(doc, "Sinh viên B", bold_prefix="Tester phản biện: ")
    add_p(doc, f"{DEPLOY_LINK} | Mã nguồn GitHub: {GITHUB_LINK}", bold_prefix="Link Triển khai Cloud (Deploy): ")
    add_p(doc, DRIVE_LINK, bold_prefix="Thư mục tài liệu Google Drive: ")
    add_p(doc, "Kế thừa trực tiếp từ URD_EventTick.docx", bold_prefix="Căn cứ phát triển: ")
    add_p(doc, "—" * 55, align=WD_ALIGN_PARAGRAPH.CENTER)

    # 1. Giới thiệu
    add_h2(doc, "1. Giới thiệu & Tổng quan Hệ thống (Introduction & System Overview)")
    add_h3(doc, "1.1. Mục đích tài liệu (Purpose)")
    add_p(doc, "Tài liệu này đặc tả chi tiết toàn bộ các yêu cầu chức năng (Functional Requirements - FR), yêu cầu phi chức năng (Non-Functional Requirements - NFR), quy tắc nghiệp vụ (Business Rules), ràng buộc dữ liệu (Data Constraints) và ma trận kiểm soát của hệ thống iTick. Đây là tài liệu căn cứ để Chủ hệ thống triển khai mã nguồn, cài đặt lỗi kiểm thử có kiểm soát, đồng thời là cơ sở duy nhất để Tester thiết kế bộ kịch bản kiểm thử thủ công, kiểm thử tự động API (Postman/Newman), kiểm thử giao diện (Puppeteer) và kiểm thử hiệu năng (JMeter).")

    add_h3(doc, "1.2. Kiến trúc & Công nghệ Thực thi (System Architecture)")
    add_bullet(doc, "Monolithic RESTful API kết hợp Server-Side Rendering (SSR).", bold_prefix="Mô hình kiến trúc: ")
    add_bullet(doc, "Python 3.11+ / FastAPI, Pydantic v2 (Validation), Uvicorn (ASGI Server), cổng chạy 8001.", bold_prefix="Backend: ")
    add_bullet(doc, "Neon Cloud PostgreSQL (SSL pooler) và SQLite 3 cục bộ dự phòng (WAL mode).", bold_prefix="Database: ")
    add_bullet(doc, "Jinja2 Templates kết hợp Tailwind CSS (Play CDN), Theme Dark Modern Mesh sang trọng.", bold_prefix="Frontend: ")
    add_bullet(doc, "JWT (JSON Web Token) HMAC-SHA256, thời hạn 60 phút, Cookie phiên HttpOnly.", bold_prefix="Authentication: ")
    add_bullet(doc, "Tích hợp kép Ví nội bộ (Internal Wallet) và Cổng thanh toán VietQR PayOS (HMAC SHA256 IPN).", bold_prefix="Thanh toán: ")

    # 2. RBAC
    add_h2(doc, "2. Ma trận Phân quyền Người dùng (RBAC - Role-Based Access Control)")
    add_p(doc, "Hệ thống phân định 4 nhóm tác nhân truy cập:")
    add_bullet(doc, "Khách vãng lai chưa đăng nhập.", bold_prefix="GUEST: ")
    add_bullet(doc, "Người tham dự / Khách hàng đã đăng nhập.", bold_prefix="ATTENDEE: ")
    add_bullet(doc, "Ban tổ chức sự kiện.", bold_prefix="ORGANIZER: ")
    add_bullet(doc, "Quản trị viên tối cao (Superadmin) với toàn quyền điều hành sàn.", bold_prefix="ADMIN: ")

    headers_rbac = ["Mã FR", "Tên chức năng", "GUEST", "ATTENDEE", "ORGANIZER", "ADMIN"]
    data_rbac = [
        ["FR-01", "Đăng ký tài khoản mới", "C", "-", "-", "-"],
        ["FR-02", "Đăng nhập & Cấp JWT Token", "R", "-", "-", "-"],
        ["FR-03", "Xem thông tin cá nhân & Đổi mật khẩu", "-", "CRUD", "CRUD", "CRUD"],
        ["FR-04", "Tìm kiếm & Lọc danh sách sự kiện", "R", "R", "R", "R"],
        ["FR-05", "Xem chi tiết sự kiện & Tồn kho vé", "R", "R", "R", "R"],
        ["FR-06", "Đặt mua vé, Tính phí sàn & Phân bổ ví", "-", "C", "C", "C"],
        ["FR-07", "Áp dụng mã giảm giá (Voucher)", "-", "R", "R", "R"],
        ["FR-08", "Xem danh sách vé cá nhân & Lấy mã vé", "-", "R", "R", "R"],
        ["FR-09", "Yêu cầu hủy vé cá nhân & Hoàn tiền mốc giờ", "-", "U", "U", "U"],
        ["FR-10", "Tạo mới & Chỉnh sửa sự kiện (Auto-Approval)", "-", "-", "CRUD", "CRUD"],
        ["FR-11", "Cấu hình phân hạng vé & Định mức kho", "-", "-", "CRUD", "CRUD"],
        ["FR-12", "Soát vé tại cổng (Check-in Scanner)", "-", "-", "U", "U"],
        ["FR-13", "Quản trị Toàn quyền (Người dùng, Đơn hàng, Vé, Sàn)", "-", "-", "-", "CRUD"],
        ["FR-14", "Báo cáo Doanh thu, Phí sàn & Đối soát Dòng tiền", "-", "-", "R (Của mình)", "R (Toàn sàn)"]
    ]
    add_styled_table(doc, headers_rbac, data_rbac, col_widths=[0.8, 2.7, 0.7, 0.9, 0.9, 0.7], num_align_cols=[0, 2, 3, 4, 5])
    add_p(doc, "(Ghi chú: C: Create, R: Read, U: Update, D: Delete, -: Không có quyền truy cập)", italic=True)

    # 3. Yêu cầu chức năng FR
    add_h2(doc, "3. Danh mục 14 Yêu cầu Chức năng Chi tiết (Functional Requirements - FR)")

    add_h3(doc, "FR-01: Đăng ký Tài khoản (User Registration)")
    add_p(doc, "Cho phép khách vãng lai đăng ký tài khoản mới trên hệ thống.", bold_prefix="Mô tả: ")
    add_p(doc, "full_name, email, password, confirm_password, role (ATTENDEE hoặc ORGANIZER).", bold_prefix="Dữ liệu đầu vào: ")
    add_p(doc, "full_name từ 2 đến 50 ký tự; email chuẩn RFC 5322 và duy nhất; password từ 6 đến 32 ký tự có ít nhất 1 chữ số; confirm_password trùng 100%.", bold_prefix="Ràng buộc xử lý: ")
    add_p(doc, "Trả về HTTP 201 Created kèm thông tin User (không gồm password) hoặc HTTP 400/422 nếu vi phạm.", bold_prefix="Đầu ra: ")

    add_h3(doc, "FR-02: Đăng nhập & Xác thực JWT (User Authentication)")
    add_p(doc, "Xác thực người dùng và cấp mã JWT Bearer Token.", bold_prefix="Mô tả: ")
    add_p(doc, "Mã hóa Bcrypt kiểm tra mật khẩu. Nếu is_active == False trả về HTTP 403 Forbidden. Thất bại quá 5 lần khóa tạm 15 phút.", bold_prefix="Ràng buộc: ")
    add_p(doc, "HTTP 200 OK kèm token và thông tin user.", bold_prefix="Đầu ra: ")

    add_h3(doc, "FR-02b: Khôi phục Mật khẩu Đa kênh (Password Reset via OTP & Token)")
    add_p(doc, "Hỗ trợ 2 cơ chế khôi phục mật khẩu linh hoạt: nhận liên kết đặt lại qua email hoặc mã OTP 6 số ngẫu nhiên có hiệu lực 15 phút.", bold_prefix="Mô tả: ")
    add_bullet(doc, "POST /api/auth/forgot-password: Tạo yêu cầu, sinh OTP 6 số và token link, gửi email.")
    add_bullet(doc, "POST /api/auth/reset-password-otp: Đặt lại mật khẩu bằng mã OTP 6 số.")
    add_bullet(doc, "POST /api/auth/reset-password: Đặt lại mật khẩu qua token link.")

    add_h3(doc, "FR-03: Quản lý Thông tin Hồ sơ (User Profile Management)")
    add_p(doc, "Người dùng xem và cập nhật thông tin cá nhân (họ tên, số điện thoại, đổi mật khẩu). Số điện thoại chuẩn VN 10 số (03, 05, 07, 08, 09).")

    add_h3(doc, "FR-04: Tìm kiếm & Lọc Danh sách Sự kiện (Event Search & Filter)")
    add_p(doc, "Tra cứu danh sách sự kiện mở bán (status = PUBLISHED, is_visible = True). Query params: keyword, category, page, limit (min 1, max 50).")

    add_h3(doc, "FR-05: Xem Chi tiết Sự kiện & Tồn kho Hạng vé (Event Details & Ticket Availability)")
    add_p(doc, "Trả về thông tin chi tiết sự kiện và tình trạng các phân hạng vé. Hạng vé có available_quantity = 0 đánh dấu is_sold_out = True.")

    add_h3(doc, "FR-06: Đặt mua Vé, Tính Phí Sàn & Phân Bổ Dòng Tiền (Booking & Revenue Allocation)")
    add_p(doc, "Người dùng chọn sự kiện, chọn hạng vé, số lượng (1 - 5 vé) và thanh toán ví hoặc PayOS.", bold_prefix="Mô tả: ")
    add_p(doc, "Kiểm tra tồn kho: available_quantity >= quantity. Giới hạn 1-5 vé/đơn và không quá 10 vé/sự kiện/tài khoản. Áp dụng phí sàn iTick mặc định 5.0%:", bold_prefix="Cơ chế Phí Sàn Nền Tảng: ")
    add_formula_block(doc, MML_PLATFORM_FEE, "Phí Sàn Nền Tảng")
    add_formula_block(doc, MML_ORGANIZER_AMOUNT, "Doanh Thu Ban Tổ Chức")
    add_p(doc, "Đơn hàng miễn phí (final_amount = 0) thì platform_fee = 0 và organizer_amount = 0.")

    add_h3(doc, "FR-07: Áp dụng Mã Giảm giá (Voucher Validation & Calculation)")
    add_p(doc, "Kiểm tra tính hợp lệ của mã giảm giá (is_active, thời hạn, lượt dùng, min_order_value). Giảm theo % áp dụng trần max_discount_cap; giảm theo số tiền cố định fixed_amount.")

    add_h3(doc, "FR-08: Xem Vé Cá nhân & Lấy Mã Vé Điện tử (My Tickets & QR E-Ticket)")
    add_p(doc, "Xem danh sách vé thuộc sở hữu của User đang đăng nhập kèm mã vé độc nhất TICK-XXXXXXXX và mã QR Base64.")

    add_h3(doc, "FR-09: Yêu cầu Hủy vé Cá nhân & Tính phí Hoàn tiền (Ticket Cancellation & Refund)")
    add_p(doc, "Chỉ hủy vé ở trạng thái CONFIRMED/VALID. Trước >= 48h phí hủy 10% (hoàn 90%); từ 24h đến < 48h phí hủy 30% (hoàn 70%); dưới 24h từ chối hủy. Sau khi hủy, available_quantity += 1.")

    add_h3(doc, "FR-10: Tạo mới Sự kiện & Cơ chế Phê duyệt Tự động (Event Creation & Auto-Approval)")
    add_p(doc, "Ban tổ chức khởi tạo sự kiện. Hệ thống tự động thẩm định và cấp trạng thái PUBLISHED, is_visible = True ngay lập tức.")

    add_h3(doc, "FR-11: Cấu hình Phân hạng Vé (Ticket Tier Setup)")
    add_p(doc, "Thiết lập các gói vé (VIP, Standard). Giá vé 0 đến 50.000.000đ; số lượng 1 đến 5.000 vé; tổng vé không vượt quá capacity sự kiện.")

    add_h3(doc, "FR-12: Soát vé tại Cổng Sự kiện (Ticket Check-in Verification)")
    add_p(doc, "Quét mã vé tại cổng. Nếu CONFIRMED chuyển sang CHECKED_IN. Nếu CHECKED_IN trả về 409 Conflict. Nếu CANCELLED trả về 400 Bad Request.")

    add_h3(doc, "FR-12b: Xuất Danh Sách Soát Vé & Đối Soát Timeline Điểm Danh")
    add_p(doc, "Xuất file Excel (.xlsx) chuẩn đẹp với Data Validation Dropdown ở cột Trạng Thái Soát Vé (ĐÃ THAM DỰ, VẮNG MẶT, CHƯA CHECK-IN, ĐÃ HỦY VÉ). Hỗ trợ CSV UTF-8 BOM và JSON API.")

    add_h3(doc, "FR-13: Quản trị Hệ thống Toàn diện (Superadmin Control Center)")
    add_bullet(doc, "Quản trị Người dùng & Phân quyền (RBAC): Xem danh sách, tạo mới, đổi role, reset mật khẩu, khóa/mở tài khoản.", bold_prefix="1. ")
    add_bullet(doc, "Quản trị Sự kiện Toàn sàn: Duyệt sự kiện, từ chối sự kiện, ẩn/hiện và xóa sự kiện.", bold_prefix="2. ")
    add_bullet(doc, "Quản trị Đơn hàng & Hủy đơn Khẩn cấp: Hủy đơn hoàn 100% tiền cho khách, tự động thu hồi tiền ví BTC, trừ phí sàn, hoàn tồn kho.", bold_prefix="3. ")
    add_bullet(doc, "Quản trị Vé Toàn sàn: Tra cứu vé và vô hiệu hóa vé gian lận (POST /api/admin/tickets/{id}/void).", bold_prefix="4. ")
    add_bullet(doc, "Cấu hình Phí Sàn Nền tảng: Tra cứu và cập nhật tỷ lệ phí sàn (GET/PUT /api/admin/system/fee).", bold_prefix="5. ")

    add_h3(doc, "FR-14: Báo cáo Thống kê Doanh thu & Đối soát Dòng tiền (Financial Reconciliation)")
    add_p(doc, "Thống kê doanh thu gộp, phân rã kênh VietQR PayOS vs Ví nội bộ, phí sàn 5%, chi trả BTC, tỷ lệ check-in cổng. Bảo toàn dòng tiền đối soát sàn tuyệt đối:")
    add_formula_block(doc, MML_RECONCILIATION, "Bảo toàn Doanh thu Gộp")
    add_formula_block(doc, MML_VARIANCE, "Độ lệch Đối soát")

    # 4. Use Cases
    add_h2(doc, "4. Đặc tả 5 Luồng Nghiệp vụ Hoàn chỉnh (Use Cases: Main, Alternative, Exception Flows)")
    add_h3(doc, "USE CASE 01: Đặt mua Vé & Phân Bổ Dòng Tiền (FLOW-01)")
    add_p(doc, "Tác nhân: Khách tham dự (Attendee). Điều kiện: Sự kiện PUBLISHED, vé còn chỗ.")
    add_bullet(doc, "1. Chọn sự kiện, chọn hạng vé và số lượng (1 - 5 vé).")
    add_bullet(doc, "2. Nhập mã voucher giảm giá (nếu có).")
    add_bullet(doc, "3. Chọn phương thức thanh toán: Ví nội bộ hoặc VietQR PayOS.")
    add_bullet(doc, "4. Hệ thống tạo Transaction: Trừ tồn kho vé, tính phí sàn 5%, tính organizer_amount, cộng ví BTC, trừ tiền khách.")
    add_bullet(doc, "5. Xuất vé điện tử QR Code và chuyển đến trang đặt vé thành công.")

    add_h3(doc, "USE CASE 02: Khởi tạo Sự kiện & Cấu hình Phân Hạng Vé (FLOW-02)")
    add_p(doc, "Tác nhân: Ban tổ chức (Organizer). Ban tổ chức điền form tạo sự kiện, hệ thống tự động kiểm tra và cấp PUBLISHED mở bán. Ban tổ chức tạo các hạng vé Standard, VIP.")

    add_h3(doc, "USE CASE 03: Soát Vé Tại Cổng Sự Kiện (FLOW-03)")
    add_p(doc, "Tác nhân: Nhân viên soát vé / BTC. Quét QR code tại /checkin-gate. Nếu hợp lệ đổi sang CHECKED_IN. Nếu vé đã dùng báo 409 Conflict; vé đã hủy báo 400 Bad Request.")

    add_h3(doc, "USE CASE 04: Hủy Vé & Hoàn Tiền Vào Ví (FLOW-04)")
    add_p(doc, "Tác nhân: Khách tham dự. Hủy vé trước >= 48h hoàn 90%; 24h đến < 48h hoàn 70%; dưới 24h từ chối hủy. Vé chuyển CANCELLED, hoàn tồn kho vé (+1 available_quantity).")

    add_h3(doc, "USE CASE 05: Thanh toán Trực tuyến Qua Cổng PayOS (FLOW-05)")
    add_p(doc, "Tác nhân: Khách tham dự, Cổng thanh toán PayOS. Tạo link VietQR PayOS -> Khách quét mã -> PayOS gửi Webhook IPN -> Hệ thống xác thực HMAC SHA256 -> Kích hoạt vé và cộng ví BTC.")

    # 5. Quy tắc nghiệp vụ BR
    add_h2(doc, "5. Quy tắc Nghiệp vụ (Business Rules - BR)")
    add_bullet(doc, "Mỗi tài khoản người dùng chỉ được đặt tối đa 5 vé trong 1 giao dịch và không quá 10 vé cho cùng một sự kiện.", bold_prefix="BR-01 (Giới hạn đặt vé): ")
    add_bullet(doc, "Thao tác trừ vé phải sử dụng kiểm soát cạnh tranh (Database Atomic Update hoặc Locking) để đảm bảo không xảy ra hiện tượng bán âm kho (Overselling).", bold_prefix="BR-02 (Cạnh tranh tài nguyên - Concurrency): ")
    add_bullet(doc, "Mỗi đơn hàng chỉ được sử dụng tối đa 1 mã giảm giá. Mức giảm tối đa không vượt quá max_discount_cap.", bold_prefix="BR-03 (Chính sách Voucher): ")
    add_bullet(doc, "Vé đã chuyển sang trạng thái CHECKED_IN hoặc CANCELLED là trạng thái cuối (Terminal State), không thể đổi ngược lại trạng thái CONFIRMED.", bold_prefix="BR-04 (Bất biến trạng thái vé): ")
    
    add_p(doc, "Quy định tỷ lệ hoàn tiền theo khoảng thời gian đến sự kiện:", bold_prefix="BR-05 (Chính sách phí phạt hủy vé cá nhân): ")
    add_formula_block(doc, MML_PIECEWISE_REFUND, "Công thức Hoàn tiền Hủy vé")

    add_bullet(doc, "Tiền tệ VNĐ không có số thập phân lẻ. Mọi phép tính phí sàn bắt buộc dùng hàm round() sang số nguyên gần nhất. Sự kiện 0đ không thu phí sàn. Phí sàn tính trên final_amount.", bold_prefix="BR-06 (Quy tắc Tính Phí Sàn & Làm tròn Tiền tệ): ")
    add_bullet(doc, "Khi Superadmin hủy đơn khẩn cấp, khách hàng được hoàn đủ 100% số tiền đã trả. Ban tổ chức bị khấu trừ lại đúng khoản tiền organizer_amount đã nhận vào ví.", bold_prefix="BR-07 (Quy tắc Hoàn tiền Khẩn cấp của Superadmin): ")

    # 6. Ràng buộc dữ liệu
    add_h2(doc, "6. Ràng buộc Dữ liệu Đo lường được (Testable Data Constraints)")
    headers_dc = ["Trường dữ liệu", "Kiểu dữ liệu", "Giá trị hợp lệ (Valid Boundary)", "Giá trị không hợp lệ (Invalid Boundary)", "Thông báo lỗi tương ứng"]
    rows_dc = [
        ["email", "String", "Format RFC 5322, dài từ 6 đến 100 ký tự", "test, test@, test@domain, dài > 100 ký tự", "Email không đúng định dạng chuẩn."],
        ["password", "String", "6 đến 32 ký tự, có ít nhất 1 chữ số", "Dưới 6 ký tự, trên 32 ký tự, không có số", "Mật khẩu phải từ 6 đến 32 ký tự và có ít nhất 1 chữ số."],
        ["phone_number", "String", "10 chữ số, bắt đầu: 03, 05, 07, 08, 09", "9 chữ số, 11 chữ số, chứa chữ cái", "Số điện thoại không hợp lệ."],
        ["event_title", "String", "5 đến 150 ký tự", "< 5 ký tự, > 150 ký tự", "Tiêu đề sự kiện phải từ 5 đến 150 ký tự."],
        ["capacity", "Integer", "10 <= capacity <= 10,000", "9, 0, âm, 10,001", "Sức chứa sự kiện phải từ 10 đến 10,000 người."],
        ["ticket_price", "Integer", "0 <= price <= 50,000,000 VNĐ", "-1, 50,000,001", "Giá vé phải từ 0 đến 50,000,000 VNĐ."],
        ["ticket_quantity", "Integer", "1 <= qty <= 5 (trên 1 đơn)", "0, -1, 6", "Số lượng vé mỗi đơn phải từ 1 đến 5 vé."],
        ["voucher_discount", "Integer", "1 <= discount <= 100 (%)", "0, 101, âm", "Tỷ lệ giảm giá phải từ 1% đến 100%."],
        ["platform_fee_rate", "Float", "0.0 <= rate <= 100.0 (%)", "Âm, > 100.0", "Tỷ lệ phí sàn phải từ 0% đến 100%."]
    ]
    add_styled_table(doc, headers_dc, rows_dc, col_widths=[1.2, 0.8, 1.8, 1.4, 1.5], num_align_cols=[0, 1])

    # 7. NFRs
    add_h2(doc, "7. Yêu cầu Phi chức năng Chi tiết (Non-Functional Requirements - NFR)")
    add_h3(doc, "7.1. Nhóm NFR Hiệu năng (Performance NFRs)")
    add_p(doc, "Thời gian phản hồi API tra cứu sự kiện dưới tải 50 CCU:", bold_prefix="NFR-01: ")
    add_formula_block(doc, MML_NFR01, "Tiêu chuẩn p95 tra cứu")
    add_p(doc, "Thời gian phản hồi & Tính toàn vẹn khi Đặt vé Cạnh tranh tải 100 CCU:", bold_prefix="NFR-02: ")
    add_formula_block(doc, MML_NFR02, "Tiêu chuẩn p90 cạnh tranh vé")
    add_bullet(doc, "Throughput >= 80 req/s trên cấu hình 1 vCPU, 512MB RAM.", bold_prefix="NFR-03 (Thông lượng Xử lý): ")
    add_bullet(doc, "Thời gian phản hồi trung bình <= 400 ms cho 20 trạm soát vé đồng thời.", bold_prefix="NFR-04 (Hiệu năng API Soát vé Check-in): ")

    add_h3(doc, "7.2. Nhóm NFR Vận hành, Bảo mật & Tương thích")
    add_bullet(doc, "Mật khẩu băm Bcrypt work factor >= 12; Token JWT HMAC-SHA256 hết hạn 24 giờ; ngăn chặn SQL Injection qua ORM parameterized.", bold_prefix="NFR-05 (Bảo mật & Xác thực): ")
    add_bullet(doc, "Hệ thống duy trì hoạt động trên cloud Render và local cổng 8001, endpoint /health phản hồi < 100 ms.", bold_prefix="NFR-06 (Tính khả dụng & Port hoạt động): ")
    add_bullet(doc, "Responsive trên màn hình di động >= 375 px, giao diện Dark Modern Mesh sang trọng, tối ưu hiển thị cho sự kiện âm nhạc và giải trí.", bold_prefix="NFR-07 (Tính tương thích Giao diện): ")
    add_bullet(doc, "100% API cung cấp đặc tả OpenAPI 3.0 tại /openapi.json và giao diện tương tác Swagger UI tại /docs.", bold_prefix="NFR-08 (Khả năng Kiểm thử & Chuẩn hóa API): ")

    add_h3(doc, "7.3. Mô hình Định giá Tài chính & Hiệu quả Dự án Nâng cao (Financial Valuation Models)")
    add_p(doc, "Mô hình Hiện giá Thuần (Net Present Value - NPV) dùng trong hoạch định tài chính dự án:")
    add_formula_block(doc, MML_NPV, "Công thức NPV")
    add_p(doc, "Mô hình Chi phí Vốn Bình quân Gia quyền (Weighted Average Cost of Capital - WACC):")
    add_formula_block(doc, MML_WACC, "Công thức WACC")

    # 8. Ma trận truy vết
    add_h2(doc, "8. Ma trận Truy vết Yêu cầu (Traceability Matrix: URD <-> SRS)")
    headers_tm = ["Mã User Story (URD)", "Tên User Story", "Mã SRS Chức năng (FR)", "Mã Luồng nghiệp vụ", "Mã NFR liên quan"]
    rows_tm = [
        ["US-01", "Đăng ký tài khoản", "FR-01", "-", "NFR-05, NFR-08"],
        ["US-02", "Đăng nhập hệ thống", "FR-02, FR-02b", "-", "NFR-05, NFR-08"],
        ["US-03", "Tìm kiếm & lọc sự kiện", "FR-04", "FLOW-01", "NFR-01, NFR-03"],
        ["US-04", "Xem chi tiết sự kiện", "FR-05", "FLOW-01", "NFR-01, NFR-07"],
        ["US-05", "Đặt mua vé & Phân bổ dòng tiền", "FR-06", "FLOW-01", "NFR-02, NFR-03, NFR-08"],
        ["US-06", "Nhập mã giảm giá Voucher", "FR-07", "FLOW-01", "NFR-08"],
        ["US-07", "Xem vé đã mua & mã QR", "FR-08", "FLOW-01", "NFR-07, NFR-08"],
        ["US-08", "Yêu cầu hủy vé hoàn tiền", "FR-09", "FLOW-04", "NFR-08"],
        ["US-09", "Tạo sự kiện mới (Auto-Approval)", "FR-10", "FLOW-02", "NFR-05, NFR-08"],
        ["US-10", "Cấu hình phân hạng vé", "FR-11", "FLOW-02", "NFR-08"],
        ["US-11", "Soát vé tại cổng", "FR-12", "FLOW-03", "NFR-04, NFR-08"],
        ["US-12", "Thống kê doanh thu & Đối soát phí", "FR-14", "-", "NFR-01, NFR-08"],
        ["US-13", "Superadmin Quản trị Toàn quyền", "FR-13", "-", "NFR-05, NFR-08"],
        ["US-14", "Quản trị Sự kiện & Vé Điện tử Toàn sàn", "FR-07, FR-13", "-", "NFR-05, NFR-08"],
        ["US-15", "Cấu hình Phí Sàn & Đối soát Dòng tiền", "FR-13, FR-14", "-", "NFR-06, NFR-08"],
        ["US-12b", "Xuất File Excel Danh Sách Soát Vé", "FR-12b", "FLOW-03", "NFR-01, NFR-08"]
    ]
    add_styled_table(doc, headers_tm, rows_tm, col_widths=[1.2, 2.2, 1.2, 1.0, 1.1], num_align_cols=[0, 2, 3, 4])

    # 9. Changelog
    add_h2(doc, "9. Lịch Sử Cập Nhật Tài Liệu (Changelog)")
    headers_cl = ["Phiên bản", "Ngày cập nhật", "Tác giả", "Nội dung thay đổi chính"]
    rows_cl = [
        ["v1.0", "Tuần 5", f"{AUTHOR_NAME} ({AUTHOR_MSSV})", "Khởi tạo tài liệu đặc tả ban đầu theo mẫu SRS chuẩn IEEE 830."],
        ["v1.1", "Tuần 6", f"{AUTHOR_NAME} ({AUTHOR_MSSV})", "Tiếp thu phiếu review của Tester: Bổ sung 4 NFR hiệu năng đo lường được, làm rõ quy tắc Concurrency BR-02 và mốc hủy vé BR-05."],
        ["v1.2", "27/10/2026", f"{AUTHOR_NAME} ({AUTHOR_MSSV})", "Nâng cấp Hệ thống iTick: Đồng bộ thương hiệu iTick; Auto-Approval; Phí Sàn 5%; Cổng Superadmin Toàn quyền 5 tabs; Mở rộng 39 endpoints / 44 operations; Đồng bộ link Deploy Render và Google Drive."]
    ]
    add_styled_table(doc, headers_cl, rows_cl, col_widths=[0.8, 1.1, 1.8, 3.0], num_align_cols=[0, 1])

print("build_srs_content appended successfully!")

# ==============================================================================
# PHẦN 4: TÀI LIỆU API (API SPECIFICATION)
# ==============================================================================
def build_api_content(doc):
    add_h1(doc, "TÀI LIỆU API (API SPECIFICATION)")
    add_p(doc, f"Hệ thống: iTick - Nền tảng Đăng ký & Bán vé Sự kiện Trực tuyến  ·  Phiên bản: 1.2.0  ·  Người lập: {AUTHOR_NAME} (MSSV: {AUTHOR_MSSV})  ·  Ngày: 27/10/2026", align=WD_ALIGN_PARAGRAPH.CENTER, italic=True)
    add_p(doc, "Hướng dẫn: Tài liệu này giúp tester viết collection Postman/Newman và đo tải Apache JMeter mà không cần xem mã nguồn. Tài liệu liệt kê ĐẦY ĐỦ 100% tất cả 39 endpoints (44 API operations) của hệ thống iTick, trả về JSON chuẩn RESTful. Mọi ràng buộc dữ liệu khớp 100% với SRS_EventTick.docx.", italic=True)
    add_p(doc, "—" * 55, align=WD_ALIGN_PARAGRAPH.CENTER)

    # 1. Thông tin chung
    add_h2(doc, "1. Thông tin chung")
    headers_info = ["Thuộc tính", "Giá trị thiết lập"]
    rows_info = [
        ["Base URL", f"Cloud Deploy: {DEPLOY_LINK} (Local fallback: http://127.0.0.1:8001)"],
        ["Định dạng dữ liệu", "JSON, mã hoá UTF-8. Header: Content-Type: application/json"],
        ["Cơ chế xác thực", "Bearer token (JWT) trong header Authorization: Bearer <token> và Cookie phiên access_token"],
        ["Cách lấy token", "Gọi POST /api/auth/login, lấy trường access_token trong JSON response"],
        ["Thời hạn token", "60 phút (3600 giây)"],
        ["Định dạng ngày giờ", "ISO 8601 (YYYY-MM-DDTHH:MM:SS), ví dụ: 2026-10-15T19:30:00"],
        ["Phân trang (nếu có)", "Tham số page (bắt đầu từ 1), limit (mặc định 10, tối đa 50)"],
        ["Link Swagger / OpenAPI", f"Cloud: {DEPLOY_LINK}docs (Local: http://127.0.0.1:8001/docs)"],
        ["Thư mục tài liệu Google Drive", DRIVE_LINK],
        ["Kho mã nguồn GitHub", GITHUB_LINK]
    ]
    add_styled_table(doc, headers_info, rows_info, col_widths=[2.4, 4.3])

    # 2. Mã lỗi chung
    add_h2(doc, "2. Mã lỗi chung")
    headers_err = ["Mã HTTP", "Ý nghĩa", "Body mẫu"]
    rows_err = [
        ["200", "Thành công (OK)", '{"success": true, "data": ...}'],
        ["201", "Tạo mới thành công (Created)", '{"id": 1, "order_code": "ORD-20261009-XXXX", "status": "CONFIRMED"}'],
        ["400", "Dữ liệu không hợp lệ / Vi phạm quy tắc (Bad Request)", '{"detail": "Số lượng vé mỗi đơn hàng phải từ 1 đến 5 vé."}'],
        ["401", "Chưa đăng nhập / Token hết hạn (Unauthorized)", '{"detail": "Chưa đăng nhập hoặc phiên làm việc đã hết hạn"}'],
        ["403", "Không có quyền thực hiện thao tác (Forbidden)", '{"detail": "Bạn không có quyền thực hiện thao tác này"}'],
        ["404", "Không tìm thấy tài nguyên (Not Found)", '{"detail": "Sự kiện không tồn tại"}'],
        ["409", "Xung đột dữ liệu / Vé đã dùng (Conflict)", '{"detail": "VÉ ĐÃ SỬ DỤNG VÀO LÚC 19:30:15 09/10/2026"}'],
        ["500", "Lỗi máy chủ nội bộ (Internal Server Error)", '{"detail": "Internal server error"}']
    ]
    add_styled_table(doc, headers_err, rows_err, col_widths=[0.9, 2.5, 3.3], num_align_cols=[0])

    # 3. Danh sách 44 operations
    add_h2(doc, "3. Danh sách endpoint đầy đủ (39 endpoints / 44 operations)")
    headers_ops = ["STT", "Method", "Endpoint", "Mô tả", "Chức năng", "Vai trò"]
    rows_ops = [
        ["1", "POST", "/api/auth/register", "Đăng ký tài khoản người dùng mới", "FR-01", "Khách vãng lai"],
        ["2", "POST", "/api/auth/login", "Đăng nhập hệ thống & cấp JWT Bearer token", "FR-02", "Tất cả"],
        ["3", "POST", "/api/auth/logout", "Đăng xuất khỏi hệ thống và vô hiệu hóa phiên", "FR-02", "Đã đăng nhập"],
        ["4", "GET", "/api/auth/me", "Lấy thông tin tài khoản hiện tại & số dư ví", "FR-01/02", "Đã đăng nhập"],
        ["5", "POST", "/api/auth/forgot-password", "Gửi liên kết khôi phục mật khẩu qua email", "FR-02b", "Khách vãng lai"],
        ["6", "POST", "/api/auth/reset-password", "Đặt lại mật khẩu mới qua token liên kết", "FR-02b", "Khách vãng lai"],
        ["7", "POST", "/api/auth/reset-password-otp", "Đặt lại mật khẩu bằng mã OTP 6 số", "FR-02b", "Khách vãng lai"],
        ["8", "GET", "/api/events", "Tra cứu danh sách sự kiện, tìm kiếm, lọc danh mục", "FR-04", "Tất cả"],
        ["9", "POST", "/api/events", "Tạo sự kiện mới (Hỗ trợ Tự duyệt Auto-Approval)", "FR-10", "BTC, Admin"],
        ["10", "GET", "/api/events/{event_id}", "Xem chi tiết sự kiện & danh sách phân hạng vé", "FR-05", "Tất cả"],
        ["11", "PUT", "/api/events/{event_id}", "Cập nhật thông tin bài đăng sự kiện", "FR-10", "BTC, Admin"],
        ["12", "DELETE", "/api/events/{event_id}", "Xóa bài đăng sự kiện khỏi hệ thống", "FR-10", "BTC, Admin"],
        ["13", "POST", "/api/events/{event_id}/tiers", "Thêm phân hạng vé mở bán (VIP, Standard...)", "FR-11", "BTC, Admin"],
        ["14", "GET", "/api/events/{event_id}/export-attendees", "Xuất file Excel (.xlsx có dropdown) / CSV / JSON đối soát", "FR-12b", "BTC, Admin"],
        ["15", "POST", "/api/bookings/vouchers/apply", "Kiểm tra tính hợp lệ & tính giảm giá của Voucher", "FR-07", "Tất cả"],
        ["16", "POST", "/api/bookings", "Đặt mua vé, tính phí sàn 5%, phân bổ ví BTC", "FR-06", "Attendee, Admin"],
        ["17", "GET", "/api/bookings/my-tickets", "Xem danh sách vé điện tử cá nhân & mã QR", "FR-08", "Attendee"],
        ["18", "POST", "/api/bookings/{ticket_id}/cancel", "Hủy vé cá nhân & hoàn tiền theo mốc thời gian", "FR-09", "Attendee, Admin"],
        ["19", "POST", "/api/check-in", "Xác thực & soát vé tại cổng qua mã định danh/QR", "FR-12", "BTC, Admin"],
        ["20", "GET", "/api/payment/payos-return", "Xử lý redirect khi khách thanh toán PayOS thành công", "FLOW-05", "Attendee"],
        ["21", "GET", "/api/payment/payos-cancel", "Xử lý redirect khi khách hủy thanh toán PayOS", "FLOW-05", "Attendee"],
        ["22", "POST", "/api/payment/payos-webhook", "Tiếp nhận webhook IPN thanh toán từ cổng PayOS", "FLOW-05", "PayOS Gateway"],
        ["23", "GET", "/api/payment/status/{order_code}", "Tra cứu trạng thái giao dịch thanh toán đơn hàng", "FLOW-05", "Attendee"],
        ["24", "GET", "/api/admin/stats", "Báo cáo doanh thu gộp, phí sàn, chi trả BTC", "FR-14", "Admin"],
        ["25", "GET", "/api/admin/events/pending", "Lấy danh sách sự kiện chờ phê duyệt", "FR-13", "Admin"],
        ["26", "POST", "/api/admin/events/{event_id}/approve", "Phê duyệt sự kiện công khai trên trang chủ", "FR-13", "Admin"],
        ["27", "POST", "/api/admin/events/{event_id}/reject", "Từ chối duyệt sự kiện vi phạm tiêu chuẩn", "FR-13", "Admin"],
        ["28", "POST", "/api/admin/events/{event_id}/status", "Thay đổi trạng thái sự kiện (PUBLISHED/HIDDEN/CANCELLED)", "FR-13", "Admin"],
        ["29", "PUT", "/api/admin/events/{event_id}", "Admin cập nhật thông tin sự kiện bất kỳ", "FR-13", "Admin"],
        ["30", "DELETE", "/api/admin/events/{event_id}", "Admin xóa bài đăng sự kiện vi phạm", "FR-13", "Admin"],
        ["31", "GET", "/api/admin/orders", "Tra cứu và quản trị toàn bộ đơn hàng trên sàn", "FR-13", "Admin"],
        ["32", "POST", "/api/admin/orders/{order_id}/cancel-refund", "Hủy đơn khẩn cấp & hoàn tiền 100% (thu hồi ví BTC)", "FR-13", "Admin"],
        ["33", "GET", "/api/admin/tickets", "Tra cứu danh sách vé điện tử toàn hệ thống", "FR-13", "Admin"],
        ["34", "PUT", "/api/admin/users/{user_id}/role", "Phân quyền người dùng (ATTENDEE / ORGANIZER / ADMIN)", "FR-13", "Admin"],
        ["35", "POST", "/api/admin/users/{user_id}/toggle-active", "Khóa hoặc kích hoạt lại tài khoản người dùng", "FR-13", "Admin"],
        ["36", "POST", "/api/admin/users/{user_id}/reset-password", "Admin đặt lại mật khẩu cho tài khoản người dùng", "FR-13", "Admin"],
        ["37", "POST", "/api/admin/users/{user_id}/adjust-balance", "Điều chỉnh cộng/trừ số dư ví tài khoản", "FR-13", "Admin"],
        ["38", "POST", "/api/admin/vouchers", "Khởi tạo chiến dịch mã giảm giá Voucher mới", "FR-13", "Admin"],
        ["39", "POST", "/api/admin/vouchers/{voucher_id}/toggle", "Bật/tắt trạng thái hiệu lực của Voucher", "FR-13", "Admin"],
        ["40", "DELETE", "/api/admin/vouchers/{voucher_id}", "Xóa mã voucher khỏi hệ thống", "FR-13", "Admin"],
        ["41", "GET", "/api/admin/system/fee", "Tra cứu tỷ lệ phần trăm phí sàn hiện tại", "FR-13", "Admin"],
        ["42", "PUT", "/api/admin/system/fee", "Cập nhật cấu hình tỷ lệ phần trăm phí sàn mới", "FR-13", "Admin"],
        ["43", "GET", "/health", "Kiểm tra tình trạng hoạt động của máy chủ và bẫy lỗi", "NFR-06", "Tất cả"],
        ["44", "POST", "/api/admin/tickets/{ticket_id}/void", "Vô hiệu hóa vé gian lận đơn lẻ", "FR-13", "Admin"]
    ]
    add_styled_table(doc, headers_ops, rows_ops, col_widths=[0.5, 0.8, 2.3, 1.8, 0.7, 0.9], num_align_cols=[0, 1, 4])

    # 4. Chi tiết một số Endpoint chính
    add_h2(doc, "4. Đặc tả chi tiết từng endpoint trọng yếu")
    
    # 4.1 Register
    add_h3(doc, "4.1. [POST /api/auth/register] – Đăng ký tài khoản người dùng mới")
    t_reg = [
        ["Method + URL", f"POST {DEPLOY_LINK}api/auth/register"],
        ["Mô tả nghiệp vụ", "Đăng ký tài khoản người dùng mới"],
        ["Chức năng liên quan", "FR-01 (Quy chuẩn hệ thống iTick)"],
        ["Vai trò được phép", "Khách vãng lai"],
        ["Headers", "Content-Type: application/json"]
    ]
    add_styled_table(doc, ["Mục", "Nội dung"], t_reg, col_widths=[2.0, 4.7])
    add_p(doc, 'Body mẫu: {"full_name": "Nguyễn Văn A", "email": "user@example.com", "password": "password123", "role": "ATTENDEE"}', italic=True)

    # 4.2 Login
    add_h3(doc, "4.2. [POST /api/auth/login] – Đăng nhập hệ thống & cấp JWT Bearer token")
    t_login = [
        ["Method + URL", f"POST {DEPLOY_LINK}api/auth/login"],
        ["Mô tả nghiệp vụ", "Đăng nhập hệ thống & cấp JWT Bearer token"],
        ["Chức năng liên quan", "FR-02 (Quy chuẩn hệ thống iTick)"],
        ["Vai trò được phép", "Tất cả"],
        ["Headers", "Content-Type: application/json"]
    ]
    add_styled_table(doc, ["Mục", "Nội dung"], t_login, col_widths=[2.0, 4.7])
    add_p(doc, 'Body mẫu: {"email": "attendee@eventtick.com", "password": "Password123!"}', italic=True)

    # 4.16 Booking
    add_h3(doc, "4.3. [POST /api/bookings] – Đặt mua vé, tính phí sàn 5%, phân bổ ví BTC")
    t_book = [
        ["Method + URL", f"POST {DEPLOY_LINK}api/bookings"],
        ["Mô tả nghiệp vụ", "Đặt mua vé, tính phí sàn 5%, phân bổ ví BTC"],
        ["Chức năng liên quan", "FR-06 (Quy chuẩn hệ thống iTick)"],
        ["Vai trò được phép", "Attendee, Admin"],
        ["Headers", "Authorization: Bearer <token>\nContent-Type: application/json"]
    ]
    add_styled_table(doc, ["Mục", "Nội dung"], t_book, col_widths=[2.0, 4.7])
    add_p(doc, 'Body mẫu: {"event_id": 1, "tier_id": 2, "quantity": 2, "voucher_code": "SUMMER2026", "payment_method": "WALLET"}', italic=True)

    # 4.19 Check-in
    add_h3(doc, "4.4. [POST /api/check-in] – Xác thực & soát vé tại cổng qua mã định danh/QR")
    t_check = [
        ["Method + URL", f"POST {DEPLOY_LINK}api/check-in"],
        ["Mô tả nghiệp vụ", "Xác thực & soát vé tại cổng qua mã định danh/QR"],
        ["Chức năng liên quan", "FR-12 (Quy chuẩn hệ thống iTick)"],
        ["Vai trò được phép", "BTC, Admin"],
        ["Headers", "Authorization: Bearer <token>\nContent-Type: application/json"]
    ]
    add_styled_table(doc, ["Mục", "Nội dung"], t_check, col_widths=[2.0, 4.7])
    add_p(doc, 'Body mẫu: {"ticket_code": "TCK-2026-SK1-001", "event_id": 1}', italic=True)

    # 5. Tài khoản mẫu
    add_h2(doc, "5. Tài khoản mẫu dùng để gọi API (Test Credentials)")
    headers_cred = ["Vai trò", "Email / Tên đăng nhập", "Mật khẩu", "Ghi chú & Quyền hạn"]
    rows_cred = [
        ["Quản trị viên (Admin)", "admin@eventtick.com", "Password123!", "Quản trị toàn sàn, duyệt sự kiện, đối soát hoàn tiền khẩn cấp, cấu hình phí sàn."],
        ["Ban tổ chức (Organizer)", "organizer@eventtick.com", "Password123!", "Tạo sự kiện, cấu hình phân hạng vé, xuất Excel soát vé có Dropdown, check-in cổng."],
        ["Người mua vé 1 (Attendee)", "attendee@eventtick.com", "Password123!", "Khách hàng mua vé, áp voucher, hủy vé cá nhân. Số dư ví: 5.000.000đ."],
        ["Người mua vé 2 (Attendee)", "student_b@eventtick.com", "Password123!", "Tài khoản tester thực hiện đo tải đồng thời JMeter. Số dư ví: 5.000.000đ."],
        ["Khách vãng lai (Guest)", "Không cần đăng nhập", "-", "Tra cứu danh sách sự kiện công khai, tìm kiếm và xem chi tiết chương trình."]
    ]
    add_styled_table(doc, headers_cred, rows_cred, col_widths=[1.5, 2.0, 1.2, 2.3], num_align_cols=[0])

print("build_api_content appended successfully!")

# ==============================================================================
# HÀM TẠO VÀ XUẤT CÁC FILE WORD THEO YÊU CẦU
# ==============================================================================
def main():
    docs_dir = r"D:\SJ_Testing\Project\docs"
    os.makedirs(docs_dir, exist_ok=True)
    
    print("\n>>> 1. Đang tạo Master Document: Ho_so_Kiem_thu_iTick_Chuan_Word.docx...")
    doc_master = docx.Document()
    apply_doc_standards(doc_master)
    build_urd_content(doc_master)
    doc_master.add_page_break()
    build_handover_content(doc_master)
    doc_master.add_page_break()
    build_srs_content(doc_master)
    doc_master.add_page_break()
    build_api_content(doc_master)
    
    path_master = os.path.join(docs_dir, "Ho_so_Kiem_thu_iTick_Chuan_Word.docx")
    doc_master.save(path_master)
    print(f" -> Đã lưu thành công: {path_master}")

    print("\n>>> 2. Đang tạo URD Document: URD_EventTick.docx...")
    doc_urd = docx.Document()
    apply_doc_standards(doc_urd)
    build_urd_content(doc_urd)
    path_urd = os.path.join(docs_dir, "URD_EventTick.docx")
    doc_urd.save(path_urd)
    print(f" -> Đã lưu thành công: {path_urd}")

    print("\n>>> 3. Đang tạo Handover Document: Bien_ban_ban_giao.docx & Mau_06...")
    doc_hb = docx.Document()
    apply_doc_standards(doc_hb)
    build_handover_content(doc_hb)
    path_bb = os.path.join(docs_dir, "Bien_ban_ban_giao.docx")
    doc_hb.save(path_bb)
    shutil.copy2(path_bb, os.path.join(docs_dir, "Mau_06_Bien_ban_ban_giao.docx"))
    print(f" -> Đã lưu thành công: {path_bb}")

    print("\n>>> 4. Đang tạo SRS Document: SRS_EventTick.docx...")
    doc_srs = docx.Document()
    apply_doc_standards(doc_srs)
    build_srs_content(doc_srs)
    path_srs = os.path.join(docs_dir, "SRS_EventTick.docx")
    doc_srs.save(path_srs)
    print(f" -> Đã lưu thành công: {path_srs}")

    print("\n>>> 5. Đang tạo API Document: Tai_lieu_API.docx & Mau_01...")
    doc_api = docx.Document()
    apply_doc_standards(doc_api)
    build_api_content(doc_api)
    path_api = os.path.join(docs_dir, "Tai_lieu_API.docx")
    doc_api.save(path_api)
    shutil.copy2(path_api, os.path.join(docs_dir, "Mau_01_Tai_lieu_API.docx"))
    print(f" -> Đã lưu thành công: {path_api}")

    print("\n=======================================================")
    print("HOÀN THÀNH 100% CÁC FILE WORD CHUẨN ĐỊNH DẠNG THEO YÊU CẦU!")
    print("=======================================================")

if __name__ == "__main__":
    main()

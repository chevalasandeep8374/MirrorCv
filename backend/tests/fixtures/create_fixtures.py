import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

FIXTURES_DIR = os.path.dirname(os.path.abspath(__file__))


def create_single_column_fixture():
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Pt(36)
    section.bottom_margin = Pt(36)
    section.left_margin = Pt(40)
    section.right_margin = Pt(40)

    # 1. Name & Contact
    p_name = doc.add_paragraph()
    p_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_name.paragraph_format.space_after = Pt(2)
    r_name = p_name.add_run("Alex Mercer")
    r_name.font.name = "Calibri"
    r_name.font.size = Pt(22)
    r_name.font.bold = True
    r_name.font.color.rgb = RGBColor(17, 24, 39)

    p_contact = doc.add_paragraph()
    p_contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_contact.paragraph_format.space_after = Pt(14)
    r_contact = p_contact.add_run("alex.mercer@example.com  |  +1 (555) 019-2834  |  San Francisco, CA  |  alexmercer.dev")
    r_contact.font.name = "Calibri"
    r_contact.font.size = Pt(9.5)
    r_contact.font.color.rgb = RGBColor(75, 85, 99)

    # 2. Professional Summary
    p_h_sum = doc.add_paragraph()
    p_h_sum.paragraph_format.space_before = Pt(8)
    p_h_sum.paragraph_format.space_after = Pt(4)
    r_h_sum = p_h_sum.add_run("PROFESSIONAL SUMMARY")
    r_h_sum.font.name = "Calibri"
    r_h_sum.font.size = Pt(12)
    r_h_sum.font.bold = True
    r_h_sum.font.color.rgb = RGBColor(37, 99, 235)

    p_sum = doc.add_paragraph()
    p_sum.paragraph_format.space_after = Pt(10)
    p_sum.paragraph_format.line_spacing = 1.15
    r_sum = p_sum.add_run(
        "Accomplished full-stack systems engineer with 9+ years building high-throughput web applications, cloud infrastructure, and document layout engines. Proven track record leading distributed engineering teams and delivering 99.99% reliability across critical SaaS products."
    )
    r_sum.font.name = "Calibri"
    r_sum.font.size = Pt(10)

    # 3. Work Experience
    p_h_exp = doc.add_paragraph()
    p_h_exp.paragraph_format.space_before = Pt(8)
    p_h_exp.paragraph_format.space_after = Pt(4)
    r_h_exp = p_h_exp.add_run("WORK EXPERIENCE")
    r_h_exp.font.name = "Calibri"
    r_h_exp.font.size = Pt(12)
    r_h_exp.font.bold = True
    r_h_exp.font.color.rgb = RGBColor(37, 99, 235)

    # Job 1 Title & Meta
    p_job1_title = doc.add_paragraph()
    p_job1_title.paragraph_format.space_after = Pt(1)
    r_j1 = p_job1_title.add_run("Principal Software Engineer")
    r_j1.font.bold = True
    r_j1.font.size = Pt(11)
    r_j1_comp = p_job1_title.add_run(" — Acme Cloud Platforms")
    r_j1_comp.font.size = Pt(10.5)

    p_job1_meta = doc.add_paragraph()
    p_job1_meta.paragraph_format.space_after = Pt(4)
    r_j1_meta = p_job1_meta.add_run("2021 - Present  |  San Francisco, CA")
    r_j1_meta.font.size = Pt(9)
    r_j1_meta.font.italic = True
    r_j1_meta.font.color.rgb = RGBColor(107, 114, 128)

    # Bullets for Job 1
    bullets_job1 = [
        ("Architected high-concurrency document rendering microservices", " processing 4.2M daily export jobs with sub-500ms latency."),
        ("Reduced AWS infrastructure costs by 38%", " ($450K ARR) via intelligent container right-sizing and spot fleet orchestration in EKS."),
        ("Established engineering excellence standards,", " RFC technical review processes, and mentored 14 engineers."),
    ]
    for bold_lead, rest in bullets_job1:
        p_b = doc.add_paragraph(style="List Bullet")
        p_b.paragraph_format.space_after = Pt(2)
        p_b.paragraph_format.line_spacing = 1.15
        r_lead = p_b.add_run(bold_lead)
        r_lead.font.bold = True
        r_lead.font.size = Pt(9.5)
        r_rest = p_b.add_run(rest)
        r_rest.font.size = Pt(9.5)

    # 4. Technical Skills
    p_h_sk = doc.add_paragraph()
    p_h_sk.paragraph_format.space_before = Pt(8)
    p_h_sk.paragraph_format.space_after = Pt(4)
    r_h_sk = p_h_sk.add_run("TECHNICAL SKILLS")
    r_h_sk.font.name = "Calibri"
    r_h_sk.font.size = Pt(12)
    r_h_sk.font.bold = True
    r_h_sk.font.color.rgb = RGBColor(37, 99, 235)

    skills = [
        ("Languages & Frameworks: ", "TypeScript, React, Next.js, Python, FastAPI, Tailwind CSS, Playwright"),
        ("Cloud & Infrastructure: ", "PostgreSQL, SQLAlchemy, Redis, Docker, Kubernetes, AWS (ECS, RDS, S3)"),
    ]
    for label, items in skills:
        p_sk = doc.add_paragraph()
        p_sk.paragraph_format.space_after = Pt(2)
        r_lbl = p_sk.add_run(label)
        r_lbl.font.bold = True
        r_lbl.font.size = Pt(9.5)
        r_items = p_sk.add_run(items)
        r_items.font.size = Pt(9.5)

    # 5. Education
    p_h_edu = doc.add_paragraph()
    p_h_edu.paragraph_format.space_before = Pt(8)
    p_h_edu.paragraph_format.space_after = Pt(4)
    r_h_edu = p_h_edu.add_run("EDUCATION")
    r_h_edu.font.name = "Calibri"
    r_h_edu.font.size = Pt(12)
    r_h_edu.font.bold = True
    r_h_edu.font.color.rgb = RGBColor(37, 99, 235)

    p_edu = doc.add_paragraph()
    p_edu.paragraph_format.space_after = Pt(2)
    r_deg = p_edu.add_run("B.S. in Computer Science")
    r_deg.font.bold = True
    r_deg.font.size = Pt(10.5)
    r_sch = p_edu.add_run(" — University of California, Berkeley (2012 - 2016)")
    r_sch.font.size = Pt(9.5)

    out_path = os.path.join(FIXTURES_DIR, "sample_single_column.docx")
    doc.save(out_path)
    print(f"Created: {out_path}")


def create_table_two_column_fixture():
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Pt(36)
    section.bottom_margin = Pt(36)
    section.left_margin = Pt(36)
    section.right_margin = Pt(36)

    # Header Name across top
    p_name = doc.add_paragraph()
    p_name.paragraph_format.space_after = Pt(2)
    r_name = p_name.add_run("ALEX MERCER")
    r_name.font.size = Pt(22)
    r_name.font.bold = True
    r_name.font.color.rgb = RGBColor(15, 118, 110)

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_after = Pt(12)
    r_title = p_title.add_run("Senior Staff Software Engineer")
    r_title.font.size = Pt(11)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(75, 85, 99)

    # 1-row, 2-column layout table (borderless)
    table = doc.add_table(rows=1, cols=2)
    table.autofit = False

    # Set column widths: Left column 30%, Right column 70%
    table.columns[0].width = Inches(2.2)
    table.columns[1].width = Inches(5.0)

    cell_left = table.cell(0, 0)
    cell_right = table.cell(0, 1)

    # --- LEFT SIDEBAR (Contact, Skills, Education) ---
    p_c_h = cell_left.paragraphs[0]
    p_c_h.paragraph_format.space_after = Pt(3)
    r_c_h = p_c_h.add_run("CONTACT")
    r_c_h.font.bold = True
    r_c_h.font.size = Pt(11)
    r_c_h.font.color.rgb = RGBColor(15, 118, 110)

    p_c_items = cell_left.add_paragraph()
    p_c_items.paragraph_format.space_after = Pt(10)
    p_c_items.add_run("alex@example.com\n+1 555-019-2834\nSan Francisco, CA\nalexmercer.dev").font.size = Pt(8.5)

    p_sk_h = cell_left.add_paragraph()
    p_sk_h.paragraph_format.space_before = Pt(8)
    p_sk_h.paragraph_format.space_after = Pt(3)
    r_sk_h = p_sk_h.add_run("SKILLS")
    r_sk_h.font.bold = True
    r_sk_h.font.size = Pt(11)
    r_sk_h.font.color.rgb = RGBColor(15, 118, 110)

    p_sk_list = cell_left.add_paragraph()
    p_sk_list.paragraph_format.space_after = Pt(10)
    p_sk_list.add_run("• Python / FastAPI\n• TypeScript / React\n• PostgreSQL / Redis\n• Docker / Kubernetes\n• AWS Cloud").font.size = Pt(8.5)

    p_edu_h = cell_left.add_paragraph()
    p_edu_h.paragraph_format.space_before = Pt(8)
    p_edu_h.paragraph_format.space_after = Pt(3)
    r_edu_h = p_edu_h.add_run("EDUCATION")
    r_edu_h.font.bold = True
    r_edu_h.font.size = Pt(11)
    r_edu_h.font.color.rgb = RGBColor(15, 118, 110)

    p_edu_txt = cell_left.add_paragraph()
    p_edu_txt.add_run("B.S. Computer Science\nUC Berkeley (2016)").font.size = Pt(8.5)

    # --- RIGHT MAIN COLUMN (Summary, Experience) ---
    p_sum_h = cell_right.paragraphs[0]
    p_sum_h.paragraph_format.space_after = Pt(3)
    r_sum_h = p_sum_h.add_run("SUMMARY")
    r_sum_h.font.bold = True
    r_sum_h.font.size = Pt(12)
    r_sum_h.font.color.rgb = RGBColor(15, 118, 110)

    p_sum_body = cell_right.add_paragraph()
    p_sum_body.paragraph_format.space_after = Pt(12)
    p_sum_body.paragraph_format.line_spacing = 1.15
    p_sum_body.add_run(
        "Staff engineer specializing in distributed backend microservices and modern frontend architectures with deep experience in document styling and cloud deployment."
    ).font.size = Pt(9.5)

    p_exp_h = cell_right.add_paragraph()
    p_exp_h.paragraph_format.space_before = Pt(6)
    p_exp_h.paragraph_format.space_after = Pt(3)
    r_exp_h = p_exp_h.add_run("WORK EXPERIENCE")
    r_exp_h.font.bold = True
    r_exp_h.font.size = Pt(12)
    r_exp_h.font.color.rgb = RGBColor(15, 118, 110)

    p_j1 = cell_right.add_paragraph()
    p_j1.paragraph_format.space_after = Pt(1)
    r_j1 = p_j1.add_run("Principal Software Engineer — Acme Cloud Platforms")
    r_j1.font.bold = True
    r_j1.font.size = Pt(10.5)

    p_j1_dates = cell_right.add_paragraph()
    p_j1_dates.paragraph_format.space_after = Pt(4)
    r_j1_dates = p_j1_dates.add_run("2021 - Present | San Francisco, CA")
    r_j1_dates.font.size = Pt(8.5)
    r_j1_dates.font.italic = True

    b1 = cell_right.add_paragraph(style="List Bullet")
    b1.paragraph_format.space_after = Pt(2)
    b1.add_run("Architected high-throughput document rendering microservices with sub-500ms latency.").font.size = Pt(9)

    b2 = cell_right.add_paragraph(style="List Bullet")
    b2.paragraph_format.space_after = Pt(2)
    b2.add_run("Reduced cloud infrastructure costs by 38% via Kubernetes spot fleet optimization.").font.size = Pt(9)

    out_path = os.path.join(FIXTURES_DIR, "sample_table_two_column.docx")
    doc.save(out_path)
    print(f"Created: {out_path}")


def create_text_box_fixture():
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Pt(36)
    section.bottom_margin = Pt(36)

    # Paragraph with a DrawingML Shape Text Box
    p_box = doc.add_paragraph()
    p_box.paragraph_format.space_after = Pt(12)

    # Inject XML for w:drawing containing a w:txBody text box
    txbox_xml = """
    <w:drawing xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
               xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
               xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
               xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">
      <wp:inline distT="0" distB="0" distL="0" distR="0">
        <wp:extent cx="5000000" cy="800000"/>
        <wp:docPr id="1" name="HeaderTextBox"/>
        <wps:wsp>
          <wps:cNvSpPr/>
          <wps:spPr>
            <a:xfrm>
              <a:off x="0" y="0"/>
              <a:ext cx="5000000" cy="800000"/>
            </a:xfrm>
            <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
            <a:solidFill><a:srgbClr val="F1F5F9"/></a:solidFill>
          </wps:spPr>
          <wps:txbx>
            <w:txBody>
              <a:bodyPr/>
              <a:lstStyle/>
              <w:p>
                <w:pPr><w:jc w:val="center"/></w:pPr>
                <w:r>
                  <w:rPr>
                    <w:b/>
                    <w:sz w:val="40"/>
                    <w:color w:val="1E40AF"/>
                  </w:rPr>
                  <w:t>ALEX MERCER - TEXT BOX HEADER</w:t>
                </w:r>
              </w:p>
              <w:p>
                <w:pPr><w:jc w:val="center"/></w:pPr>
                <w:r>
                  <w:rPr><w:sz w:val="18"/><w:color w:val="4B5563"/></w:rPr>
                  <w:t>alex@example.com | San Francisco, CA | Senior Engineer</w:t>
                </w:r>
              </w:p>
            </w:txBody>
          </wps:txbx>
        </wps:wsp>
      </wp:inline>
    </w:drawing>
    """
    p_box._p.append(parse_xml(txbox_xml))

    # Standard body content following the text box
    p_h = doc.add_paragraph()
    p_h.paragraph_format.space_before = Pt(8)
    p_h.paragraph_format.space_after = Pt(4)
    r_h = p_h.add_run("EXPERIENCE")
    r_h.font.bold = True
    r_h.font.size = Pt(12)
    r_h.font.color.rgb = RGBColor(30, 64, 175)

    p_j = doc.add_paragraph()
    p_j.paragraph_format.space_after = Pt(1)
    r_j = p_j.add_run("Principal Software Engineer — Acme Cloud Platforms")
    r_j.font.bold = True
    r_j.font.size = Pt(11)

    p_b1 = doc.add_paragraph(style="List Bullet")
    p_b1.paragraph_format.space_after = Pt(2)
    p_b1.add_run("Architected high-throughput document rendering microservices.").font.size = Pt(9.5)

    out_path = os.path.join(FIXTURES_DIR, "sample_text_box.docx")
    doc.save(out_path)
    print(f"Created: {out_path}")


if __name__ == "__main__":
    os.makedirs(FIXTURES_DIR, exist_ok=True)
    create_single_column_fixture()
    create_table_two_column_fixture()
    create_text_box_fixture()
    print("All 3 test fixtures successfully created!")

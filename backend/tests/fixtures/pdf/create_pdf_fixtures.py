import os
import io
import fitz
from PIL import Image, ImageDraw

FIXTURES_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(FIXTURES_DIR, exist_ok=True)

PAGE_W = 595.3  # A4 width in pt
PAGE_H = 841.9  # A4 height in pt


def create_fixture_a_word():
    """Fixture (a): Word-style single-column clean resume."""
    doc = fitz.open()
    page = doc.new_page(width=PAGE_W, height=PAGE_H)

    # 1. Header (Name, Title, Contact)
    page.insert_text(fitz.Point(40, 60), "ALEX MERCER", fontname="helv", fontsize=22, color=(0.1, 0.1, 0.1))
    page.insert_text(fitz.Point(40, 80), "Senior Full Stack Systems Engineer", fontname="helv", fontsize=11, color=(0.3, 0.3, 0.3))

    contact_text = "alex.mercer@example.com  |  +1 (555) 019-2834  |  San Francisco, CA  |  alexmercer.dev"
    page.insert_text(fitz.Point(40, 98), contact_text, fontname="helv", fontsize=9, color=(0.4, 0.4, 0.4))

    # Add link annotation for website
    link_rect = fitz.Rect(400, 88, 480, 102)
    page.insert_link({"kind": fitz.LINK_URI, "from": link_rect, "uri": "https://alexmercer.dev"})

    # Divider line
    page.draw_line(fitz.Point(40, 108), fitz.Point(555, 108), color=(0.8, 0.8, 0.8), width=0.75)

    y = 128
    # 2. Professional Summary
    page.insert_text(fitz.Point(40, y), "PROFESSIONAL SUMMARY", fontname="helv", fontsize=12, color=(0.1, 0.1, 0.1))
    page.draw_line(fitz.Point(40, y + 4), fitz.Point(555, y + 4), color=(0.85, 0.85, 0.85), width=0.5)
    y += 20
    summary_text = (
        "Accomplished systems engineer with 8+ years architecting high-throughput distributed applications, "
        "cloud infrastructure, and document layout engines. Proven track record leading distributed engineering "
        "teams and delivering 99.99% availability across critical enterprise SaaS platforms."
    )
    rect = fitz.Rect(40, y, 555, y + 40)
    page.insert_textbox(rect, summary_text, fontname="helv", fontsize=9.5, color=(0.15, 0.15, 0.15), lineheight=1.3)
    y += 50

    # 3. Work Experience
    page.insert_text(fitz.Point(40, y), "WORK EXPERIENCE", fontname="helv", fontsize=12, color=(0.1, 0.1, 0.1))
    page.draw_line(fitz.Point(40, y + 4), fitz.Point(555, y + 4), color=(0.85, 0.85, 0.85), width=0.5)
    y += 22

    # Job 1 Title + Right-aligned dates on same baseline
    page.insert_text(fitz.Point(40, y), "Principal Software Engineer", fontname="helv", fontsize=10.5, color=(0.1, 0.1, 0.1))
    page.insert_text(fitz.Point(460, y), "2021 - Present", fontname="helv", fontsize=9, color=(0.4, 0.4, 0.4))
    y += 14
    page.insert_text(fitz.Point(40, y), "Acme Cloud Platforms  |  San Francisco, CA", fontname="helv", fontsize=9.5, color=(0.3, 0.3, 0.3))
    y += 18

    # Bullets
    b1 = "\x95 Architected high-concurrency document rendering microservices processing 4.2M daily export jobs with sub-500ms latency."
    b2 = "\x95 Reduced AWS infrastructure costs by 38% ($450K ARR) via intelligent container right-sizing and spot fleet orchestration."
    b3 = "\x95 Established engineering excellence standards, RFC technical review processes, and mentored 14 engineers."
    for b in [b1, b2, b3]:
        rect = fitz.Rect(52, y - 4, 555, y + 26)
        page.insert_textbox(rect, b, fontname="helv", fontsize=9.5, color=(0.15, 0.15, 0.15), lineheight=1.25)
        y += 28

    y += 10
    # 4. Technical Skills
    page.insert_text(fitz.Point(40, y), "TECHNICAL SKILLS", fontname="helv", fontsize=12, color=(0.1, 0.1, 0.1))
    page.draw_line(fitz.Point(40, y + 4), fitz.Point(555, y + 4), color=(0.85, 0.85, 0.85), width=0.5)
    y += 20
    page.insert_text(fitz.Point(40, y), "Languages & Frameworks: TypeScript, React, Next.js, Python, FastAPI, Tailwind CSS", fontname="helv", fontsize=9.5, color=(0.15, 0.15, 0.15))
    y += 16
    page.insert_text(fitz.Point(40, y), "Cloud & Infrastructure: PostgreSQL, Docker, Kubernetes, AWS (ECS, RDS, S3), Redis", fontname="helv", fontsize=9.5, color=(0.15, 0.15, 0.15))
    y += 26

    # 5. Education
    page.insert_text(fitz.Point(40, y), "EDUCATION", fontname="helv", fontsize=12, color=(0.1, 0.1, 0.1))
    page.draw_line(fitz.Point(40, y + 4), fitz.Point(555, y + 4), color=(0.85, 0.85, 0.85), width=0.5)
    y += 20
    page.insert_text(fitz.Point(40, y), "B.S. in Computer Science — University of California, Berkeley", fontname="helv", fontsize=9.5, color=(0.1, 0.1, 0.1))
    page.insert_text(fitz.Point(475, y), "2012 - 2016", fontname="helv", fontsize=9, color=(0.4, 0.4, 0.4))

    out_path = os.path.join(FIXTURES_DIR, "fixture_a_word_single_col.pdf")
    doc.save(out_path)
    doc.close()
    print(f"Created: {out_path}")


def create_fixture_b_latex():
    """Fixture (b): Academic/LaTeX-style resume with Times-Roman serif font and tight rules."""
    doc = fitz.open()
    page = doc.new_page(width=PAGE_W, height=PAGE_H)

    # Centered Header
    page.insert_text(fitz.Point(180, 55), "DR. ELENA ROSTOVA", fontname="times-bold", fontsize=20, color=(0, 0, 0))
    contact = "erostova@stanford.edu  *  +1 (650) 723-2300  *  Stanford, CA  *  linkedin.com/in/erostova"
    page.insert_text(fitz.Point(110, 72), contact, fontname="times-roman", fontsize=9.5, color=(0.2, 0.2, 0.2))

    page.draw_line(fitz.Point(36, 82), fitz.Point(559, 82), color=(0, 0, 0), width=1.0)

    y = 104
    # Education
    page.insert_text(fitz.Point(36, y), "EDUCATION", fontname="times-bold", fontsize=12, color=(0, 0, 0))
    page.draw_line(fitz.Point(36, y + 3), fitz.Point(559, y + 3), color=(0.3, 0.3, 0.3), width=0.5)
    y += 18
    page.insert_text(fitz.Point(36, y), "Ph.D. in Computer Science, Stanford University", fontname="times-bold", fontsize=10.5, color=(0, 0, 0))
    page.insert_text(fitz.Point(480, y), "2017 - 2021", fontname="times-roman", fontsize=9.5, color=(0.2, 0.2, 0.2))
    y += 14
    page.insert_text(fitz.Point(48, y), "Dissertation: High-Performance Distributed Tensor Graph Scheduling", fontname="times-roman", fontsize=9.5, color=(0.25, 0.25, 0.25))
    y += 26

    # Research & Work Experience
    page.insert_text(fitz.Point(36, y), "RESEARCH & PROFESSIONAL EXPERIENCE", fontname="times-bold", fontsize=12, color=(0, 0, 0))
    page.draw_line(fitz.Point(36, y + 3), fitz.Point(559, y + 3), color=(0.3, 0.3, 0.3), width=0.5)
    y += 18

    page.insert_text(fitz.Point(36, y), "Senior AI Infrastructure Scientist, DeepAI Labs", fontname="times-bold", fontsize=10.5, color=(0, 0, 0))
    page.insert_text(fitz.Point(475, y), "2021 - Present", fontname="times-roman", fontsize=9.5, color=(0.2, 0.2, 0.2))
    y += 18

    bullets = [
        "- Designed multi-node GPU cluster scheduler accelerating LLM pretraining runs by 2.4x across 1,024 H100s.",
        "- Implemented zero-copy tensor caching system using PyTorch and CUDA C++ cutting GPU memory footprint by 32%.",
        "- Authored 4 papers in NeurIPS and ICML on adaptive checkpointing and distributed fault recovery."
    ]
    for b in bullets:
        rect = fitz.Rect(48, y - 9, 559, y + 16)
        page.insert_textbox(rect, b, fontname="times-roman", fontsize=9.5, color=(0.1, 0.1, 0.1), lineheight=1.2)
        y += 20

    y += 10
    # Technical Skills
    page.insert_text(fitz.Point(36, y), "TECHNICAL EXPERTISE", fontname="times-bold", fontsize=12, color=(0, 0, 0))
    page.draw_line(fitz.Point(36, y + 3), fitz.Point(559, y + 3), color=(0.3, 0.3, 0.3), width=0.5)
    y += 18
    page.insert_text(fitz.Point(36, y), "Programming: Python, C++, CUDA, PyTorch, JAX, Rust", fontname="times-roman", fontsize=9.5, color=(0.1, 0.1, 0.1))
    y += 15
    page.insert_text(fitz.Point(36, y), "Systems: Kubernetes, Ray, Slurm, InfiniBand, Docker, NCCL", fontname="times-roman", fontsize=9.5, color=(0.1, 0.1, 0.1))

    out_path = os.path.join(FIXTURES_DIR, "fixture_b_latex.pdf")
    doc.save(out_path)
    doc.close()
    print(f"Created: {out_path}")


def create_fixture_c_canva_twocol():
    """Fixture (c): Canva-style two-column with sidebar colored card, decorative vector shapes, and contact icon."""
    doc = fitz.open()
    page = doc.new_page(width=PAGE_W, height=PAGE_H)

    # 1. Left Sidebar Background Colored Rectangle (Navy / Slate Blue)
    sidebar_rect = fitz.Rect(0, 0, 190, PAGE_H)
    page.draw_rect(sidebar_rect, color=None, fill=(0.12, 0.18, 0.28))

    # Sidebar Header Avatar/Icon placeholder (circle vector)
    page.draw_circle(fitz.Point(95, 75), 32, color=(0.25, 0.45, 0.75), fill=(0.2, 0.35, 0.55), width=2)
    page.insert_text(fitz.Point(82, 82), "MC", fontname="helv", fontsize=20, color=(1, 1, 1))

    # Sidebar: Contact Section
    y = 140
    page.insert_text(fitz.Point(24, y), "CONTACT", fontname="helv", fontsize=11, color=(0.55, 0.75, 0.95))
    page.draw_line(fitz.Point(24, y + 4), fitz.Point(166, y + 4), color=(0.3, 0.4, 0.55), width=1)
    y += 20
    page.insert_text(fitz.Point(24, y), "marcus.chen@example.com", fontname="helv", fontsize=8.5, color=(0.9, 0.9, 0.9))
    y += 16
    page.insert_text(fitz.Point(24, y), "+1 (415) 890-1234", fontname="helv", fontsize=8.5, color=(0.9, 0.9, 0.9))
    y += 16
    page.insert_text(fitz.Point(24, y), "Austin, TX", fontname="helv", fontsize=8.5, color=(0.9, 0.9, 0.9))
    y += 16
    page.insert_text(fitz.Point(24, y), "marcuschen.tech", fontname="helv", fontsize=8.5, color=(0.9, 0.9, 0.9))

    # Sidebar: Skills Card
    y += 40
    page.insert_text(fitz.Point(24, y), "SKILLS", fontname="helv", fontsize=11, color=(0.55, 0.75, 0.95))
    page.draw_line(fitz.Point(24, y + 4), fitz.Point(166, y + 4), color=(0.3, 0.4, 0.55), width=1)
    y += 20
    skills = ["Python / Django", "TypeScript / React", "PostgreSQL / Redis", "Docker & Kubernetes", "AWS Cloud Architecture", "CI/CD & Terraform"]
    for s in skills:
        page.draw_rect(fitz.Rect(24, y - 8, 166, y + 8), color=None, fill=(0.18, 0.25, 0.38))
        page.insert_text(fitz.Point(30, y + 3), s, fontname="helv", fontsize=8.5, color=(0.95, 0.95, 0.95))
        y += 22

    # 2. Main Right Column Content
    main_x = 215
    page.insert_text(fitz.Point(main_x, 60), "MARCUS CHEN", fontname="helv", fontsize=24, color=(0.12, 0.18, 0.28))
    page.insert_text(fitz.Point(main_x, 82), "Lead Cloud Solutions Architect", fontname="helv", fontsize=12, color=(0.25, 0.45, 0.75))
    page.draw_line(fitz.Point(main_x, 96), fitz.Point(565, 96), color=(0.85, 0.88, 0.92), width=1.5)

    # Summary
    y = 120
    page.insert_text(fitz.Point(main_x, y), "PROFILE", fontname="helv", fontsize=12, color=(0.12, 0.18, 0.28))
    page.draw_line(fitz.Point(main_x, y + 3), fitz.Point(565, y + 3), color=(0.25, 0.45, 0.75), width=1)
    y += 18
    prof_text = "Pragmatic enterprise architect specialized in migrating legacy on-prem systems to secure, observable Kubernetes and AWS serverless infrastructures. Passionate about developer velocity and automated governance."
    rect = fitz.Rect(main_x, y, 565, y + 36)
    page.insert_textbox(rect, prof_text, fontname="helv", fontsize=9.5, color=(0.2, 0.2, 0.2), lineheight=1.3)
    y += 48

    # Experience
    page.insert_text(fitz.Point(main_x, y), "EXPERIENCE", fontname="helv", fontsize=12, color=(0.12, 0.18, 0.28))
    page.draw_line(fitz.Point(main_x, y + 3), fitz.Point(565, y + 3), color=(0.25, 0.45, 0.75), width=1)
    y += 20

    page.insert_text(fitz.Point(main_x, y), "Lead Solutions Architect  -  Nexus Financial", fontname="helv", fontsize=10.5, color=(0.12, 0.18, 0.28))
    page.insert_text(fitz.Point(485, y), "2020 - Present", fontname="helv", fontsize=9, color=(0.4, 0.4, 0.4))
    y += 18

    bullets = [
        "➤ Designed zero-downtime multi-region banking API handling $12B annual transaction volume with 99.999% SLA.",
        "➤ Migrated 85 monolithic microservices into Amazon EKS with Istio service mesh and automated blue/green canary deployments.",
        "➤ Spearheaded compliance readiness for SOC2 Type II and PCI-DSS v4.0 across all cloud environments."
    ]
    for b in bullets:
        rect = fitz.Rect(main_x + 8, y - 8, 565, y + 16)
        page.insert_textbox(rect, b, fontname="helv", fontsize=9.2, color=(0.2, 0.2, 0.2), lineheight=1.25)
        y += 22

    out_path = os.path.join(FIXTURES_DIR, "fixture_c_canva_twocol.pdf")
    doc.save(out_path)
    doc.close()
    print(f"Created: {out_path}")


def create_fixture_d_gdocs():
    """Fixture (d): Google Docs export style with clean sans-serif layout, bold headers, and subtle rules."""
    doc = fitz.open()
    page = doc.new_page(width=PAGE_W, height=PAGE_H)

    page.insert_text(fitz.Point(45, 55), "Sarah Jenkins", fontname="helv", fontsize=21, color=(0.13, 0.13, 0.13))
    page.insert_text(fitz.Point(45, 74), "Staff Frontend Engineer | React & Design Systems", fontname="helv", fontsize=10.5, color=(0.35, 0.35, 0.35))
    page.insert_text(fitz.Point(45, 90), "sarah.j@example.com * (312) 555-0149 * Chicago, IL * github.com/sarahjenkins", fontname="helv", fontsize=9, color=(0.4, 0.4, 0.4))

    y = 118
    # Experience
    page.insert_text(fitz.Point(45, y), "Experience", fontname="helv", fontsize=13, color=(0.13, 0.13, 0.13))
    page.draw_line(fitz.Point(45, y + 4), fitz.Point(550, y + 4), color=(0.8, 0.8, 0.8), width=0.75)
    y += 20

    page.insert_text(fitz.Point(45, y), "Staff UI Engineer — Stripe", fontname="helv", fontsize=10.5, color=(0.13, 0.13, 0.13))
    page.insert_text(fitz.Point(460, y), "Aug 2021 – Present", fontname="helv", fontsize=9, color=(0.4, 0.4, 0.4))
    y += 18

    bullets = [
        "\x95 Led frontend architecture for global billing dashboard used by 2M+ businesses.",
        "\x95 Rebuilt design system token pipeline reducing bundle sizes by 42% across 18 web apps.",
        "\x95 Championed WCAG 2.1 AA accessibility audit achieving 100% compliance across all payment checkout flows."
    ]
    for b in bullets:
        rect = fitz.Rect(58, y - 4, 550, y + 26)
        page.insert_textbox(rect, b, fontname="helv", fontsize=9.5, color=(0.2, 0.2, 0.2), lineheight=1.25)
        y += 26

    y += 12
    # Skills
    page.insert_text(fitz.Point(45, y), "Technical Skills", fontname="helv", fontsize=13, color=(0.13, 0.13, 0.13))
    page.draw_line(fitz.Point(45, y + 4), fitz.Point(550, y + 4), color=(0.8, 0.8, 0.8), width=0.75)
    y += 20
    page.insert_text(fitz.Point(45, y), "Core: JavaScript, TypeScript, React, Next.js, HTML5/CSS3, Tailwind CSS", fontname="helv", fontsize=9.5, color=(0.2, 0.2, 0.2))
    y += 16
    page.insert_text(fitz.Point(45, y), "Tooling & Testing: Jest, Playwright, Storybook, Webpack, Vite, Git", fontname="helv", fontsize=9.5, color=(0.2, 0.2, 0.2))

    out_path = os.path.join(FIXTURES_DIR, "fixture_d_gdocs.pdf")
    doc.save(out_path)
    doc.close()
    print(f"Created: {out_path}")


def create_fixture_e_scanned():
    """Fixture (e): Scanned PDF - renders fixture (a) to a 300 DPI rasterized image and embeds it as an image-only page."""
    # First render fixture a to 300 DPI image
    a_path = os.path.join(FIXTURES_DIR, "fixture_a_word_single_col.pdf")
    if not os.path.exists(a_path):
        create_fixture_a_word()

    doc_a = fitz.open(a_path)
    page_a = doc_a[0]
    # 300 DPI = zoom of 300 / 72 ≈ 4.1667
    zoom = 300 / 72
    mat = fitz.Matrix(zoom, zoom)
    pix = page_a.get_pixmap(matrix=mat)
    img_bytes = pix.tobytes("png")
    doc_a.close()

    # Now create new PDF containing only that rasterized image
    doc_e = fitz.open()
    page_e = doc_e.new_page(width=PAGE_W, height=PAGE_H)
    page_e.insert_image(fitz.Rect(0, 0, PAGE_W, PAGE_H), stream=img_bytes)

    out_path = os.path.join(FIXTURES_DIR, "fixture_e_scanned.pdf")
    doc_e.save(out_path)
    doc_e.close()
    print(f"Created: {out_path}")


if __name__ == "__main__":
    create_fixture_a_word()
    create_fixture_b_latex()
    create_fixture_c_canva_twocol()
    create_fixture_d_gdocs()
    create_fixture_e_scanned()
    print("All 5 fixtures generated successfully.")

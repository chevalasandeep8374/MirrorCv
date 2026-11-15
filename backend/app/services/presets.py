from typing import List, Dict, Any
from app.schemas.content import (
    ResumeContent,
    HeaderContent,
    ContactLink,
    ResumeSection,
    SectionItem,
    BulletItem,
)
from app.schemas.style import (
    ResumeStyle,
    Margins,
    Typography,
    FontSizes,
    Spacing,
    Colors,
    ColumnLayout,
    Decorations,
)


def get_classic_single_column_preset() -> ResumeStyle:
    """Preset 1: Classic single-column layout with clean bar section headings."""
    return ResumeStyle(
        templateId="classic-single-column",
        pageSize="A4",
        margins=Margins(top=36, bottom=36, left=42, right=42, unit="pt"),
        typography=Typography(
            baseFontFamily="Inter",
            headingFontFamily="Inter",
            nameFontFamily="Inter",
            fontSizeScale=1.0,
            fontSizes=FontSizes(
                name=22,
                headerTitle=11,
                contact=9,
                sectionHeading=12.5,
                itemTitle=10.5,
                itemSubtitle=9.5,
                body=9.5,
                meta=8.5,
                unit="pt",
            ),
            lineHeight=1.45,
        ),
        spacing=Spacing(
            sectionSpacing=14,
            itemSpacing=8,
            bulletSpacing=3,
            headerBottomSpacing=16,
            unit="pt",
        ),
        colors=Colors(
            accent="#2563eb",
            text="#111827",
            muted="#4b5563",
            background="#ffffff",
            sidebarBackground="#f8fafc",
            divider="#e5e7eb",
        ),
        bulletStyle="disc",
        headingStyle="bar",
        layout=ColumnLayout(
            type="single",
            sidebarWidthPercent=32,
            sidebarSectionIds=[],
            mainSectionIds=[
                "sec-summary",
                "sec-exp",
                "sec-skills",
                "sec-proj",
                "sec-edu",
                "sec-cert",
            ],
        ),
    )


def get_modern_sidebar_left_preset() -> ResumeStyle:
    """Preset 2: Modern two-column layout with a sleek shaded sidebar on the left."""
    return ResumeStyle(
        templateId="modern-sidebar-left",
        pageSize="A4",
        margins=Margins(top=32, bottom=32, left=32, right=32, unit="pt"),
        typography=Typography(
            baseFontFamily="Inter",
            headingFontFamily="Inter",
            fontSizeScale=1.0,
            fontSizes=FontSizes(
                name=20,
                headerTitle=11,
                contact=8.5,
                sectionHeading=12,
                itemTitle=10,
                itemSubtitle=9,
                body=9,
                meta=8,
                unit="pt",
            ),
            lineHeight=1.4,
        ),
        spacing=Spacing(
            sectionSpacing=12,
            itemSpacing=7,
            bulletSpacing=2.5,
            headerBottomSpacing=14,
            unit="pt",
        ),
        colors=Colors(
            accent="#0f766e",  # Deep Teal
            text="#1f2937",
            muted="#6b7280",
            background="#ffffff",
            sidebarBackground="#f0fdfa",
            divider="#cbd5e1",
        ),
        bulletStyle="square",
        headingStyle="underline",
        layout=ColumnLayout(
            type="sidebar_left",
            sidebarWidthPercent=33,
            sidebarSectionIds=["sec-skills", "sec-edu", "sec-cert", "sec-lang"],
            mainSectionIds=["sec-summary", "sec-exp", "sec-proj"],
        ),
    )


# Alias for backward compatibility
get_modern_two_column_preset = get_modern_sidebar_left_preset


def get_executive_sidebar_right_preset() -> ResumeStyle:
    """Preset 3: Executive two-column layout with sidebar on the right."""
    return ResumeStyle(
        templateId="executive-sidebar-right",
        pageSize="A4",
        margins=Margins(top=36, bottom=36, left=36, right=36, unit="pt"),
        typography=Typography(
            baseFontFamily="Inter",
            headingFontFamily="Inter",
            fontSizeScale=1.0,
            fontSizes=FontSizes(
                name=22,
                headerTitle=11.5,
                contact=9,
                sectionHeading=12.5,
                itemTitle=10.5,
                itemSubtitle=9.5,
                body=9.5,
                meta=8.5,
                unit="pt",
            ),
            lineHeight=1.42,
        ),
        spacing=Spacing(
            sectionSpacing=14,
            itemSpacing=8,
            bulletSpacing=3,
            headerBottomSpacing=16,
            unit="pt",
        ),
        colors=Colors(
            accent="#18181b",  # Charcoal
            text="#0f172a",
            muted="#64748b",
            background="#ffffff",
            sidebarBackground="#f8fafc",
            divider="#e2e8f0",
        ),
        bulletStyle="disc",
        headingStyle="bar",
        layout=ColumnLayout(
            type="sidebar_right",
            sidebarWidthPercent=34,
            sidebarSectionIds=["sec-skills", "sec-edu", "sec-cert", "sec-awards"],
            mainSectionIds=["sec-summary", "sec-exp", "sec-proj"],
        ),
    )


def get_header_banner_preset() -> ResumeStyle:
    """Preset 4: Header Banner layout with inverted dark header card."""
    return ResumeStyle(
        templateId="header-banner",
        pageSize="A4",
        margins=Margins(top=28, bottom=32, left=36, right=36, unit="pt"),
        typography=Typography(
            baseFontFamily="Inter",
            headingFontFamily="Inter",
            fontSizeScale=1.0,
            fontSizes=FontSizes(
                name=24,
                headerTitle=12,
                contact=9,
                sectionHeading=12.5,
                itemTitle=10.5,
                itemSubtitle=9.5,
                body=9.5,
                meta=8.5,
                unit="pt",
            ),
            lineHeight=1.45,
        ),
        spacing=Spacing(
            sectionSpacing=13,
            itemSpacing=7.5,
            bulletSpacing=2.5,
            headerBottomSpacing=18,
            unit="pt",
        ),
        colors=Colors(
            accent="#3b82f6",  # Bright Blue
            text="#1e293b",
            muted="#64748b",
            background="#ffffff",
            sidebarBackground="#f8fafc",
            divider="#e2e8f0",
            headerBannerColor="#0f172a",
            headerBannerTextColor="#ffffff",
        ),
        bulletStyle="circle",
        headingStyle="pill",
        layout=ColumnLayout(
            type="header_banner",
            sidebarWidthPercent=32,
            sidebarSectionIds=[],
            mainSectionIds=[
                "sec-summary",
                "sec-exp",
                "sec-skills",
                "sec-proj",
                "sec-edu",
                "sec-cert",
            ],
        ),
        decorations=Decorations(
            headerBanner=True,
            headerBannerColor="#0f172a",
            headerBannerTextColor="#ffffff",
        ),
    )


def get_compact_dense_preset() -> ResumeStyle:
    """Preset 5: High-density single-column layout for technical 1-page resumes."""
    return ResumeStyle(
        templateId="compact-dense",
        pageSize="A4",
        margins=Margins(top=24, bottom=24, left=28, right=28, unit="pt"),
        typography=Typography(
            baseFontFamily="Inter",
            headingFontFamily="Inter",
            fontSizeScale=0.92,
            fontSizes=FontSizes(
                name=18,
                headerTitle=10,
                contact=8,
                sectionHeading=11,
                itemTitle=9.5,
                itemSubtitle=8.5,
                body=8.5,
                meta=7.5,
                unit="pt",
            ),
            lineHeight=1.28,
        ),
        spacing=Spacing(
            sectionSpacing=9,
            itemSpacing=5,
            bulletSpacing=1.5,
            headerBottomSpacing=10,
            unit="pt",
        ),
        colors=Colors(
            accent="#2563eb",
            text="#0f172a",
            muted="#475569",
            background="#ffffff",
            sidebarBackground="#f8fafc",
            divider="#cbd5e1",
        ),
        bulletStyle="disc",
        headingStyle="plain",
        layout=ColumnLayout(
            type="compact",
            sidebarWidthPercent=30,
            sidebarSectionIds=[],
            mainSectionIds=[
                "sec-summary",
                "sec-exp",
                "sec-skills",
                "sec-proj",
                "sec-edu",
                "sec-cert",
            ],
        ),
    )


def get_creative_accent_preset() -> ResumeStyle:
    """Preset 6: Creative layout with vibrant emerald accents and boxed section headers."""
    return ResumeStyle(
        templateId="creative-accent",
        pageSize="A4",
        margins=Margins(top=32, bottom=32, left=34, right=34, unit="pt"),
        typography=Typography(
            baseFontFamily="Inter",
            headingFontFamily="Inter",
            fontSizeScale=1.0,
            fontSizes=FontSizes(
                name=22,
                headerTitle=11.5,
                contact=8.5,
                sectionHeading=12,
                itemTitle=10.5,
                itemSubtitle=9,
                body=9,
                meta=8,
                unit="pt",
            ),
            lineHeight=1.42,
        ),
        spacing=Spacing(
            sectionSpacing=13,
            itemSpacing=7.5,
            bulletSpacing=2.5,
            headerBottomSpacing=15,
            unit="pt",
        ),
        colors=Colors(
            accent="#059669",  # Emerald Green
            text="#111827",
            muted="#4b5563",
            background="#ffffff",
            sidebarBackground="#ecfdf5",
            divider="#a7f3d0",
        ),
        bulletStyle="arrow",
        headingStyle="boxed",
        layout=ColumnLayout(
            type="creative",
            sidebarWidthPercent=32,
            sidebarSectionIds=["sec-skills", "sec-edu", "sec-cert"],
            mainSectionIds=["sec-summary", "sec-exp", "sec-proj"],
        ),
    )


def get_minimal_editorial_preset() -> ResumeStyle:
    """Preset 7: Minimal editorial monochromatic layout focusing purely on typography."""
    return ResumeStyle(
        templateId="minimal-editorial",
        pageSize="A4",
        margins=Margins(top=40, bottom=40, left=44, right=44, unit="pt"),
        typography=Typography(
            baseFontFamily="Inter",
            headingFontFamily="Inter",
            fontSizeScale=1.0,
            fontSizes=FontSizes(
                name=22,
                headerTitle=11,
                contact=8.5,
                sectionHeading=12,
                itemTitle=10,
                itemSubtitle=9,
                body=9,
                meta=8,
                unit="pt",
            ),
            lineHeight=1.52,
        ),
        spacing=Spacing(
            sectionSpacing=16,
            itemSpacing=9,
            bulletSpacing=3.5,
            headerBottomSpacing=18,
            unit="pt",
        ),
        colors=Colors(
            accent="#09090b",  # Pitch Black
            text="#18181b",
            muted="#71717a",
            background="#ffffff",
            sidebarBackground="#ffffff",
            divider="#e4e4e7",
        ),
        bulletStyle="dash",
        headingStyle="caps",
        layout=ColumnLayout(
            type="minimal",
            sidebarWidthPercent=30,
            sidebarSectionIds=[],
            mainSectionIds=[
                "sec-summary",
                "sec-exp",
                "sec-skills",
                "sec-proj",
                "sec-edu",
                "sec-cert",
            ],
        ),
    )


def get_academic_cv_preset() -> ResumeStyle:
    """Preset 8: Academic curriculum vitae layout with serif typography and hanging list indents."""
    return ResumeStyle(
        templateId="academic-cv",
        pageSize="A4",
        margins=Margins(top=42, bottom=42, left=46, right=46, unit="pt"),
        typography=Typography(
            baseFontFamily="Liberation Serif",
            headingFontFamily="Liberation Serif",
            nameFontFamily="Liberation Serif",
            fontSizeScale=1.02,
            fontSizes=FontSizes(
                name=24,
                headerTitle=12,
                contact=9.5,
                sectionHeading=13,
                itemTitle=11,
                itemSubtitle=10,
                body=10,
                meta=9,
                unit="pt",
            ),
            lineHeight=1.48,
        ),
        spacing=Spacing(
            sectionSpacing=15,
            itemSpacing=8.5,
            bulletSpacing=3,
            headerBottomSpacing=16,
            unit="pt",
        ),
        colors=Colors(
            accent="#1e3a8a",  # Classic Navy
            text="#0f172a",
            muted="#475569",
            background="#ffffff",
            sidebarBackground="#f8fafc",
            divider="#cbd5e1",
        ),
        bulletStyle="disc",
        headingStyle="underline",
        layout=ColumnLayout(
            type="academic",
            sidebarWidthPercent=30,
            sidebarSectionIds=[],
            mainSectionIds=[
                "sec-summary",
                "sec-edu",
                "sec-exp",
                "sec-proj",
                "sec-skills",
                "sec-cert",
            ],
        ),
    )


def get_all_system_presets() -> List[Dict[str, Any]]:
    """Returns metadata and style tokens for all 8 system template presets."""
    return [
        {
            "id": "classic-single-column",
            "name": "Classic Single Column",
            "category": "single",
            "description": "Timeless single-column design with clean bar headings and balanced margins.",
            "style": get_classic_single_column_preset().model_dump(),
        },
        {
            "id": "modern-sidebar-left",
            "name": "Modern Left Sidebar",
            "category": "sidebar",
            "description": "Two-column layout with a shaded sidebar for skills, contact, and credentials.",
            "style": get_modern_sidebar_left_preset().model_dump(),
        },
        {
            "id": "executive-sidebar-right",
            "name": "Executive Right Sidebar",
            "category": "sidebar",
            "description": "High-contrast right sidebar for certifications and education; primary space for experience.",
            "style": get_executive_sidebar_right_preset().model_dump(),
        },
        {
            "id": "header-banner",
            "name": "Header Banner",
            "category": "banner",
            "description": "Prominent colored header card with crisp inverted white title typography.",
            "style": get_header_banner_preset().model_dump(),
        },
        {
            "id": "compact-dense",
            "name": "Compact Technical",
            "category": "compact",
            "description": "High-density formatting engineered to maximize content on a single page.",
            "style": get_compact_dense_preset().model_dump(),
        },
        {
            "id": "creative-accent",
            "name": "Creative Accent",
            "category": "creative",
            "description": "Vibrant emerald green accents, boxed section headings, and dynamic list arrows.",
            "style": get_creative_accent_preset().model_dump(),
        },
        {
            "id": "minimal-editorial",
            "name": "Minimal Editorial",
            "category": "minimal",
            "description": "Monochromatic typography-focused design with generous leading and hairline rules.",
            "style": get_minimal_editorial_preset().model_dump(),
        },
        {
            "id": "academic-cv",
            "name": "Academic CV",
            "category": "academic",
            "description": "Formal serif curriculum vitae format with hanging indents for extensive credentials.",
            "style": get_academic_cv_preset().model_dump(),
        },
    ]


def get_realistic_seed_content() -> ResumeContent:
    """Realistic production resume content."""
    return ResumeContent(
        header=HeaderContent(
            name="Alex Mercer",
            title="Senior Staff Software Engineer",
            email="alex.mercer@example.com",
            phone="+1 (555) 019-2834",
            location="San Francisco, CA",
            website="https://alexmercer.dev",
            links=[
                ContactLink(id="link-1", label="GitHub", url="https://github.com/alexmercer"),
                ContactLink(id="link-2", label="LinkedIn", url="https://linkedin.com/in/alexmercer"),
            ],
        ),
        sections=[
            ResumeSection(
                id="sec-summary",
                type="summary",
                title="Professional Summary",
                visible=True,
                items=[
                    SectionItem(
                        id="item-sum-1",
                        title="",
                        subtitle="",
                        location="",
                        dateRange="",
                        bullets=[
                            BulletItem(
                                id="b-sum-1",
                                text="Staff Software Engineer with 10+ years architecting distributed microservices, realtime document rendering engines, and high-concurrency cloud systems.",
                            )
                        ],
                    )
                ],
            ),
            ResumeSection(
                id="sec-exp",
                type="experience",
                title="Work Experience",
                visible=True,
                items=[
                    SectionItem(
                        id="item-exp-1",
                        title="Staff Systems Architect",
                        subtitle="Stripe",
                        location="San Francisco, CA",
                        dateRange="2022 - Present",
                        bullets=[
                            BulletItem(
                                id="b-exp-1-1",
                                text="Spearheaded real-time settlement pipeline processing $12B+ annually, reducing reconciliation latency from 4 hours to 180ms.",
                            ),
                            BulletItem(
                                id="b-exp-1-2",
                                text="Mentored 14 engineers across 3 distributed pods; led architectural review for global idempotent transaction ledger.",
                            ),
                        ],
                    ),
                    SectionItem(
                        id="item-exp-2",
                        title="Senior Full Stack Engineer",
                        subtitle="Datadog",
                        location="New York, NY",
                        dateRange="2018 - 2022",
                        bullets=[
                            BulletItem(
                                id="b-exp-2-1",
                                text="Re-engineered core dashboard charting engine in TypeScript, dropping Time-to-Interactive by 42% on high-cardinality metrics.",
                            ),
                            BulletItem(
                                id="b-exp-2-2",
                                text="Authored open-source distributed tracing connector adopted by over 2,000 enterprise customers.",
                            ),
                        ],
                    ),
                ],
            ),
            ResumeSection(
                id="sec-skills",
                type="skills",
                title="Core Competencies",
                visible=True,
                items=[
                    SectionItem(
                        id="item-sk-1",
                        title="Languages & Runtimes",
                        subtitle="",
                        location="",
                        dateRange="",
                        bullets=[
                            BulletItem(id="b-sk-1", text="Python (AsyncIO, FastAPI), TypeScript, Go, Rust, SQL"),
                        ],
                    ),
                    SectionItem(
                        id="item-sk-2",
                        title="Cloud & Data",
                        subtitle="",
                        location="",
                        dateRange="",
                        bullets=[
                            BulletItem(id="b-sk-2", text="PostgreSQL, Redis, Kafka, Docker, Kubernetes, AWS, Terraform"),
                        ],
                    ),
                ],
            ),
            ResumeSection(
                id="sec-proj",
                type="projects",
                title="Key Projects",
                visible=True,
                items=[
                    SectionItem(
                        id="item-proj-1",
                        title="MirrorCV Document Engine",
                        subtitle="Author / Maintainer",
                        location="",
                        dateRange="2024",
                        bullets=[
                            BulletItem(
                                id="b-proj-1",
                                text="Created zero-deviation headless PDF renderer marrying React state with Playwright Chromium.",
                            )
                        ],
                    )
                ],
            ),
            ResumeSection(
                id="sec-edu",
                type="education",
                title="Education",
                visible=True,
                items=[
                    SectionItem(
                        id="item-edu-1",
                        title="B.S. in Computer Science",
                        subtitle="UC Berkeley",
                        location="Berkeley, CA",
                        dateRange="2014 - 2018",
                        bullets=[
                            BulletItem(id="b-edu-1", text="Regents Scholar · Dean's Honor Roll (GPA: 3.92/4.0)")
                        ],
                    )
                ],
            ),
            ResumeSection(
                id="sec-cert",
                type="certifications",
                title="Certifications",
                visible=True,
                items=[
                    SectionItem(
                        id="item-cert-1",
                        title="AWS Certified Solutions Architect",
                        subtitle="Amazon Web Services",
                        location="",
                        dateRange="2023",
                        bullets=[],
                    )
                ],
            ),
        ],
    )

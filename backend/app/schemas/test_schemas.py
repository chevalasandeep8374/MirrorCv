import json
from app.schemas.content import (
    ContactLink,
    HeaderContent,
    BulletItem,
    SectionItem,
    ResumeSection,
    ResumeContent,
)
from app.schemas.style import (
    Margins,
    FontSizes,
    Typography,
    Spacing,
    Colors,
    ColumnLayout,
    ResumeStyle,
)


def get_default_sample_content() -> ResumeContent:
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
                        bullets=[
                            BulletItem(
                                id="b-sum-1",
                                text="Full-stack engineer with 8+ years architecting distributed web platforms and real-time document engines at scale.",
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
                        title="Principal Engineer",
                        subtitle="Acme Cloud Platforms",
                        location="San Francisco, CA",
                        dateRange="2021 - Present",
                        bullets=[
                            BulletItem(
                                id="b-exp-1",
                                text="Spearheaded migration of multi-tenant document engine to micro-frontends, reducing load latency by 42%.",
                            ),
                            BulletItem(
                                id="b-exp-2",
                                text="Mentored 12 mid-level and senior engineers across 3 distributed teams.",
                            ),
                        ],
                    )
                ],
            ),
            ResumeSection(
                id="sec-skills",
                type="skills",
                title="Skills",
                visible=True,
                items=[
                    SectionItem(
                        id="item-sk-1",
                        title="Frontend",
                        bullets=[
                            BulletItem(
                                id="b-sk-1",
                                text="TypeScript, React, Next.js, Tailwind CSS, Playwright, Web Audio/Canvas",
                            )
                        ],
                    ),
                    SectionItem(
                        id="item-sk-2",
                        title="Backend & Cloud",
                        bullets=[
                            BulletItem(
                                id="b-sk-2",
                                text="Python, FastAPI, PostgreSQL, SQLAlchemy, Docker, Redis, Kubernetes",
                            )
                        ],
                    ),
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
                        subtitle="University of California, Berkeley",
                        location="Berkeley, CA",
                        dateRange="2013 - 2017",
                        bullets=[
                            BulletItem(
                                id="b-edu-1",
                                text="Graduated Magna Cum Laude; President of ACM Student Chapter.",
                            )
                        ],
                    )
                ],
            ),
        ],
    )


def get_default_sample_style() -> ResumeStyle:
    return ResumeStyle(
        templateId="classic-single-column",
        pageSize="A4",
        margins=Margins(top=36, bottom=36, left=40, right=40, unit="pt"),
        typography=Typography(
            baseFontFamily="Inter",
            headingFontFamily="Inter",
            fontSizes=FontSizes(
                name=22,
                headerTitle=12,
                contact=9,
                sectionHeading=13,
                itemTitle=11,
                itemSubtitle=10,
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
            sidebarSectionIds=["sec-skills", "sec-edu"],
            mainSectionIds=["sec-summary", "sec-exp"],
        ),
    )


if __name__ == "__main__":
    content = get_default_sample_content()
    style = get_default_sample_style()

    content_json = content.model_dump_json(indent=2)
    style_json = style.model_dump_json(indent=2)

    # Validate roundtrip
    reloaded_content = ResumeContent.model_validate_json(content_json)
    reloaded_style = ResumeStyle.model_validate_json(style_json)

    print("Content and Style Pydantic schemas validated successfully!")
    print(f"Content sections: {len(reloaded_content.sections)}")
    print(f"Template ID: {reloaded_style.templateId}")

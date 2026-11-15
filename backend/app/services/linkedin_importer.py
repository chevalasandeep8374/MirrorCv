import io
import csv
import zipfile
import uuid
from typing import Dict, Any, Tuple, List


def parse_csv_from_zip(zf: zipfile.ZipFile, filename: str) -> List[Dict[str, str]]:
    """Finds and reads a CSV file from a zipfile ignoring case and directory prefixes."""
    target = filename.lower()
    for name in zf.namelist():
        if name.lower().endswith(target):
            try:
                raw_bytes = zf.read(name)
                # Decode with utf-8-sig to handle Excel BOM
                text = raw_bytes.decode("utf-8-sig", errors="replace")
                reader = csv.DictReader(io.StringIO(text))
                return [row for row in reader]
            except Exception:
                continue
    return []


def import_linkedin_zip(zip_bytes: bytes) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Parses a LinkedIn data export ZIP file and maps it into MirrorCV content schema."""
    mapped_sources: List[str] = []
    unmapped_sources: List[str] = []

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        profile_rows = parse_csv_from_zip(zf, "profile.csv")
        positions_rows = parse_csv_from_zip(zf, "positions.csv")
        education_rows = parse_csv_from_zip(zf, "education.csv")
        skills_rows = parse_csv_from_zip(zf, "skills.csv")
        certs_rows = parse_csv_from_zip(zf, "certifications.csv")

    header: Dict[str, Any] = {
        "name": "LinkedIn User",
        "title": "",
        "email": "",
        "phone": "",
        "location": "",
        "website": "",
        "links": [],
    }

    sections: List[Dict[str, Any]] = []

    # 1. Profile / Header
    if profile_rows:
        p = profile_rows[0]
        first = p.get("First Name", "").strip()
        last = p.get("Last Name", "").strip()
        full_name = f"{first} {last}".strip()
        if full_name:
            header["name"] = full_name

        header["title"] = p.get("Headline", "").strip()
        header["location"] = p.get("Geo Location", "").strip()
        mapped_sources.append("Profile.csv")

        summary_text = p.get("Summary", "").strip()
        if summary_text:
            sections.append({
                "id": f"sec-summary-{uuid.uuid4().hex[:6]}",
                "type": "summary",
                "title": "Professional Summary",
                "visible": True,
                "items": [
                    {
                        "id": f"item-{uuid.uuid4().hex[:8]}",
                        "title": "",
                        "subtitle": "",
                        "location": "",
                        "dateRange": "",
                        "itemType": "paragraph",
                        "bullets": [{"id": f"b-{uuid.uuid4().hex[:8]}", "text": summary_text}],
                    }
                ],
            })
    else:
        unmapped_sources.append("Profile.csv (not found in zip)")

    # 2. Positions / Experience
    if positions_rows:
        items = []
        for pos in positions_rows:
            desc = pos.get("Description", "").strip()
            bullets = []
            if desc:
                # Split lines by bullet or newline
                lines = [l.strip().lstrip("•-*▪➤ ") for l in desc.splitlines() if l.strip()]
                for l in lines:
                    if l:
                        bullets.append({"id": f"b-{uuid.uuid4().hex[:8]}", "text": l})

            start = pos.get("Started On", "").strip()
            end = pos.get("Finished On", "").strip() or "Present"
            date_range = f"{start} - {end}" if start else ""

            items.append({
                "id": f"item-{uuid.uuid4().hex[:8]}",
                "title": pos.get("Title", "").strip() or "Role",
                "subtitle": pos.get("Company Name", "").strip(),
                "location": pos.get("Location", "").strip(),
                "dateRange": date_range,
                "bullets": bullets,
            })

        sections.append({
            "id": f"sec-experience-{uuid.uuid4().hex[:6]}",
            "type": "experience",
            "title": "Work Experience",
            "visible": True,
            "items": items,
        })
        mapped_sources.append(f"Positions.csv ({len(items)} roles)")
    else:
        unmapped_sources.append("Positions.csv")

    # 3. Education
    if education_rows:
        items = []
        for edu in education_rows:
            start = edu.get("Start Date", "").strip()
            end = edu.get("End Date", "").strip()
            date_range = f"{start} - {end}" if start else ""
            notes = edu.get("Notes", "").strip()
            bullets = [{"id": f"b-{uuid.uuid4().hex[:8]}", "text": notes}] if notes else []

            items.append({
                "id": f"item-{uuid.uuid4().hex[:8]}",
                "title": edu.get("Degree Name", "").strip() or "Degree",
                "subtitle": edu.get("School Name", "").strip(),
                "location": "",
                "dateRange": date_range,
                "bullets": bullets,
            })

        sections.append({
            "id": f"sec-education-{uuid.uuid4().hex[:6]}",
            "type": "education",
            "title": "Education",
            "visible": True,
            "items": items,
        })
        mapped_sources.append(f"Education.csv ({len(items)} entries)")
    else:
        unmapped_sources.append("Education.csv")

    # 4. Skills
    if skills_rows:
        skill_names = [s.get("Name", "").strip() for s in skills_rows if s.get("Name", "").strip()]
        if skill_names:
            items = [
                {
                    "id": f"item-{uuid.uuid4().hex[:8]}",
                    "title": s,
                    "subtitle": "",
                    "location": "",
                    "dateRange": "",
                    "itemType": "tags",
                    "bullets": [],
                }
                for s in skill_names
            ]
            sections.append({
                "id": f"sec-skills-{uuid.uuid4().hex[:6]}",
                "type": "skills",
                "title": "Skills",
                "visible": True,
                "items": items,
            })
            mapped_sources.append(f"Skills.csv ({len(skill_names)} skills)")
    else:
        unmapped_sources.append("Skills.csv")

    # 5. Certifications
    if certs_rows:
        items = []
        for c in certs_rows:
            items.append({
                "id": f"item-{uuid.uuid4().hex[:8]}",
                "title": c.get("Name", "").strip() or "Certification",
                "subtitle": c.get("Authority", "").strip(),
                "location": "",
                "dateRange": c.get("Started On", "").strip(),
                "bullets": [],
            })
        sections.append({
            "id": f"sec-certifications-{uuid.uuid4().hex[:6]}",
            "type": "certifications",
            "title": "Certifications",
            "visible": True,
            "items": items,
        })
        mapped_sources.append(f"Certifications.csv ({len(items)} entries)")

    content_dict = {
        "header": header,
        "sections": sections,
    }

    report = {
        "source": "linkedin_zip",
        "mapped_sources": mapped_sources,
        "unmapped_sources": unmapped_sources,
        "total_sections_imported": len(sections),
    }

    return content_dict, report

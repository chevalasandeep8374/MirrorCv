import uuid
from typing import Dict, Any, Tuple, List


def format_date_range(start: Any, end: Any) -> str:
    """Formats start and end dates gracefully."""
    s_str = str(start).strip() if start else ""
    e_str = str(end).strip() if end else "Present"
    if s_str and e_str:
        return f"{s_str} - {e_str}"
    return s_str or e_str or ""


def import_json_resume(data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Imports standard JSON Resume schema (schema.json) into MirrorCV content schema.

    Returns (mapped_content_dict, mapping_report).
    """
    mapped_fields: List[str] = []
    unmapped_fields: List[str] = []

    basics = data.get("basics", {})
    location = basics.get("location", {})
    loc_parts = [p for p in (location.get("city"), location.get("region"), location.get("countryCode")) if p]
    loc_str = ", ".join(loc_parts)

    links = []
    for p in basics.get("profiles", []):
        if p.get("url"):
            links.append({
                "id": f"link-{uuid.uuid4().hex[:8]}",
                "label": p.get("network") or "Link",
                "url": p["url"],
            })

    header = {
        "name": basics.get("name") or "Imported Candidate",
        "title": basics.get("label") or "",
        "email": basics.get("email") or "",
        "phone": basics.get("phone") or "",
        "location": loc_str,
        "website": basics.get("url") or "",
        "photoUrl": basics.get("image") or None,
        "links": links,
    }
    mapped_fields.extend(["basics.name", "basics.label", "basics.email", "basics.phone", "basics.location", "basics.profiles"])

    sections: List[Dict[str, Any]] = []

    # 1. Summary
    if basics.get("summary"):
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
                    "bullets": [{"id": f"b-{uuid.uuid4().hex[:8]}", "text": basics["summary"]}],
                }
            ],
        })
        mapped_fields.append("basics.summary")

    # 2. Work / Experience
    work_items = data.get("work", [])
    if work_items:
        items = []
        for w in work_items:
            bullets = []
            for h in w.get("highlights", []):
                bullets.append({"id": f"b-{uuid.uuid4().hex[:8]}", "text": str(h).strip()})
            if not bullets and w.get("summary"):
                bullets.append({"id": f"b-{uuid.uuid4().hex[:8]}", "text": str(w["summary"]).strip()})

            items.append({
                "id": f"item-{uuid.uuid4().hex[:8]}",
                "title": w.get("position") or "Role",
                "subtitle": w.get("name") or "",
                "location": w.get("location") or "",
                "dateRange": format_date_range(w.get("startDate"), w.get("endDate")),
                "bullets": bullets,
            })
        sections.append({
            "id": f"sec-experience-{uuid.uuid4().hex[:6]}",
            "type": "experience",
            "title": "Work Experience",
            "visible": True,
            "items": items,
        })
        mapped_fields.append("work")

    # 3. Education
    edu_items = data.get("education", [])
    if edu_items:
        items = []
        for ed in edu_items:
            degree = ed.get("studyType", "")
            area = ed.get("area", "")
            title = f"{degree} in {area}".strip(" in ") if (degree or area) else "Degree"
            courses = ed.get("courses", [])
            bullets = [{"id": f"b-{uuid.uuid4().hex[:8]}", "text": f"Relevant Coursework: {', '.join(courses)}"}] if courses else []

            items.append({
                "id": f"item-{uuid.uuid4().hex[:8]}",
                "title": title,
                "subtitle": ed.get("institution") or "",
                "location": "",
                "dateRange": format_date_range(ed.get("startDate"), ed.get("endDate")),
                "bullets": bullets,
            })
        sections.append({
            "id": f"sec-education-{uuid.uuid4().hex[:6]}",
            "type": "education",
            "title": "Education",
            "visible": True,
            "items": items,
        })
        mapped_fields.append("education")

    # 4. Skills
    skills_data = data.get("skills", [])
    if skills_data:
        items = []
        for sk in skills_data:
            keywords = sk.get("keywords", [])
            bullets = [{"id": f"b-{uuid.uuid4().hex[:8]}", "text": k} for k in keywords]
            items.append({
                "id": f"item-{uuid.uuid4().hex[:8]}",
                "title": sk.get("name") or "Skills",
                "subtitle": sk.get("level") or "",
                "location": "",
                "dateRange": "",
                "itemType": "tags" if keywords else "list",
                "bullets": bullets,
            })
        sections.append({
            "id": f"sec-skills-{uuid.uuid4().hex[:6]}",
            "type": "skills",
            "title": "Skills",
            "visible": True,
            "items": items,
        })
        mapped_fields.append("skills")

    # 5. Projects
    projects_data = data.get("projects", [])
    if projects_data:
        items = []
        for proj in projects_data:
            bullets = [{"id": f"b-{uuid.uuid4().hex[:8]}", "text": h} for h in proj.get("highlights", [])]
            if not bullets and proj.get("description"):
                bullets.append({"id": f"b-{uuid.uuid4().hex[:8]}", "text": proj["description"]})
            items.append({
                "id": f"item-{uuid.uuid4().hex[:8]}",
                "title": proj.get("name") or "Project",
                "subtitle": proj.get("url") or "",
                "location": "",
                "dateRange": format_date_range(proj.get("startDate"), proj.get("endDate")),
                "bullets": bullets,
            })
        sections.append({
            "id": f"sec-projects-{uuid.uuid4().hex[:6]}",
            "type": "projects",
            "title": "Projects",
            "visible": True,
            "items": items,
        })
        mapped_fields.append("projects")

    # 6. Certificates
    certs_data = data.get("certificates", [])
    if certs_data:
        items = []
        for c in certs_data:
            items.append({
                "id": f"item-{uuid.uuid4().hex[:8]}",
                "title": c.get("name") or "Certification",
                "subtitle": c.get("issuer") or "",
                "location": "",
                "dateRange": str(c.get("date") or ""),
                "bullets": [],
            })
        sections.append({
            "id": f"sec-certifications-{uuid.uuid4().hex[:6]}",
            "type": "certifications",
            "title": "Certifications",
            "visible": True,
            "items": items,
        })
        mapped_fields.append("certificates")

    # 7. Languages
    langs_data = data.get("languages", [])
    if langs_data:
        items = []
        for l in langs_data:
            items.append({
                "id": f"item-{uuid.uuid4().hex[:8]}",
                "title": l.get("language") or "Language",
                "subtitle": l.get("fluency") or "",
                "location": "",
                "dateRange": "",
                "bullets": [],
            })
        sections.append({
            "id": f"sec-languages-{uuid.uuid4().hex[:6]}",
            "type": "languages",
            "title": "Languages",
            "visible": True,
            "items": items,
        })
        mapped_fields.append("languages")

    # Check unmapped root keys
    recognized_keys = {"basics", "work", "volunteer", "education", "awards", "publications", "skills", "languages", "interests", "references", "projects", "certificates"}
    for k in data.keys():
        if k not in recognized_keys:
            unmapped_fields.append(k)

    content_dict = {
        "header": header,
        "sections": sections,
    }

    report = {
        "source": "json_resume",
        "mapped_fields": mapped_fields,
        "unmapped_fields": unmapped_fields,
        "total_sections_imported": len(sections),
    }

    return content_dict, report

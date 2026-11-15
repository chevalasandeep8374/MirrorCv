import os
import logging
from langgraph.graph import StateGraph, END
from app.graph.state import TailoringState
from app.services.docx_fingerprint import fingerprint_docx
from app.services.role_classifier import classify_paragraphs
from app.services.content_extractor import extract_content_and_style
from app.services.jd_analyzer import analyze_job_description_sync
from app.services.tailor_agent import tailor_resume_content, calculate_pdf_bullet_budgets
from app.services.fidelity_writer import write_tailored_docx
from app.services.pdf_converter import convert_docx_to_pdf
from app.services.fit_checker import check_pdf_fit_overflow
from app.services.match_scorer import calculate_match_score
from app.services.pdf_extractor import extract_pdf_spans_and_assets
from app.services.pdf_layout_analyzer import analyze_pdf_layout
from app.services.pdf_font_analyzer import analyze_pdf_fonts
from app.services.pdf_role_adapter import process_pdf_roles_and_content
from app.services.pdf_strategy_selector import select_best_strategy
from app.schemas.template import DocxFingerprint, RoleMap
from app.schemas.pdf_template import PdfLayout, FontResolutionTable

logger = logging.getLogger(__name__)


def node_parse_fingerprint(state: TailoringState) -> TailoringState:
    logger.info("Executing node: parse_fingerprint")
    is_pdf = state.get("template_type") == "pdf" or (
        state.get("original_pdf_path", "").lower().endswith(".pdf")
        and not state.get("original_docx_path")
    )
    if is_pdf:
        state["template_type"] = "pdf"
        if not state.get("layout"):
            pdf_path = state["original_pdf_path"]
            raw_layout = extract_pdf_spans_and_assets(pdf_path)
            layout = analyze_pdf_layout(raw_layout)
            font_table = analyze_pdf_fonts(pdf_path, layout)
            role_map, content, style, c_to_p, c_to_boxes = process_pdf_roles_and_content(layout)

            state["layout"] = layout.model_dump()
            state["font_table"] = font_table.model_dump()
            state["role_map"] = role_map.model_dump()
            state["source_content"] = content
            state["source_style"] = style
            state["content_to_paragraphs"] = c_to_p
    else:
        state["template_type"] = "docx"
        if not state.get("fingerprint"):
            fp = fingerprint_docx(state["original_docx_path"])
            state["fingerprint"] = fp.model_dump()

    state["current_step"] = "fingerprinted"
    return state


def node_classify_roles(state: TailoringState) -> TailoringState:
    logger.info("Executing node: classify_roles")
    if not state.get("role_map"):
        fp = DocxFingerprint.model_validate(state["fingerprint"])
        rm = classify_paragraphs(fp)
        state["role_map"] = rm.model_dump()
    state["current_step"] = "roles_classified"
    return state


def node_extract_content(state: TailoringState) -> TailoringState:
    logger.info("Executing node: extract_content")
    if not state.get("source_content") or not state.get("content_to_paragraphs"):
        fp = DocxFingerprint.model_validate(state["fingerprint"])
        rm = RoleMap.model_validate(state["role_map"])
        content, style, c_to_p = extract_content_and_style(fp, rm)
        state["source_content"] = content
        state["source_style"] = style
        state["content_to_paragraphs"] = c_to_p
    state["current_step"] = "content_extracted"
    return state


def node_analyze_jd(state: TailoringState) -> TailoringState:
    logger.info("Executing node: analyze_jd")
    jd_analysis = analyze_job_description_sync(state["jd_text"])
    state["jd_analysis"] = jd_analysis
    state["current_step"] = "jd_analyzed"
    return state


def node_score_before(state: TailoringState) -> TailoringState:
    logger.info("Executing node: score_before")
    score_before = calculate_match_score(state["source_content"], state["jd_analysis"])
    state["match_score_before"] = score_before
    state["fit_attempt"] = 0
    state["warnings"] = []
    state["current_step"] = "score_before_computed"
    return state


def node_tailor(state: TailoringState) -> TailoringState:
    attempt = state.get("fit_attempt", 0) + 1
    state["fit_attempt"] = attempt
    logger.info(f"Executing node: tailor (attempt {attempt}/3)")

    stricter = state.get("stricter_budgets", {})
    custom_budgets = None
    if state.get("template_type") == "pdf" and state.get("layout"):
        custom_budgets = calculate_pdf_bullet_budgets(
            state["source_content"],
            state["layout"],
            state.get("content_to_paragraphs", {}),
        )

    tailored_out = tailor_resume_content(
        source_content=state["source_content"],
        jd_analysis=state["jd_analysis"],
        stricter_budgets=stricter,
        custom_budgets=custom_budgets,
    )

    state["tailored_content"] = tailored_out.tailored_content
    state["changes"] = tailored_out.changes
    state["skills_missing"] = tailored_out.skills_missing
    state["current_step"] = f"tailored_round_{attempt}"
    return state


def node_write_docx(state: TailoringState) -> TailoringState:
    if state.get("template_type") == "pdf":
        logger.info("Bypassing write_docx for PDF template")
        state["current_step"] = "pdf_template_bypassed_docx"
        return state

    logger.info("Executing node: write_docx")
    out_dir = os.path.dirname(os.path.abspath(state["original_docx_path"]))
    tailored_docx_path = os.path.join(out_dir, f"tailored_{state['job_id']}.docx")

    write_tailored_docx(
        template_docx_path=state["original_docx_path"],
        tailored_content=state["tailored_content"],
        content_to_paragraphs=state["content_to_paragraphs"],
        output_docx_path=tailored_docx_path,
    )
    state["tailored_docx_path"] = tailored_docx_path
    state["current_step"] = "docx_written"
    return state


def node_render_pdf(state: TailoringState) -> TailoringState:
    logger.info("Executing node: render_pdf")
    if state.get("template_type") == "pdf":
        out_dir = os.path.dirname(os.path.abspath(state["original_pdf_path"]))
        tailored_pdf_path = os.path.join(out_dir, f"tailored_{state['job_id']}.pdf")

        layout_obj = PdfLayout.model_validate(state["layout"]) if isinstance(state.get("layout"), dict) else state.get("layout")
        role_map_obj = RoleMap.model_validate(state["role_map"]) if isinstance(state.get("role_map"), dict) else state.get("role_map")
        font_tbl_obj = FontResolutionTable.model_validate(state["font_table"]) if isinstance(state.get("font_table"), dict) else state.get("font_table")

        writer, score, _ = select_best_strategy(
            template_path=state["original_pdf_path"],
            layout=layout_obj,
            role_map=role_map_obj,
            content=state["tailored_content"],
            style=state["source_style"],
            content_to_paragraphs=state["content_to_paragraphs"],
            font_table=font_tbl_obj,
            work_dir=out_dir,
        )

        writer.write(
            content=state["tailored_content"],
            template_path=state["original_pdf_path"],
            output_path=tailored_pdf_path,
            template_data={
                "layout": layout_obj,
                "role_map": role_map_obj,
                "style": state["source_style"],
                "content_to_paragraphs": state["content_to_paragraphs"],
                "font_table": font_tbl_obj,
                "is_scanned": layout_obj.document_metadata.is_scanned if layout_obj else False,
            },
        )

        state["tailored_pdf_path"] = tailored_pdf_path
        state["fidelity_score"] = score.model_dump()
        state["fidelity_tier"] = score.tier
        state["selected_strategy"] = score.selected_strategy

        # Add warnings for substituted fonts
        if font_tbl_obj and font_tbl_obj.substitutions:
            for sub in font_tbl_obj.substitutions:
                state["warnings"].append(f"Font '{sub.original}' substituted with '{sub.replacement}'.")

        state["current_step"] = "pdf_rendered"
        return state

    out_dir = os.path.dirname(os.path.abspath(state["tailored_docx_path"]))
    tailored_pdf_path = os.path.join(out_dir, f"tailored_{state['job_id']}.pdf")

    # Also render original PDF if not already rendered
    if not state.get("original_pdf_path") or not os.path.exists(state["original_pdf_path"]):
        orig_pdf = os.path.join(out_dir, f"original_{state['job_id']}.pdf")
        convert_docx_to_pdf(state["original_docx_path"], orig_pdf)
        state["original_pdf_path"] = orig_pdf

    convert_docx_to_pdf(state["tailored_docx_path"], tailored_pdf_path)
    state["tailored_pdf_path"] = tailored_pdf_path
    state["current_step"] = "pdf_rendered"
    return state


def node_fit_check(state: TailoringState) -> TailoringState:
    logger.info("Executing node: fit_check")
    passed, orig_p, tail_p, offending, stricter_budgets = check_pdf_fit_overflow(
        original_pdf_path=state["original_pdf_path"],
        tailored_pdf_path=state["tailored_pdf_path"],
        tailored_content=state["tailored_content"],
        original_content=state["source_content"],
    )

    state["fit_passed"] = passed
    state["original_page_count"] = orig_p
    state["tailored_page_count"] = tail_p
    state["offending_bullet_ids"] = offending
    state["stricter_budgets"] = stricter_budgets

    if not passed and state.get("fit_attempt", 1) >= 3:
        state["warnings"].append(
            f"Fidelity warning: Document expanded from {orig_p} to {tail_p} pages despite 3 compression rounds."
        )

    state["current_step"] = "fit_checked"
    return state


def condition_fit_decision(state: TailoringState) -> str:
    """If overflow detected and under 3 attempts, loop back to tailor; else finalize."""
    if not state.get("fit_passed", True) and state.get("fit_attempt", 1) < 3:
        logger.info(f"Fit loop triggered: attempt {state.get('fit_attempt')} had overflow, re-tailoring with stricter budgets.")
        return "re_tailor"
    return "score_final"


def node_score_after(state: TailoringState) -> TailoringState:
    logger.info("Executing node: score_after")
    score_after = calculate_match_score(state["tailored_content"], state["jd_analysis"])
    state["match_score_after"] = score_after
    state["current_step"] = "completed"
    return state


def build_tailoring_graph():
    """Compiles the LangGraph state graph for end-to-end resume tailoring."""
    builder = StateGraph(TailoringState)

    builder.add_node("parse_fingerprint", node_parse_fingerprint)
    builder.add_node("classify_roles", node_classify_roles)
    builder.add_node("extract_content", node_extract_content)
    builder.add_node("analyze_jd", node_analyze_jd)
    builder.add_node("score_before", node_score_before)
    builder.add_node("tailor", node_tailor)
    builder.add_node("write_docx", node_write_docx)
    builder.add_node("render_pdf", node_render_pdf)
    builder.add_node("fit_check", node_fit_check)
    builder.add_node("score_after", node_score_after)

    builder.set_entry_point("parse_fingerprint")

    builder.add_edge("parse_fingerprint", "classify_roles")
    builder.add_edge("classify_roles", "extract_content")
    builder.add_edge("extract_content", "analyze_jd")
    builder.add_edge("analyze_jd", "score_before")
    builder.add_edge("score_before", "tailor")
    builder.add_edge("tailor", "write_docx")
    builder.add_edge("write_docx", "render_pdf")
    builder.add_edge("render_pdf", "fit_check")

    builder.add_conditional_edges(
        "fit_check",
        condition_fit_decision,
        {
            "re_tailor": "tailor",
            "score_final": "score_after",
        },
    )

    builder.add_edge("score_after", END)

    return builder.compile()


tailoring_pipeline_graph = build_tailoring_graph()

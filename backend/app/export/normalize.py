import base64
import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.config.settings import settings

logger = logging.getLogger("proposalcraft.export.normalize")

_OBJECTID_PATTERN = re.compile(r"^[0-9a-fA-F]{24}$")


def _resolve_logo_path(path: str) -> Path:
    p = Path(path)
    if p.is_absolute():
        return p
    return Path(__file__).resolve().parent.parent.parent / p


def _encode_logo(path_or_url: str) -> str:
    """Encode a logo as a base64 data URI for embedding in HTML/PDF."""
    if not path_or_url:
        return ""
    if path_or_url.startswith("data:"):
        return path_or_url
    try:
        if path_or_url.startswith(("http://", "https://")):
            import urllib.request

            with urllib.request.urlopen(path_or_url, timeout=5) as resp:
                data = resp.read()
                mime = resp.headers.get_content_type() or "image/png"
        else:
            p = _resolve_logo_path(path_or_url)
            data = p.read_bytes()
            mime = "image/svg+xml" if p.suffix.lower() == ".svg" else "image/png"
        encoded = base64.b64encode(data).decode("ascii")
        return f"data:{mime};base64,{encoded}"
    except Exception as e:
        logger.warning("Could not encode logo '%s': %s", path_or_url, e)
        return ""


@lru_cache(maxsize=1)
def _default_logo() -> str:
    return _encode_logo(settings.DEFAULT_LOGO_PATH)


def _parse_cost(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = re.sub(r"[^\d.]", "", value)
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0
    return 0.0


def normalize_proposal(proposal: dict) -> dict:
    """Normalize proposal data to the flat structure expected by renderers.
    Handles two input shapes:
      - Flat: { executive_summary: {...}, pricing: {...}, metadata: {...} }
      - Nested: { sections: { executive_summary: {...}, ... }, metadata: {...} }
    """
    # Build metadata from raw DB document fields if not already present
    if "metadata" not in proposal or not proposal["metadata"]:
        proposal["metadata"] = {
            "proposal_title": proposal.get("title", "Proposal"),
            "subtitle": "",
            "client_name": proposal.get("client_name", ""),
            "company_name": proposal.get("company_name") or "",
            "company_logo": _encode_logo(proposal.get("company_logo", "")) or _default_logo(),
            "proposal_id": proposal.get("proposal_id", ""),
            "date": str(proposal.get("created_at", "")).split("T")[0],
            "version": str(proposal.get("version", "1.0")),
            "status": proposal.get("status", "Draft"),
        }
    else:
        proposal["metadata"].setdefault("company_logo", _encode_logo(proposal.get("company_logo", "")) or _default_logo())
        if not proposal["metadata"].get("company_name"):
            proposal["metadata"]["company_name"] = proposal.get("company_name") or ""

    if "sections" in proposal:
        sections = proposal.pop("sections", {})
        if isinstance(sections, dict):
            for key, value in sections.items():
                if key not in proposal:
                    proposal[key] = value

    # Flatten diagram_data into top-level keys before normalizing sections
    diagram_data = proposal.pop("diagram_data", None)
    if isinstance(diagram_data, dict):
        workflow_svg = diagram_data.get("workflow_svg", "")
        timeline_svg = diagram_data.get("timeline_svg", "")
        architecture_svg = diagram_data.get("architecture_svg", "")
        if workflow_svg:
            proposal["workflow_diagram_svg"] = workflow_svg
        if timeline_svg:
            proposal["timeline_diagram_svg"] = timeline_svg
        if architecture_svg:
            proposal["architecture_diagram_svg"] = architecture_svg

    for key, value in list(proposal.items()):
        if key == "metadata":
            continue
        if isinstance(value, dict):
            _normalize_section_dict(proposal, key, value)
        elif isinstance(value, str):
            _normalize_section_string(proposal, key, value)
        elif isinstance(value, list):
            _normalize_section_list(proposal, key, value)

    return proposal


def _normalize_section_dict(proposal: dict, key: str, data: dict) -> None:
    if key == "executive_summary":
        proposal[key] = {
            "business_overview": data.get("business_overview") or data.get("text", ""),
            "problem_statement": data.get("problem_statement") or data.get("challenge", ""),
            "proposed_solution": data.get("proposed_solution") or data.get("solution", ""),
            "expected_roi": data.get("expected_roi") or data.get("roi", ""),
            "business_value": data.get("business_value") or "",
            "key_benefits": data.get("key_benefits", data.get("benefits", [])),
        }
    elif key == "pricing" or key == "investment":
        total_cost_str = data.get("development_cost") or data.get("one_time_cost", "") or data.get("total_cost", "")
        monthly_cost_str = data.get("cloud_cost") or data.get("monthly_cost", "")
        proposal["pricing"] = {
            "development_cost": total_cost_str if isinstance(total_cost_str, str) else str(total_cost_str),
            "cloud_cost": monthly_cost_str if isinstance(monthly_cost_str, str) else str(monthly_cost_str),
            "support_cost": data.get("support_cost") or "",
            "amc": data.get("amc") or "",
            "payment_terms": data.get("payment_terms") or "",
            "one_time_cost": data.get("one_time_cost", 0) or _parse_cost(total_cost_str),
            "monthly_cost": data.get("monthly_cost", 0) or _parse_cost(monthly_cost_str),
            "annual_cost": data.get("annual_cost", 0),
            "five_year_tco": data.get("five_year_tco", 0),
            "total_effort_hours": data.get("total_effort_hours", 0),
            "effort_breakdown": data.get("effort_breakdown", {}),
            "payment_options": data.get("payment_options", []),
        }
        if key != "pricing":
            proposal.pop(key, None)
    elif key == "timeline":
        proposal[key] = {
            "gantt_chart": data.get("gantt_chart", ""),
            "milestones": data.get("milestones", data.get("phases", [])),
            "phases": data.get("phases", []),
        }
    elif key == "sla":
        proposal[key] = {
            "uptime_guarantee": data.get("uptime_guarantee", ""),
            "sla_tiers": data.get("sla_tiers", []),
            "service_credits": data.get("service_credits", {}),
            "maintenance_windows": data.get("maintenance_windows", {}),
        }
    elif key == "project_overview":
        proposal["client_understanding"] = {
            "business_overview": data.get("background", ""),
            "business_goals": data.get("objectives", []),
        }
        proposal["requirement_analysis"] = {
            "scope": data.get("scope", ""),
            "out_of_scope": data.get("out_of_scope", []),
        }
        proposal.pop(key, None)
    elif key == "why_choose_us":
        parts = []
        if data.get("expertise"):
            parts.append(data["expertise"])
        if data.get("approach"):
            parts.append(data["approach"])
        if data.get("support"):
            parts.append(data["support"])
        proposal["about_company"] = {
            "why_choose_us": parts,
            "who_we_are": data.get("expertise", ""),
        }
        proposal.pop(key, None)
    elif key == "implementation_plan":
        proposal["project_plan"] = {
            "timeline": data.get("timeline", ""),
            "milestones": data.get("milestones", []),
            "team": data.get("team", ""),
        }
        proposal.pop(key, None)


def _normalize_section_list(proposal: dict, key: str, items: list) -> None:
    if key == "core_features":
        proposal["module_breakdown"] = [
            {
                "module_name": item.get("name", str(item)),
                "description": item.get("description", ""),
                "benefit": item.get("benefit", ""),
            }
            for item in items
        ]
        proposal.pop(key, None)
    elif key == "next_steps":
        conclusion = proposal.get("conclusion", {})
        if isinstance(conclusion, str):
            conclusion = {"summary": conclusion}
        if not isinstance(conclusion, dict):
            conclusion = {}
        conclusion["next_steps"] = [str(s) for s in items]
        proposal["conclusion"] = conclusion
        proposal.pop(key, None)


def _normalize_section_string(proposal: dict, key: str, value: str) -> None:
    if key == "executive_summary":
        proposal[key] = {
            "business_overview": value,
            "problem_statement": "",
            "proposed_solution": "",
            "expected_roi": "",
            "business_value": "",
            "key_benefits": [],
        }
    elif key == "pricing":
        proposal[key] = {
            "development_cost": value,
            "cloud_cost": "",
            "support_cost": "",
            "amc": "",
            "payment_terms": "",
        }

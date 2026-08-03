"""Shared section iteration and content shaping for all export renderers.

Single source of truth: SECTION_RULES (order) + normalize_proposal (shape).
Each renderer only decides HOW to lay out the blocks; never WHAT the content is.
"""

from app.templates.section_rules import SECTION_RULES

SECTION_LABELS = {
    "about_company": "About Us",
    "executive_summary": "Executive Summary",
    "client_understanding": "Client Understanding",
    "requirement_analysis": "Requirement Analysis",
    "proposed_solution": "Proposed Solution",
    "module_breakdown": "Module Breakdown",
    "user_journey": "User Journey",
    "technology_stack": "Technology Stack",
    "ai_architecture": "AI Architecture",
    "system_architecture": "System Architecture",
    "database_design": "Database Design",
    "security": "Security",
    "methodology": "Methodology",
    "timeline": "Timeline",
    "deliverables": "Deliverables",
    "pricing": "Investment",
    "custom_development_charges": "Custom Development Charges",
    "sla": "Service Level Agreement",
    "support": "Support Plan",
    "terms": "Terms & Conditions",
    "case_studies": "Case Studies",
    "team": "Team",
    "conclusion": "Conclusion",
    "diagrams": "Appendix A: Solution Architecture & Workflow",
}

RENDERED_SECTION_KEYS = {
    "about_company", "executive_summary", "client_understanding", "requirement_analysis",
    "proposed_solution", "module_breakdown", "technology_stack", "methodology", "timeline",
    "deliverables", "pricing", "custom_development_charges", "sla", "support", "security",
    "terms", "case_studies", "team", "conclusion", "diagrams",
}

DIAGRAM_SECTION_KEYS = ("workflow_diagram_svg", "architecture_diagram_svg", "timeline_diagram_svg")


def section_order_from_rules() -> list[str]:
    """Derive render order from SECTION_RULES — the single source of truth."""
    return [
        key
        for key, _ in sorted(SECTION_RULES.items(), key=lambda kv: kv[1].get("order", 999))
        if key in RENDERED_SECTION_KEYS
    ]


def iter_renderable_sections(proposal: dict, include_diagrams: bool = False):
    """Yield (key, label, data) for every present section in canonical order."""
    for key in section_order_from_rules():
        data = proposal.get(key)
        if key == "diagrams":
            if not include_diagrams or not any(proposal.get(dk) for dk in DIAGRAM_SECTION_KEYS):
                continue
        elif not data:
            continue
        yield key, SECTION_LABELS.get(key, key.replace("_", " ").title()), data


def _money(value) -> str:
    if value in (None, ""):
        return ""
    try:
        return f"${float(value):,.0f}"
    except (TypeError, ValueError):
        return str(value)


def build_section_blocks(key: str, data) -> list[tuple]:
    """Build format-neutral content blocks for a section.

    Block types: ("h3", text), ("p", text), ("bullets", [..]), ("table", [headers], [[rows]]).
    """
    if key == "module_breakdown":
        return _blocks_module_breakdown(data)
    if key == "technology_stack":
        return _blocks_technology_stack(data)
    if key == "timeline":
        return _blocks_timeline(data)
    if key == "pricing":
        return _blocks_pricing(data)
    if key == "sla":
        return _blocks_sla(data)
    if key == "team":
        return _blocks_team(data)
    if key == "about_company":
        return _blocks_about_company(data)
    if key == "executive_summary":
        return _blocks_executive_summary(data)
    if key == "conclusion":
        return _blocks_conclusion(data)
    if key == "security":
        return _blocks_security(data)
    if key == "terms":
        return _blocks_terms(data)
    if key == "methodology":
        return _blocks_methodology(data)
    return _blocks_generic(data)


def _dict_items(data: dict, order: list[str], labels: dict[str, str]) -> list[tuple]:
    blocks = []
    for k in order:
        v = data.get(k)
        if not v:
            continue
        label = labels.get(k, k.replace("_", " ").title())
        if isinstance(v, list):
            blocks.append(("h3", label))
            blocks.append(("bullets", [str(x) for x in v]))
        else:
            blocks.append(("h3", label))
            blocks.append(("p", str(v)))
    return blocks


def _blocks_about_company(data: dict) -> list[tuple]:
    blocks = []
    for k, label in [
        ("who_we_are", "Who We Are"),
        ("experience", "Experience"),
        ("vision", "Vision"),
        ("mission", "Mission"),
    ]:
        if data.get(k):
            blocks.append(("h3", label))
            blocks.append(("p", str(data[k])))
    for k, label in [("why_choose_us", "Why Choose Us"), ("achievements", "Achievements")]:
        if data.get(k):
            blocks.append(("h3", label))
            blocks.append(("bullets", [str(x) for x in data[k]]))
    return blocks


def _blocks_executive_summary(data: dict) -> list[tuple]:
    blocks = []
    for k, label in [
        ("business_overview", "Overview"),
        ("problem_statement", "Problem Statement"),
        ("proposed_solution", "Proposed Solution"),
        ("expected_roi", "Expected ROI"),
        ("business_value", "Business Value"),
    ]:
        if data.get(k):
            blocks.append(("p", f"{label}: {data[k]}"))
    if data.get("key_benefits"):
        blocks.append(("h3", "Key Benefits"))
        blocks.append(("bullets", [str(b) for b in data["key_benefits"]]))
    return blocks


def _blocks_conclusion(data: dict) -> list[tuple]:
    blocks = []
    if data.get("summary"):
        blocks.append(("p", str(data["summary"])))
    if data.get("next_steps"):
        blocks.append(("h3", "Next Steps"))
        blocks.append(("bullets", [str(s) for s in data["next_steps"]]))
    return blocks


def _blocks_security(data: dict) -> list[tuple]:
    labels = {
        "authentication": "Authentication",
        "authorization": "Authorization",
        "encryption": "Encryption",
        "audit_logs": "Audit Logs",
        "backup": "Backup & Recovery",
        "owasp": "OWASP Compliance",
    }
    blocks = []
    for k, label in labels.items():
        if data.get(k):
            blocks.append(("p", f"{label}: {data[k]}"))
    return blocks


def _blocks_terms(data: dict) -> list[tuple]:
    blocks = []
    for k, label in [("assumptions", "Assumptions"), ("exclusions", "Cost Exclusions")]:
        if data.get(k):
            blocks.append(("h3", label))
            blocks.append(("bullets", [str(x) for x in data[k]]))
    for k, label in [("confidentiality", "Confidentiality"), ("warranty", "Warranty")]:
        if data.get(k):
            blocks.append(("h3", label))
            blocks.append(("p", str(data[k])))
    return blocks


def _blocks_methodology(data: dict) -> list[tuple]:
    blocks = []
    if isinstance(data, dict):
        if data.get("approach"):
            blocks.append(("p", str(data["approach"])))
        if data.get("phases"):
            blocks.append(("bullets", [str(p) for p in data["phases"]]))
        if data.get("ceremonies"):
            blocks.append(("h3", "Ceremonies"))
            blocks.append(("bullets", [str(c) for c in data["ceremonies"]]))
    else:
        blocks.append(("bullets", [str(p) for p in data]))
    return blocks


def _blocks_module_breakdown(data) -> list[tuple]:
    blocks = []
    if isinstance(data, dict) and ("standard_modules" in data or "custom_modules" in data):
        for sub, label in [("standard_modules", "Standard Modules"), ("custom_modules", "Custom Modules")]:
            items = data.get(sub) or []
            if items:
                blocks.append(("h3", label))
                rows = []
                for m in items:
                    if isinstance(m, dict):
                        rows.append([str(m.get("name") or m.get("module_name") or ""), str(m.get("description") or "")])
                    else:
                        rows.append([str(m), ""])
                blocks.append(("table", ["Module", "Description"], rows))
    elif isinstance(data, list):
        rows = []
        for m in data:
            if isinstance(m, dict):
                rows.append([str(m.get("name") or m.get("module_name") or ""), str(m.get("description") or "")])
            else:
                rows.append([str(m), ""])
        blocks.append(("table", ["Module", "Description"], rows))
    return blocks


def _blocks_technology_stack(data) -> list[tuple]:
    blocks = []
    if isinstance(data, dict):
        rows = []
        for layer, techs in data.items():
            if layer == "rationale" or not techs:
                continue
            names = []
            for t in techs:
                if isinstance(t, dict):
                    names.append(t.get("name", str(t)))
                else:
                    names.append(str(t))
            rows.append([layer.replace("_", " ").title(), ", ".join(names)])
        if rows:
            blocks.append(("table", ["Layer", "Technologies"], rows))
        if data.get("rationale"):
            blocks.append(("p", str(data["rationale"])))
    return blocks


def _blocks_timeline(data: dict) -> list[tuple]:
    blocks = []
    phases = data.get("phases") or []
    if phases:
        week_detail = isinstance(phases[0], dict) and "output" in phases[0]
        if week_detail:
            rows = []
            for p in phases:
                if not isinstance(p, dict):
                    continue
                rows.append([
                    f"{p.get('duration_weeks', '')} weeks" if p.get("duration_weeks") else "",
                    str(p.get("scope") or ""),
                    ", ".join(p.get("modules_used") or []) if isinstance(p.get("modules_used"), list) else "",
                    str(p.get("output") or ""),
                ])
            blocks.append(("table", ["Week", "Scope", "Modules Used", "Output"], rows))
        else:
            rows = []
            for p in phases:
                if not isinstance(p, dict):
                    rows.append([str(p), "", ""])
                    continue
                rows.append([
                    str(p.get("name") or ""),
                    f"{p.get('duration_weeks', '')} weeks" if p.get("duration_weeks") else "",
                    ", ".join(str(a) for a in p.get("activities") or []),
                ])
            blocks.append(("table", ["Phase", "Duration", "Activities"], rows))
    if data.get("milestones"):
        blocks.append(("h3", "Milestones"))
        blocks.append(("bullets", [str(m.get("event", m)) if isinstance(m, dict) else str(m) for m in data["milestones"]]))
    return blocks


def _blocks_pricing(data: dict) -> list[tuple]:
    blocks = []
    if data.get("one_time_cost") or data.get("monthly_cost"):
        rows = []
        if data.get("one_time_cost"):
            rows.append(["One-Time Development", _money(data["one_time_cost"])])
        if data.get("monthly_cost"):
            rows.append(["Monthly Subscription", f"{_money(data['monthly_cost'])}/month"])
        if data.get("annual_cost"):
            rows.append(["Annual Cost (Year 1)", _money(data["annual_cost"])])
        if data.get("five_year_tco"):
            rows.append(["5-Year TCO", _money(data["five_year_tco"])])
        blocks.append(("table", ["Item", "Amount"], rows))
    if data.get("total_effort_hours"):
        blocks.append(("p", f"Total Effort: {data['total_effort_hours']} hours"))
    if data.get("support_hours_included"):
        blocks.append(("p", f"Support Hours Included: {data['support_hours_included']} hours/month"))
    breakdown = data.get("effort_breakdown") or {}
    if isinstance(breakdown, dict) and breakdown:
        rows = []
        for name, details in breakdown.items():
            if isinstance(details, dict):
                rows.append([
                    str(name),
                    str(details.get("hours", "")),
                    f"${details.get('hourly_rate', '')}/hr" if details.get("hourly_rate") else "",
                    _money(details.get("cost")),
                ])
            else:
                rows.append([str(name), str(details), "", ""])
        blocks.append(("h3", "Effort Breakdown"))
        blocks.append(("table", ["Module", "Hours", "Rate", "Cost"], rows))
    if data.get("payment_options"):
        rows = []
        for opt in data["payment_options"]:
            if isinstance(opt, dict):
                rows.append([str(opt.get("type") or ""), str(opt.get("description") or ""), _money(opt.get("amount"))])
            else:
                rows.append([str(opt), "", ""])
        blocks.append(("h3", "Payment Options"))
        blocks.append(("table", ["Option", "Description", "Amount"], rows))
    return blocks


def _blocks_sla(data: dict) -> list[tuple]:
    blocks = []
    if data.get("uptime_guarantee"):
        blocks.append(("p", f"Uptime Guarantee: {data['uptime_guarantee']}"))
    tiers = data.get("sla_tiers") or []
    if tiers:
        rows = []
        for t in tiers:
            if isinstance(t, dict):
                rows.append([
                    str(t.get("priority") or ""),
                    str(t.get("description") or ""),
                    str(t.get("response_time") or ""),
                    str(t.get("resolution_time") or ""),
                ])
            else:
                rows.append([str(t), "", "", ""])
        blocks.append(("table", ["Priority", "Description", "Response Time", "Resolution Time"], rows))
    credits = data.get("service_credits") or {}
    if isinstance(credits, dict) and credits:
        blocks.append(("h3", "Service Credits"))
        blocks.append(("table", ["Condition", "Credit"], [[str(k), str(v)] for k, v in credits.items()]))
    windows = data.get("maintenance_windows") or {}
    if isinstance(windows, dict) and windows:
        blocks.append(("h3", "Maintenance Windows"))
        blocks.append(("bullets", [f"{k.replace('_', ' ').title()}: {v}" for k, v in windows.items()]))
    return blocks


def _blocks_team(data) -> list[tuple]:
    rows = []
    if isinstance(data, list):
        for m in data:
            if isinstance(m, dict):
                rows.append([str(m.get("role") or m.get("title") or ""), str(m.get("seniority") or ""), str(m.get("allocation") or "")])
            else:
                rows.append([str(m), "", ""])
    if rows:
        return [("table", ["Role", "Seniority", "Allocation"], rows)]
    return []


def _blocks_generic(data) -> list[tuple]:
    blocks = []
    if isinstance(data, list):
        blocks.append(("bullets", [str(x) for x in data]))
    elif isinstance(data, dict):
        for k, v in data.items():
            if not v:
                continue
            if isinstance(v, list):
                blocks.append(("h3", k.replace("_", " ").title()))
                blocks.append(("bullets", [str(x) for x in v]))
            else:
                blocks.append(("p", f"{k.replace('_', ' ').title()}: {v}"))
    else:
        blocks.append(("p", str(data)))
    return blocks

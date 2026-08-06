import logging

from app.graph.state import ProposalState
from app.llm import llm_client
from app.agents import RequirementAgent, RAGAgent, WriterAgent, ReviewerAgent
from app.engines.proposal_context_builder import ProposalContextBuilder

logger = logging.getLogger("proposalcraft.graph.nodes")

requirement_agent = RequirementAgent(llm_client)
rag_agent = RAGAgent(llm_client)
writer_agent = WriterAgent(llm_client)
reviewer_agent = ReviewerAgent(llm_client)
context_builder = ProposalContextBuilder(llm_client)

# Cap on writer re-runs driven by rubric findings (avoids infinite loops).
MAX_RUBRIC_RETRIES = 2

ENGINE_SECTION_MAP = {
    "pricing": "pricing_data",
    "sla": "sla_data",
    "timeline": "timeline_data",
}


def _generate_about_company(state: ProposalState) -> dict | None:
    """LLM-generated About Us grounded in the client's stated project.
    Returns None when there is no description to ground on or the call fails —
    callers then fall back to deterministic text and log a warning."""
    reqs = state.get("requirements") or {}
    description = reqs.get("description") or reqs.get("project_domain_description") or ""
    if not str(description).strip():
        return None
    try:
        from app.llm.prompts import ABOUT_COMPANY_SYSTEM_PROMPT, ABOUT_COMPANY_TEMPLATE

        prompt = f"{ABOUT_COMPANY_SYSTEM_PROMPT}\n\n{ABOUT_COMPANY_TEMPLATE.format(
            domain=reqs.get("domain", "custom"),
            project_domain_description=reqs.get("project_domain_description") or description,
            core_features=", ".join(str(f) for f in (reqs.get("core_features") or [])[:8]) or "not specified",
        )}"
        return llm_client.generate_json(prompt, complexity="simple", max_tokens=1200)
    except Exception as e:
        logger.warning("about_company LLM generation failed: %s", e)
        return None


def _generate_methodology(state: ProposalState, phases: list) -> dict | None:
    """LLM-generated methodology wording grounded in the actual timeline phases.
    Returns None when there is no description to ground on or the call fails."""
    reqs = state.get("requirements") or {}
    description = reqs.get("description") or reqs.get("project_domain_description") or ""
    if not str(description).strip():
        return None
    try:
        from app.llm.prompts import METHODOLOGY_SYSTEM_PROMPT, METHODOLOGY_TEMPLATE
        import json as _json

        prompt = f"{METHODOLOGY_SYSTEM_PROMPT}\n\n{METHODOLOGY_TEMPLATE.format(
            domain=reqs.get("domain", "custom"),
            description=description,
            phases=_json.dumps(phases, indent=2, ensure_ascii=False),
        )}"
        return llm_client.generate_json(prompt, complexity="simple", max_tokens=1200)
    except Exception as e:
        logger.warning("methodology LLM generation failed: %s", e)
        return None


def _merge_engine_sections(final: dict, business_context: dict) -> None:
    for section_key, data_key in ENGINE_SECTION_MAP.items():
        data = business_context.get(data_key) or {}
        if isinstance(data, dict) and data:
            final[section_key] = data

    stack = (business_context.get("tech_stack_data") or {}).get("technology_stack") or {}
    if isinstance(stack, dict):
        final["technology_stack"] = {
            layer: [item.get("name", str(item)) for item in techs if isinstance(item, dict)]
            for layer, techs in stack.items()
            if techs
        }
        rationale = (business_context.get("tech_stack_data") or {}).get("rationale")
        if rationale:
            final["technology_stack"]["rationale"] = rationale

    modules = (business_context.get("module_data") or {}).get("modules") or []
    if modules:
        core = (business_context.get("module_data") or {}).get("core_modules") or []
        advanced = (business_context.get("module_data") or {}).get("advanced_modules") or []
        if core or advanced:
            final["module_breakdown"] = {
                "standard_modules": [
                    {"module_name": m.get("name", ""), "description": m.get("description", "")}
                    for m in core
                    if isinstance(m, dict)
                ],
                "custom_modules": [
                    {"module_name": m.get("name", ""), "description": m.get("description", "")}
                    for m in advanced
                    if isinstance(m, dict)
                ],
            }
        else:
            final["module_breakdown"] = [
                {"module_name": m.get("name", ""), "description": m.get("description", "")}
                for m in modules
                if isinstance(m, dict)
            ]

    members = (business_context.get("team_data") or {}).get("team_members") or []
    if members:
        final["team"] = [
            {
                "role": m.get("title", m.get("role", "")),
                "seniority": m.get("seniority", ""),
                "allocation": m.get("allocation", ""),
            }
            for m in members
            if isinstance(m, dict)
        ]

    support = (business_context.get("support_data") or {}).get("recommended_plan") or {}
    if support:
        final["support"] = {
            "recommended_plan": support.get("name", ""),
            "hours": support.get("hours", ""),
            "response_time": support.get("response_time", ""),
            "channels": ", ".join(support.get("channels", [])),
            "included": support.get("included", []),
        }

    deliverables = []
    for phase in (business_context.get("timeline_data") or {}).get("phases", []):
        for d in phase.get("deliverables", []):
            if d not in deliverables:
                deliverables.append(d)
    if not deliverables:
        for m in modules:
            name = m.get("name", "") if isinstance(m, dict) else ""
            if name:
                deliverables.append(name)
    if deliverables:
        final["deliverables"] = deliverables


def _merge_system_sections(final: dict, business_context: dict, state: ProposalState) -> None:
    phases = (business_context.get("timeline_data") or {}).get("phases") or []
    if isinstance(phases, list) and phases and not final.get("methodology"):
        llm_methodology = _generate_methodology(state, phases)
        if llm_methodology and not llm_methodology.get("_parse_error"):
            if isinstance(llm_methodology.get("phases"), list) and llm_methodology["phases"]:
                final["methodology"] = {
                    "approach": str(llm_methodology.get("approach", "")),
                    "phases": [str(p) for p in llm_methodology["phases"]],
                    "ceremonies": [str(c) for c in (llm_methodology.get("ceremonies") or [])],
                }
        if not final.get("methodology"):
            logger.warning("methodology LLM fallback fired — using deterministic phase text")
            steps = []
            for p in phases:
                if not isinstance(p, dict):
                    continue
                name = str(p.get("name") or p.get("phase") or "").strip()
                if not name or name.isdigit():
                    continue
                duration = p.get("duration_weeks") or ""
                activities = p.get("activities") or []
                detail = f"{name} ({duration} weeks)" if duration else name
                if isinstance(activities, list) and activities:
                    detail += " — " + "; ".join(str(a) for a in activities[:3])
                steps.append(detail)
            if steps:
                final["methodology"] = {
                    "approach": "Agile-Scrum with iterative sprint cycles and regular stakeholder reviews",
                    "phases": steps,
                    "ceremonies": [
                        "Daily standups",
                        "Sprint planning and review",
                        "Retrospectives",
                        "Stakeholder demo sessions",
                    ],
                }

    rag = state.get("rag_context") or {}
    cs = rag.get("relevant_case_studies") or []
    if isinstance(cs, list) and cs and not final.get("case_studies"):
        final["case_studies"] = [
            c
            if isinstance(c, dict)
            else {
                "title": (str(c).split(".")[0][:60] or "Case Study"),
                "description": str(c),
            }
            for c in cs[:2]
        ]

    if not final.get("about_company"):
        requirements = state.get("requirements") or {}
        domain = requirements.get("domain", "custom")
        llm_about = _generate_about_company(state)
        if llm_about and not llm_about.get("_parse_error"):
            final["about_company"] = llm_about
        else:
            if llm_about is None:
                logger.warning(
                    "about_company LLM fallback fired — no description to ground on; "
                    "using deterministic text"
                )
            else:
                logger.warning("about_company LLM fallback fired — using deterministic text")
            why = []
            for key in ("best_practices", "domain_insights"):
                items = rag.get(key) or []
                if isinstance(items, list):
                    why.extend([x for x in items if isinstance(x, str)][:2])
            if not why:
                why = [
                    f"Specialized delivery of {domain} solutions by a dedicated cross-functional team",
                    "Transparent milestone-based engagement with regular progress reviews",
                ]
            final["about_company"] = {
                "who_we_are": (
                    f"We are a software development agency focused on building reliable, scalable {domain} "
                    "systems that address the specific operational challenges outlined in this proposal. "
                    "Our engineers work in small, senior-led delivery teams so every engagement gets direct "
                    "access to the people building the product, from discovery through launch and support."
                ),
                "experience": (
                    f"Our delivery team has hands-on experience shipping {domain} platforms, combining modern "
                    "architecture with a pragmatic, business-first approach. That experience covers the full "
                    "lifecycle of this type of engagement — requirements analysis, design, build, QA, and "
                    "post-launch operations — which is why the scope in this proposal is structured the way it is."
                ),
                "why_choose_us": why[:4],
            }


def finalizer_node(state: ProposalState) -> ProposalState:
    logger.info("Finalizing proposal output")
    draft = state.get("proposal_draft", {})
    review = state.get("review", {})
    business_context = state.get("business_context", {}) or {}

    improved = review.get("improved_proposal", {}) if isinstance(review, dict) else {}

    final = dict(draft) if isinstance(draft, dict) else {}
    if isinstance(improved, dict) and improved:
        final.update({k: v for k, v in improved.items() if v})

    from app.templates.section_rules import SECTION_RULES

    known_keys = set(SECTION_RULES.keys()) | {"diagram_data", "deliverables"}
    final = {k: v for k, v in final.items() if k in known_keys}

    _merge_engine_sections(final, business_context)
    _merge_system_sections(final, business_context, state)

    diagrams = business_context.get("diagram_data", {})
    if diagrams:
        final["diagram_data"] = {
            "workflow_svg": diagrams.get("workflow_svg", ""),
            "timeline_svg": diagrams.get("timeline_svg", ""),
            "architecture_svg": diagrams.get("architecture_svg", ""),
        }
        if diagrams.get("architecture_svg"):
            final["system_architecture"] = {"diagram": diagrams["architecture_svg"], "description": ""}

    state["final_proposal"] = final
    return state


def requirement_node(state: ProposalState) -> ProposalState:
    logger.info("Running requirement extraction agent")
    try:
        state = requirement_agent.run(state)
    except Exception as e:
        logger.error("Requirement agent failed: %s", e, exc_info=True)
        state["error"] = str(e)
    return state


def business_engines_node(state: ProposalState) -> ProposalState:
    logger.info("Running business engines")
    reqs = state.get("requirements", {}) or {}
    engine_input = {
        "domain": reqs.get("domain", "custom"),
        "project_type": reqs.get("project_type", "web_app"),
        "description": reqs.get("description", ""),
        "project_domain_description": reqs.get("project_domain_description") or reqs.get("description", ""),
        "core_features": reqs.get("core_features", []) or [],
        "budget_range": reqs.get("budget_range", "mid"),
        "timeline_constraint": reqs.get("timeline_constraint", "normal"),
    }
    try:
        context = context_builder.run(engine_input)
        state["business_context"] = context
    except Exception as e:
        logger.error("Business engines failed: %s", e, exc_info=True)
        state["business_context"] = {}
        state["error"] = str(e)
    return state


def rag_node(state: ProposalState) -> ProposalState:
    reqs = state.get("requirements", {})
    domain = reqs.get("domain", "custom")
    description = reqs.get("description", "")
    project_type = reqs.get("project_type", "web_app")
    org_id = state.get("organization_id")

    try:
        from app.rag import qdrant_service
        qdrant_service.initialize()
        rag_chunks = []
        case_study_chunks = []
        query = f"{domain} {project_type} {description}"
        if len(query.strip()) > 10:
            for coll in ["industry_knowledge", "best_practices", "technology_knowledge", "pricing_data", "case_studies"]:
                try:
                    # Org-scoped knowledge (uploaded documents) takes priority,
                    # then the shared built-in knowledge bases.
                    if org_id:
                        for r in qdrant_service.search(query, collection_name=coll, top_k=3, org_id=org_id):
                            rag_chunks.append(r.content)
                            if coll == "case_studies":
                                case_study_chunks.append(r.content)
                    results = qdrant_service.search(query, collection_name=coll, top_k=3)
                    for r in results:
                        rag_chunks.append(r.content)
                        if coll == "case_studies":
                            case_study_chunks.append(r.content)
                except Exception:
                    continue
        state["rag_chunks"] = rag_chunks[:12]
        state["case_study_chunks"] = case_study_chunks[:3]
    except Exception as e:
        logger.warning("Qdrant search failed, using empty RAG: %s", e)
        state["rag_chunks"] = []

    logger.info("Running RAG context agent with %d chunks", len(state.get("rag_chunks", [])))
    try:
        state = rag_agent.run(state)
    except Exception as e:
        logger.error("RAG agent failed: %s", e, exc_info=True)
        state["error"] = str(e)
    return state


def writer_node(state: ProposalState) -> ProposalState:
    logger.info("Running proposal writer agent")
    try:
        state = writer_agent.run(state)
    except Exception as e:
        logger.error("Writer agent failed: %s", e, exc_info=True)
        state["error"] = str(e)
    return state


def reviewer_node(state: ProposalState) -> ProposalState:
    logger.info("Running proposal reviewer agent")
    try:
        state = reviewer_agent.run(state)
    except Exception as e:
        logger.error("Reviewer agent failed: %s", e, exc_info=True)
        state["error"] = str(e)
    return state


def rubric_node(state: ProposalState) -> ProposalState:
    """In-graph quality gate: check the finalized proposal against the rubric.
    Runs AFTER finalizer so it evaluates what actually ships (engine sections
    merged in). Failures are recorded in state so the conditional edge can
    route back to the writer with specific findings (capped at
    MAX_RUBRIC_RETRIES)."""
    from app.agents.rubric_checker import check_proposal

    logger.info("Running rubric check on finalized proposal")
    document = state.get("final_proposal") or state.get("proposal_draft") or {}

    business_context = state.get("business_context") or {}
    result = check_proposal(document, business_context)

    issues: list[str] = []
    if result.missing_sections:
        issues.append(f"Missing sections: {result.missing_sections}")
    if result.placeholder_sections:
        issues.append(f"Placeholder content in: {result.placeholder_sections}")
    if result.number_mismatches:
        issues.append(f"Number mismatches vs engine output: {result.number_mismatches}")
    if result.word_count_issues:
        issues.append(f"Word count too low: {result.word_count_issues}")
    if result.density_issues:
        issues.append(f"Sections too sparse: {result.density_issues}")
    if result.genericness_issues:
        issues.append(f"Generic phrasing: {result.genericness_issues}")

    state["rubric_result"] = {
        "passed": result.passed,
        "missing_sections": result.missing_sections,
        "placeholder_sections": result.placeholder_sections,
        "number_mismatches": result.number_mismatches,
        "word_count_issues": result.word_count_issues,
        "density_issues": result.density_issues,
        "genericness_issues": result.genericness_issues,
        "issues": issues,
    }
    state["rubric_issues"] = issues
    state["rubric_retries"] = (state.get("rubric_retries") or 0) + 1

    logger.info("Rubric result: passed=%s retries=%d %s", result.passed, state["rubric_retries"], result)
    return state

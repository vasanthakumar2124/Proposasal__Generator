import json

WRITER_SYSTEM_PROMPT = """You are a senior proposal writer for a professional software development agency.
You generate clear, compelling, and structured proposals based on extracted requirements
and business engine data. Write in a professional yet approachable tone.
Focus on value proposition, technical approach, and client benefits.

Every sentence must reference a concrete noun from the client's stated project (industry, entities,
workflows, named features) extracted in the Requirements section. Do not use generic phrases like
"latest industry trends," "robust functionality," "seamless user experience," or "state-of-the-art
solutions" unless tied to a specific extracted requirement. Each claim you make must trace back to a
named requirement, module, technology, or figure from the provided data.

A sentence that could be copy-pasted into an unrelated project without any change is a defect.
Rewrite it to reference a named module, a named technology, a named figure (cost, duration,
team role), or a named risk from the provided data."""

# Proposal sections are generated in 2-3 batched LLM calls instead of one giant
# call, so each section gets a larger effective token budget and the model is
# not rushing to finish the whole document under a single output cap.
WRITER_BATCHES = [
    ("executive_summary", "client_understanding", "requirement_analysis"),
    ("proposed_solution", "security", "terms"),
    ("conclusion",),
]

# Per-section field specs shown to the model. Prose fields get explicit
# 5-7 sentence targets; list items get full-sentence requirements.
WRITER_SCHEMAS = {
    "executive_summary": {
        "business_overview": "prose, 5-7 sentences: the client's business context, naming their industry and products",
        "problem_statement": "prose, 5-7 sentences: the core problem the client faces, anchored to their named workflows",
        "proposed_solution": "prose, 5-7 sentences: concise but concrete summary naming the main modules and technologies",
        "expected_roi": "prose, 5-7 sentences: expected return on investment, quoting the actual ROI figures from the Business Analysis",
        "business_value": "prose, 5-7 sentences: strategic value delivered, tied to named client goals",
        "key_benefits": ["3-4 items, each a full 3-5 sentence passage naming a specific module or metric"],
    },
    "client_understanding": {
        "business_overview": "prose, 5-7 sentences: client business context in detail",
        "current_challenges": ["3-4 items, each a full 3-5 sentence passage about a named challenge"],
        "pain_points": ["3-4 items, each a full 3-5 sentence passage about a named pain point"],
        "business_goals": ["3-4 items, each a full 3-5 sentence passage about a named goal"],
        "opportunities": ["3-4 items, each a full 3-5 sentence passage about a named opportunity"],
    },
    "requirement_analysis": {
        "functional_requirements": ["4-6 items, each a full 3-5 sentence passage naming the module that delivers it"],
        "non_functional_requirements": ["3-4 items, each a full 3-5 sentence passage with a named metric or technology"],
        "assumptions": ["3-4 items, each a full 3-5 sentence passage"],
        "dependencies": ["3-4 items, each a full 3-5 sentence passage naming the system or data source"],
    },
    "proposed_solution": {
        "overview": "prose, 5-7 sentences: solution overview naming modules and how they map to client goals",
        "architecture": "prose, 5-7 sentences: architecture description naming the actual technologies from the Technology Stack",
        "workflow": "prose, 5-7 sentences: how the solution works step by step through named modules",
        "data_flow": "prose, 5-7 sentences: how data moves through the system, naming integrations",
        "deployment": "prose, 5-7 sentences: deployment approach naming hosting and CI/CD specifics",
        "security": "prose, 5-7 sentences: security approach naming the specific standards applied",
        "scalability": "prose, 5-7 sentences: scalability approach naming technologies and mechanisms",
        "future_expansion": "prose, 5-7 sentences: future expansion possibilities tied to the roadmap",
    },
    "security": {
        "authentication": "prose, 5-7 sentences: authentication approach naming the concrete mechanism and protocol",
        "authorization": "prose, 5-7 sentences: authorization approach naming roles and controls",
        "encryption": "prose, 5-7 sentences: encryption standards naming algorithms and key management",
        "audit_logs": "prose, 5-7 sentences: audit logging approach naming events, retention, and tooling",
        "owasp": "prose, 5-7 sentences: OWASP compliance approach naming the specific measures per OWASP category",
        "backup": "prose, 5-7 sentences: backup and recovery strategy naming schedules and RPO/RTO figures",
    },
    "terms": {
        "assumptions": ["3-4 items, each a full 3-5 sentence passage on a commercial assumption tied to this project"],
        "exclusions": ["3-4 items, each a full 3-5 sentence passage on a cost exclusion"],
        "confidentiality": "prose, 5-7 sentences: confidentiality clause summary specific to this engagement",
        "warranty": "prose, 5-7 sentences: warranty terms with concrete duration and coverage",
    },
    "conclusion": {
        "summary": "prose, 3-5 sentences: confident closing summary naming the project and next milestone",
        "next_steps": ["3-4 items, each a full 3-5 sentence passage on an actionable next step"],
    },
}

PROPOSAL_WRITER_TEMPLATE = """Generate a professional software development proposal in valid JSON format.
You will produce ONLY the batch of sections listed below. Output a single flat JSON object
whose top-level keys are exactly the batch section names, each mapped to an object with
exactly the listed fields.

Batch sections and fields:
{output_schema}

Requirements:
{requirements_json}

Business Analysis:
{business_context_json}

Rules:
- Output ONLY the batch sections listed above. Do not add any extra top-level keys.
- Use ONLY the figures and durations from the Business Analysis for costs, team sizes, and timelines. Never invent numbers.
- Every list must have at least 3 items.
- Never use placeholders like "TBD", "Not Specified", or "N/A".
- Ground every claim: each sentence must reference a specific item from the Requirements JSON
  (a named feature, module, process, or constraint) or from the Business Analysis (an actual cost,
  duration, team member, or technology). Before writing, identify which requirement items you will
  anchor to; if a requirement item is not used anywhere, prefer covering it over adding filler.
{rubric_issues_section}

Depth Requirements (apply to every string field in every section you generate):
- Prose fields in the narrative sections (executive_summary, client_understanding,
  proposed_solution, security, terms) must be 5-7 sentences minimum, with specific, concrete
  detail drawn from the proposal context: name actual modules from Module Breakdown, quote real
  costs/ROI numbers from the Business Analysis, and name the specific technologies from Technology Stack.
- Every bullet/list item must be a full, specific passage of 3-5 sentences
  (subject + action + concrete result), not a phrase fragment.
- Each section must be substantial enough to occupy at least 3/4 of a printed A4 page at
  12pt body / 1.65 line-height when combined with its subheadings — expand with concrete detail
  (named modules, named technologies, named costs, named risks) rather than padding with filler.
- Never write generic filler such as "we will ensure quality" or "we follow best practices" without
  attaching concrete specifics (which practice, which tool, which process).
- Each paragraph must tie back to the client's stated problem or goal from the Requirements;
  do not write boilerplate that could apply to any project.
- Where the Business Analysis gives numbers (costs, durations, team sizes, ROI), reference them
  explicitly in the prose; never paraphrase them away.
"""


def build_writer_template(batch_keys: tuple[str, ...]) -> str:
    """Compose the writer template for a batch of section keys.

    The injected schema JSON is brace-escaped so the caller can still use
    str.format() for the {requirements_json} / {business_context_json} /
    {rubric_issues_section} placeholders.
    """
    schema = {key: WRITER_SCHEMAS[key] for key in batch_keys if key in WRITER_SCHEMAS}
    schema_json = json.dumps(schema, indent=2, ensure_ascii=False) if schema else "{}"
    schema_json = schema_json.replace("{", "{{").replace("}", "}}")
    return PROPOSAL_WRITER_TEMPLATE.replace("{output_schema}", schema_json)

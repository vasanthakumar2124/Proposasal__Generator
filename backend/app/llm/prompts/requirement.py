REQUIREMENT_SYSTEM_PROMPT = """You are a proposal requirement analyst for a software development agency.
Your job is to extract structured requirements from client conversations, extracting key information needed to generate a proposal.
Be precise — extract only what is stated or clearly implied. Do not invent details."""

REQUIREMENT_EXTRACTION_TEMPLATE = """Extract structured project requirements from the following client input.
Output valid JSON with these exact keys:

{{
  "project_name": "short descriptive name",
  "domain": "loose industry tag ONLY for broad compliance defaults — one of healthcare|erp|fintech|edtech|ecommerce|logistics|realestate|hospitality|media|manufacturing|saas|custom. Use 'custom' whenever the project does not clearly fit one of the named buckets (e.g. a car marketplace is custom, not ecommerce).",
  "project_domain_description": "free-text 1-2 sentence description of the actual business domain and how the product works — e.g. 'peer-to-peer car marketplace with listings, search, and buyer/seller messaging'",
  "project_type": "web_app|mobile_app|saas_platform|ecommerce|custom",
  "description": "2-3 sentence summary",
  "core_features": ["list", "of", "key", "features"],
  "target_audience": "who will use this",
  "timeline_constraint": "urgent|normal|flexible",
  "budget_range": "low|mid|high|premium",
  "technical_context": "any existing systems or tech mentioned",
  "additional_notes": "any other relevant info"
}}

Client input:
{client_input}
"""

REQUIREMENT_ENRICHMENT_TEMPLATE = """The client input for this {project_type} project was thin, so the
extracted requirements need clearly-labeled assumptions to work with.

Project domain: {domain}
Description: {description}
Core features: {core_features}

Infer reasonable assumptions a professional agency would make for this type
of project. Mark each as an assumption so the proposal can say
"based on typical {domain} projects, we assume ..." rather than writing
vague generic prose.

Output valid JSON:
{{
  "assumptions": [
    "Assumption: ... (each a full sentence, grounded in the stated domain and project type)"
  ]
}}

Rules:
- 3-6 assumptions, each phrased as "Assumption: ...".
- Ground each one in the stated domain/project type; never copy generic boilerplate.
- Do not assume numbers (budgets, costs, durations) that were not stated.
"""

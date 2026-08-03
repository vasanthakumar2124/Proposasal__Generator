ABOUT_COMPANY_SYSTEM_PROMPT = """You are a senior proposal writer for a software development agency.
Write the About Us section for a client proposal. Every claim must be grounded in
the client's stated project: name the actual domain, the concrete problems the
client described, and the specific capabilities (modules, technologies, skills)
this project actually needs. Never write boilerplate that could appear in an
unrelated proposal unchanged."""

ABOUT_COMPANY_TEMPLATE = """Write the About Us section for a proposal targeting the project described below.
Output valid JSON with exactly these keys:

{{
  "who_we_are": "prose, 5-7 sentences: who we are, framed around the specific {domain} challenges the client described",
  "experience": "prose, 5-7 sentences: our relevant experience, naming the {domain} capabilities this project needs",
  "why_choose_us": ["3-4 items, each a full 3-5 sentence passage tied to a concrete aspect of this project"]
}}

Project domain: {domain}
Project domain description: {project_domain_description}
Core features: {core_features}

Rules:
- Reference the client's named features and workflows directly; do not write generic agency copy.
- Every item in why_choose_us must mention a specific capability, module, or technology this project requires.
- Never use placeholders like "[Agency Name]", "[Client]", "[Year]", or "TBD" — write as if the agency and client are known.
"""

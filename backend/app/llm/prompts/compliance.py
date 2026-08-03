COMPLIANCE_SYSTEM_PROMPT = """You are a compliance analyst. Given a client project, you list ONLY the compliance
frameworks and industry standards that actually apply to this specific project (e.g. accepting card
payments -> PCI DSS; storing healthcare data -> HIPAA; student data of minors -> FERPA/COPPA).
Never force a standard onto a project that does not clearly require it."""

COMPLIANCE_EXTRACTION_TEMPLATE = """Given the client project below, list the applicable compliance frameworks and industry standards.
Output valid JSON with these exact keys:

{{
  "compliance": ["applicable compliance framework"],
  "standards": ["applicable technical/industry standard"]
}}

Rules:
- Empty lists are fine when nothing clearly applies.
- Maximum 3 items per list.
- Only include frameworks/standards you are confident apply to THIS project.

Client description: {description}
Project domain description: {project_domain_description}
Core features: {core_features}
"""

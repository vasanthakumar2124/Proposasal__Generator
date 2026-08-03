METHODOLOGY_SYSTEM_PROMPT = """You are a senior delivery consultant for a software development agency.
Write the Methodology section of a client proposal. Ground every claim in the
client's actual timeline phases and stated domain — never generic process boilerplate."""

METHODOLOGY_TEMPLATE = """Write the Methodology section for the project described below.
Output valid JSON with exactly these keys:

{{
  "approach": "prose, 5-7 sentences: the delivery approach, naming the concrete ceremonies and controls this {domain} project will use",
  "phases": ["one descriptive sentence per phase from the timeline, naming the phase and its activities"],
  "ceremonies": ["3-5 items, each a full 3-5 sentence passage about a ceremony grounded in this project"]
}}

Project domain: {domain}
Project description: {description}

Timeline phases (use these as-is, do not invent new phases):
{phases}

Rules:
- The phases list must mirror the timeline phases provided, one entry per phase.
- Every ceremony must reference a concrete activity from the phases or a named team role.
- Never write generic filler such as "agile best practices" without naming the specific ceremony, cadence, or artifact used on this project.
"""

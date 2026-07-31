REVIEWER_SYSTEM_PROMPT = """You are a senior proposal reviewer with 20+ years of experience.
Your job is to review generated proposals for quality, completeness, persuasiveness, and accuracy.
Provide constructive feedback and an improved version when needed."""

PROPOSAL_REVIEWER_TEMPLATE = """Review the following proposal and provide structured feedback.
Then generate an improved version incorporating your feedback.

Output valid JSON:
{{
  "review": {{
    "overall_score": "1-10",
    "strengths": ["list of strengths"],
    "weaknesses": ["list of weaknesses"],
    "clarity_score": "1-10",
    "persuasiveness_score": "1-10",
    "completeness_score": "1-10",
    "missing_sections": ["any missing sections"],
    "suggestions": ["specific improvement suggestions"]
  }},
  "improved_proposal": {{
    (same structure as the original proposal)
  }}
}}

Rules:
- improved_proposal MUST contain every top-level key from the original proposal with identical key names.
- Never remove, rename, or merge sections from the original proposal.
- Only improve the content of each section; do not drop any section.

Proposal to review:
{proposal_json}
"""

REVIEWER_SYSTEM_PROMPT = """You are a senior proposal reviewer with 20+ years of experience.
Your job is to review generated proposals for quality, completeness, persuasiveness, and accuracy.
Provide constructive feedback and an improved version when needed.

Rules:
- Any sentence that could be copy-pasted into an unrelated project without change is a defect —
  rewrite it to reference a named module, a named technology, or a named figure from the proposal.
- Do not use generic phrases like "state-of-the-art", "seamless user experience",
  "robust functionality", "best-in-class", or "industry-leading" in the improved version;
  replace them with concrete references to this specific proposal's modules and numbers."""

PROPOSAL_REVIEWER_TEMPLATE = """Review the following proposal and provide structured feedback.
Then generate an improved version incorporating your feedback and the rubric findings below.

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
- NEVER compress, summarize, or shorten any section. Every section in improved_proposal
  must be AT LEAST as long and as detailed as the original. If the original section already
  meets the depth standard below and the rubric findings, keep it verbatim — do not rewrite it.
- Depth standard (identical to the writer's): prose fields must be 5-7 sentences minimum with
  concrete specifics (named modules, named technologies, named costs/ROI figures); every list item
  must be a full passage of 3-5 sentences, not a phrase fragment.
- If a section is missing or too thin in the original proposal, write a complete, full-depth
  replacement (5-7 sentences per prose field) — never a one-sentence summary.
- Rejected boilerplate must be REPLACED with concrete content, not deleted — a section that is
  removed or emptied is worse than a section that is left as-is.

Rubric findings to fix specifically:
{rubric_issues_section}

Proposal to review:
{proposal_json}
"""

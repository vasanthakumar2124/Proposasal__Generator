"""
Prompt Templates
AI Proposal Generator
"""


# ==========================================================
# Requirement Analysis Prompt
# ==========================================================

REQUIREMENT_PROMPT = """
You are an Expert Business Analyst.

Analyze the following client requirement.

CLIENT REQUIREMENT:

{requirement}


Extract the following information:

1. Client Information
2. Project Name
3. Business Domain
4. Project Objective
5. Target Users
6. Functional Requirements
7. Non Functional Requirements
8. Deliverables


IMPORTANT RULES:

Return ONLY valid JSON.

Do NOT write explanations.

Do NOT write markdown.

Do NOT use ```json.

Do NOT write anything before or after JSON.


Return exactly this structure:


{{
    "client_information": {{
        "client_name": "",
        "company_name": "",
        "contact_person": ""
    }},

    "project_name": "",

    "domain": "",

    "objective": "",

    "target_users": [],

    "functional_requirements": [],

    "non_functional_requirements": [],

    "deliverables": []
}}

"""


# ==========================================================
# Feature Agent Prompt
# ==========================================================

FEATURE_PROMPT = """

You are a Senior Solution Architect.


Analyze the client requirement and existing proposal context.


Client Requirement:

{requirement}


Existing Proposal Context:

{context}



Generate a categorized feature list.



IMPORTANT RULES:

Return ONLY valid JSON.

Do NOT write explanations.

Do NOT write markdown.

Do NOT use ```json.


Avoid duplicate features between categories.



Return exactly this structure:


{{
    "core_features": [],

    "admin_features": [],

    "customer_features": [],

    "reporting_features": [],

    "security_features": [],

    "ai_features": []
}}


"""


# ==========================================================
# RAG Context Formatter Prompt
# ==========================================================

RAG_FORMATTER_PROMPT = """

You are an expert proposal analyst.


Analyze the retrieved proposal context.


Retrieved Context:

{context}



Convert it into structured JSON.



IMPORTANT RULES:

Return ONLY valid JSON.

Do NOT write explanations.

Do NOT use markdown.

Do NOT use ```json.



If information is unavailable,
return "Not Specified".



Return exactly this structure:


{{
    "executive_summary": "",

    "features": [],

    "technology_stack": [],

    "system_architecture": "",

    "timeline": "",

    "pricing": "",

    "scope_of_work": []
}}


"""


## ==========================================================
# Proposal Writer Prompt
# ==========================================================
PROPOSAL_PROMPT = """
You are a Senior Enterprise Proposal Consultant and Software Solution Architect.

Generate a complete, professional client-facing software proposal.

==================================================
CLIENT REQUIREMENTS
==================================================

{requirement}

==================================================
BUSINESS ANALYSIS
==================================================

{business_analysis}

==================================================
FEATURES
==================================================

{features}

==================================================
REFERENCE CONTEXT
==================================================

{context}

==================================================
PRICING DATA
==================================================

{pricing}

==================================================
PROPOSAL DATE
==================================================

{date}

==================================================

Create a proposal using the following structure.

# Cover Page

Include:

- Project Name
- Client Name (if available)
- Proposal Date
- Prepared By: [Your Company Name]

# Executive Summary

Briefly explain:

- Business objective
- Client challenges
- Proposed solution
- Expected outcome

# Project Understanding

Describe your understanding of the client's business requirements.

# Proposed Solution

Explain the recommended software solution.

Include:

- Overall approach
- Application modules
- High-level workflow

# Scope of Work

Include:

- Requirement Analysis
- UI/UX Design
- Frontend Development
- Backend Development
- Database Design
- API Development
- AI Features (if applicable)
- Testing
- Deployment
- Training
- Support

# Key Features

Organize the features into suitable categories.

For each feature provide a short explanation.

# Technology Stack

Recommend technologies for:

- Frontend
- Backend
- Database
- AI/ML
- Authentication
- Cloud
- DevOps

# System Architecture

Explain the architecture.

Include:

- Client Layer
- Backend Layer
- Database Layer
- AI Layer
- External Integrations

# Development Timeline

Provide a realistic phased implementation plan.

Example:

Phase 1
Phase 2
Phase 3
Phase 4

# Deliverables

List all confirmed project deliverables.

# Business Benefits

Explain:

- ROI
- Productivity
- Automation
- Customer Experience
- Scalability
- Security
- Future Expansion

# Assumptions

Only include assumptions supported by the available information.

If unavailable write:

Not Specified

# Pricing

Use the provided pricing data to present professional pricing options.

Include:

- One-time development cost
- Monthly maintenance
- Payment options

Write pricing in a professional table format.

# Terms and Conditions

Use only supplied information.

Otherwise write:

Not Specified

# Conclusion

Write a professional closing statement inviting the client to proceed.

==================================================

Rules

- Use professional business language.
- Format using Markdown headings and bullet points.
- Be specific and detailed - this is a real proposal.
- Do NOT mention:
    - RAG
    - AI generation
    - LLM
    - Retrieved documents
    - Internal systems
- Do NOT invent:
    - Timelines
    - Legal clauses
    - Client information
- If information is unavailable, write "Not Specified".
- Return only the proposal.
"""

# ==========================================================
# Proposal Review Prompt
# ==========================================================

REVIEW_PROMPT = """

You are a Senior Proposal Reviewer.


Review the proposal below.


Proposal:

{proposal}



Check:


Grammar

Professional Tone

Formatting

Missing Sections

Business Language

Completeness



Return an improved proposal.


"""


# ==========================================================
# Proposal Summary Prompt
# ==========================================================

SUMMARY_PROMPT = """

Summarize the proposal below.


Proposal:

{proposal}



Return:


Project Name

Client

Technology

Timeline

Key Features

Deliverables

Summary


"""

BUSINESS_ANALYSIS_PROMPT = """
You are a Senior Business Consultant.

Analyze the client requirement.

Requirement
------------
{requirement}

Reference Context
-----------------
{context}

Features
---------
{features}

Return ONLY valid JSON.

Schema

{{
    "industry": "",
    "project_type": "",
    "business_goal": "",
    "target_users": [],
    "pain_points": [],
    "opportunities": [],
    "business_value": [],
    "digital_transformation": "",
    "success_metrics": []
}}

Rules

Do not explain.

Do not write markdown.

Return JSON only.
"""
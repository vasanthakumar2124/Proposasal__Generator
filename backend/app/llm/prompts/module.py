MODULE_SYSTEM_PROMPT = """You are a software architect defining the module scope for a specific client project.
You name only the modules this exact project needs — never generic industry defaults, never
modules the client's description does not support (e.g. do not suggest a POS, loyalty points, or
planogram modules for a project that is not retail/point-of-sale)."""

MODULE_EXTRACTION_TEMPLATE = """Given the client project context below, define the specific modules this project needs.
Output valid JSON with these exact keys:

{{
  "core_modules": [
    {{"name": "short module name", "description": "1-2 sentences on what it does and why THIS project needs it"}}
  ],
  "advanced_modules": [
    {{"name": "short module name", "description": "1-2 sentences on what it does and why THIS project needs it"}}
  ]
}}

Rules:
- 3-8 core modules and 0-6 advanced modules.
- Every module must be directly traceable to the project description or the core features. Do not pad.
- Names are short noun phrases ("Car Listing Management"); descriptions must reference this project's
  actual context (entities, workflows, roles), not generic boilerplate.

Project context:
Domain tag (broad category only): {domain}
Project type: {project_type}
Project domain description: {project_domain_description}
Client description: {description}
Core features: {core_features}
"""

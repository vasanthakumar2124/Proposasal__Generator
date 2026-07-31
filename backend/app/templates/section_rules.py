SECTION_RULES = {
    "cover_page": {
        "generated_by": "system",
        "required": True,
        "order": 1,
        "fallback": "Cover page generated from project metadata"
    },
    "table_of_contents": {
        "generated_by": "system",
        "required": True,
        "order": 2,
        "fallback": "Auto-generated from section list"
    },
    "executive_summary": {
        "generated_by": "llm",
        "required": True,
        "order": 3,
        "fallback": "Executive summary could not be generated."
    },
    "about_company": {
        "generated_by": "rag",
        "required": True,
        "order": 4,
        "fallback": "Information about the company was unavailable."
    },
    "client_understanding": {
        "generated_by": "llm",
        "required": True,
        "order": 5,
        "fallback": "Client context could not be analyzed."
    },
    "requirement_analysis": {
        "generated_by": "llm",
        "required": True,
        "order": 6,
        "fallback": "Requirement details were not specified."
    },
    "proposed_solution": {
        "generated_by": "llm",
        "required": True,
        "order": 7,
        "fallback": "A proposed solution could not be formulated based on available data."
    },
    "module_breakdown": {
        "generated_by": "system",
        "required": True,
        "order": 8,
        "fallback": "Module breakdown will be determined during the discovery phase."
    },
    "user_journey": {
        "generated_by": "system",
        "required": False,
        "order": 9,
        "fallback": "User journey details will be mapped during the design phase."
    },
    "technology_stack": {
        "generated_by": "tech_stack_engine",
        "required": True,
        "order": 10,
        "fallback": "Technology recommendations will be finalized during architecture planning."
    },
    "ai_architecture": {
        "generated_by": "system",
        "required": False,
        "order": 11,
        "fallback": "AI architecture will be designed based on specific requirements."
    },
    "system_architecture": {
        "generated_by": "diagram_engine",
        "required": True,
        "order": 12,
        "fallback": "System architecture diagram will be produced during detailed design."
    },
    "database_design": {
        "generated_by": "system",
        "required": False,
        "order": 13,
        "fallback": "Database schema will be designed during the implementation phase."
    },
    "security": {
        "generated_by": "llm",
        "required": True,
        "order": 14,
        "fallback": "Security measures will be implemented following industry best practices."
    },
    "methodology": {
        "generated_by": "system",
        "required": False,
        "order": 15,
        "fallback": "Agile methodology will be followed with iterative sprint cycles."
    },
    "timeline": {
        "generated_by": "timeline_engine",
        "required": True,
        "order": 16,
        "fallback": "Project timeline will be finalized after requirement finalization."
    },
    "deliverables": {
        "generated_by": "system",
        "required": True,
        "order": 17,
        "fallback": "Detailed deliverables list will be prepared in the project plan."
    },
    "pricing": {
        "generated_by": "pricing_engine",
        "required": True,
        "order": 18,
        "fallback": None,
        "notes": "MUST come from pricing_engine output — never LLM-authored numbers"
    },
    "sla": {
        "generated_by": "sla_engine",
        "required": True,
        "order": 19,
        "fallback": "SLA terms will be defined during contract finalization."
    },
    "support": {
        "generated_by": "sla_engine",
        "required": True,
        "order": 20,
        "fallback": "Support plan will be customized based on specific requirements."
    },
    "terms": {
        "generated_by": "llm",
        "required": True,
        "order": 21,
        "fallback": None,
        "notes": "Generate from project context + standard clauses — never hardcode 'Not Specified'"
    },
    "case_studies": {
        "generated_by": "rag",
        "required": False,
        "order": 22,
        "fallback": "Relevant case studies were not available."
    },
    "team": {
        "generated_by": "team_engine",
        "required": True,
        "order": 23,
        "fallback": "Team composition will be finalized during project initiation."
    },
    "conclusion": {
        "generated_by": "llm",
        "required": True,
        "order": 24,
        "fallback": "We look forward to partnering with you on this initiative."
    },
}

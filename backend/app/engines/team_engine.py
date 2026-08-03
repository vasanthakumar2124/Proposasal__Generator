from app.engines.base_engine import BaseEngine

TEAM_ROLES = {
    "project_manager": {"title": "Project Manager", "seniority": "Senior", "allocation": "full_time"},
    "solution_architect": {"title": "Solution Architect", "seniority": "Lead", "allocation": "full_time"},
    "tech_lead": {"title": "Technical Lead", "seniority": "Lead", "allocation": "full_time"},
    "backend_dev": {"title": "Backend Developer", "seniority": "Senior", "allocation": "full_time"},
    "frontend_dev": {"title": "Frontend Developer", "seniority": "Senior", "allocation": "full_time"},
    "uiux_designer": {"title": "UI/UX Designer", "seniority": "Senior", "allocation": "part_time"},
    "qa_engineer": {"title": "QA Engineer", "seniority": "Senior", "allocation": "part_time"},
    "devops_engineer": {"title": "DevOps Engineer", "seniority": "Senior", "allocation": "part_time"},
    "ai_engineer": {"title": "AI/ML Engineer", "seniority": "Senior", "allocation": "as_needed"},
    "business_analyst": {"title": "Business Analyst", "seniority": "Senior", "allocation": "part_time"},
}

TEAM_SCALING = {
    "small": {
        "roles": ["project_manager", "solution_architect", "backend_dev", "frontend_dev", "uiux_designer", "qa_engineer"],
        "description": "Core team of 4-6 members covering all essential functions",
    },
    "medium": {
        "roles": ["project_manager", "solution_architect", "tech_lead", "backend_dev", "frontend_dev", "uiux_designer", "qa_engineer", "devops_engineer", "business_analyst"],
        "description": "Extended team of 6-9 members with specialized roles",
    },
    "large": {
        "roles": ["project_manager", "solution_architect", "tech_lead", "backend_dev", "frontend_dev", "uiux_designer", "qa_engineer", "devops_engineer", "ai_engineer", "business_analyst"],
        "description": "Full-scale team of 10+ members including AI and security specialists",
    },
}


class TeamEngine(BaseEngine):
    name = "team"

    def run(self, context: dict) -> dict:
        modules = (context.get("module_data") or {}).get("modules", [])
        complexity = (context.get("industry_data") or {}).get("complexity", "medium")

        module_count = len(modules)
        if module_count <= 4 or complexity == "low":
            size = "small"
        elif module_count <= 10:
            size = "medium"
        else:
            size = "large"

        # Long engagements need a bigger team even with the same module count:
        # staffing must cover sustained delivery, QA, and operations over time.
        total_weeks = 0
        for phase in (context.get("timeline_data") or {}).get("phases", []):
            if isinstance(phase, dict):
                total_weeks += phase.get("duration_weeks") or 0
        if total_weeks >= 16 and size == "small":
            size = "medium"
        elif total_weeks >= 24 and size == "medium":
            size = "large"

        scale = TEAM_SCALING[size]
        team_members = []
        for role_key in scale["roles"]:
            role_info = TEAM_ROLES.get(role_key, {})
            team_members.append({
                "role": role_key,
                "title": role_info.get("title", role_key.replace("_", " ").title()),
                "seniority": role_info.get("seniority", "Senior"),
                "allocation": role_info.get("allocation", "full_time"),
            })

        return {
            "team_size": len(team_members),
            "team_scale": size,
            "team_description": scale["description"],
            "team_members": team_members,
            "roles": [m["title"] for m in team_members],
        }

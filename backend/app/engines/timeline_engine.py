from app.engines.base_engine import BaseEngine

PHASE_TEMPLATES = {
    "small": {
        "label": "Small (1-3 months)",
        "phases": [
            {"phase": 1, "name": "Discovery & Planning", "duration_weeks": 2,
             "activities": ["Requirements workshop", "Technical architecture design", "Project plan", "Sprint 0 setup"],
             "deliverables": ["PRD", "Architecture document", "Project timeline"]},
            {"phase": 2, "name": "Design & Prototype", "duration_weeks": 2,
             "activities": ["UI/UX design", "Wireframes", "Design system", "Technical prototype"],
             "deliverables": ["Design mockups", "Interactive prototype", "Design system"]},
            {"phase": 3, "name": "Core Development", "duration_weeks": 4,
             "activities": ["Backend API development", "Frontend implementation", "Database schema", "Integration"],
             "deliverables": ["Working MVP", "API documentation", "Test suite"]},
            {"phase": 4, "name": "Testing & Launch", "duration_weeks": 2,
             "activities": ["QA testing", "UAT", "Bug fixes", "Deployment"],
             "deliverables": ["Test reports", "Deployment guide", "Live system"]},
        ],
    },
    "medium": {
        "label": "Medium (3-6 months)",
        "phases": [
            {"phase": 1, "name": "Discovery & Architecture", "duration_weeks": 3,
             "activities": ["Stakeholder interviews", "Requirements analysis", "System architecture", "Technology selection"],
             "deliverables": ["Requirements specification", "Architecture blueprint", "Tech stack decision"]},
            {"phase": 2, "name": "Design Sprint", "duration_weeks": 3,
             "activities": ["UX research", "UI design", "Design system", "Prototype testing"],
             "deliverables": ["Design system", "All screens mockups", "User flow diagrams"]},
            {"phase": 3, "name": "Sprint 1 - Core Platform", "duration_weeks": 4,
             "activities": ["Backend foundation", "Database setup", "Auth system", "Core APIs"],
             "deliverables": ["Working backend", "API documentation", "Database schema"]},
            {"phase": 4, "name": "Sprint 2 - Feature Development", "duration_weeks": 4,
             "activities": ["Feature modules", "Frontend pages", "Integration", "Notifications"],
             "deliverables": ["Feature modules", "Integrated frontend"]},
            {"phase": 5, "name": "Sprint 3 - Advanced Features", "duration_weeks": 4,
             "activities": ["Advanced features", "Reporting", "AI/ML features", "Admin panel"],
             "deliverables": ["Complete feature set", "Admin dashboard"]},
            {"phase": 6, "name": "Testing, Deployment & Handover", "duration_weeks": 4,
             "activities": ["QA testing", "Performance testing", "Security audit", "Production deployment", "Documentation", "Training"],
             "deliverables": ["Test reports", "Security clearance", "User manuals", "Live system"]},
        ],
    },
    "large": {
        "label": "Large (6-12 months)",
        "phases": [
            {"phase": 1, "name": "Discovery & Strategy", "duration_weeks": 4,
             "activities": ["Business analysis", "Technical discovery", "Stakeholder alignment", "Roadmap creation"],
             "deliverables": ["Business requirements", "Technical assessment", "Phase roadmap"]},
            {"phase": 2, "name": "Architecture & Design", "duration_weeks": 4,
             "activities": ["Solution architecture", "Data architecture", "Security architecture", "UI/UX design", "Design review"],
             "deliverables": ["Architecture document", "Security plan", "Design mockups"]},
            {"phase": 3, "name": "Foundation Development", "duration_weeks": 6,
             "activities": ["Infrastructure setup", "Core backend", "Database implementation", "Authentication", "CI/CD pipeline"],
             "deliverables": ["Infrastructure as code", "Core platform", "CI/CD pipeline"]},
            {"phase": 4, "name": "Module Development - Batch 1", "duration_weeks": 6,
             "activities": ["Core modules development", "API integration", "Frontend implementation", "Unit testing"],
             "deliverables": ["Module batch 1", "Integration tests"]},
            {"phase": 5, "name": "Module Development - Batch 2", "duration_weeks": 6,
             "activities": ["Advanced modules", "Reporting system", "Admin features", "Integration testing"],
             "deliverables": ["Module batch 2", "Complete feature set"]},
            {"phase": 6, "name": "AI/ML & Advanced Features", "duration_weeks": 4,
             "activities": ["AI model development", "ML pipeline", "Advanced analytics", "Optimization"],
             "deliverables": ["AI/ML models", "Analytics dashboards"]},
            {"phase": 7, "name": "Quality Assurance", "duration_weeks": 4,
             "activities": ["System testing", "Performance testing", "Security testing", "UAT", "Bug fixes"],
             "deliverables": ["Test reports", "Performance benchmarks", "Security audit"]},
            {"phase": 8, "name": "Deployment & Transition", "duration_weeks": 4,
             "activities": ["Production deployment", "Data migration", "Documentation", "Training", "Go-live support"],
             "deliverables": ["Live production system", "Operations manual", "Training materials"]},
        ],
    },
}


class TimelineEngine(BaseEngine):
    name = "timeline"

    def run(self, context: dict) -> dict:
        modules = (context.get("module_data") or {}).get("modules", [])
        complexity = (context.get("industry_data") or {}).get("complexity", "medium")

        module_count = len(modules)
        if module_count <= 4 or complexity == "low":
            size = "small"
        elif module_count <= 10 or complexity == "medium":
            size = "medium"
        else:
            size = "large"

        template = PHASE_TEMPLATES[size]
        total_weeks = sum(p["duration_weeks"] for p in template["phases"])
        total_months = round(total_weeks / 4.33, 1)

        return {
            "project_size": size,
            "total_duration_weeks": total_weeks,
            "total_duration_months": total_months,
            "phases": template["phases"],
            "phase_count": len(template["phases"]),
            "milestones": [
                {"week": sum(template["phases"][i]["duration_weeks"] for i in range(p)), "event": phase["name"] + " Complete"}
                for p, phase in enumerate(template["phases"])
            ],
        }

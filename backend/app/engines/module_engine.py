import json
import logging
from app.engines.base_engine import BaseEngine
from app.llm.prompts import MODULE_SYSTEM_PROMPT, MODULE_EXTRACTION_TEMPLATE

logger = logging.getLogger("proposalcraft.engines.module")

MODULES_BY_INDUSTRY = {
    "healthcare": {
        "core": [
            {"name": "Patient Management", "description": "Centralized patient records, demographics, medical history"},
            {"name": "Appointment Scheduling", "description": "Multi-provider scheduling with reminders"},
            {"name": "EHR/EMR", "description": "Electronic Health Records with HL7 FHIR integration"},
            {"name": "Billing & Claims", "description": "Insurance claim processing, coding, revenue cycle"},
            {"name": "Pharmacy Management", "description": "Prescription management, drug interaction checks"},
            {"name": "Laboratory Information System", "description": "Lab orders, results, integrations"},
        ],
        "advanced": [
            {"name": "Telemedicine Platform", "description": "Virtual consultations, remote monitoring"},
            {"name": "AI Diagnostics", "description": "ML-assisted diagnosis from imaging and lab data"},
            {"name": "Patient Portal", "description": "Self-service appointments, records, payments"},
            {"name": "Population Health", "description": "Analytics, risk stratification, outreach"},
        ],
    },
    "erp": {
        "core": [
            {"name": "Financial Management", "description": "GL, AP, AR, fixed assets, budgeting"},
            {"name": "Supply Chain Management", "description": "Procurement, inventory, warehouse, logistics"},
            {"name": "Production Planning", "description": "MRP, capacity planning, shop floor control"},
            {"name": "Order Management", "description": "Order-to-cash lifecycle, pricing, invoicing"},
            {"name": "HR & Payroll", "description": "Employee master, attendance, payroll processing"},
            {"name": "Business Intelligence", "description": "Reports, dashboards, financial analytics"},
        ],
        "advanced": [
            {"name": "AI Demand Forecasting", "description": "ML-based demand prediction and inventory optimization"},
            {"name": "IoT Integration", "description": "Real-time machine monitoring and predictive maintenance"},
            {"name": "Multi-company Consolidation", "description": "Intercompany transactions, currency consolidation"},
            {"name": "Advanced Analytics", "description": "What-if analysis, scenario planning, profitability"},
        ],
    },
    "crm": {
        "core": [
            {"name": "Contact Management", "description": "360-degree customer view, segmentation"},
            {"name": "Sales Pipeline", "description": "Lead-to-opportunity tracking, forecasting"},
            {"name": "Marketing Automation", "description": "Campaign management, email, lead scoring"},
            {"name": "Customer Support", "description": "Ticketing, knowledge base, SLA management"},
        ],
        "advanced": [
            {"name": "AI Sales Assistant", "description": "Predictive lead scoring, next-best-action recommendations"},
            {"name": "Conversational CRM", "description": "Chat, WhatsApp, social media integration"},
            {"name": "Customer Analytics", "description": "Churn prediction, lifetime value, sentiment analysis"},
            {"name": "CPQ", "description": "Configure-Price-Quote for complex products"},
        ],
    },
    "hrms": {
        "core": [
            {"name": "Employee Database", "description": "Central HR records, documents, compliance"},
            {"name": "Payroll Management", "description": "Salary, deductions, tax filings, compliance"},
            {"name": "Leave & Attendance", "description": "Time tracking, leave policies, calendar"},
            {"name": "Performance Management", "description": "Reviews, OKRs, feedback, goal tracking"},
        ],
        "advanced": [
            {"name": "AI Recruiting", "description": "Resume parsing, candidate matching, automated screening"},
            {"name": "People Analytics", "description": "Turnover analysis, engagement, workforce planning"},
            {"name": "Learning Management", "description": "Course management, certifications, compliance training"},
            {"name": "Employee Self-Service", "description": "Portal for payslips, requests, updates"},
        ],
    },
    "manufacturing": {
        "core": [
            {"name": "Production Scheduling", "description": "Finite capacity scheduling, Gantt charts"},
            {"name": "Quality Management", "description": "Inspection, non-conformance, CAPA"},
            {"name": "Inventory Management", "description": "Multi-warehouse, bin locations, cycle counting"},
            {"name": "Maintenance Management", "description": "Preventive, predictive, work orders"},
        ],
        "advanced": [
            {"name": "Digital Twin", "description": "Real-time virtual replica of production line"},
            {"name": "Predictive Maintenance", "description": "ML-based equipment failure prediction"},
            {"name": "MES Integration", "description": "Manufacturing Execution System connectivity"},
            {"name": "Energy Management", "description": "Energy monitoring, optimization, reporting"},
        ],
    },
    "education": {
        "core": [
            {"name": "Student Information System", "description": "Enrollment, grades, attendance, transcripts"},
            {"name": "Learning Management System", "description": "Course delivery, assessments, collaboration"},
            {"name": "Fee Management", "description": "Tuition, payments, scholarships, financial aid"},
        ],
        "advanced": [
            {"name": "Virtual Classroom", "description": "Live sessions, recording, interactive whiteboard"},
            {"name": "Adaptive Learning", "description": "AI-powered personalized learning paths"},
            {"name": "Alumni Management", "description": "Network, fundraising, events"},
        ],
    },
    "government": {
        "core": [
            {"name": "Citizen Portal", "description": "Service requests, applications, status tracking"},
            {"name": "Document Management", "description": "Records, archiving, version control, compliance"},
            {"name": "Permitting & Licensing", "description": "Application workflow, inspections, renewals"},
            {"name": "Financial Management", "description": "Budgeting, procurement, grant management"},
        ],
        "advanced": [
            {"name": "Open Data Platform", "description": "Public data publishing, APIs, visualization"},
            {"name": "Smart City Integration", "description": "IoT sensors, traffic, utilities monitoring"},
            {"name": "AI Audit System", "description": "Fraud detection, anomaly detection, compliance"},
        ],
    },
    "retail": {
        "core": [
            {"name": "POS System", "description": "Point of sale, billing, returns, exchanges"},
            {"name": "Inventory Management", "description": "Stock tracking, reorder, multi-store"},
            {"name": "Order Management", "description": "Omnichannel orders, fulfillment, returns"},
            {"name": "Customer Loyalty", "description": "Loyalty programs, points, rewards"},
        ],
        "advanced": [
            {"name": "Personalization Engine", "description": "AI-driven product recommendations"},
            {"name": "Supply Chain Analytics", "description": "Demand forecasting, vendor performance"},
            {"name": "E-commerce Platform", "description": "Online store, cart, payment, shipping"},
            {"name": "Visual Merchandising", "description": "Planograms, shelf analytics, layout"},
        ],
    },
    "logistics": {
        "core": [
            {"name": "Fleet Management", "description": "Vehicle tracking, maintenance, fuel"},
            {"name": "Warehouse Management", "description": "Receiving, putaway, picking, shipping"},
            {"name": "Route Optimization", "description": "AI-powered route planning and optimization"},
            {"name": "Shipment Tracking", "description": "Real-time tracking, ETA, notifications"},
        ],
        "advanced": [
            {"name": "Last Mile Delivery", "description": "Driver app, customer notifications, proof of delivery"},
            {"name": "Freight Management", "description": "Rate management, carrier selection, documentation"},
            {"name": "Warehouse Automation", "description": "Robotics integration, automated sorting"},
        ],
    },
    "construction": {
        "core": [
            {"name": "Project Management", "description": "Scheduling, budgeting, resource allocation"},
            {"name": "BIM Integration", "description": "Building Information Modeling collaboration"},
            {"name": "Estimating & Bidding", "description": "Cost estimation, bid management, takeoffs"},
            {"name": "Field Operations", "description": "Daily reports, inspections, punch lists"},
        ],
        "advanced": [
            {"name": "Drone Survey", "description": "Aerial mapping, progress tracking, volume calculation"},
            {"name": "Safety Management", "description": "Incident reporting, training, compliance"},
            {"name": "Subcontractor Management", "description": "Contracts, payments, performance tracking"},
        ],
    },
    "finance": {
        "core": [
            {"name": "Core Banking", "description": "Accounts, transactions, interest, statements"},
            {"name": "Loan Management", "description": "Origination, underwriting, servicing, collections"},
            {"name": "Payment Processing", "description": "ACH, wire, card, real-time payments"},
            {"name": "Compliance & Reporting", "description": "Regulatory reporting, AML screening, audit"},
        ],
        "advanced": [
            {"name": "Fraud Detection", "description": "ML-based transaction monitoring and alerting"},
            {"name": "Risk Management", "description": "Credit risk, market risk, operational risk"},
            {"name": "Digital Banking", "description": "Mobile app, online banking, open banking APIs"},
            {"name": "Wealth Management", "description": "Portfolio management, advisory, robo-advisor"},
        ],
    },
}


class ModuleEngine(BaseEngine):
    name = "module"

    def __init__(self, llm=None):
        self.llm = llm

    def run(self, context: dict) -> dict:
        modules = self._generate_modules(context)
        used_llm = self.llm is not None and bool((context.get("description") or "").strip())
        all_modules = modules.get("core", []) + modules.get("advanced", [])
        return {
            "modules": all_modules,
            "core_modules": modules.get("core", []),
            "advanced_modules": modules.get("advanced", []),
            "module_count": len(all_modules),
            "module_source": "llm" if used_llm else "lookup",
        }

    def _generate_modules(self, context: dict) -> dict:
        industry = (context.get("industry_data") or {}).get("industry", "custom")
        fallback = MODULES_BY_INDUSTRY.get(industry, MODULES_BY_INDUSTRY.get("custom", {
            "core": [{"name": "User Management", "description": "User registration, roles, permissions"}],
            "advanced": [{"name": "Analytics Dashboard", "description": "Reports, charts, data export"}],
        }))

        if self.llm is None:
            return fallback

        description = (context.get("description") or "").strip()
        if not description:
            return fallback

        try:
            prompt = f"{MODULE_SYSTEM_PROMPT}\n\n{MODULE_EXTRACTION_TEMPLATE.format(
                domain=context.get("domain", "custom"),
                project_type=context.get("project_type", "custom"),
                project_domain_description=context.get("project_domain_description") or description,
                description=description,
                core_features=json.dumps(context.get("core_features", []))[:1500],
            )}"
            result = self.llm.generate_json(prompt, complexity="simple", max_tokens=2048)
            if "_parse_error" in result:
                logger.warning("Module LLM parse error, using lookup fallback")
                return fallback

            core = self._validate_modules(result.get("core_modules"))
            advanced = self._validate_modules(result.get("advanced_modules"))
            if not core:
                logger.warning("Module LLM returned no valid core modules, using lookup fallback")
                return fallback

            return {"core": core[:8], "advanced": advanced[:6]}
        except Exception as e:
            logger.warning("Module LLM call failed (%s), using lookup fallback", e)
            return fallback

    @staticmethod
    def _validate_modules(items) -> list:
        if not isinstance(items, list):
            return []
        seen = set()
        valid = []
        for item in items:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).strip()
            description = str(item.get("description", "")).strip()
            if not name or len(name) < 2 or len(description) < 10:
                continue
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            valid.append({"name": name, "description": description})
        return valid

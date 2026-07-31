from enum import Enum


class OrganizationPlan(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class UserRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class ProposalStatus(str, Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENT = "sent"


class IndustryType(str, Enum):
    ERP = "erp"
    CRM = "crm"
    HRMS = "hrms"
    MANUFACTURING = "manufacturing"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    GOVERNMENT = "government"
    RETAIL = "retail"
    LOGISTICS = "logistics"
    CONSTRUCTION = "construction"
    AI = "ai"
    SAAS = "saas"
    MOBILE = "mobile"
    WEB = "web"
    CUSTOM = "custom"


class KnowledgeType(str, Enum):
    CASE_STUDY = "case_study"
    BEST_PRACTICE = "best_practice"
    TECHNOLOGY = "technology"
    PRICING = "pricing"
    INDUSTRY = "industry"


class ExportFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"
    PPTX = "pptx"


DEFAULT_PERMISSIONS = {
    UserRole.ADMIN: [
        "proposal:create", "proposal:read", "proposal:update", "proposal:delete",
        "proposal:approve", "proposal:submit",
        "client:create", "client:read", "client:update", "client:delete",
        "project:create", "project:read", "project:update", "project:delete",
        "template:create", "template:read", "template:update", "template:delete",
        "workspace:create", "workspace:read", "workspace:update", "workspace:delete",
        "member:create", "member:read", "member:update", "member:delete",
        "settings:read", "settings:update",
        "billing:read", "billing:update",
        "knowledge:create", "knowledge:read", "knowledge:update", "knowledge:delete",
    ],
    UserRole.EDITOR: [
        "proposal:create", "proposal:read", "proposal:update",
        "client:create", "client:read", "client:update",
        "project:create", "project:read", "project:update",
        "template:read",
        "workspace:read",
        "knowledge:read",
        "settings:read",
    ],
    UserRole.VIEWER: [
        "proposal:read",
        "client:read",
        "project:read",
        "template:read",
        "workspace:read",
        "knowledge:read",
    ],
}

PLAN_LIMITS = {
    OrganizationPlan.FREE: {"proposals_per_month": 3, "team_members": 1, "storage_mb": 50},
    OrganizationPlan.STARTER: {"proposals_per_month": 20, "team_members": 5, "storage_mb": 500},
    OrganizationPlan.PROFESSIONAL: {"proposals_per_month": 100, "team_members": 20, "storage_mb": 2000},
    OrganizationPlan.ENTERPRISE: {"proposals_per_month": 999999, "team_members": 999, "storage_mb": 50000},
}

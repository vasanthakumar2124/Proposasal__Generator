import json
import logging

from app.engines.base_engine import BaseEngine
from app.llm.prompts import STACK_RATIONALE_SYSTEM_PROMPT, STACK_RATIONALE_TEMPLATE

logger = logging.getLogger("proposalcraft.engines.tech_stack")

STACK_TEMPLATES = {
    "web_app": {
        "frontend": [
            {"name": "React 19", "category": "Framework", "description": "Component-based UI library with hooks and server components"},
            {"name": "TypeScript", "category": "Language", "description": "Type-safe JavaScript superset"},
            {"name": "Tailwind CSS", "category": "Styling", "description": "Utility-first CSS framework"},
            {"name": "React Query", "category": "State Management", "description": "Server state management and caching"},
            {"name": "Redux Toolkit", "category": "State Management", "description": "Client state management"},
        ],
        "backend": [
            {"name": "Python 3.12+", "category": "Language", "description": "High-level programming language"},
            {"name": "FastAPI", "category": "Framework", "description": "Async Python web framework with OpenAPI"},
            {"name": "LangGraph", "category": "AI Orchestration", "description": "Stateful agent workflow orchestration"},
            {"name": "Celery", "category": "Task Queue", "description": "Distributed task queue for background jobs"},
        ],
        "database": [
            {"name": "MongoDB", "category": "Primary Database", "description": "Document database for flexible schemas"},
            {"name": "Redis", "category": "Cache & Queue", "description": "In-memory cache and message broker"},
            {"name": "Qdrant", "category": "Vector Database", "description": "Vector similarity search for RAG"},
        ],
        "cloud": [
            {"name": "Docker", "category": "Containerization", "description": "Application containerization"},
            {"name": "Kubernetes", "category": "Orchestration", "description": "Container orchestration (production)"},
            {"name": "AWS / GCP / Azure", "category": "Cloud Provider", "description": "Cloud infrastructure provider"},
            {"name": "Cloudflare", "category": "CDN & Security", "description": "Content delivery and DDoS protection"},
        ],
        "ai_ml": [
            {"name": "OpenAI / Groq", "category": "LLM Provider", "description": "Large language model API access"},
            {"name": "Sentence Transformers", "category": "Embeddings", "description": "Text embedding generation for RAG"},
            {"name": "LangChain", "category": "AI Framework", "description": "LLM application framework"},
        ],
        "devops": [
            {"name": "GitHub Actions", "category": "CI/CD", "description": "Automated build, test, and deployment"},
            {"name": "Terraform", "category": "IaC", "description": "Infrastructure as Code"},
            {"name": "Prometheus + Grafana", "category": "Monitoring", "description": "Metrics collection and visualization"},
        ],
    },
    "mobile_app": {
        "frontend": [
            {"name": "React Native", "category": "Framework", "description": "Cross-platform mobile development"},
            {"name": "TypeScript", "category": "Language", "description": "Type-safe JavaScript"},
            {"name": "Expo", "category": "Toolchain", "description": "React Native toolchain and SDK"},
        ],
        "backend": [
            {"name": "Python 3.12+", "category": "Language", "description": "High-level programming language"},
            {"name": "FastAPI", "category": "Framework", "description": "Async Python REST API framework"},
            {"name": "Firebase", "category": "Backend Service", "description": "Auth, push notifications, analytics"},
        ],
        "database": [
            {"name": "PostgreSQL", "category": "Primary Database", "description": "Relational database for structured data"},
            {"name": "Redis", "category": "Cache", "description": "Session management and caching"},
        ],
        "cloud": [
            {"name": "Docker", "category": "Containerization", "description": "Application containerization"},
            {"name": "AWS / GCP", "category": "Cloud Provider", "description": "Cloud infrastructure provider"},
        ],
        "ai_ml": [
            {"name": "OpenAI API", "category": "LLM Provider", "description": "Large language model API access"},
        ],
        "devops": [
            {"name": "GitHub Actions", "category": "CI/CD", "description": "Automated build, test, and deployment"},
            {"name": "TestFlight / Play Console", "category": "Distribution", "description": "Mobile app distribution"},
        ],
    },
    "saas": {
        "frontend": [
            {"name": "React 19", "category": "Framework", "description": "Component-based UI library"},
            {"name": "TypeScript", "category": "Language", "description": "Type-safe JavaScript"},
            {"name": "Tailwind CSS", "category": "Styling", "description": "Utility-first CSS framework"},
            {"name": "Next.js", "category": "Meta-framework", "description": "SSR, SSG, and API routes"},
        ],
        "backend": [
            {"name": "Python 3.12+", "category": "Language", "description": "High-level programming language"},
            {"name": "FastAPI", "category": "Framework", "description": "Async Python REST API framework"},
            {"name": "Stripe", "category": "Payments", "description": "Subscription billing and payment processing"},
        ],
        "database": [
            {"name": "PostgreSQL", "category": "Primary Database", "description": "Relational database"},
            {"name": "Redis", "category": "Cache & Queue", "description": "In-memory cache and message broker"},
            {"name": "Qdrant", "category": "Vector DB", "description": "Vector similarity search"},
        ],
        "cloud": [
            {"name": "Docker", "category": "Containerization", "description": "Application containerization"},
            {"name": "Kubernetes", "category": "Orchestration", "description": "Container orchestration"},
            {"name": "AWS / GCP / Azure", "category": "Cloud Provider", "description": "Cloud infrastructure"},
        ],
        "ai_ml": [
            {"name": "OpenAI / Anthropic", "category": "LLM Provider", "description": "Large language model API access"},
            {"name": "LangChain", "category": "AI Framework", "description": "LLM application framework"},
        ],
        "devops": [
            {"name": "GitHub Actions", "category": "CI/CD", "description": "Automated build, test, and deployment"},
            {"name": "Datadog", "category": "Monitoring", "description": "Application performance monitoring"},
        ],
    },
    "ecommerce": {
        "frontend": [
            {"name": "React 19", "category": "Framework", "description": "Component-based UI library"},
            {"name": "TypeScript", "category": "Language", "description": "Type-safe JavaScript"},
            {"name": "Tailwind CSS", "category": "Styling", "description": "Utility-first CSS framework"},
        ],
        "backend": [
            {"name": "Python 3.12+", "category": "Language", "description": "High-level programming language"},
            {"name": "FastAPI", "category": "Framework", "description": "Async Python REST API framework"},
            {"name": "Stripe", "category": "Payments", "description": "Payment processing, subscriptions, payouts"},
        ],
        "database": [
            {"name": "PostgreSQL", "category": "Primary Database", "description": "Relational database for orders and inventory"},
            {"name": "Redis", "category": "Cache & Queue", "description": "Session caching and cart state"},
            {"name": "Elasticsearch", "category": "Search", "description": "Product search and faceted filtering"},
        ],
        "cloud": [
            {"name": "Docker", "category": "Containerization", "description": "Application containerization"},
            {"name": "AWS / GCP", "category": "Cloud Provider", "description": "Cloud infrastructure provider"},
            {"name": "Cloudflare", "category": "CDN & Security", "description": "Content delivery and DDoS protection"},
        ],
        "ai_ml": [
            {"name": "OpenAI / Groq", "category": "LLM Provider", "description": "Product descriptions, recommendations"},
            {"name": "Relevance AI", "category": "Personalization", "description": "Product recommendation engine"},
        ],
        "devops": [
            {"name": "GitHub Actions", "category": "CI/CD", "description": "Automated build, test, and deployment"},
            {"name": "Prometheus + Grafana", "category": "Monitoring", "description": "Metrics collection and visualization"},
        ],
    },
}

# requirement prompt enum uses these keys; aliases normalize them to template keys.
STACK_TEMPLATE_ALIASES = {
    "saas_platform": "saas",
    "web": "web_app",
    "webapp": "web_app",
    "mobile": "mobile_app",
}


class TechStackEngine(BaseEngine):
    name = "tech_stack"

    def __init__(self, llm=None):
        self.llm = llm

    def run(self, context: dict) -> dict:
        project_type = self._resolve_project_type(context.get("project_type", "web_app"))
        template = STACK_TEMPLATES.get(project_type, STACK_TEMPLATES["web_app"])

        flat_stack = []
        for category, items in template.items():
            for item in items:
                flat_stack.append(item)

        rationale = self._rationale(context, template, flat_stack)

        return {
            "technology_stack": template,
            "full_stack": flat_stack,
            "rationale": rationale,
            "architecture_pattern": "Clean Architecture with Domain-Driven Design",
            "api_style": "RESTful + WebSocket for real-time features",
            "deployment_strategy": "Containerized microservices on Kubernetes",
        }

    @staticmethod
    def _resolve_project_type(raw: str) -> str:
        normalized = STACK_TEMPLATE_ALIASES.get((raw or "").lower().strip(), (raw or "").lower().strip())
        return normalized if normalized in STACK_TEMPLATES else "web_app"

    def _rationale(self, context: dict, template: dict, flat_stack: list) -> str:
        fallback = self._fallback_rationale(context, template)
        if self.llm is None:
            return fallback

        description = (context.get("description") or "").strip()
        if not description:
            return fallback

        try:
            stack_json = json.dumps({
                layer: [item.get("name") for item in items if isinstance(item, dict)]
                for layer, items in template.items()
            })
            prompt = f"{STACK_RATIONALE_SYSTEM_PROMPT}\n\n{STACK_RATIONALE_TEMPLATE.format(
                domain=context.get("domain", "custom"),
                project_type=context.get("project_type", "web_app"),
                description=description[:2000],
                stack_json=stack_json,
            )}"
            result = self.llm.generate_json(prompt, complexity="simple", max_tokens=512)
            if "_parse_error" not in result and str(result.get("rationale", "")).strip():
                return str(result["rationale"]).strip()
        except Exception as e:
            logger.warning("Tech stack rationale LLM call failed (%s), using fallback", e)
        return fallback

    @staticmethod
    def _fallback_rationale(context: dict, template: dict) -> str:
        layers = [
            item.get("name")
            for items in template.values()
            for item in items
            if isinstance(item, dict)
        ]
        key_names = [n for n in layers if n][:4]
        return (
            f"This stack is selected to match the project's {context.get('project_type', 'web_app')} "
            f"requirements, combining {', '.join(key_names)} to deliver the scope described in this "
            "proposal with a balance of development speed, operational stability, and long-term maintainability."
        )

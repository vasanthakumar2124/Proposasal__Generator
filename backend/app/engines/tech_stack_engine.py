from app.engines.base_engine import BaseEngine

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
}


class TechStackEngine(BaseEngine):
    name = "tech_stack"

    def run(self, context: dict) -> dict:
        project_type = context.get("project_type", "web_app")
        template = STACK_TEMPLATES.get(project_type, STACK_TEMPLATES["web_app"])

        flat_stack = []
        for category, items in template.items():
            for item in items:
                flat_stack.append(item)

        return {
            "technology_stack": template,
            "full_stack": flat_stack,
            "architecture_pattern": "Clean Architecture with Domain-Driven Design",
            "api_style": "RESTful + WebSocket for real-time features",
            "deployment_strategy": "Containerized microservices on Kubernetes",
        }

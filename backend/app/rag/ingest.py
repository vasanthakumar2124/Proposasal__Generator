import logging
from typing import Generator

from app.rag.chunker import DocumentChunker
from app.rag.service import qdrant_service
from app.rag.schemas import IngestDocument

logger = logging.getLogger("proposalcraft.ingest")


class IngestPipeline:
    def __init__(self):
        self.chunker = DocumentChunker()

    def ingest_text(self, document: IngestDocument, org_id: str | None = None) -> list[str]:
        chunks = self.chunker.chunk_text(document.content)
        point_ids = []
        for chunk in chunks:
            pid = qdrant_service.insert_document(
                collection_name=document.collection_name,
                content=chunk,
                metadata=document.metadata,
                org_id=org_id,
            )
            point_ids.append(pid)
        logger.info(
            "Ingested %d chunks into collection '%s' (org=%s)",
            len(point_ids),
            document.collection_name,
            org_id,
        )
        return point_ids

    def ingest_documents(
        self, documents: list[dict], collection_name: str, org_id: str | None = None
    ) -> list[str]:
        point_ids = []
        for doc in documents:
            content = doc.get("content", doc.get("page_content", ""))
            if not content:
                continue
            metadata = {k: v for k, v in doc.items() if k not in ("content", "page_content")}
            chunks = self.chunker.chunk_text(content)
            for chunk in chunks:
                pid = qdrant_service.insert_document(
                    collection_name=collection_name,
                    content=chunk,
                    metadata=metadata,
                    org_id=org_id,
                )
                point_ids.append(pid)
        logger.info("Ingested %d chunks total into '%s' (org=%s)", len(point_ids), collection_name, org_id)
        return point_ids

    def seed_default_knowledge(self, org_id: str | None = None) -> None:
        qdrant_service.initialize()
        for collection_name, data in DEFAULT_KNOWLEDGE.items():
            existing = qdrant_service.count_documents(collection_name, org_id=org_id)
            if existing > 0:
                logger.info("Collection '%s' already has %d documents, skipping seed", collection_name, existing)
                continue
            for entry in data:
                qdrant_service.insert_document(
                    collection_name=collection_name,
                    content=entry["content"],
                    metadata=entry.get("metadata", {}),
                    org_id=org_id,
                )
            logger.info("Seeded %d documents into '%s'", len(data), collection_name)


DEFAULT_KNOWLEDGE = {
    "industry_knowledge": [
        {"content": "HIPAA compliance requires PHI encryption at rest and in transit, audit controls, access controls, and breach notification. Healthcare software must implement RBAC, session timeout, and detailed audit logging.", "metadata": {"industry": "healthcare"}},
        {"content": "PCI DSS compliance is required for any software handling credit card data. Requirements include encryption, access control, regular security testing, and network segmentation.", "metadata": {"industry": "fintech"}},
        {"content": "GDPR compliance requires data protection by design, user consent management, right to erasure, data portability, and breach notification within 72 hours.", "metadata": {"industry": "saas"}},
        {"content": "SOC 2 compliance requires security, availability, processing integrity, confidentiality, and privacy controls. Relevant for SaaS platforms handling customer data.", "metadata": {"industry": "saas"}},
        {"content": "ERP systems typically require integration with existing accounting, inventory, HR, and CRM systems. Key considerations include data migration, user training, and business process reengineering.", "metadata": {"industry": "erp"}},
        {"content": "EdTech platforms must comply with FERPA/COPPA for student data privacy. Requirements include parent consent, data encryption, and restricted data access.", "metadata": {"industry": "edtech"}},
    ],
    "best_practices": [
        {"content": "Agile methodology with 2-week sprints is recommended for most web development projects. Daily standups, sprint planning, and retrospectives ensure continuous delivery.", "metadata": {"category": "methodology"}},
        {"content": "Test-driven development (TDD) reduces bug rates by 40-80%. Aim for 80%+ code coverage with unit, integration, and E2E tests.", "metadata": {"category": "development"}},
        {"content": "API-first design enables frontend and mobile development to proceed in parallel. Document APIs with OpenAPI/Swagger and version from day one.", "metadata": {"category": "architecture"}},
        {"content": "CI/CD pipeline with automated testing, linting, and deployment reduces release cycles from weeks to hours. Use staging environments for pre-production validation.", "metadata": {"category": "devops"}},
        {"content": "Microservices architecture suits complex domains with multiple bounded contexts. Start monolith, extract services as needed based on coupling and scaling requirements.", "metadata": {"category": "architecture"}},
    ],
    "pricing_data": [
        {"content": "Enterprise SaaS projects typically range from $150k-$500k for MVP. Mid-market solutions $50k-$150k. Small business solutions $15k-$50k.", "metadata": {"category": "benchmarks"}},
        {"content": "Hourly rates: Senior architect $150-200/hr, Full-stack developer $100-150/hr, Frontend specialist $80-120/hr, QA engineer $60-90/hr, Project manager $80-120/hr.", "metadata": {"category": "rates"}},
        {"content": "Fixed-price projects typically include a 20-30% contingency buffer. Maintenance contracts range from 15-20% of development cost annually.", "metadata": {"category": "pricing_models"}},
    ],
    "automation_patterns": [
        {"content": "Document workflow automation: OCR ingestion, AI classification, approval routing, and archival. Reduces processing time by 60-80%.", "metadata": {"pattern": "document_processing"}},
        {"content": "Email automation: Template-based generation, smart categorization, auto-reply rules, CRM integration. Saves 10-15 hours per employee weekly.", "metadata": {"pattern": "communication"}},
    ],
    "technology_knowledge": [
        {"content": "Modern web stack: React/Next.js frontend, FastAPI or Node.js backend, PostgreSQL primary store, Redis for caching and queues. Serverless-friendly for elastic workloads.", "metadata": {"stack": "web"}},
        {"content": "Enterprise data stack: Snowflake/BigQuery warehouse, dbt transformations, Airflow orchestration, Tableau/PowerBI for BI dashboards. Streaming via Kafka for real-time pipelines.", "metadata": {"stack": "data"}},
        {"content": "AI/ML integration: Retrieval-augmented generation over domain corpora, embedding-based semantic search, guardrails for hallucination control, LLM evals in CI.", "metadata": {"stack": "ai"}},
        {"content": "Cloud-native deployment: Kubernetes with Helm, infrastructure as code via Terraform, observability with Prometheus/Grafana/OpenTelemetry, zero-downtime rolling deploys.", "metadata": {"stack": "devops"}},
        {"content": "Mobile strategy: React Native or Flutter for cross-platform, offline-first sync, push notifications, app store compliance and staged rollouts.", "metadata": {"stack": "mobile"}},
    ],
    "case_studies": [
        {"content": "Logistics CRM implementation: reduced onboarding cycle from 21 to 5 days via automated KYC and workflow engine; 200 users adopted the platform within one quarter.", "metadata": {"industry": "logistics", "outcome": "process_efficiency"}},
        {"content": "Healthcare portal rollout: patient self-service cut call-center volume 45% while HIPAA-aligned audit logging satisfied provider compliance review.", "metadata": {"industry": "healthcare", "outcome": "compliance"}},
        {"content": "Fintech payment migration: PCI DSS-aligned card processing with tokenization, fraud rules engine, and 99.95% uptime during a 4-month staged cutover.", "metadata": {"industry": "fintech", "outcome": "migration"}},
        {"content": "EdTech analytics upgrade: 120k-student platform added real-time dashboards and FERPA-safe role scoping, improving retention 12% year over year.", "metadata": {"industry": "edtech", "outcome": "analytics"}},
    ],
    "compliance_standards": [
        {"content": "GDPR: consent records, data mapping, right to erasure flows, 72-hour breach notification, and DPIA for high-risk processing.", "metadata": {"standard": "gdpr"}},
        {"content": "SOC 2 Type II: trust services criteria for security, availability, confidentiality; continuous monitoring, vendor risk reviews, incident response drills.", "metadata": {"standard": "soc2"}},
        {"content": "ISO 27001: ISMS scope, risk assessment, asset management, access control policy, and annual internal audits with management review.", "metadata": {"standard": "iso27001"}},
        {"content": "HIPAA Security Rule: administrative, physical, and technical safeguards; PHI minimization, encryption, and business associate agreements for every subprocessor.", "metadata": {"standard": "hipaa"}},
    ],
    "proposal_examples": [
        {"content": "Executive summary pattern: state the business problem in one paragraph, the proposed solution in one paragraph, expected outcomes with numbers, and investment ask with timeline.", "metadata": {"pattern": "executive_summary"}},
        {"content": "Solution architecture pattern: diagram of components, data flow narrative, security boundaries, and integration points with existing systems.", "metadata": {"pattern": "architecture"}},
        {"content": "Implementation plan pattern: phased milestones with owner, dependency, and acceptance criteria per phase; risks table with mitigation owners.", "metadata": {"pattern": "implementation_plan"}},
        {"content": "Pricing pattern: value-based tiers, transparent assumptions, ROI calculation showing payback period, and optional maintenance/support add-ons.", "metadata": {"pattern": "pricing"}},
    ],
}


ingest_pipeline = IngestPipeline()

import logging
from typing import Generator

from app.rag.chunker import DocumentChunker
from app.rag.service import qdrant_service
from app.rag.schemas import IngestDocument

logger = logging.getLogger("proposalcraft.ingest")


class IngestPipeline:
    def __init__(self):
        self.chunker = DocumentChunker()

    def ingest_text(self, document: IngestDocument) -> list[str]:
        chunks = self.chunker.chunk_text(document.content)
        point_ids = []
        for chunk in chunks:
            pid = qdrant_service.insert_document(
                collection_name=document.collection_name,
                content=chunk,
                metadata=document.metadata,
            )
            point_ids.append(pid)
        logger.info(
            "Ingested %d chunks into collection '%s'",
            len(point_ids),
            document.collection_name,
        )
        return point_ids

    def ingest_documents(self, documents: list[dict], collection_name: str) -> list[str]:
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
                )
                point_ids.append(pid)
        logger.info("Ingested %d chunks total into '%s'", len(point_ids), collection_name)
        return point_ids

    def seed_default_knowledge(self) -> None:
        qdrant_service.initialize()
        for collection_name, data in DEFAULT_KNOWLEDGE.items():
            existing = qdrant_service.count_documents(collection_name)
            if existing > 0:
                logger.info("Collection '%s' already has %d documents, skipping seed", collection_name, existing)
                continue
            for entry in data:
                qdrant_service.insert_document(
                    collection_name=collection_name,
                    content=entry["content"],
                    metadata=entry.get("metadata", {}),
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
}


ingest_pipeline = IngestPipeline()

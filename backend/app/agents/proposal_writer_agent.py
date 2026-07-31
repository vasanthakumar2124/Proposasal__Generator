from datetime import datetime
import uuid
import json

from app.llm.client import generate_response
from app.llm.prompts import PROPOSAL_PROMPT
from app.pricing.engine import generate_pricing_section


class ProposalWriterAgent:
    def __init__(self):
        self.name = "Proposal Writer Agent"

    def run(self, requirement, rag_context, features, business_analysis):
        requirement_text = json.dumps(requirement, indent=2)
        rag_text = json.dumps(rag_context, indent=2) if isinstance(rag_context, dict) else str(rag_context)
        features_text = json.dumps(features, indent=2) if isinstance(features, dict) else str(features)
        analysis_text = json.dumps(business_analysis, indent=2) if isinstance(business_analysis, dict) else str(business_analysis)

        pricing = generate_pricing_section(features)
        pricing_text = json.dumps(pricing, indent=2)

        prompt = PROPOSAL_PROMPT.format(
            requirement=requirement_text,
            context=rag_text,
            features=features_text,
            business_analysis=analysis_text,
            pricing=pricing_text,
            date=datetime.now().strftime("%d %B %Y"),
        )

        proposal_content = generate_response(prompt, complexity="complex", max_tokens=4096)

        return {
            "proposal_id": str(uuid.uuid4()),
            "project_name": requirement.get("project_name", "Software Project"),
            "generated_date": datetime.now().strftime("%d %B %Y"),
            "proposal_content": proposal_content,
            "pricing": pricing,
        }

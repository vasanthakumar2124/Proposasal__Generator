from datetime import datetime
import uuid
import json

from app.llm.client import generate_response
from app.llm.prompts import PROPOSAL_PROMPT


class ProposalWriterAgent:

    def __init__(self):
        self.name = "Proposal Writer Agent"

    def run(
        self,
        requirement,
        rag_context,
        features,
        business_analysis
    ):

        # Convert dictionaries/lists into formatted text
        requirement_text = json.dumps(requirement, indent=2)

        if isinstance(rag_context, dict):
            rag_context = json.dumps(rag_context, indent=2)

        if isinstance(features, dict):
            features_text = json.dumps(features, indent=2)
        else:
            features_text = str(features)

        if isinstance(business_analysis, dict):
            business_analysis_text = json.dumps(
                business_analysis,
                indent=2
            )
        else:
            business_analysis_text = str(
                business_analysis
            )

        prompt = PROPOSAL_PROMPT.format(
            requirement=requirement_text,
            context=rag_context,
            features=features_text,
            business_analysis=business_analysis_text,
            date=datetime.now().strftime("%d %B %Y")
        )

        proposal_content = generate_response(prompt)

        return {

            "proposal_id": str(uuid.uuid4()),

            "project_name": requirement.get(
                "project_name",
                "Software Project"
            ),

            "generated_date": datetime.now().strftime(
                "%d %B %Y"
            ),

            "proposal_content": proposal_content

        }
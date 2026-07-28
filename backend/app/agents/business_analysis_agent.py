from app.llm.client import generate_response
from app.llm.prompts import BUSINESS_ANALYSIS_PROMPT
import json


class BusinessAnalysisAgent:

    def __init__(self):
        self.name = "Business Analysis Agent"

    def run(
        self,
        requirement,
        rag_context,
        features
    ):

        prompt = BUSINESS_ANALYSIS_PROMPT.format(

            requirement=requirement,

            context=rag_context,

            features=features

        )

        response = generate_response(prompt)

        try:
            return json.loads(response)

        except Exception:

            return {

                "industry": "",

                "project_type": "",

                "business_goal": "",

                "target_users": [],

                "pain_points": [],

                "opportunities": [],

                "business_value": [],

                "digital_transformation": "",

                "success_metrics": []

            }
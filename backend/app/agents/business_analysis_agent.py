from app.llm.client import generate_json_response
from app.llm.prompts import BUSINESS_ANALYSIS_PROMPT


class BusinessAnalysisAgent:
    def __init__(self):
        self.name = "Business Analysis Agent"

    def run(self, requirement, rag_context, features):
        prompt = BUSINESS_ANALYSIS_PROMPT.format(
            requirement=requirement,
            context=rag_context,
            features=features,
        )
        return generate_json_response(prompt, complexity="medium")

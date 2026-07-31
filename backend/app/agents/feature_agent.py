from app.llm.client import generate_json_response
from app.llm.prompts import FEATURE_PROMPT


class FeatureAgent:
    def __init__(self):
        self.name = "Feature Agent"

    def run(self, requirement, rag_context):
        prompt = FEATURE_PROMPT.format(
            requirement=requirement,
            context=rag_context
        )
        return generate_json_response(prompt, complexity="medium")

import json

from app.llm.prompts import FEATURE_PROMPT
from app.llm.client import generate_response


class FeatureAgent:


    def __init__(self):
        self.name = "Feature Agent"



    def run(self, requirement, rag_context):


        prompt = FEATURE_PROMPT.format(
            requirement=requirement,
            context=rag_context
        )


        response = generate_response(
            prompt
        )

        try:

            features = json.loads(
                response
            )

        except json.JSONDecodeError:

            features = {
                "raw_response": response
            }


        return features
import json

from app.llm.client import generate_response
from app.llm.prompts import REQUIREMENT_PROMPT

def analyze_requirement(requirement: str) -> dict:


    prompt = REQUIREMENT_PROMPT.format(
        requirement=requirement
    )

    response = generate_response(prompt)

    try:
        result = json.loads(response)
    except Exception:
        result = {
            "raw_response": response
        }

    return result
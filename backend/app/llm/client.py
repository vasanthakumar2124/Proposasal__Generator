from groq import Groq

from app.config.settings import settings

client = Groq(
    api_key=settings.GROQ_API_KEY
)

def generate_response(prompt: str) -> str:

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=1024
    )

    return response.choices[0].message.content
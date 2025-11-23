from openai import OpenAI
from src.utils.env import Env
from src.utils.config import Config

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=Env.OPEN_ROUTER,
)

def get_response(msg: str, model="x-ai/grok-4.1-fast"):
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": f"{Config.DEFAULT_PROMPT} {msg}."
            }
        ],
        extra_body={"reasoning": {"enabled": False}}
    )
    
    return completion.choices[0].message.content
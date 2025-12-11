from openai import OpenAI
from src.utils.env import Env
from src.utils.config import Config
from dataclasses import dataclass

class Model:
    def __init__(
            self, system_prompt: str, role: str = "user",
            temperature: float = 0.55, top_p: float = 0.8,
            presence_penalty: float = 0.25, frequency_penalty: float = 0.4
        ):
        self.system_prompt = system_prompt
        self.role = role

        self.temperature = temperature
        self.top_p = top_p
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty

    def make_request(
            self, msg: str, api_key: str = Env.OPEN_ROUTER, 
            model: str = "x-ai/grok-4.1-fast"
        ) -> str:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": self.role,
                    "content": f"{self.system_prompt} {msg}."
                }
            ],
            temperature=self.temperature,
            top_p=self.top_p,
            presence_penalty=self.presence_penalty,
            frequency_penalty=self.frequency_penalty
        )
        
        return completion.choices[0].message.content

@dataclass
class DefaultModels:
    AGRESSIVE = Model(
        system_prompt=Config.SYSTEM_PROMPTS.AGRESSIVE_PROMPT,
        temperature=0.7,
        top_p=0.9,
        presence_penalty=0.25,
        frequency_penalty=0.4
    )
    PETER = Model(
        system_prompt=Config.SYSTEM_PROMPTS.PETER_PROMPT,
        temperature=0.9,
        top_p=0.92,
        presence_penalty=0.8,
        frequency_penalty=0.7
    )
    SMART = Model(
        system_prompt=Config.SYSTEM_PROMPTS.SMART_PROMPT,
        temperature=0.3,
        top_p=0.85,
        presence_penalty=0.1,
        frequency_penalty=0.1
    )
    MODERATOR = Model(
        system_prompt=Config.SYSTEM_PROMPTS.MODERATOR_PROMPT,
        role="assistant",
        temperature=0.3,
        top_p=0.85,
        presence_penalty=0.1,
        frequency_penalty=0.1
    )
    KAWAII = Model(
        system_prompt=Config.SYSTEM_PROMPTS.KAWAII_PROMPT,
        temperature=0.65,
        top_p=0.92,
        presence_penalty=0.3,
        frequency_penalty=0.5
    )


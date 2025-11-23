from openai import OpenAI
from src.utils.env import Env
from src.utils.config import Config
from dataclasses import dataclass

class Model:
    def __init__(
            self, system_prompt: str, role: str = "user",
            temperature: float = 0.7, top_p: float = 0.95,
            presence_penalty: float = 0.0, frequency_penalty: float = 0.0
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
        # TODO Добавить характеристики умной модели
    )
    MODERATOR = Model(
        system_prompt=Config.SYSTEM_PROMPTS.MODERATOR_PROMPT,
        role="assistant"
        # TODO Добавить характеристики модели-модератора
    )

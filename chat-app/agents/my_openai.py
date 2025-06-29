import os
from openai import AsyncOpenAI

class MyOpenAI:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def ainvoke(self, messages, model="gpt-4-turbo"):
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message 
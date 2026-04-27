"""Serviço LLM — parametrizável (Anthropic | OpenAI | Ollama)."""

from abc import ABC, abstractmethod

from backend.app.core.config import get_settings


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        ...


class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str, max_tokens: int, temperature: float):
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)
        message = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_prompt if system_prompt else "Você é um neurofisiologista experiente.",
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str, max_tokens: int, temperature: float):
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=messages,
        )
        return response.choices[0].message.content


class OllamaProvider(LLMProvider):
    def __init__(self, model: str, base_url: str):
        self.model = model
        self.base_url = base_url or "http://localhost:11434"

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        import httpx

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system_prompt,
                    "stream": False,
                },
            )
            response.raise_for_status()
            return response.json()["response"]


class MockLLMProvider(LLMProvider):
    """Provider de teste — usado quando não há API key configurada."""

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        return (
            "LAUDO DE ELETROENCEFALOGRAMA\n\n"
            "[LLM não configurado — este é um laudo de exemplo]\n\n"
            "Configure a variável LLM_API_KEY no arquivo .env para gerar laudos reais.\n\n"
            "CONCLUSÃO:\n"
            "EEG não analisado — LLM indisponível."
        )


def get_llm() -> LLMProvider:
    """Factory: retorna o provider LLM configurado no .env"""
    settings = get_settings()

    # Ollama não precisa de API key
    if settings.llm_provider == "ollama":
        return OllamaProvider(
            model=settings.llm_model,
            base_url=settings.llm_base_url,
        )

    # Para outros providers, se não tem API key, retorna mock
    if not settings.llm_api_key or settings.llm_api_key == "COLOQUE-SUA-API-KEY-AQUI":
        return MockLLMProvider()

    if settings.llm_provider == "anthropic":
        return AnthropicProvider(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
        )
    elif settings.llm_provider == "openai":
        return OpenAIProvider(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
        )
    else:
        raise ValueError(f"LLM provider não suportado: {settings.llm_provider}")

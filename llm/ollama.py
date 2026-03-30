import requests
import logging

from llm.base import BaseLLM

class OllamaLLMClient(BaseLLM):
    """Клиент для работы с Ollama (Gemma, LLaMA и др.)"""

    def __init__(self, config):
        self.config = config
        self.base_url = config.get("base_url")  # http://127.0.0.1:11434
        self.model = config.get("model")        # gemma3:27b
        self.timeout = config.get("timeout", 60)
        self.temperature = config.get("temperature", 0.0)
        self.max_tokens = config.get("max_tokens", 512)

        self.logger = logging.getLogger("OllamaLLMClient")

    def generate(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)

            self.logger.info("OLLAMA STATUS CODE: %s", response.status_code)
            self.logger.info("OLLAMA RAW RESPONSE: %s", response.text)

            response.raise_for_status()

            data = response.json()

            # Ollama возвращает:
            # { "response": "text..." }
            if "response" not in data:
                raise ValueError(f"Unexpected Ollama response: {data}")

            return data["response"]

        except Exception as e:
            self.logger.error("Error in OllamaLLMClient: %s", e)
            return "Ошибка при генерации ответа."
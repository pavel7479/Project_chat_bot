# intents/llm__intent_classifier.py

from typing import List, Dict
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

from intents.base_intents import BaseIntentClassifier
from intents.intent_rules import IntentRules
from llm.base import BaseLLM


# --- Pydantic схема ---
class IntentItem(BaseModel):
    intent: str = Field(..., description="Название интента")
    score: float = Field(..., description="Уверенность от 0 до 1")


class IntentOutput(BaseModel):
    intents: List[IntentItem]


class LLMIntentClassifier(BaseIntentClassifier):
    def __init__(
        self,
        llm: BaseLLM,
        intents_path: str,
        prompt_path: str,
        max_history_messages: int = 10,
        use_rules: bool = True,
        use_llm: bool = True,
    ):
        self.llm = llm
        self.intents_path = Path(intents_path)
        self.prompt_path = Path(prompt_path)
        self.max_history_messages = max_history_messages
        self.rules = IntentRules()
        self.use_rules = use_rules
        self.use_llm = use_llm

        # загрузка данных
        self.intents = self._load_intents()
        self.prompt_template = self._load_prompt()

        # parser
        self.parser = JsonOutputParser(pydantic_object=IntentOutput)

    # -------------------------
    # LOADERS
    # -------------------------
    def _load_intents(self) -> List[str]:
        if not self.intents_path.exists():
            raise FileNotFoundError(f"Файл интентов не найден: {self.intents_path}")

        return [
            line.strip()
            for line in self.intents_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def _load_prompt(self) -> str:
        if not self.prompt_path.exists():
            raise FileNotFoundError(f"Файл промпта не найден: {self.prompt_path}")

        return self.prompt_path.read_text(encoding="utf-8")

    # -------------------------
    # CORE
    # -------------------------
    def _build_prompt(
        self,
        query: str,
        history: List[Dict],
        docs: List[Dict]
    ) -> str:

        # история
        history_text = "\n".join(f"{msg.role}: {msg.content}" for msg in history)

        # интенты
        intents_text = "\n".join(self.intents)

        # инструкции JSON
        format_instructions = self.parser.get_format_instructions()

        return self.prompt_template.format(
            query=query,
            history=history_text,
            docs='',
            available_intents=intents_text,
            format_instructions=format_instructions,
        )

    def _call_llm(self, prompt: str) -> str:
        return self.llm.generate(prompt)

    def _parse_response(self, response: str) -> List[Dict]:
        try:
            parsed = self.parser.invoke(response)
            return [
                {"intent": item.intent, "score": item.score}
                for item in parsed.intents
            ]
        except Exception:
            return []

    # -------------------------
    # MAIN METHOD
    # -------------------------
    def predict_intents(
        self,
        query: str,
        history: List[Dict],
        docs: List[Dict]
    ) -> List[Dict]:

        # 1. Проверка: полностью вне профиля
        if self.use_rules and self.rules.is_fully_offtopic(query):
            return [{"intent": "вне профиля", "score": 1.0}]

        # 2. Сигнал о "вне профиля"
        has_offtopic_signal = False
        if self.use_rules:
            has_offtopic_signal = self.rules.detect_offtopic(query)

        # 3. LLM классификация
        intents = []
        if self.use_llm:
            prompt = self._build_prompt(query, history, docs)

            print("=== INTENT LLM INPUT ===")
            print(prompt)
            print("QUERY:", query)
            print("HISTORY:", history)
            
            response = self._call_llm(prompt)
            print("=== INTENT LLM RESPOSE ===")
            print(response)

            intents = self._parse_response(response)
            
            print("=== INTENTS PARSED ===")
            print(intents)

        # 4. Добавляем сигнал rules
        if has_offtopic_signal:
            intents.append({"intent": "вне профиля", "score": 0.3})

        return intents
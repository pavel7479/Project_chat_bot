from typing import List
from schemas.message import Message


class ContextBuilder:
    def __init__(self):
        prompt_path = "Project_chat_bot/prompts/prompt_user.txt"

        with open(prompt_path, "r", encoding="utf-8") as f:
            self.prompt_template = f.read()
            
    def build(
        self,
        query: str,
        docs: List[str],
        history: List[Message],
        intents: List[str] | None = None
    ) -> str:
        history_text = "\n".join(
            [f"{m.role}: {m.content}" for m in history]
        )

        docs_text = "\n\n".join([doc["text"] for doc in docs])

        # преобразуем каждый интент в строку, например через ключ "intent"
        intent_names = [i["intent"] for i in intents] if intents else []

        # управление поведением
        if "вне профиля" in intent_names:
            behavior = "Вежливо откажись отвечать. Объясни, что ты консультируешь только по продукту."
        elif "не по теме" in intent_names:
            behavior = "Сообщи, что вопрос непонятен. Попроси уточнить."
        elif "информация о каталогах" in intent_names:
            behavior = "Отвечай строго по контексту."
        else:
            behavior = "Отвечай по стандартным правилам."

        return self.prompt_template.format(
            history=history_text,
            intents=", ".join(intent_names) if intent_names else "не определены",
            docs=docs_text,
            query=query,
            behavior=behavior
        )
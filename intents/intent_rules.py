# intents/rules.py

from typing import List


class IntentRules:
    """
    Правила для определения явно НЕ профильных запросов.
    НЕ заменяет LLM, а только дополняет.
    """

    def __init__(self):
        self.offtopic_keywords = [
            "погода",
            "дождь",
            "температура",
            "политика",
            "президент",
            "новости",
            "курс валют",
            "доллар",
            "евро",
            "спорт",
            "футбол",
            "баскетбол",
        ]

    def detect_offtopic(self, query: str) -> bool:
        """
        Проверяет, есть ли в запросе признаки "не по теме"
        """
        query_lower = query.lower()

        for word in self.offtopic_keywords:
            if word in query_lower:
                return True

        return False

    def is_fully_offtopic(self, query: str) -> bool:
        """
        Определяет, что ВЕСЬ запрос не по теме
        (простой вариант — если нет признаков автобизнеса)
        """
        auto_keywords = [
            # базовые
            "каталог", "каталоги",
            "запчаст", "запчасти",
            "vin", "вин", "вин код",

            # EPC
            "epc", "епс", "ипс",

            # TIS
            "tis", "тис", "т.и.с",

            # коммерция
            "подписка", "доступ", "цена", "стоимость",

            # бренды (минимум)
            "honda", "хонда",
            "kia", "киа",
            "toyota", "тойота",
        ]

        query_lower = query.lower()

        has_auto = any(word in query_lower for word in auto_keywords)
        has_offtopic = self.detect_offtopic(query)

        return has_offtopic and not has_auto
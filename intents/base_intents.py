from abc import ABC, abstractmethod
from typing import List, Dict

class BaseIntentClassifier(ABC):
    @abstractmethod
    def predict_intents(self, query: str, history: List[Dict], docs: List[Dict]) -> List[Dict]:
        """
        Определяет список интентов на основе запроса и найденных документов
        """
        pass
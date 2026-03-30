from abc import ABC, abstractmethod
from typing import List, Dict


class BaseRetriever(ABC):
    @abstractmethod
    def search(self, query: str) -> List[Dict]:
        """
        Возвращает список документов:
        [
            {"text": "...", "metadata": {...}},
        ]
        """
        pass
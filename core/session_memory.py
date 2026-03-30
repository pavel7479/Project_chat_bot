from typing import List
from schemas.message import Message


class SessionMemory:
    def __init__(self, max_messages: int = 10):
        self.history: List[Message] = []
        self.max_messages = max_messages

    def get_history(self) -> List[Message]:
        return self.history

    def add_message(self, message: Message):
        self.history.append(message)
            # ограничиваем историю
        if len(self.history) > self.max_messages:
            self.history = self.history[-self.max_messages:]

    def clear(self):
        self.history = []
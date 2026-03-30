from dataclasses import dataclass
from typing import List


@dataclass
class ChatResponse:
    text: str
    media: List[str]
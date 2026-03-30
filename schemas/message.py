from dataclasses import dataclass


@dataclass
class Message:
    role: str  # "user" | "assistant"
    content: str
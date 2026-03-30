
from datetime import datetime
import os

class Logger:
    def __init__(self, log_file: str = "app_logging/chat.log"):
        self.log_file = log_file

    def _write(self, text: str):
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)  # создаём папку если нет

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {text}"

        print(line)

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def log(self, message: str):
        self._write(message)

    def log_prompt(self, prompt: str):
        self._write("=== PROMPT ===")
        self._write(prompt)

    def log_response(self, response: str):
        self._write("=== RESPONSE ===")
        self._write(response)

    def log_intents(self, intents):
        self._write("=== INTENTS ===")
        self._write(str(intents))
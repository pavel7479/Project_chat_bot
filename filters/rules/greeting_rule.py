from .base_rule import BaseRule


class GreetingRule(BaseRule):
    def handle(self, query: str, history):
        return "Привет! Чем могу помочь?"
from .base_rule import BaseRule


class OfftopicRule(BaseRule):
    def handle(self, query: str, history):
        return "Я могу помочь только с каталогами EPC и TIS."
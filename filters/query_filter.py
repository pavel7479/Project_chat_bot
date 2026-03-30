from filters.rules.greeting_rule import GreetingRule
from filters.rules.offtopic_rule import OfftopicRule
# from filters.rules.name_rule import NameRule


class QueryFilter:
    def __init__(self, rules_config: dict):
        self.rules = self._build_rules(rules_config)

    def _build_rules(self, config: dict):
        return [
            GreetingRule(config.get("GREETING", [])),
            OfftopicRule(config.get("OFFTOPIC", [])),
            # NameRule(config.get("NAME", [])),
        ]

    def process(self, query: str, history):
        for rule in self.rules:
            if rule.match(query, history):
                return rule.handle(query, history)

        return None
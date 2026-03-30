class BaseRule:
    def __init__(self, keywords: list):
        self.keywords = [k.lower() for k in keywords]

    def match(self, query: str, history) -> bool:
        q = query.lower()
        return any(k in q for k in self.keywords)

    def handle(self, query: str, history):
        raise NotImplementedError
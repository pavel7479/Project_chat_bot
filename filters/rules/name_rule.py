# from .base_rule import BaseRule


# class NameRule(BaseRule):
#     def handle(self, query: str, history):
#         for msg in reversed(history):
#             if "меня зовут" in msg.content.lower():
#                 return msg.content.split()[-1]

#         return "Я не запомнил ваше имя"
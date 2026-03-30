# main.py
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from Project_chat_bot.factory.builder import Builder

def main():
    # 1. путь к конфигу
    config_path = "Project_chat_bot/config/config_project_chat_bot.yaml"

    # 2. собираем систему
    builder = Builder(config_path)
    chat_service = builder.build_chat_service()

    print("Чат-бот запущен. Введите 'exit' для выхода.\n")

    # 3. цикл общения
    while True:
        user_input = input("Вы: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("Завершение работы.")
            break

        if not user_input:
            continue

        # 4. обработка
        response = chat_service.handle(user_input)

        # 5. вывод
        print(f"Бот: {response.text}\n")


if __name__ == "__main__":
    main()

# Запуск:
# cd /root/ChatBot
# python -m Project_chat_bot.main
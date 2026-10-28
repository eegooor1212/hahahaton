# -*- coding: utf-8 -*-

import json
import ollama
import time
import copy
import os
from openai import OpenAI
import requests
import httpx

SYSTEM_PROMPT = """
Ты — модуль извлечения требований для поиска отелей.

Преобразуй запрос пользователя в JSON.

Извлекай только информацию, явно присутствующую в запросе.
Не делай предположений и не выводи одно требование из другого.

Разрешено географическое уточнение destination 
(city → country → region).

Для каждого найденного параметра указывай:
- value — значение, обязательно на английском языке;
- weight — важность требования от 0 до 100.

Обычное требование: 60.
"желательно": 30.
"важно": 80.
"обязательно": 100.

Не возвращай параметры, которых нет в запросе.
Не возвращай null.
Не возвращай weight = 0.

Используй только параметры из разрешённой схемы.

Возвращай только валидный JSON без Markdown и пояснений.
"""

http_client = httpx.Client(
    trust_env=False,
    timeout=60.0
)

client = OpenAI(
    api_key=os.environ["LLM_API_KEY"],
    base_url="https://api.inferhold.com/v1",
    http_client=http_client
)

def parse_query(user_query):

    response = client.chat.completions.create(
        model="gpt-6.1-terra",

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_query
            }
        ],

        temperature=0,
        max_tokens=500
    )

    return response.choices[0].message.content

def merge_query_with_template(template_path, model_result, output_path="query.json"):
    """
    Накладывает результат модели на JSON-шаблон
    и сохраняет итоговый JSON в файл.

    template_path:
        путь к JSON-шаблону

    model_result:
        dict с результатом работы модели

    output_path:
        куда сохранить итоговый JSON
    """

    # Загружаем шаблон
    with open(template_path, "r", encoding="utf-8") as file:
        template = json.load(file)

    # Создаём копию, чтобы не изменять исходный шаблон
    result = copy.deepcopy(template)

    def deep_merge(target, source):
        for key, value in source.items():

            # Если оба значения являются словарями —
            # продолжаем рекурсивно
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                deep_merge(target[key], value)

            # Иначе заменяем значение шаблона
            else:
                target[key] = value

    # Накладываем результат модели
    deep_merge(result, model_result)

    # Сохраняем итоговый JSON
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            result,
            file,
            ensure_ascii=False,
            indent=4
        )

    return result


def main():
    print("Qwen Hotel Query Parser")
    print("=======================\n")

    while True:

        user_query = input("Запрос: ")

        if user_query.lower() == "exit":
            break
        if ''.join(user_query.split()) == '':
            print("Введите хоть что-то в запрос")
        else:
            try:

                raw_result = parse_query(user_query)

                print("\n--- Ответ модели ---")
                print(raw_result)

                # Проверяем, действительно ли модель вернула JSON
                parsed = json.loads(raw_result)
                result = merge_query_with_template(
                    template_path="schema.json",
                    model_result=parsed,
                    output_path="query.json"
                )

                print("\n--- JSON успешно распознан Python ---")

                print(
                    json.dumps(
                        parsed,
                        ensure_ascii=False,
                        indent=4
                    )
                )

            except json.JSONDecodeError:

                print("\nМодель вернула невалидный JSON.")

            except Exception as e:

                print("\nОшибка:")
                print(e)

            print("\n" + "=" * 60 + "\n")


if __name__=='__main__':
    main()
import json
import ollama
import time


SYSTEM_PROMPT = """
Ты — модуль анализа запросов для сервиса поиска отелей.

Твоя задача — прочитать запрос пользователя и определить,
какие характеристики отеля для него важны.

Для каждого явно выраженного требования определи
важность от 0 до 100.

100 = критически важно.
80-99 = очень важно.
60-79 = важно.
40-59 = желательно.
20-39 = слабое предпочтение.
0-19 = почти не важно.

Оценивай ТОЛЬКО те требования, которые пользователь
явно или однозначно выразил.

Не придумывай требования.

Верни ТОЛЬКО Python-подобный список кортежей:

[
    ["требование", рейтинг],
    ["требование", рейтинг]
]

Пример:

Запрос:
"Хочу бюджетный отдых у моря, но чтобы рядом была
ночная жизнь."

Ответ:
[
    ["близость к морю", 95],
    ["бюджетная цена", 90],
    ["ночная жизнь рядом", 70]
]

Никакого дополнительного текста.
"""


def parse_query(user_query):

    response = ollama.chat(
        model="qwen3:8b",

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

        think=False,

        options={
            "temperature": 0,
            "num_predict": 300
        }
    )

    return response["message"]["content"]


def main():

    print("Qwen Hotel Query Parser")
    print("=======================\n")

    while True:

        user_query = input("Запрос: ")

        if user_query.lower() == "exit":
            break

        try:

            raw_result = parse_query(user_query)

            print("\n--- RAW ---")
            print(raw_result)

            parsed = json.loads(raw_result)

            print("\n--- Результат ---")

            for requirement, rating in parsed:
                print(
                    f"{requirement}: {rating}/100"
                )

        except json.JSONDecodeError as e:

            print("\nМодель вернула невалидный JSON.")
            print("Ошибка:", e)

        except Exception as e:

            print("\nОшибка:")
            print(e)

        print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
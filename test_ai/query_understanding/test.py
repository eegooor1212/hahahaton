import json
import ollama
import time
import copy


SYSTEM_PROMPT = """
Ты — модуль понимания запросов для сервиса поиска отелей.

Твоя задача:
преобразовать естественный язык пользователя в структурированный JSON.

Никогда не придумывай значения, которых нет в запросе.

Верни только те параметры, которые пользователь
упомянул в запросе.

Не возвращай параметры со значением null.

Для каждого найденного параметра верни value и weight.

Например:

Запрос:
"Хочу недорогой отдых в горах, чтобы рядом были
хорошие пешие маршруты"

Ответ:

{
    "budget": {
        "level": {
            "value": "budget",
            "weight": 90
        }
    },
    "landscape": {
        "value": "mountains",
        "weight": 90
    },
    "preferences": {
        "hiking": {
            "value": true,
            "weight": 85
        }
    }
}
"""


def parse_query(user_query):

    start = time.time()

    response = ollama.chat(
        model="qwen3:1.7b",
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
            "num_predict": 2000
        }
    )

    elapsed = time.time() - start

    print(f"\nВремя: {elapsed:.2f} сек")
    print(f"Сгенерировано токенов: {response.get('eval_count')}")
    print(f"Скорость: {response.get('eval_count', 0) / elapsed:.2f} ток/сек")
    print(f"Причина остановки: {response.get('done_reason')}")

    return response["message"]["content"]

    return response["message"]["content"]

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


if __name__ == "__main__":
    main()
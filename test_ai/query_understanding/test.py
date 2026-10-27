import json
import ollama
import time
import copy


SYSTEM_PROMPT = """
Ты — модуль понимания запросов для сервиса поиска отелей.

Твоя задача:
преобразовать естественный язык пользователя в структурированный JSON.

Никогда не придумывай значения, которых нет в запросе. добавляй поля ТОЛЬКО если они указаны в запросе явно

Шаблон:
{
    "destination": {
        "region": {
            "value": null,
            "weight": 0
        },
        "country": {
            "value": null,
            "weight": 0
        },
        "city": {
            "value": null,
            "weight": 0
        },
        "area": {
            "value": null,
            "weight": 0
        }
    },

    "dates": {
        "start": {
            "value": null,
            "weight": 0
        },
        "end": {
            "value": null,
            "weight": 0
        },
        "flexible": {
            "value": null,
            "weight": 0
        },
        "duration_days": {
            "value": null,
            "weight": 0
        }
    },

    "budget": {
        "max_per_night": {
            "value": null,
            "weight": 0
        },
        "currency": {
            "value": null,
            "weight": 0
        },
        "level": {
            "value": null,
            "weight": 0
        }
    },

    "travelers": {
        "adults": {
            "value": null,
            "weight": 0
        },
        "children": {
            "value": null,
            "weight": 0
        },
        "children_ages": {
            "value": null,
            "weight": 0
        }
    },

    "hotel_preferences": {

        "hotel_rating": {
            "value": null,
            "weight": 0
        },

        "room_size": {
            "value": null,
            "weight": 0
        },

        "breakfast": {
            "value": null,
            "weight": 0
        },

        "pool": {
            "value": null,
            "weight": 0
        },

        "parking": {
            "value": null,
            "weight": 0
        },

        "air_conditioning": {
            "value": null,
            "weight": 0
        },

        "kitchen": {
            "value": null,
            "weight": 0
        },

        "balcony": {
            "value": null,
            "weight": 0
        },

        "terrace": {
            "value": null,
            "weight": 0
        },

        "pet_friendly": {
            "value": null,
            "weight": 0
        },

        "adults_only": {
            "value": null,
            "weight": 0
        }
    },
    "trip_type": {
            "value": null,
            "weight": 0
        },
    
        "landscape": {
            "value": null,
            "weight": 0
        },
    
        "view": {
            "type": {
                "value": null,
                "weight": 0
            },
            "quality": {
                "value": null,
                "weight": 0
            },
            "from_room": {
                "value": null,
                "weight": 0
            }
        },
    
        "preferences": {
    
            "near_sea": {
                "value": null,
                "weight": 0
            },
    
            "beach": {
                "value": null,
                "weight": 0
            },
    
            "mountains": {
                "value": null,
                "weight": 0
            },
    
            "nature": {
                "value": null,
                "weight": 0
            },
    
            "skiing": {
                "value": null,
                "weight": 0
            },
    
            "hiking": {
                "value": null,
                "weight": 0
            },
    
            "cycling": {
                "value": null,
                "weight": 0
            },
    
            "water_activities": {
                "value": null,
                "weight": 0
            },
    
            "spa": {
                "value": null,
                "weight": 0
            },
    
            "wellness": {
                "value": null,
                "weight": 0
            },
    
            "quiet": {
                "value": null,
                "weight": 0
            },
    
            "nightlife": {
                "value": null,
                "weight": 0
            },
    
            "walkability": {
                "value": null,
                "weight": 0
            },
    
            "restaurants_nearby": {
                "value": null,
                "weight": 0
            },
    
            "bars_nearby": {
                "value": null,
                "weight": 0
            },
    
            "attractions_nearby": {
                "value": null,
                "weight": 0
            },
    
            "old_town_nearby": {
                "value": null,
                "weight": 0
            },
    
            "city_center_nearby": {
                "value": null,
                "weight": 0
            },
    
            "public_transport_nearby": {
                "value": null,
                "weight": 0
            },
    
            "family_friendly": {
                "value": null,
                "weight": 0
            },
    
            "romantic": {
                "value": null,
                "weight": 0
            },
    
            "luxury": {
                "value": null,
                "weight": 0
            },
    
            "authentic_local_experience": {
                "value": null,
                "weight": 0
            }
        },
}

заполни его данными, учитывая что value это значение конкретного поля из запроса вноси его на английском языке, если поля в запросе нет, но оставляй его без изменения. weight отражает важность каждого поля запроса, его также заполнять только если поле есть в запросе. weight идёт по 100-бальной шкале где 0-20 низкая важность поля, 21-40 ниже среднего важность поля, 41-60 средняя важность поля, 61-80 выше среднего важность поля 81-100 очень важное поле

Верни только те параметры, которые пользователь
упомянул в запросе. Не додумывай за пользователя значения, заполняй поля ТОЛЬКО ЕСЛИ ОНИ УКАЗАНЫ ЯВНО.

Не возвращай параметры со значением null.

В JSON который ты генерируешь оставляй ТОЛЬКО те поля которые есть в запросе пользователя НИКАКИХ дургих полей писать нельзя, если во всём json данные остаются null, возвращай просто пустой json
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


if __name__ == "__main__":
    main()
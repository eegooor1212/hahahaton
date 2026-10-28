
import json


# Какой параметр запроса с каким параметром отеля сравниваем
SEARCH_FIELDS = [
    ("destination.region", "destination.region"),
    ("destination.country", "destination.country"),
    ("destination.city", "destination.city"),
    ("destination.area", "destination.area"),

    ("budget.max_per_night", "budget.max_per_night"),
    ("budget.level", "budget.level"),

    ("travelers.adults", "travelers.adults"),
    ("travelers.children", "travelers.children"),

    ("hotel_preferences.hotel_rating", "hotel_preferences.hotel_rating"),
    ("hotel_preferences.room_size", "hotel_preferences.room_size"),
    ("hotel_preferences.breakfast", "hotel_preferences.breakfast"),
    ("hotel_preferences.pool", "hotel_preferences.pool"),
    ("hotel_preferences.parking", "hotel_preferences.parking"),
    ("hotel_preferences.air_conditioning", "hotel_preferences.air_conditioning"),
    ("hotel_preferences.kitchen", "hotel_preferences.kitchen"),
    ("hotel_preferences.balcony", "hotel_preferences.balcony"),
    ("hotel_preferences.terrace", "hotel_preferences.terrace"),
    ("hotel_preferences.pet_friendly", "hotel_preferences.pet_friendly"),
    ("hotel_preferences.adults_only", "hotel_preferences.adults_only"),
    ("hotel_preferences.room_type", "hotel_preferences.room_type"),

    ("trip_type", "trip_type"),
    ("landscape", "landscape"),

    ("view.type", "view.type"),
    ("view.quality", "view.quality"),
    ("view.from_room", "view.from_room"),
]


def get_nested(data, path):
    """Получает значение из вложенного JSON по пути."""
    current = data

    for key in path.split("."):
        if not isinstance(current, dict) or key not in current:
            return None

        current = current[key]

    # В запросе и отеле поле обычно имеет вид {"value": ..., "weight": ...}
    if isinstance(current, dict) and "value" in current:
        return current["value"]

    return current


def normalize(value):
    """Нормализует строки перед сравнением."""
    if isinstance(value, str):
        return value.strip().casefold()

    return value


def values_match(user_value, hotel_value, field):
    """Проверяет, соответствует ли отель требованию пользователя."""

    if user_value is None or hotel_value is None:
        return False

    # bool нужно проверять ДО чисел, поскольку bool является подклассом int
    if isinstance(user_value, bool):
        return (
            isinstance(hotel_value, bool)
            and hotel_value == user_value
        )

    # Цена отеля должна быть не выше бюджета пользователя
    if field == "budget.max_per_night":
        try:
            return float(hotel_value) <= float(user_value)
        except (TypeError, ValueError):
            return False

    # Рейтинг отеля должен быть не ниже требуемого
    if field == "hotel_preferences.hotel_rating":
        try:
            return float(hotel_value) >= float(user_value)
        except (TypeError, ValueError):
            return False

    # Площадь номера: трактуем указанное значение как минимальное
    if field == "hotel_preferences.room_size":
        try:
            return float(hotel_value) >= float(user_value)
        except (TypeError, ValueError):
            return False

    # Остальные числовые поля сравниваем точно
    if isinstance(user_value, (int, float)):
        if isinstance(hotel_value, bool):
            return False

        try:
            return float(hotel_value) == float(user_value)
        except (TypeError, ValueError):
            return False

    # Строки
    if isinstance(user_value, str) and isinstance(hotel_value, str):
        return normalize(user_value) == normalize(hotel_value)

    return user_value == hotel_value


def score_hotel(hotel, query):
    """
    Рассчитывает соответствие одного отеля запросу.
    Возвращает оценку от 0 до 100.
    Неизвестные характеристики не считаются ни совпадением,
    ни несовпадением.
    """

    total_weight = 0
    matched_weight = 0
    matched_fields = []
    mismatched_fields = []
    unknown_fields = []
    for query_path, hotel_path in SEARCH_FIELDS:
        requirement = get_nested(query, query_path)

        # Получаем значение и вес из исходного объекта запроса
        requirement_obj = query
        for key in query_path.split("."):
            if not isinstance(requirement_obj, dict):
                requirement_obj = None
                break
            requirement_obj = requirement_obj.get(key)

        if not isinstance(requirement_obj, dict):
            continue

        user_value = requirement_obj.get("value")
        weight = requirement_obj.get("weight", 0)

        if user_value is None:
            continue

        if (
            not isinstance(weight, (int, float))
            or isinstance(weight, bool)
            or not 0 < weight <= 100
        ):
            continue

        # Получаем фактическое значение характеристики отеля
        hotel_value = get_nested(hotel, hotel_path)

        # Если значение неизвестно, не штрафуем отель,
        # но и не засчитываем совпадение
        if hotel_value is None:
            unknown_fields.append(query_path)
            continue

        total_weight += weight

        if values_match(user_value, hotel_value, query_path):
            matched_weight += weight
            matched_fields.append(query_path)
        else:
            mismatched_fields.append(query_path)

    if total_weight == 0:
        score = 0
    else:
        score = round(matched_weight / total_weight * 100, 2)

    return {
        "score": score,
        "matched_fields": matched_fields,
        "mismatched_fields": mismatched_fields,
        "unknown_fields": unknown_fields,
        "matched_weight": matched_weight,
        "total_weight": total_weight
    }


def search_hotels(query, hotels_file="hotel_test.json", limit=5):
    """Загружает отели, оценивает их и сортирует по score."""

    with open(hotels_file, "r", encoding="utf-8") as file:
        hotels = json.load(file)

    if not isinstance(hotels, list):
        raise ValueError(
            "Файл с отелями должен содержать JSON-массив объектов."
        )

    results = []

    for hotel in hotels:
        evaluation = score_hotel(hotel, query)

        results.append({
            "hotel": hotel,
            **evaluation
        })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results[:limit]


# Оставь здесь свой существующий блок main без изменений/
if __name__=='__main__':
    with open("query_test.json", "r", encoding="utf-8") as f:
        query = json.load(f)

    results = search_hotels(query)

    print(results[0]['score'])



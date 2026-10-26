import json


def load_hotels(path="hotels.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def search_hotels(query, hotels):
    """
    query — JSON, который вернула Qwen.
    hotels — список отелей.

    Возвращает подходящие отели.
    """

    results = []

    destination = query.get("destination", {})
    budget = query.get("budget", {})
    preferences = query.get("preferences", {})

    country = destination.get("country")
    city = destination.get("city")
    region = destination.get("region")

    max_price = budget.get("max_per_night")
    budget_level = budget.get("level")

    for hotel in hotels:

        score = 0
        reasons = []

        # -------------------------
        # 1. Место
        # -------------------------

        if country:
            if hotel["country"].lower() != country.lower():
                continue

            score += 10
            reasons.append("подходит страна")

        if city:
            if hotel["city"].lower() != city.lower():
                continue

            score += 20
            reasons.append("подходит город")

        if region:
            if hotel["region"].lower() == region.lower():
                score += 10
                reasons.append("подходит регион")

        # -------------------------
        # 2. Бюджет
        # -------------------------

        if max_price is not None:

            if hotel["price_per_night"] > max_price:
                continue

            score += 15
            reasons.append("подходит по бюджету")

        elif budget_level == "budget":

            if hotel["price_per_night"] <= 100:
                score += 10
                reasons.append("бюджетный вариант")

        # -------------------------
        # 3. Море
        # -------------------------

        if preferences.get("near_sea"):

            if not hotel["near_sea"]:
                continue

            score += 20
            reasons.append("рядом с морем")

        # -------------------------
        # 4. Вид на море
        # -------------------------

        if preferences.get("sea_view"):

            if not hotel["sea_view"]:
                continue

            score += 15
            reasons.append("есть вид на море")

        # -------------------------
        # 5. Рестораны
        # -------------------------

        if preferences.get("restaurants_nearby"):

            if hotel["restaurants_nearby"]:
                score += 8
                reasons.append("рядом рестораны")

        # -------------------------
        # 6. Старый город
        # -------------------------

        if preferences.get("old_town_nearby"):

            if hotel["walk_to_old_town_min"] <= 15:
                score += 10
                reasons.append("старый город рядом")

        # -------------------------
        # 7. Ночная жизнь
        # -------------------------

        if preferences.get("nightlife"):

            if hotel["nightlife"] in ["medium", "high"]:
                score += 8
                reasons.append("есть ночная жизнь")

        # -------------------------
        # Добавляем результат
        # -------------------------

        results.append({
            "hotel": hotel,
            "score": score,
            "reasons": reasons
        })

    # Сначала лучшие совпадения
    results.sort(
        key=lambda x: (
            x["score"],
            x["hotel"]["rating"]
        ),
        reverse=True
    )

    return results
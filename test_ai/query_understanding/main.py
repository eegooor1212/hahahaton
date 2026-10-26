from search import load_hotels, search_hotels


query = {
    "destination": {
        "country": None,
        "city": None,
        "region": "Europe"
    },

    "budget": {
        "max_per_night": None,
        "currency": "EUR",
        "level": "budget"
    },

    "preferences": {
        "near_sea": True,
        "sea_view": False,
        "quiet": None,
        "nightlife": True,
        "walkability": "high",
        "restaurants_nearby": True,
        "attractions_nearby": True,
        "old_town_nearby": True
    }
}


hotels = load_hotels()

results = search_hotels(query, hotels)


for result in results:

    hotel = result["hotel"]

    print("=" * 50)

    print(
        f"{hotel['name']} — "
        f"{hotel['city']}, {hotel['country']}"
    )

    print(
        f"Цена: "
        f"{hotel['price_per_night']} "
        f"{hotel['currency']}/ночь"
    )

    print(
        f"Рейтинг: {hotel['rating']}"
    )

    print(
        f"Score: {result['score']}"
    )

    print(
        "Почему подходит: "
        + ", ".join(result["reasons"])
    )
"""
Misc API views
"""
import json
import random
import typing
import requests
from django import http
import googlesearch
from googlesearch.exceptions import GoogleSearchException
from api.utils import creditcard_generator

cc_generator = creditcard_generator.CreditCardGenerator()

# /api/v3/misc/fml
def fml(_request: http.HttpRequest) -> http.HttpResponse:
    """
    Random Fuck My Life story
    """
    with open("./data/fml.json", "r", encoding="utf8") as file:
        fml_list: typing.List = json.load(file)

    return http.JsonResponse({"status": 200, "fml": random.choice(fml_list)})


# /api/v3/misc/riddle
def riddle(_request: http.HttpRequest) -> http.HttpResponse:
    """
    Random riddle
    """
    with open("./data/riddles.json", "r", encoding="utf8") as file:
        riddles_list: typing.List = json.load(file)

    return http.JsonResponse({"status": 200, "riddle": random.choice(riddles_list)})


# /api/v3/misc/joke
def joke(_request: http.HttpRequest) -> http.HttpResponse:
    """
    Random joke
    """
    with open("./data/jokes.json", "r", encoding="utf8") as file:
        jokes_list: typing.List = json.load(file)

    return http.JsonResponse({"status": 200, "joke": random.choice(jokes_list)})


# /api/v3/misc/wyr
def wyr(_request: http.HttpRequest) -> http.HttpResponse:
    """
    Random Would You Rather question
    """
    with open("./data/questions.json", "r", encoding="utf8") as file:
        questions_list: typing.List = json.load(file)

    return http.JsonResponse({"status": 200, "question": random.choice(questions_list)})


# /api/v3/misc/topic
def topic(_request: http.HttpRequest) -> http.HttpResponse:
    """
    Random conversation topic
    """
    with open("./data/topics.json", "r", encoding="utf8") as file:
        topics_list: typing.List = json.load(file)

    return http.JsonResponse({"status": 200, "topic": random.choice(topics_list)})


# /api/v3/misc/breaking-bad-quote
def breaking_bad_quote(_request: http.HttpRequest) -> http.HttpResponse:
    """
    Random Breaking Bad quote
    """
    with open("./data/breakingbadquotes.json", "r", encoding="utf8") as file:
        quotes_list: typing.List = json.load(file)

    return http.JsonResponse({"status": 200, **random.choice(quotes_list)})


# /api/v3/misc/game-of-thrones-quote
def game_of_thrones_quote(_request: http.HttpRequest) -> http.HttpResponse:
    """
    Random Game of Thrones quote
    """
    with open("./data/gameofthronesquotes.json", "r", encoding="utf8") as file:
        quotes_list: typing.List = json.load(file)

    return http.JsonResponse({"status": 200, **random.choice(quotes_list)})


# /api/v3/misc/lucifer-quote
def lucifer_quote(_request: http.HttpRequest) -> http.HttpResponse:
    """
    Random Lucifer quote
    """
    with open("./data/luciferquotes.json", "r", encoding="utf8") as file:
        quotes_list: typing.List = json.load(file)

    return http.JsonResponse({"status": 200, **random.choice(quotes_list)})


# /api/v3/misc/stranger-things-quote
def stranger_things_quote(_request: http.HttpRequest) -> http.HttpResponse:
    """
    Random Lucifer quote
    """
    with open("./data/strangerthingsquotes.json", "r", encoding="utf8") as file:
        quotes_list: typing.List = json.load(file)

    return http.JsonResponse({"status": 200, **random.choice(quotes_list)})


# /api/v3/misc/search
def search(request: http.HttpRequest) -> http.HttpResponse:
    """
    Google search
    """
    try:
        results = googlesearch.search(
            request.GET.get("query", ""), num_results=5, advanced=True
        )
    except GoogleSearchException:
        return http.JsonResponse(
            {
                "status": 500,
                "message": "An error occurred while fetching the results.",
            },
            status=500,
        )

    raw_results: typing.List[typing.Dict] = []

    for result in results:
        raw_results.append(
            {
                "url": result.url,
                "title": result.title,
                "description": result.description,
            }
        )

    return http.JsonResponse({"status": 200, "results": list(raw_results)})


# /api/v3/misc/ccgen
def ccgen(request: http.HttpRequest) -> http.HttpResponse:
    """
    Credit card generator
    """
    valid_types = [
        "mastercard",
        "visa16",
        "visa13",
        "amex",
        "discover",
        "diners",
        "jcb",
    ]
    credit_card_type = request.GET.get("type")
    if credit_card_type not in valid_types:
        return http.JsonResponse(
            {
                "status": 400,
                "message": "Invalid type.",
            },
            status=400,
        )

    credit_card: typing.Dict[str, str] = {}

    match credit_card_type:
        case "mastercard":
            credit_card = cc_generator.credit_card_number(
                creditcard_generator.mastercard_prefix_list, 16, "mastercard"
            )
        case "visa16":
            credit_card = cc_generator.credit_card_number(
                creditcard_generator.visa_prefix_list, 16, "visa"
            )
        case "visa13":
            credit_card = cc_generator.credit_card_number(
                creditcard_generator.visa_prefix_list, 13, "visa"
            )
        case "amex":
            credit_card = cc_generator.credit_card_number(
                creditcard_generator.amex_prefix_list, 15, "amex"
            )
        case "discover":
            credit_card = cc_generator.credit_card_number(
                creditcard_generator.discover_prefix_list, 16, "discover"
            )
        case "diners":
            credit_card = cc_generator.credit_card_number(
                creditcard_generator.diners_prefix_list, 14, "diners"
            )
        case "jcb":
            credit_card = cc_generator.credit_card_number(
                creditcard_generator.jcb_prefix_list, 16, "jcb"
            )

    return http.JsonResponse({"status": 200, **credit_card})


reddit_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Opera GX";v="93", "Not\\A)Brand";v="99", "Chromium";v="93"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

# /api/v3/misc/ccgen
def meme(_request: http.HttpRequest) -> http.HttpResponse:
    """
    Meme generator
    """

    fetching_error = http.JsonResponse(
        {
            "status": 500,
            "message": "An error occurred while fetching the results.",
        },
        status=500,
    )

    response = requests.get(
        "https://www.reddit.com/r/memes/hot.json",
        headers=reddit_headers,
        timeout=10,
    )

    if response.status_code != 200:
        return fetching_error

    try:
        memes = response.json()["data"]["children"]
    except KeyError:
        return fetching_error

    try:
        memes = [meme["data"] for meme in memes if meme["data"]["url"].endswith(".jpg")]
    except (KeyError, AttributeError):
        return fetching_error

    if not memes:
        return fetching_error

    raw_meme_data = random.choice(memes)

    meme_data = {
        "title": raw_meme_data["title"],
        "imagelink": raw_meme_data["url"],
        "upvotes": raw_meme_data["ups"],
        "permalink": "https://reddit.com" + raw_meme_data["permalink"],
        "subreddit": raw_meme_data["subreddit_name_prefixed"],
        "author": raw_meme_data["author"],
    }

    return http.JsonResponse({"status": 200, "meme": meme_data})

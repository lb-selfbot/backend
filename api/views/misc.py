"""
Misc API views
"""
import json
import random
import typing
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
                creditcard_generator.mastercard_prefix_list, 16
            )
        case "visa16":
            credit_card = cc_generator.credit_card_number(
                creditcard_generator.visa_prefix_list, 16
            )
        case "visa13":
            credit_card = cc_generator.credit_card_number(
                creditcard_generator.visa_prefix_list, 13
            )
        case "amex":
            credit_card = cc_generator.credit_card_number(
                creditcard_generator.amex_prefix_list, 15
            )
        case "discover":
            credit_card = cc_generator.credit_card_number(
                creditcard_generator.discover_prefix_list, 16
            )
        case "diners":
            credit_card = cc_generator.credit_card_number(
                creditcard_generator.diners_prefix_list, 14
            )
        case "jcb":
            credit_card = cc_generator.credit_card_number(
                creditcard_generator.jcb_prefix_list, 16
            )

    return http.JsonResponse({"status": 200, **credit_card})

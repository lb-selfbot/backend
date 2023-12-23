"""
Image generation API views
"""

from django import http
from django_ratelimit.decorators import ratelimit

from imagegeneration import imagegeneration

from ..utils import misc

from ..models import Image

alexflipnote = imagegeneration.AlexFlipNote()


def save_image(image: bytes, format: str) -> Image:
    """
    Save an image to the database
    """

    name = misc.random_string(16)

    return Image.objects.create(
        image=image, format=format, name=f"{name}.{format}".lower()
    )


# /api/v3/imagegen/achievement
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def achievement(request: http.HttpRequest) -> http.HttpResponse:
    """
    Minecraft achievement image
    """
    try:
        image = alexflipnote.create_achievement(request.GET.get("text", ""))
        return http.HttpResponse(misc.image_to_bytes(image), content_type="image/png")
    except Exception as e:
        return http.JsonResponse({"error": "An error has occurred: " + str(e)})


# /api/v3/imagegen/amiajoke
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def amiajoke(request: http.HttpRequest) -> http.HttpResponse:
    """
    Am I a joke to you?
    """
    try:
        image = alexflipnote.am_i_a_joke(request.GET.get("url", ""))
        return http.HttpResponse(misc.image_to_bytes(image), content_type="image/png")
    except Exception:
        return http.JsonResponse({"error": "An error has occurred"})


# /api/v3/imagegen/bad
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def bad(request: http.HttpRequest) -> http.HttpResponse:
    """
    Bad
    """
    try:
        image = alexflipnote.bad(request.GET.get("url", ""))
        return http.HttpResponse(misc.image_to_bytes(image), content_type="image/png")
    except Exception:
        return http.JsonResponse({"error": "An error has occurred"})


# /api/v3/imagegen/calling
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def calling(request: http.HttpRequest) -> http.HttpResponse:
    """
    Calling
    """
    try:
        image = alexflipnote.calling(request.GET.get("text", ""))
        return http.HttpResponse(misc.image_to_bytes(image), content_type="image/png")
    except Exception:
        return http.JsonResponse({"error": "An error has occurred"})


# /api/v3/imagegen/captcha
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def captcha(request: http.HttpRequest) -> http.HttpResponse:
    """
    Captcha
    """
    try:
        image = alexflipnote.captcha(request.GET.get("text", ""))
        return http.HttpResponse(misc.image_to_bytes(image), content_type="image/png")
    except Exception:
        return http.JsonResponse({"error": "An error has occurred"})


# /api/v3/imagegen/didyoumean
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def didyoumean(request: http.HttpRequest) -> http.HttpResponse:
    """
    Did you mean?
    """
    try:
        image = alexflipnote.did_you_mean(
            request.GET.get("top", ""), request.GET.get("bottom", "")
        )
        return http.HttpResponse(misc.image_to_bytes(image), content_type="image/png")
    except Exception:
        return http.JsonResponse({"error": "An error has occurred"})


# /api/v3/imagegen/drake
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def drake(request: http.HttpRequest) -> http.HttpResponse:
    """
    Drake meme
    """
    try:
        image = alexflipnote.drake(
            request.GET.get("top", ""),
            request.GET.get("bottom", ""),
            request.GET.get("ayano", "").lower() == "true",
        )
        return http.HttpResponse(misc.image_to_bytes(image), content_type="image/png")
    except Exception:
        return http.JsonResponse({"error": "An error has occurred"})


# /api/v3/imagegen/facts
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def facts(request: http.HttpRequest) -> http.HttpResponse:
    """
    Facts
    """
    try:
        image = alexflipnote.facts(request.GET.get("text", ""))
        return http.HttpResponse(misc.image_to_bytes(image), content_type="image/png")
    except Exception:
        return http.JsonResponse({"error": "An error has occurred"})


# /api/v3/imagegen/filter
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def filter_image(request: http.HttpRequest) -> http.HttpResponse:
    """
    Filter
    """
    try:
        image = alexflipnote.filter(
            request.GET.get("url", ""), request.GET.get("filter", "")
        )
        return http.HttpResponse(misc.image_to_bytes(image), content_type="image/png")
    except Exception:
        return http.JsonResponse({"error": "An error has occurred"})


# /api/v3/imagegen/floor
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def floor(request: http.HttpRequest) -> http.HttpResponse:
    """
    Floor
    """
    try:
        image = alexflipnote.floor(
            request.GET.get("text", ""), request.GET.get("url", "")
        )
        return http.HttpResponse(misc.image_to_bytes(image), content_type="image/png")
    except Exception:
        return http.JsonResponse({"error": "An error has occurred"})


# /api/v3/imagegen/jokeoverhead
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def jokeoverhead(request: http.HttpRequest) -> http.HttpResponse:
    """
    Joke overhead
    """
    try:
        image = alexflipnote.joke_over_head(request.GET.get("url", ""))
        return http.HttpResponse(misc.image_to_bytes(image), content_type="image/png")
    except Exception:
        return http.JsonResponse({"error": "An error has occurred"})


# /api/v3/imagegen/trash
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def trash(request: http.HttpRequest) -> http.HttpResponse:
    """
    Trash
    """
    try:
        image = alexflipnote.trash(
            request.GET.get("url", ""), request.GET.get("url_trash", "")
        )
        return http.HttpResponse(misc.image_to_bytes(image), content_type="image/png")
    except Exception:
        return http.JsonResponse({"error": "An error has occurred"})


# /api/v3/imagegen/pornhub
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def pornhub(request: http.HttpRequest) -> http.HttpResponse:
    """
    Pornhub
    """
    try:
        image = alexflipnote.porn_hub(
            request.GET.get("text1", ""), request.GET.get("text2", "")
        )
        return http.HttpResponse(misc.image_to_bytes(image), content_type="image/png")
    except Exception:
        return http.JsonResponse({"error": "An error has occurred"})


# /api/v3/imagegen/salty
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def salty(request: http.HttpRequest) -> http.HttpResponse:
    """
    Salty
    """
    try:
        image = alexflipnote.salty(request.GET.get("url", ""))
        return http.HttpResponse(misc.image_to_bytes(image), content_type="image/png")
    except Exception:
        return http.JsonResponse({"error": "An error has occurred"})


# /api/v3/imagegen/scroll
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def scroll(request: http.HttpRequest) -> http.HttpResponse:
    """
    Scroll
    """
    try:
        image = alexflipnote.scroll(request.GET.get("text", ""))
        return http.HttpResponse(misc.image_to_bytes(image), content_type="image/png")
    except Exception:
        return http.JsonResponse({"error": "An error has occurred"})


# /api/v3/imagegen/shame
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def shame(request: http.HttpRequest) -> http.HttpResponse:
    """
    Shame
    """
    try:
        image = alexflipnote.shame(request.GET.get("url", ""))
        return http.HttpResponse(misc.image_to_bytes(image), content_type="image/png")
    except Exception:
        return http.JsonResponse({"error": "An error has occurred"})


# /api/v3/imagegen/ship
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def ship(request: http.HttpRequest) -> http.HttpResponse:
    """
    Ship
    """
    try:
        image = alexflipnote.ship(
            request.GET.get("url1", ""), request.GET.get("url2", "")
        )
        return http.HttpResponse(misc.image_to_bytes(image), content_type="image/png")
    except Exception:
        return http.JsonResponse({"error": "An error has occurred"})


# /api/v3/imagegen/what
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def what(request: http.HttpRequest) -> http.HttpResponse:
    """
    What
    """
    try:
        image = alexflipnote.what(request.GET.get("url", ""))
        return http.HttpResponse(misc.image_to_bytes(image), content_type="image/png")
    except Exception:
        return http.JsonResponse({"error": "An error has occurred"})


# /api/v3/imagegen/speechbubble
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def speechbubble(request: http.HttpRequest) -> http.HttpResponse:
    """
    Speechbubble
    """
    try:
        format = request.GET.get("format", "png").lower()
        image, format = alexflipnote.speechbubble(
            request.GET.get("url", ""), format == "gif"
        )

        image = save_image(image, format)

        return http.HttpResponseRedirect(f"/api/v3/imagegen/view/{image.name}")
    except Exception as e:
        return http.JsonResponse({"error": f"An error has occurred: {e}"})


# /api/v3/imagegen/quote
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def quote(request: http.HttpRequest) -> http.HttpResponse:
    """
    Quote
    """
    try:
        author = request.GET.get("author", "")
        text = request.GET.get("text", "")
        background = request.GET.get("background", "")

        image = alexflipnote.quote(author, text, background)

        return http.HttpResponse(misc.image_to_bytes(image), content_type="image/png")
    except Exception as e:
        return http.JsonResponse({"error": "An error has occurred: " + str(e)})


# /api/v3/imagegen/discordquote
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def discordquote(request: http.HttpRequest) -> http.HttpResponse:
    """
    Quote
    """
    try:
        author = request.GET.get("author", "")
        author_url = request.GET.get("author_url", "")
        author_color = request.GET.get("author_color", "")
        text = request.GET.get("text", "")
        timestamp = request.GET.get("timestamp", "")

        image = alexflipnote.discordquote(
            author, author_url, author_color, text, timestamp
        )

        return http.HttpResponse(misc.image_to_bytes(image), content_type="image/png")
    except Exception as e:
        return http.JsonResponse({"error": "An error has occurred: " + str(e)})


# /api/v3/imagegen/view/image
@ratelimit(key="ip", rate="5/s", method=ratelimit.ALL, block=True)
@ratelimit(group="global", key="ip", rate="15/s", method=ratelimit.ALL, block=True)
def view_image(_request: http.HttpRequest, image: str) -> http.HttpResponse:
    """
    View image
    """
    image = Image.objects.filter(name=image).first()
    if image is None:
        return http.JsonResponse({"error": "Image not found"}, status=404)

    return http.HttpResponse(image.image, content_type="image/png")

"""
Image generation API views
"""

from django import http

from imagegeneration import imagegeneration

from ..utils import misc

from ..models import Image

alexflipnote = imagegeneration.AlexFlipNote()

def save_image(image: bytes, format: str) -> Image:
    """
    Save an image to the database
    """

    name = misc.random_string(16)

    return Image.objects.create(image=image, format=format, name=f"{name}.{format}".lower())



# /api/v3/imagegen/achievement
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
        raise e
        return http.JsonResponse({"error": "An error has occurred: " + str(e)})


# /api/v3/imagegen/view/image
def view_image(_request: http.HttpRequest, image: str) -> http.HttpResponse:
    """
    View image
    """
    image = Image.objects.filter(name=image).first()
    if image is None:
        return http.JsonResponse({"error": "Image not found"}, status=404)
    
    return http.HttpResponse(image.image, content_type="image/png")

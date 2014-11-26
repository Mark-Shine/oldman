from django.conf import settings

MEDIA_URL = getattr(settings, "MEDIA_URL", "")


def common(request):

    context = dict(
        MEDIA_URL=MEDIA_URL,
    )
    return context
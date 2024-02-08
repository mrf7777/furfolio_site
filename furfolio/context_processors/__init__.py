from django.conf import settings

def is_beta(request):
    return {"is_beta": settings.IS_BETA}

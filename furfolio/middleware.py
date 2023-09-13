import zoneinfo
from django.utils import timezone
from django.shortcuts import render

# https://stackoverflow.com/a/76585802


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tz = request.COOKIES.get("mytz")
        if tz:
            timezone.activate(zoneinfo.ZoneInfo(tz))
        else:
            timezone.activate(zoneinfo.ZoneInfo("UTC"))
        return self.get_response(request)

from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views import generic
from . import models

class Home(generic.ListView):
    model = models.Offer
    
    def get_queryset(self) -> QuerySet[Any]:
        return models.Offer.objects.all().order_by("-created date")
    
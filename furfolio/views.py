from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from . import models
from .forms import CustomUserCreationForm

class Home(generic.ListView):
    model = models.Offer
    template_name = "furfolio/home.html"
    context_object_name = "offer_list"
    
    def get_queryset(self) -> QuerySet[Any]:
        return models.Offer.objects.all().order_by("-created date")
    
class Offer(generic.DetailView):
    model = models.Offer
    context_object_name = "offer"

class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
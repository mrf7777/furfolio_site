from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name="offer_list"),
    path('offers/<pk>/', views.Offer.as_view(), name="offer_detail"),
    path('accounts/signup/', views.SignUp.as_view(), name="signup"),
]

from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name="home"),
    path('offers/create/', views.CreateOffer.as_view(), name="create_offer"),
    path('offers/<pk>/', views.Offer.as_view(), name="offer_detail"),
    path('accounts/signup/', views.SignUp.as_view(), name="signup"),
]

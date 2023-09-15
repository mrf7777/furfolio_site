from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from furfolio import forms as furfolio_forms

urlpatterns = [
    path('', views.OfferList.as_view(), name="offer_list"),
    # offers
    path('offers/create/', views.CreateOffer.as_view(), name="create_offer"),
    path('offers/<pk>/update/', views.UpdateOffer.as_view(), name="update_offer"),
    path('offers/<pk>/delete/', views.DeleteOffer.as_view(), name="delete_offer"),
    path('offers/<pk>/', views.Offer.as_view(), name="offer_detail"),
    # users
    path('users/<username>/', views.User.as_view(), name="user"),
    path('users/', views.UserList.as_view(), name="user-list"),
    # accounts
    path('accounts/signup/', views.SignUp.as_view(), name="signup"),
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(
            authentication_form=furfolio_forms.LoginForm
        ),
        name="login"
    ),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name="logout"),
]

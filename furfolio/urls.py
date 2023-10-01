from django.urls import path, include
from .views import views
from .views import pages
from django.contrib.auth import views as auth_views
from furfolio import forms as furfolio_forms

urlpatterns = [
    path('', views.Home.as_view(), name="home"),
    # offers
    path('offers/', views.OfferList.as_view(), name="offer_list"),
    path('offers/create/', views.CreateOffer.as_view(), name="create_offer"),
    path('offers/<pk>/update/', views.UpdateOffer.as_view(), name="update_offer"),
    path('offers/<pk>/delete/', views.DeleteOffer.as_view(), name="delete_offer"),
    path('offers/<pk>/', views.Offer.as_view(), name="offer_detail"),
    # users
    path('users/<username>/', views.User.as_view(), name="user"),
    path('users/<username>/update/',
         views.UpdateUser.as_view(), name="update_user"),
    path('users/', views.UserList.as_view(), name="user_list"),
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
    # dashboards
    path('dashboard/', views.DashboardRedirector.as_view(), name="dashboard"),
    path('dashboard/creator/', views.CreatorDashboard.as_view(),
         name="creator_dashboard"),
    path('dashboard/buyer/', views.BuyerDashboard.as_view(), name="buyer_dashboard"),
    # commissions
    path('commissions/<pk>', views.Commission.as_view(), name="commission_detail"),
    path('commissions/create/', views.CreateCommission.as_view(),
         name="create_commission"),
    path('commissions/<pk>/update/',
         views.UpdateCommission.as_view(), name="update_commission"),
    path('commissions/<pk>/update/status/',
         views.UpdateCommissionStatus.as_view(), name="update_commission_status"),
    # commission chat
    path('commissions/<pk>/chat',
         views.CommissionChat.as_view(), name="commission_chat"),
    # static pages
    path('legal/terms-of-service',
         pages.TermsOfService.as_view(), name="terms_of_service"),
    path('legal/privacy-policy',
         pages.PrivacyPolicy.as_view(), name="privacy_policy"),
]

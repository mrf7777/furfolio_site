from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from .views import views
from .views import pages
from .sitemaps import sitemaps
from django.contrib.auth import views as auth_views
from furfolio import forms as furfolio_forms

urlpatterns = [
    # sitemaps
    path('sitemap.xml', sitemap, {"sitemaps": sitemaps},
         name="django.contrib.sitemaps.views.sitemap"),
    # home
    path('', views.Home.as_view(), name="home"),
    # offers
    path('offers/', views.OfferList.as_view(), name="offer_list"),
    path('offers/create/', views.CreateOffer.as_view(), name="create_offer"),
    path(
        'offers/<pk>/update/',
        views.UpdateOffer.as_view(),
        name="update_offer"),
    path(
        'offers/<pk>/delete/',
        views.DeleteOffer.as_view(),
        name="delete_offer"),
    path('offers/<pk>/', views.Offer.as_view(), name="offer_detail"),
    # users
    path('users/<username>/', views.User.as_view(), name="user"),
    path('users/<username>/update/',
         views.UpdateUser.as_view(), name="update_user"),
    path('users/', views.UserList.as_view(), name="user_list"),
    # user following
    path('users/<username>/follow/',
         views.MakeUserFollowUser.as_view(), name="follow_user"),
    path('users/<username>/unfollow/',
         views.MakeUserUnfollowUser.as_view(), name="unfollow_user"),
    path('users/<username>/followed/',
         views.FollowedList.as_view(), name="followed_list"),
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
    path('accounts/password_reset',
         auth_views.PasswordResetView.as_view(), name="password_reset"),
    path('accounts/password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('accounts/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(),
         name="password_reset_complete"),
    # dashboards
    path('dashboard/', views.DashboardRedirector.as_view(), name="dashboard"),
    path('dashboard/creator/', views.CreatorDashboard.as_view(),
         name="creator_dashboard"),
    path(
        'dashboard/buyer/',
        views.BuyerDashboard.as_view(),
        name="buyer_dashboard"),
    # commissions
    path(
        'commissions/<pk>',
        views.Commission.as_view(),
        name="commission_detail"),
    path('offers/<offer_pk>/commissions/create/', views.CreateCommission.as_view(),
         name="create_commission"),
    path('commissions/<pk>/update/',
         views.UpdateCommission.as_view(), name="update_commission"),
    path('commissions/<pk>/update/status/',
         views.UpdateCommissionStatus.as_view(), name="update_commission_status"),
    path('commissions/', views.Commissions.as_view(), name="commissions"),
    # tags
    path('tags/', views.TagList.as_view(), name="tags"),
    path('tags/create/', views.CreateTag.as_view(), name="create_tag"),
    path('tags/<name>/update/', views.UpdateTag.as_view(), name="update_tag"),
    path('tags/<name>/delete/', views.DeleteTag.as_view(), name="delete_tag"),
    path('tags/<name>/', views.Tag.as_view(), name="tag_detail"),
    # commission chat
    path('commissions/<pk>/chat',
         views.CommissionChat.as_view(), name="commission_chat"),
    # static pages
    path('legal/', pages.Legal.as_view(), name="legal"),
    path('legal/terms-of-service/',
         pages.TermsOfService.as_view(), name="terms_of_service"),
    path('legal/privacy-policy/',
         pages.PrivacyPolicy.as_view(), name="privacy_policy"),
    path('legal/credit/', pages.Credit.as_view(), name="credit"),
    # help pages
    path('help/', pages.Help.as_view(), name="help"),
    path(
        'help/getting-started/',
        pages.GettingStarted.as_view(),
        name="getting_started"),
    path('help/reference/', pages.Reference.as_view(), name="reference"),
    path('help/what-is-furfolio/',
         pages.WhatIsFurfolio.as_view(), name="what_is_furfolio"),
    path('help/offers-and-commissions',
         pages.OffersAndCommissions.as_view(),
         name="offers_and_commissions"),
    path('help/commission-search/', pages.CommissionSearchHelp.as_view(),
         name="commission_search_help"),
    # error pages
    path('413/', pages.Error413.as_view(), name="413"),
]

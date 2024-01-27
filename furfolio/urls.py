from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from .views import commissions
from .views import dashboards
from .views import offers
from .views import registration
from .views import tags
from .views import users
from .views import pages
from .views import chat
from .views import notifications
from .views import support
from .sitemaps import sitemaps
from django.contrib.auth import views as auth_views
from django_email_verification import urls as email_verification_urls
from furfolio import forms as furfolio_forms

urlpatterns = [
    # sitemaps
    path('sitemap.xml', sitemap, {"sitemaps": sitemaps},
         name="django.contrib.sitemaps.views.sitemap"),
    # home
    path('', pages.Home.as_view(), name="home"),
    # offers
    path('offers/', offers.OfferList.as_view(), name="offer_list"),
    path('offers/create/', offers.CreateOffer.as_view(), name="create_offer"),
    path(
        'offers/<pk>/update/',
        offers.UpdateOffer.as_view(),
        name="update_offer"),
    path(
        'offers/<pk>/delete/',
        offers.DeleteOffer.as_view(),
        name="delete_offer"),
    path('offers/<pk>/', offers.Offer.as_view(), name="offer_detail"),
    # users
    path('users/<username>/', users.User.as_view(), name="user"),
    path('users/<username>/update/',
         users.UpdateUser.as_view(), name="update_user"),
    path('users/', users.UserList.as_view(), name="user_list"),
    # user following
    path('users/<username>/follow/',
         users.MakeUserFollowUser.as_view(), name="follow_user"),
    path('users/<username>/unfollow/',
         users.MakeUserUnfollowUser.as_view(), name="unfollow_user"),
    path('users/<username>/followed/',
         users.FollowedList.as_view(), name="followed_list"),
    # accounts
    path('accounts/signup/', registration.SignUp.as_view(), name="signup"),
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
    path(
        'accounts/after-sign-up/',
        registration.AfterSignUp.as_view(),
        name="after_sign_up"),
    ## email verification
    path('accounts/please-verify-email/', registration.PleaseVerifyEmail.as_view(), name="please_verify_email"),
    path('accounts/email/verify/', include(email_verification_urls)),
    # dashboards
    path('dashboard/', dashboards.CreatorDashboard.as_view(),
         name="dashboard"),
    # commissions
    path(
        'commissions/<pk>',
        commissions.Commission.as_view(),
        name="commission_detail"),
    path('offers/<offer_pk>/commissions/create/', commissions.CreateCommission.as_view(),
         name="create_commission"),
    path('commissions/<pk>/update/',
         commissions.UpdateCommission.as_view(), name="update_commission"),
    path('commissions/<pk>/update/status/',
         commissions.UpdateCommissionStatus.as_view(), name="update_commission_status"),
    path(
        'commissions/',
        commissions.Commissions.as_view(),
        name="commissions"),
    # tags
    path('tags/', tags.TagList.as_view(), name="tags"),
    path('tags/create/', tags.CreateTag.as_view(), name="create_tag"),
    path('tags/<name>/update/', tags.UpdateTag.as_view(), name="update_tag"),
    path('tags/<name>/delete/', tags.DeleteTag.as_view(), name="delete_tag"),
    path('tags/<name>/', tags.Tag.as_view(), name="tag_detail"),
    # tag categories
    path(
        'tag-categories/',
        tags.TagCategoryList.as_view(),
        name="tag_categories"),
    path(
        'tag-categories/create/',
        tags.CreateTagCategory.as_view(),
        name="create_tag_category"),
    path(
        'tag-categories/<name>/update/',
        tags.UpdateTagCategory.as_view(),
        name="update_tag_category"),
    path(
        'tag-categories/<name>/delete/',
        tags.DeleteTagCategory.as_view(),
        name="delete_tag_category"),
    path(
        'tag-categories/<name>/',
        tags.TagCategory.as_view(),
        name="tag_category_detail"),
    # chat
    path('chat/<pk>/', chat.Chat.as_view(), name="chat"),
    path('chat/<pk>/messages/', chat.ChatMessagesComponent.as_view(), name="chat_messages_component"),
    # notifications
    path(
        'notifications/',
        notifications.Notifications.as_view(),
        name="notifications"),
    path(
        'notifications/<pk>/view/',
        notifications.OpenNotification.as_view(),
        name="open_notification"),
    # support
    path('support/', support.Support.as_view(), name="support"),
    path('support/create/', support.CreateSupportTicket.as_view(), name="create_support_ticket"),
    path('support/<pk>/', support.SupportTicket.as_view(), name="support_ticket_detail"),
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
        'help/welcome-to-furfolio/',
        pages.WelcomeToFurfolio.as_view(),
        name="welcome_to_furfolio"),
    path(
        'help/getting-started/',
        pages.GettingStarted.as_view(),
        name="getting_started"),
    path('help/reference/', pages.Reference.as_view(), name="reference"),
    path('help/what-is-furfolio/',
         pages.WhatIsFurfolio.as_view(), name="what_is_furfolio"),
    path('help/offers-and-commissions/',
         pages.OffersAndCommissions.as_view(),
         name="offers_and_commissions"),
    path(
        'help/offer-reference/',
        pages.OfferReference.as_view(),
        name="offer_reference"),
    path(
        'help/commission-reference/',
        pages.CommissionReference.as_view(),
        name="commission_reference"),
    path('help/commission-search/', pages.CommissionSearchHelp.as_view(),
         name="commission_search_help"),
    path(
        'help/localization',
        pages.LocalizationReference.as_view(),
        name="localization_reference"),
    # error pages
    path('413/', pages.Error413.as_view(), name="413"),
]

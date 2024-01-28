from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.views import generic
from ..queries import chat as chat_queries
from ..queries import notifications as notification_queries
from .. import models
from .. import forms


class Chat(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = models.ChatMessage
    form_class = forms.ChatMessageForm
    template_name = "furfolio/chat/chat.html"

    def get_chat(self):
        return chat_queries.get_chat_by_pk(self.kwargs["pk"])

    def get_initial(self) -> dict[str, Any]:
        chat = self.get_chat()
        initial = super().get_initial()
        initial["chat"] = chat
        initial["author"] = self.request.user
        return initial

    def test_func(self):
        chat = self.get_chat()
        return chat_queries.test_user_is_participant_of_chat(
            chat, self.request.user)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        chat = self.get_chat()
        context["messages"] = chat_queries.get_messages_from_chat(chat)
        context["chat"] = chat
        return context


class ChatMessagesComponent(LoginRequiredMixin, UserPassesTestMixin, generic.TemplateView):
    model = models.ChatMessage
    template_name = "furfolio/chat/messages.html"

    def get_chat(self):
        return chat_queries.get_chat_by_pk(self.kwargs["pk"])

    def test_func(self):
        chat = self.get_chat()
        return chat_queries.test_user_is_participant_of_chat(
            chat, self.request.user)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        chat = self.get_chat()
        context["messages"] = chat_queries.get_messages_from_chat(chat)
        context["current_user"] = self.request.user
        return context
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        response = super().get(request, *args, **kwargs)
        chat = self.get_chat()
        notification_queries.make_chat_message_notifications_seen_for_user_and_chat(
            chat,
            self.request.user,
        )
        return response
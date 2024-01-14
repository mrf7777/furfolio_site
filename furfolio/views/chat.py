from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from ..queries import chat as chat_queries
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

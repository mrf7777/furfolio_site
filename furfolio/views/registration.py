from typing import Any, List
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseServerError
from django.shortcuts import redirect, get_object_or_404
from django.views import generic
from django.core.paginator import Page
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib import auth
from django.urls import reverse_lazy, reverse
from django.utils.http import urlencode
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from honeypot.decorators import check_honeypot
from .. import models
from .. import mixins
from .. import utils
from ..queries import users as user_queries
from ..queries import commissions as commission_queries
from ..queries import offers as offer_queries
from ..queries import commission_messages as commission_messages_queries
from ..queries import user_following_user as user_following_user_queries
from ..queries import tags as tag_queries
from ..queries import tag_categories as tag_category_queries
from ..queries import chat as chat_queries
from .. import forms

# decorate the 'post' method of this class to check for honeypot


@method_decorator(check_honeypot, name="post")
class SignUp(generic.CreateView):
    form_class = forms.CustomUserCreationForm
    success_url = reverse_lazy("welcome_to_furfolio")
    template_name = "registration/signup.html"

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)
        # sign in the new user
        # TODO: consider testing via LiveServerTestCase class
        username = self.request.POST["username"]
        password = self.request.POST["password1"]
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(self.request, user)
        else:
            return HttpResponseServerError()
        return response

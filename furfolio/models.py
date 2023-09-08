from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from datetime import datetime, timedelta

class User(AbstractUser):
    pass

class Offer(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=80, name="name")
    cutoff_date = models.DateTimeField(name="cutoff date", default=lambda:(datetime.now() + timedelta(days=7)))
    created_date = models.DateTimeField(name="created date", auto_now_add=True)
    updated_date = models.DateTimeField(name="updated date", auto_now=True)
    
    def __str__(self):
        return "Id: %i. \"%s\" by %s." % (self.id, self.name, self.author.username)
    
    def get_absolute_url(self):
        return reverse("offer_detail", kwargs={"pk": self.pk})
    
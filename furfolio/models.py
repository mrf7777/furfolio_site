from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class Offer(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=80, name="name")
    created_date = models.DateTimeField(name="created date", auto_now_add=True)
    updated_date = models.DateTimeField(name="updated date", auto_now=True)
    
    def __str__(self):
        return "\"%s\" by %s" % (self.name, self.author.username)
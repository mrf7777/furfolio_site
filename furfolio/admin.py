from django.contrib import admin

from .models import User, Offer, Commission

admin.site.register(User)
admin.site.register(Offer)
admin.site.register(Commission)
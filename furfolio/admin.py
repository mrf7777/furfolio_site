from django.contrib import admin

from .models import User, Offer, Commission, CommissionMessage, UserFollowingUser, Tag, TagCategory

admin.site.register(User)
admin.site.register(Offer)
admin.site.register(Commission)
admin.site.register(CommissionMessage)
admin.site.register(UserFollowingUser)
admin.site.register(Tag)
admin.site.register(TagCategory)
from django.contrib import admin

from .models import Chat, ChatMessage, ChatParticipant, User, Offer, Commission, UserFollowingUser, Tag, TagCategory

admin.site.register(User)
admin.site.register(Offer)
admin.site.register(Commission)
admin.site.register(UserFollowingUser)
admin.site.register(Tag)
admin.site.register(TagCategory)
admin.site.register(Chat)
admin.site.register(ChatParticipant)
admin.site.register(ChatMessage)

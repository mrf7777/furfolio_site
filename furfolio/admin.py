from django.contrib import admin

from .models import SupportTicket, Notification, ChatMessageNotification, CommissionChat, SupportTicketChat, Chat, ChatMessage, ChatParticipant, User, Offer, Commission, UserFollowingUser, Tag, TagCategory

admin.site.register(User)
admin.site.register(Offer)
admin.site.register(Commission)
admin.site.register(UserFollowingUser)
admin.site.register(Tag)
admin.site.register(TagCategory)
admin.site.register(Chat)
admin.site.register(CommissionChat)
admin.site.register(SupportTicketChat)
admin.site.register(ChatParticipant)
admin.site.register(ChatMessage)
admin.site.register(Notification)
admin.site.register(ChatMessageNotification)
admin.site.register(SupportTicket)

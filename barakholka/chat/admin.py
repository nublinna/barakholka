from django.contrib import admin
from chat.models import ChatRoom, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'seller', 'ad', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('buyer__username', 'seller__username', 'ad__title')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'chat_room', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('sender__username', 'content')
    readonly_fields = ('timestamp',)

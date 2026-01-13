from django.urls import path
from chat.views import (chat_list, chat_detail, create_general_chat,
                        create_chat_for_ad)

app_name = 'chat'

urlpatterns = [
    path('', chat_list, name='chat_list'),

    path('new/', create_general_chat, name='create_general_chat'),

    path('ad/<int:ad_id>/', create_chat_for_ad, name='create_chat_for_ad'),

    path('<int:chat_id>/', chat_detail, name='chat_detail'),
]
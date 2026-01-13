from django.db import models
from django.conf import settings


class ChatRoom(models.Model):
    ad = models.ForeignKey(
        'ads.Ads',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='chats',
        verbose_name="Объявление"
    )

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='buyer_chats',
        verbose_name="Покупатель"
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seller_chats',
        verbose_name="Продавец"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        unique_together = ['buyer', 'seller', 'ad']
        ordering = ['-created_at']

    def __str__(self):
        if self.ad:
            return f"Чат по объявлению '{self.ad.title}'"
        return f"Чат {self.buyer} - {self.seller}"


class Message(models.Model):
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name="Комната чата"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Отправитель"
    )
    content = models.TextField(verbose_name="Содержание")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Время отправки")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender}: {self.content[:50]}..."
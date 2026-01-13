from django.core.validators import FileExtensionValidator
from django.db import models
from django.conf import settings


class Ads(models.Model):
    NEW = 'new'
    USED = 'used'
    TYPE_CHOICES = [
        (NEW, 'Новое'),
        (USED, 'б/у'),
    ]
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ads',
        verbose_name="Продавец"
    )
    title = models.CharField(max_length=500, verbose_name="Название объявления")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    address = models.CharField(max_length=500, verbose_name="Адрес")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    available = models.BooleanField(default=True, verbose_name="Доступно")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Состояние")
    category = models.CharField(max_length=100, help_text='Например: Бытовая техника, Конспекты, Одежда и т.д.', verbose_name="Категория")

    def __str__(self):
        return self.title

    @property
    def main_image(self):
        main = self.images.filter(is_main=True).first()
        if main:
            return main.image
        first_image = self.images.first()
        return first_image.image if first_image else None

    @property
    def main_image_url(self):
        image = self.main_image
        return image.url if image else None

    def is_favorited_by(self, user):
        if not user.is_authenticated:
            return False
        return self.favorited_by.filter(user=user).exists()

    class Meta:
        ordering = ['-created_at']

class AdsImage(models.Model):
    ads = models.ForeignKey(
        Ads,
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField(
        upload_to='ads/images/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
    )
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Image for {self.ads.title}"

    def save(self, *args, **kwargs):
        if self.is_main:
            AdsImage.objects.filter(ads=self.ads, is_main=True).exclude(id=self.id).update(is_main=False)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-is_main', 'order']



class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Пользователь'
    )
    ads = models.ForeignKey(
        Ads,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Объявление'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        unique_together = ['user', 'ads']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}"


class SiteStatistics(models.Model):
    # Объявления
    total_ads = models.PositiveIntegerField(default=0, verbose_name='Всего объявлений')
    active_ads = models.PositiveIntegerField(default=0, verbose_name='Активных объявлений')
    total_users = models.PositiveIntegerField(default=0, verbose_name='Всего пользователей')

    # Чаты и сообщения
    total_chats = models.PositiveIntegerField(default=0, verbose_name='Всего чатов')
    total_messages = models.PositiveIntegerField(default=0, verbose_name='Всего сообщений')

    # Избранное
    total_favorites = models.PositiveIntegerField(default=0, verbose_name='Добавлено в избранное')


    # Дата обновления
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = "Статистика сайта"
        verbose_name_plural = "Статистика сайта"
        ordering = ['-updated_at']

    def __str__(self):
        return f"Статистика на {self.updated_at.strftime('%d.%m.%Y %H:%M')}"

    @classmethod
    def get_current_stats(cls):
        stats, created = cls.objects.get_or_create(pk=1)
        return stats

    def update_stats(self):
        from chat.models import ChatRoom, Message
        from django.contrib.auth import get_user_model

        User = get_user_model()

        self.total_ads = Ads.objects.count()
        self.active_ads = Ads.objects.filter(available=True).count()
        self.total_users = User.objects.count()

        self.total_chats = ChatRoom.objects.count()
        self.total_messages = Message.objects.count()

        self.total_favorites = Favorite.objects.count()

        self.save()

        return self
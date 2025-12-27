from django.core.validators import FileExtensionValidator
from django.db import models
from django.conf import settings


class Ads(models.Model):
    NEW = 'new'
    USED = 'used'
    TYPE_CHOICES = [(NEW, 'new'), (USED, 'used')]
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ads',
    )
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    available = models.BooleanField(default=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    category = models.CharField(max_length=100, help_text='Например: Бытовая техника, Конспекты, Одежда и т.д.')

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


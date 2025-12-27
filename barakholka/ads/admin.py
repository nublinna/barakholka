from django.contrib import admin
from ads.models import Ads, AdsImage

@admin.register(Ads)
class AdsAdmin(admin.ModelAdmin):
    class AdsImageAdmin(admin.TabularInline):
        model = AdsImage
        extra = 2

    inlines = [AdsImageAdmin]
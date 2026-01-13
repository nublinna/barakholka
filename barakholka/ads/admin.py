from django.contrib import admin
from ads.models import Ads, AdsImage, Favorite, SiteStatistics

@admin.register(Ads)
class AdsAdmin(admin.ModelAdmin):
    class AdsImageAdmin(admin.TabularInline):
        model = AdsImage
        extra = 2

    inlines = [AdsImageAdmin]

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'ads', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'ads__title']
    readonly_fields = ['created_at']

@admin.register(SiteStatistics)
class SiteStatisticsAdmin(admin.ModelAdmin):
    list_display = ['total_ads', 'active_ads', 'total_users', 'total_chats', 'total_messages', 'updated_at']
    readonly_fields = ['total_ads', 'active_ads', 'total_users', 'total_chats', 'total_messages', 'total_favorites', 'updated_at']

    def has_add_permission(self, request):
        # Запрещаем добавлять новые записи статистики
        return False

    def has_delete_permission(self, request, obj=None):
        # Запрещаем удалять статистику
        return False
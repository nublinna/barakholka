from django.urls import path
from ads.views import (ads_list, ads_detail, ad_create,
                       ad_edit, ad_delete,
                       add_to_favorites, remove_from_favorites, favorites_list,
                       site_statistics, my_ads)


app_name = 'ads'

urlpatterns = [
    path('', ads_list, name='ads_list'),

    path('<int:ad_id>/', ads_detail, name='ads_detail'),

    path('add/', ad_create, name='ad_create'),

    path('<int:ad_id>/edit/', ad_edit, name='ad_edit'),

    path('<int:ad_id>/delete/', ad_delete, name='ad_delete'),


    path('favorites/', favorites_list, name='favorites_list'),

    path('<int:ad_id>/add-to-favorites/', add_to_favorites, name='add_to_favorites'),

    path('<int:ad_id>/remove-from-favorites/', remove_from_favorites, name='remove_from_favorites'),

    path('statistics/', site_statistics, name='site_statistics'),

    path('my-ads/', my_ads, name='my_ads'),
]
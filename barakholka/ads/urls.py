from django.urls import path
from ads.views import ads_list


app_name = 'ads'

urlpatterns = [
    path('', ads_list, name='ads_list'),

]
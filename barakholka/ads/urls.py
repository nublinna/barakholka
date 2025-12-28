from django.urls import path
from ads.views import ads_list, ads_detail


app_name = 'ads'

urlpatterns = [
    path('', ads_list, name='ads_list'),
    path('<int:ad_id>/', ads_detail, name='ad_detail'),
]
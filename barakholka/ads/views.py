from django.shortcuts import render
from ads.models import Ads


def ads_list(request):
    all_ads = Ads.objects.filter(available=True)
    return render(request, 'ads_list.html', context={
        'all_ads': all_ads
    })

from django.shortcuts import render, get_object_or_404
from ads.models import Ads



def ads_list(request):
    all_ads = Ads.objects.filter(available=True)
    return render(request, 'ads_list.html', context={
        'all_ads': all_ads
    })

def ads_detail(request, ad_id):
    # filter -> list()
    # ad_from_db = Ads.objects.filter(id=ad_id).first()

    # get returns only one item
    # ad_from_db = Ads.objects.get(id=ad_id)

    ad_from_db = get_object_or_404(Ads, id=ad_id)
    return render(request, 'ad_detail.html', context={
        'ad': ad_from_db,
    })


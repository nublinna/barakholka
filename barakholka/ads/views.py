from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ads.models import Ads, Favorite, SiteStatistics
from django.contrib.auth.decorators import login_required
from ads.forms import AdsForm, AdsImageFormSet


def ads_list(request):
    all_ads = Ads.objects.filter(available=True)
    return render(request, 'ads_list.html', context={
        'all_ads': all_ads
    })

def ads_detail(request, ad_id):
    ad_from_db = get_object_or_404(Ads, id=ad_id)
    return render(request, 'ad_detail.html', context={
        'ad': ad_from_db,
    })


@login_required
def ad_create(request):
    if not request.user.is_seller():
        return redirect("ads:ads_list")

    if request.method == "POST":
        form = AdsForm(request.POST, request.FILES)
        image_formset = AdsImageFormSet(request.POST, request.FILES)
        if form.is_valid() and image_formset.is_valid():
            ad = form.save(commit=False)
            if request.user.is_authenticated:
                ad.seller = request.user
            else:
                # Это не должно происходить из-за @login_required, но на всякий случай
                messages.error(request, 'Необходимо войти в систему для создания объявления.')
                return redirect("user:login")
            ad.save()

            image_formset.instance = ad
            image_formset.save()

            messages.success(request, f'Объявление "{ad.title}" успешно создано!')
            return redirect("ads:ads_list")
        else:
            # Более детальная обработка ошибок
            error_messages = []
            if not form.is_valid():
                error_messages.append("Ошибки в основных данных объявления:")
                for field, errors in form.errors.items():
                    field_name = form.fields[field].label if hasattr(form.fields[field], 'label') else field
                    error_messages.append(f"- {field_name}: {', '.join(errors)}")

            if not image_formset.is_valid():
                error_messages.append("Ошибки в изображениях:")
                for form_errors in image_formset.errors:
                    if form_errors:
                        for field, errors in form_errors.items():
                            error_messages.append(f"- {field}: {', '.join(errors)}")

            if error_messages:
                messages.error(request, ' '.join(error_messages))
            else:
                messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = AdsForm()
        image_formset = AdsImageFormSet(instance=Ads())

    return render(request, "ad_create.html", context={
        "form": form,
        "image_formset": image_formset,
        "empty_image_form": image_formset.empty_form
    })

@login_required
def ad_edit(request, ad_id):
    ad = get_object_or_404(Ads, id=ad_id, seller=request.user)

    if request.method == "POST":
        form = AdsForm(request.POST, request.FILES, instance=ad)
        image_formset = AdsImageFormSet(request.POST, request.FILES, instance=ad)
        if form.is_valid() and image_formset.is_valid():
            form.save()
            image_formset.save()
            messages.success(request, 'Объявление успешно обновлено!')
            return redirect("ads:ads_detail", ad_id=ad_id)
        else:
            # Более детальная обработка ошибок
            error_messages = []
            if not form.is_valid():
                error_messages.append("Ошибки в основных данных объявления:")
                for field, errors in form.errors.items():
                    field_name = form.fields[field].label if hasattr(form.fields[field], 'label') else field
                    error_messages.append(f"- {field_name}: {', '.join(errors)}")

            if not image_formset.is_valid():
                error_messages.append("Ошибки в изображениях:")
                for form_errors in image_formset.errors:
                    if form_errors:
                        for field, errors in form_errors.items():
                            error_messages.append(f"- {field}: {', '.join(errors)}")

            if error_messages:
                messages.error(request, ' '.join(error_messages))
            else:
                messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = AdsForm(instance=ad)
        image_formset = AdsImageFormSet(instance=ad)

    return render(request, "ad_edit.html", context={
        "form": form,
        "image_formset": image_formset,
        "empty_image_form": image_formset.empty_form,
        "ad": ad
    })


@login_required
def ad_delete(request, ad_id):
    ad = get_object_or_404(Ads, id=ad_id, seller=request.user)

    if request.method == "POST":
        ad_title = ad.title  # Сохраняем название для сообщения
        ad.delete()
        messages.success(request, f'Объявление "{ad_title}" успешно удалено!')
        return redirect("ads:ads_list")

    return render(request, "ad_confirm_delete.html", context={"ad": ad})

@login_required
def add_to_favorites(request, ad_id):
    """Добавление товара в избранное"""
    ad = get_object_or_404(Ads, id=ad_id)

    # Проверяем, что пользователь не пытается добавить свой же товар
    if request.user == ad.seller:
        messages.warning(request, 'Нельзя добавить в избранное свой собственный товар.')
        return redirect('ads:ads_detail', ad_id=ad_id)

    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        ads=ad
    )

    if created:
        messages.success(request, f'Товар "{ad.title}" добавлен в избранное!')
    else:
        messages.info(request, 'Этот товар уже в вашем избранном.')

    return redirect('ads:ads_detail', ad_id=ad_id)


@login_required
def remove_from_favorites(request, ad_id):
    """Удаление товара из избранного"""
    ad = get_object_or_404(Ads, id=ad_id)

    try:
        favorite = Favorite.objects.get(user=request.user, ads=ad)
        favorite.delete()
        messages.success(request, f'Товар "{ad.title}" удален из избранного.')
    except Favorite.DoesNotExist:
        messages.warning(request, 'Этот товар не был в избранном.')

    # Определяем, откуда пришел запрос
    next_url = request.GET.get('next', 'ads:favorites_list')
    return redirect(next_url)


@login_required
def favorites_list(request):
    """Страница с избранными товарами"""
    favorites = Favorite.objects.filter(user=request.user).select_related('ad', 'ad__seller')

    context = {
        'favorites': favorites,
        'favorites_count': favorites.count(),
    }

    return render(request, 'ads/favorites.html', context)

@login_required
def add_to_favorites(request, ad_id):
    ad = get_object_or_404(Ads, id=ad_id)

    if request.user == ad.seller:
        return redirect("ads:ads_detail", ad_id=ad_id)

    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        ads=ad
    )

    if created:
        messages.success(request, f"Товар {ad.title} добавлен в избранное")
    else:
        messages.info(request, "Товар уже добавлен в ваше избранное")

    return redirect("ads:ads_detail", ad_id=ad_id)

@login_required
def remove_from_favorites(request, ad_id):
    ad = get_object_or_404(Ads, id=ad_id)

    try:
        favorite = Favorite.objects.get(user=request.user, ads=ad)
        favorite.delete()
        messages.success(request, f"Товар '{ad.title}' удален из избранного")
    except Favorite.DoesNotExist:
        messages.warning(request, "Этот товар не был в избранном")

    # Определяем, откуда пришел запрос
    next_url = request.GET.get('next', 'ads:favorites_list')
    return redirect(next_url)


@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('ads', 'ads__seller')

    return render(request, "ads/favorites.html", context={
        "favorites": favorites,
        "favorites_count": favorites.count(),
    })


@login_required
def site_statistics(request):
    """Статистика сайта для администраторов"""
    if not request.user.is_staff:
        from django.contrib import messages
        messages.error(request, 'У вас нет прав для просмотра статистики.')
        return redirect('ads:ads_list')

    # Получаем текущую статистику
    stats = SiteStatistics.get_current_stats()

    # Обновляем статистику перед показом
    stats.update_stats()

    # Дополнительная статистика по пользователям
    from django.db.models import Count
    from chat.models import ChatRoom, Message

    # Топ пользователей по количеству объявлений
    top_users_by_ads = Ads.objects.values('seller__username').annotate(
        ads_count=Count('id')
    ).order_by('-ads_count')[:10]

    # Топ пользователей по количеству сообщений
    top_users_by_messages = Message.objects.values('sender__username').annotate(
        messages_count=Count('id')
    ).order_by('-messages_count')[:10]

    # Рассчитанные метрики для шаблона
    avg_ads_per_user = stats.total_ads / stats.total_users if stats.total_users > 0 else 0
    avg_messages_per_chat = stats.total_messages / stats.total_chats if stats.total_chats > 0 else 0
    active_ads_percentage = (stats.active_ads / stats.total_ads * 100) if stats.total_ads > 0 else 0

    context = {
        'stats': stats,
        'top_users_by_ads': top_users_by_ads,
        'top_users_by_messages': top_users_by_messages,
        'avg_ads_per_user': avg_ads_per_user,
        'avg_messages_per_chat': avg_messages_per_chat,
        'active_ads_percentage': active_ads_percentage,
    }

    return render(request, 'ads/statistics.html', context)


@login_required
def my_ads(request):
    """Показать все объявления текущего пользователя (включая неактивные)"""
    user_ads = Ads.objects.filter(seller=request.user).select_related('seller').order_by('-created_at')

    context = {
        'user_ads': user_ads,
    }

    return render(request, 'ads/my_ads.html', context)


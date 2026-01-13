from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User

from chat.models import ChatRoom, Message
from chat.forms import MessageForm


@login_required
def chat_list(request):
    """Список чатов для пользователя"""
    from django.db.models import Count, Q

    if request.user.is_staff:
        # Если пользователь - продавец/админ
        chats = ChatRoom.objects.filter(seller=request.user, is_active=True)
    else:
        # Если пользователь - покупатель
        chats = ChatRoom.objects.filter(buyer=request.user, is_active=True)

    # Добавляем количество непрочитанных сообщений для каждого чата
    for chat in chats:
        if request.user == chat.buyer:
            # Для покупателя считаем непрочитанные сообщения от продавца
            chat.unread_count = chat.messages.filter(is_read=False, sender=chat.seller).count()
        else:
            # Для продавца считаем непрочитанные сообщения от покупателя
            chat.unread_count = chat.messages.filter(is_read=False, sender=chat.buyer).count()

    return render(request, 'chat/chat_list.html', {'chats': chats})


@login_required
def create_chat_for_ad(request, ad_id):
    """Создать чат по конкретному объявлению"""
    from ads.models import Ads
    ad = get_object_or_404(Ads, id=ad_id)
    seller = ad.seller

    # Проверяем, не пытается ли автор написать сам себе
    if request.user == seller:
        return redirect('ads:ads_detail', ad_id=ad_id)

    # Ищем существующий активный чат по этому объявлению
    chat_room = ChatRoom.objects.filter(
        buyer=request.user,
        seller=seller,
        ad=ad,
        is_active=True
    ).first()

    # Если нет активного чата - создаем
    if not chat_room:
        chat_room = ChatRoom.objects.create(
            buyer=request.user,
            seller=seller,
            ad=ad
        )

    return redirect('chat:chat_detail', chat_id=chat_room.id)


@login_required
def create_general_chat(request):
    """Создать общий чат с продавцом (не привязанный к объявлению)"""
    # Находим продавца (например, первого администратора)
    seller = User.objects.filter(is_staff=True).first()

    if not seller:
        return redirect('chat:chat_list')

    # Ищем существующий общий чат (без привязки к объявлению)
    chat_room = ChatRoom.objects.filter(
        buyer=request.user,
        seller=seller,
        ad__isnull=True,  # ищем чаты без объявления
        is_active=True
    ).first()

    # Если нет активного чата - создаем
    if not chat_room:
        chat_room = ChatRoom.objects.create(
            buyer=request.user,
            seller=seller,
            # ad не указываем - будет NULL
        )

    return redirect('chat:chat_detail', chat_id=chat_room.id)


@login_required
def chat_detail(request, chat_id):
    """Страница чата"""
    chat_room = get_object_or_404(ChatRoom, id=chat_id)

    # Проверка прав доступа
    if request.user not in [chat_room.buyer, chat_room.seller]:
        return redirect('chat:chat_list')

    messages = chat_room.messages.all()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat_room = chat_room
            message.sender = request.user
            message.save()

            # AJAX обработка
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': message.content,
                    'sender': message.sender.username,
                    'timestamp': message.timestamp.strftime('%H:%M')
                })

            # Обновляем список сообщений и показываем страницу чата
            messages = chat_room.messages.all()
            context = {
                'chat_room': chat_room,
                'messages': messages,
                'form': MessageForm(),
            }
            return render(request, 'chat/chat_detail.html', context)
    else:
        form = MessageForm()

    # Помечаем сообщения как прочитанные для получателя
    if request.user == chat_room.seller:
        # Продавец читает сообщения от покупателя
        chat_room.messages.filter(is_read=False, sender=chat_room.buyer).update(is_read=True)
    else:
        # Покупатель читает сообщения от продавца
        chat_room.messages.filter(is_read=False, sender=chat_room.seller).update(is_read=True)

    context = {
        'chat_room': chat_room,
        'messages': messages,
        'form': form,
    }

    return render(request, 'chat/chat_detail.html', context)


@login_required
def get_new_messages(request, chat_id, last_message_id):
    """AJAX запрос для получения новых сообщений"""
    chat_room = get_object_or_404(ChatRoom, id=chat_id)

    if request.user not in [chat_room.buyer, chat_room.seller]:
        return JsonResponse({'error': 'Нет доступа'}, status=403)

    new_messages = chat_room.messages.filter(
        id__gt=last_message_id
    ).order_by('timestamp')

    messages_data = []
    for msg in new_messages:
        messages_data.append({
            'id': msg.id,
            'content': msg.content,
            'sender': msg.sender.username,
            'sender_id': msg.sender.id,
            'timestamp': msg.timestamp.strftime('%H:%M'),
            'is_mine': msg.sender.id == request.user.id
        })

    return JsonResponse({'messages': messages_data})
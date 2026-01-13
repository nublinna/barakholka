from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from ads.models import Ads
from chat.models import ChatRoom, Message
from chat.forms import MessageForm


@login_required
def chat_list(request):

    if request.user.is_staff:
        chats = ChatRoom.objects.filter(seller=request.user, is_active=True)
    else:
        chats = ChatRoom.objects.filter(buyer=request.user, is_active=True)

    for chat in chats:
        if request.user == chat.buyer:
            chat.unread_count = chat.messages.filter(is_read=False, sender=chat.seller).count()
        else:
            chat.unread_count = chat.messages.filter(is_read=False, sender=chat.buyer).count()

    return render(request, 'chat_list.html', {'chats': chats})


@login_required
def create_chat_for_ad(request, ad_id):
    ad = get_object_or_404(Ads, id=ad_id)
    seller = ad.seller

    if request.user == seller:
        return redirect('ads:ads_detail', ad_id=ad_id)

    chat_room = ChatRoom.objects.filter(
        buyer=request.user,
        seller=seller,
        ad=ad,
        is_active=True
    ).first()

    if not chat_room:
        chat_room = ChatRoom.objects.create(
            buyer=request.user,
            seller=seller,
            ad=ad
        )

    return redirect('chat:chat_detail', chat_id=chat_room.id)


@login_required
def create_general_chat(request):
    seller = User.objects.filter(is_staff=True).first()

    if not seller:
        return redirect('chat:chat_list')

    chat_room = ChatRoom.objects.filter(
        buyer=request.user,
        seller=seller,
        ad__isnull=True,
        is_active=True
    ).first()

    if not chat_room:
        chat_room = ChatRoom.objects.create(
            buyer=request.user,
            seller=seller,
        )

    return redirect('chat:chat_detail', chat_id=chat_room.id)


@login_required
def chat_detail(request, chat_id):
    chat_room = get_object_or_404(ChatRoom, id=chat_id)

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

            messages = chat_room.messages.all()
            context = {
                'chat_room': chat_room,
                'messages': messages,
                'form': MessageForm(),
            }
            return render(request, 'chat_detail.html', context)
    else:
        form = MessageForm()

    if request.user == chat_room.seller:
        chat_room.messages.filter(is_read=False, sender=chat_room.buyer).update(is_read=True)
    else:
        chat_room.messages.filter(is_read=False, sender=chat_room.seller).update(is_read=True)

    context = {
        'chat_room': chat_room,
        'messages': messages,
        'form': form,
    }

    return render(request, 'chat_detail.html', context)
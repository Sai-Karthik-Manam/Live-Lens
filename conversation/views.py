from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from market.models import Item
from .models import Conversation, Message
from .forms import MessageForm


@login_required
def inbox(request):
    """Shows all conversations for the logged-in user (as buyer or seller)."""
    conversations = Conversation.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).select_related('item', 'buyer', 'seller').order_by('-updated_at')

    return render(request, 'conversation/inbox.html', {
        'conversations': conversations,
    })


@login_required
def conversation_detail(request, pk):
    """Shows a single conversation thread and allows replying."""
    conversation = get_object_or_404(
        Conversation, pk=pk
    )

    # Security: only the buyer or seller can view this conversation
    if request.user != conversation.buyer and request.user != conversation.seller:
        return redirect('conversation:inbox')

    form = MessageForm()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                body=form.cleaned_data['body']
            )
            # Bump updated_at so it appears at top of inbox
            conversation.save()
            return redirect('conversation:detail', pk=pk)

    return render(request, 'conversation/detail.html', {
        'conversation': conversation,
        'form': form,
        'messages': conversation.messages.all(),
    })


@login_required
def new_conversation(request, item_pk):
    """Starts a new conversation OR redirects to existing one."""
    item = get_object_or_404(Item, pk=item_pk)

    # Can't message yourself
    if item.seller == request.user:
        return redirect('market:detail', pk=item_pk)

    # Get existing or create new conversation
    conversation, created = Conversation.objects.get_or_create(
        item=item,
        seller=item.seller,
        buyer=request.user,
    )

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                body=form.cleaned_data['body']
            )
            conversation.save()
            return redirect('conversation:detail', pk=conversation.pk)
    else:
        form = MessageForm()

    return render(request, 'conversation/new.html', {
        'form': form,
        'item': item,
    })
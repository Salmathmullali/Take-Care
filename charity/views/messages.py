from django.contrib import messages as django_messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from charity.forms import MessageForm
from charity.models.blood import BloodMatch
from charity.models.food import FoodPickupRequest
from charity.models.medical import MedicalMatch
from charity.services import connections

CONNECTION_MODELS = {
    'blood': BloodMatch,
    'medical': MedicalMatch,
    'food': FoodPickupRequest,
}


@login_required
def connection_messages(request, pillar, pk):
    model = CONNECTION_MODELS.get(pillar)
    if not model:
        raise Http404
    connection = get_object_or_404(model, pk=pk)
    if not connections.user_is_party(connection, request.user):
        raise PermissionDenied
    if not connection.is_unlocked:
        raise PermissionDenied

    msgs = connections.get_messages(connection)
    contact = connections.get_unlocked_contact(connection)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            connections.add_message(connection, request.user, form.cleaned_data['body'])
            django_messages.success(request, 'Message sent.')
            return redirect('charity:messages', pillar=pillar, pk=pk)
    else:
        form = MessageForm()

    return render(
        request,
        'charity/components/messages.html',
        {
            'connection': connection,
            'pillar': pillar,
            'messages_list': msgs,
            'form': form,
            'contact': contact,
        },
    )

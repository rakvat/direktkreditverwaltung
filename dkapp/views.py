from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse

from .models import Contact


def index(request):
    return HttpResponse("Hello, world. Direktkreditverwaltung. TODO links")


def contacts(request):
    contacts = Contact.objects.order_by('last_name', 'first_name')
    return render(request, 'contacts/index.html', {'contacts': contacts})


def contact(request, contact_id):
    # TODO class based views
    if request.method == 'GET':
        contact = get_object_or_404(Contact, pk=contact_id)
        return render(request, 'contacts/show.html', {'contact': contact})
    elif request.method == 'POST':
        contact = get_object_or_404(Contact, pk=contact_id)
        contact.first_name = request.POST['first_name']
        contact.save()
        return HttpResponseRedirect(reverse('dkapp:contact', args=(contact_id,)))

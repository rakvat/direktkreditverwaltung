from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic

from .models import Contact


class IndexView(generic.TemplateView):
    template_name = 'index.html'


class ContactsView(generic.ListView):
    template_name = 'contacts/index.html'
    context_object_name = 'contacts'

    def get_queryset(self):
        return Contact.objects.order_by('last_name', 'first_name')


class ContactView(generic.DetailView):
    model = Contact
    template_name = 'contacts/detail.html'

    def post(self, *args, **kwargs):
        contact_id = kwargs['pk']
        contact = get_object_or_404(Contact, pk=contact_id)
        contact.first_name = self.request.POST['first_name']
        contact.save()
        return HttpResponseRedirect(reverse('dkapp:contact', args=(contact_id,)))

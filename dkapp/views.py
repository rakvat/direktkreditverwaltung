from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic

from .models import Contact
from .forms import ContactForm


class IndexView(generic.TemplateView):
    template_name = 'index.html'


class ContactsView(generic.ListView):
    template_name = 'contacts/index.html'
    context_object_name = 'contacts'

    def get_queryset(self):
        return Contact.objects.order_by('last_name', 'first_name')


def contact2(request):
    form = ContactForm()
    return render(request, 'form.html', {'form': form})


class ContactView(generic.DetailView):
    model = Contact
    template_name = 'contacts/detail.html'

    def get(self, *args, **kwargs):
        contact_id = kwargs['pk']
        contact = get_object_or_404(Contact, pk=contact_id)
        form = ContactForm(contact)


    def post(self, *args, **kwargs):
        form = ContactForm(self.request.POST)
        if form.is_valid():
            contact_id = kwargs['pk']
            contact = get_object_or_404(Contact, pk=contact_id)
            contact.first_name = form.cleaned_data['first_name']
            contact.last_name = form.cleaned_data['first_name']
            contact.address = form.cleaned_data['address']
            contact.iban = form.cleaned_data['iban']
            contact.bic = form.cleaned_data['bic']
            contact.bank_name = form.cleaned_data['bank_name']
            contact.phone = form.cleaned_data['phone']
            contact.email = form.cleaned_data['email']
            contact.remark = form.cleaned_data['remark']
            contact.save()
        return HttpResponseRedirect(reverse('dkapp:contact', args=(contact_id,)))

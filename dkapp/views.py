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

    @staticmethod
    def new(request):
        form = ContactForm()
        return render(request, 'form.html', {'form': form, 'action_url': reverse('dkapp:contacts')})

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            return HttpResponseRedirect(reverse('dkapp:contact', args=(contact.id,)))

        return HttpResponseRedirect(reverse('dkapp:contacts'))


class ContactView(generic.DetailView):
    model = Contact
    template_name = 'contacts/detail.html'

    @staticmethod
    def edit(request, *args, **kwargs):
        contact_id = kwargs['pk']
        contact = get_object_or_404(Contact, pk=contact_id)
        form = ContactForm(instance=contact)
        return render(request, 'form.html', {
            'form': form,
            'action_url': reverse('dkapp:contact', args=(contact.id,)),
        })

    def post(self, *args, **kwargs):
        contact_id = kwargs['pk']
        contact = get_object_or_404(Contact, pk=contact_id)
        form = ContactForm(self.request.POST, instance=contact)
        if form.is_valid():
            form.save()

        return HttpResponseRedirect(reverse('dkapp:contact', args=(contact.id,)))


class ContractsView(generic.ListView):
    def interest(self):
        pass

    def interest_transfer_list(self):
        pass

    def interest_average(self):
        pass

    def expiring(self):
        pass

class ContractVersionsView(generic.ListView):
    pass


class AccountingEntriesView(generic.ListView):
    pass

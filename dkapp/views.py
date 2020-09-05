from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic

from .models import Contact, Contract, ContractVersion, AccountingEntry
from .forms import ContactForm, ContractForm, ContractVersionForm, AccountingEntryForm


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


class ContactDeleteView(generic.edit.DeleteView):
    template_name = 'object_confirm_delete.html'

    def get_object(self, *args, **kwargs):
        return get_object_or_404(Contact, pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('dkapp:contacts')


class ContractsView(generic.ListView):
    template_name = 'contracts/index.html'
    context_object_name = 'contracts'

    def get_queryset(self):
        contact_id = self.request.GET.get('contact_id')
        if contact_id is None:
            return Contract.objects.order_by('number')
        else:
            return Contract.objects.filter(contact_id=contact_id).order_by('number')

    def get_context_data(self, **kwargs):
        context = super(ContractsView, self).get_context_data(**kwargs)
        contact_id = self.request.GET.get('contact_id')
        if not contact_id is None:
            contact = get_object_or_404(Contact, pk=contact_id)
            context['contact'] = contact
        return context

    @staticmethod
    def new(request):
        form = ContractForm()
        return render(request, 'form.html', {'form': form, 'action_url': reverse('dkapp:contracts')})

    def post(self, request):
        form = ContractForm(request.POST)
        if form.is_valid():
            contract = form.save()
            return HttpResponseRedirect(reverse('dkapp:contract', args=(contract.id,)))

        return HttpResponseRedirect(reverse('dkapp:contracts'))

    def interest(self):
        pass

    def interest_transfer_list(self):
        pass

    def interest_average(self):
        pass

    def expiring(self):
        pass


class ContractView(generic.DetailView):
    model = Contract
    template_name = 'contracts/detail.html'

    @staticmethod
    def edit(request, *args, **kwargs):
        contract_id = kwargs['pk']
        contract = get_object_or_404(Contract, pk=contract_id)
        form = ContractForm(instance=contract)
        return render(request, 'form.html', {
            'form': form,
            'action_url': reverse('dkapp:contract', args=(contract.id,)),
        })

    def post(self, *args, **kwargs):
        contract_id = kwargs['pk']
        contract = get_object_or_404(Contact, pk=contract_id)
        form = ContractForm(self.request.POST, instance=contract)
        if form.is_valid():
            form.save()

        return HttpResponseRedirect(reverse('dkapp:contract', args=(contract.id,)))


class ContractDeleteView(generic.edit.DeleteView):
    template_name = 'object_confirm_delete.html'

    def get_object(self, *args, **kwargs):
        return get_object_or_404(Contact, pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('dkapp:contacts')


class ContractVersionsView(generic.ListView):
    template_name = 'contract_versions/index.html'
    context_object_name = 'contract_versions'

    def get_queryset(self):
        return ContractVersion.objects.order_by('start')

    @staticmethod
    def new(request):
        form = ContractVersionForm()
        return render(request, 'form.html', {'form': form, 'action_url': reverse('dkapp:contract_versions')})

    def post(self, request):
        form = ContractVersionForm(request.POST)
        if form.is_valid():
            contract_version = form.save()
            return HttpResponseRedirect(reverse('dkapp:contract_version', args=(contract_version.id,)))

        return HttpResponseRedirect(reverse('dkapp:contacts'))


class AccountingEntriesView(generic.ListView):
    template_name = 'accounting_entries/index.html'
    context_object_name = 'accounting_entries'

    def get_queryset(self):
        return AccountingEntry.objects.order_by('date')

    @staticmethod
    def new(request):
        form = AccountingEntryForm()
        return render(request, 'form.html', {'form': form, 'action_url': reverse('dkapp:accounting_entries')})

    def post(self, request):
        form = AccountingEntryForm(request.POST)
        if form.is_valid():
            accounting_entry = form.save()
            return HttpResponseRedirect(reverse('dkapp:accounting_entry', args=(accounting_entry.id,)))

        return HttpResponseRedirect(reverse('dkapp:accounting_entries'))

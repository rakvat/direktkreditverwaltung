import urllib
from operator import attrgetter
from datetime import datetime

from django.http import HttpResponseRedirect, FileResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic

from dkapp.models import Contact, Contract, ContractVersion, AccountingEntry
from dkapp.forms import ContactForm, ContractForm, ContractVersionForm, AccountingEntryForm
from dkapp.operations.reports import (
    AverageInterestRateReport,
    InterestTransferListReport,
)
from dkapp.operations.pdf.thanks_letters import ThanksLettersGenerator


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
        contact_id = request.GET.get('contact_id')
        contact = Contact.objects.get(pk=contact_id) if contact_id else None
        form = ContractForm(contact=contact, contract_version=None)
        return render(request, 'form.html', {
            'form': form,
            'action_url': reverse('dkapp:contracts')},
         )

    def post(self, request):
        form = ContractForm(request.POST, contact=None, contract_version=None)
        if form.is_valid():
            contract = form.save()
            return HttpResponseRedirect(reverse('dkapp:contract', args=(contract.id,)))

        return HttpResponseRedirect(reverse('dkapp:contracts'))


class ContractsInterest(generic.TemplateView):
    template_name = 'contracts/interest.html'
    OUTPUT_FORMATS = {
        'html': 'HTML',
        'overview': 'PDF-Übersicht',
        'thanks': 'PDF-Dankesbriefe',
        'interest_letter': 'PDF-Zinsbriefe',
    }

    def get(self, request):
        this_year = datetime.now().year
        year = int(request.GET.get('year') or this_year)
        format = request.GET.get('format') or 'html'
        report = InterestTransferListReport.create(year)
        if format == 'html':
            return render(request, self.template_name, {
                'today': datetime.now().strftime('%d.%m.%Y'),
                'current_year': year,
                'current_format': format,
                'all_years': list(range(this_year, this_year-10, -1)),
                'all_formats': self.OUTPUT_FORMATS,
                'report': report,
            })
        else:
            pdf_generator = ThanksLettersGenerator(
                contacts=[data.contact for data in report.per_contract_data]
            )
            return FileResponse(pdf_generator.buffer, filename='thanks.pdf')

    @staticmethod
    def filter(request):
        year = request.POST.get('year') or datetime.now().year
        format = request.POST.get('format') or 'html'
        filter_args = {'year': year, 'format': format}
        filter_query_string = urllib.parse.urlencode(filter_args)
        return HttpResponseRedirect("?".join([reverse('dkapp:contracts_interest'), filter_query_string]))


class ContractsInterestTransferListView(generic.TemplateView):
    template_name = 'contracts/interest_transfer_list.html'

    def get(self, request):
        this_year = datetime.now().year
        year = int(request.GET.get('year') or this_year)
        return render(request, self.template_name, {
            'current_year': year,
            'all_years': list(range(this_year, this_year-10, -1)),
            'report': InterestTransferListReport.create(year),
        })

    def post(self, request):
        year = request.POST.get('year')
        return HttpResponseRedirect(
            reverse('dkapp:contracts_interest_transfer_list') + f"?year={year}"
        )


class ContractsAverageInterestView(generic.TemplateView):
    template_name = 'contracts/average_interest.html'

    def get(self, request):
        return render(request, self.template_name, {
            'report': AverageInterestRateReport.create(),
        })


class ContractsExpiringView(generic.ListView):
    template_name = 'contracts/expiring.html'
    context_object_name = 'contracts'

    def get_queryset(self):
        contracts = Contract.objects.order_by('created_at')
        # this could be done in SQL to avoid n+1 queries but I'll go for fast
        # dev speed here
        return sorted(filter(lambda c: c.balance > 0, contracts), key=attrgetter('expiring'))


class ContractView(generic.DetailView):
    model = Contract
    template_name = 'contracts/detail.html'

    @staticmethod
    def edit(request, *args, **kwargs):
        contract_id = kwargs['pk']
        contract = get_object_or_404(Contract, pk=contract_id)
        form = ContractForm(
            instance=contract,
            contact=contract.contact,
            contract_version=contract.last_version
        )
        return render(request, 'form.html', {
            'form': form,
            'action_url': reverse('dkapp:contract', args=(contract.id,)),
        })

    def post(self, *args, **kwargs):
        contract_id = kwargs['pk']
        contract = get_object_or_404(Contract, pk=contract_id)
        form = ContractForm(
            self.request.POST,
            instance=contract,
            contact=contract.contact,
            contract_version=contract.last_version,
        )
        if form.is_valid():
            form.save()

        return HttpResponseRedirect(reverse('dkapp:contract', args=(contract.id,)))


class ContractDeleteView(generic.edit.DeleteView):
    template_name = 'object_confirm_delete.html'

    def get_object(self, *args, **kwargs):
        return get_object_or_404(Contract, pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('dkapp:contracts')


class ContractVersionsView(generic.ListView):
    template_name = 'contract_versions/index.html'
    context_object_name = 'contract_versions'

    def get_queryset(self):
        return ContractVersion.objects.order_by('contract_id', 'start')

    @staticmethod
    def new(request, *args, **kwargs):
        contract_id = kwargs['pk']
        contract = get_object_or_404(Contract, pk=contract_id)
        form = ContractVersionForm(contract=contract)
        return render(request, 'form.html', {'form': form, 'action_url': reverse('dkapp:contract_versions')})

    def post(self, request):
        contract_id = request.POST.get('contract')
        contract = get_object_or_404(Contract, pk=contract_id)
        form = ContractVersionForm(request.POST, contract=contract)
        if form.is_valid():
            contract_version = form.save()
            return HttpResponseRedirect(reverse('dkapp:contract_version', args=(contract_version.id,)))

        return HttpResponseRedirect(reverse('dkapp:contacts'))


class ContractVersionView(generic.DetailView):
    model = ContractVersion
    template_name = 'contract_versions/detail.html'

    @staticmethod
    def edit(request, *args, **kwargs):
        contract_version_id = kwargs['pk']
        contract_version = get_object_or_404(ContractVersion, pk=contract_version_id)
        form = ContractVersionForm(instance=contract_version, contract=contract_version.contract)
        return render(request, 'form.html', {
            'form': form,
            'action_url': reverse('dkapp:contract_version', args=(contract_version.id,)),
        })

    def post(self, *args, **kwargs):
        contract_version_id = kwargs['pk']
        contract_version = get_object_or_404(ContractVersion, pk=contract_version_id)
        form = ContractVersionForm(self.request.POST, instance=contract_version, contract=contract_version.contract)
        if form.is_valid():
            form.save()

        return HttpResponseRedirect(reverse('dkapp:contract_version', args=(contract_version.id,)))


class ContractVersionDeleteView(generic.edit.DeleteView):
    template_name = 'object_confirm_delete.html'

    def get_object(self, *args, **kwargs):
        return get_object_or_404(ContractVersion, pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('dkapp:contract_versions')


class AccountingEntriesView(generic.ListView):
    template_name = 'accounting_entries/index.html'
    context_object_name = 'accounting_entries'

    def get_queryset(self, *args, **kwargs):
        contract_id = self.request.GET.get('contract_id')
        if contract_id is not None:
            return AccountingEntry.objects.filter(contract_id=contract_id).order_by('date')
        year = self.request.GET.get('year')
        if year is not None:
            return AccountingEntry.objects.filter(date__year=year).order_by('date')
        from_date = self.request.GET.get('from')
        to_date = self.request.GET.get('to')
        if from_date and to_date is not None:
            return AccountingEntry.objects.filter(
                date__gte=datetime.strptime(from_date, "%d.%m.%Y"),
                date__lte=datetime.strptime(to_date, "%d.%m.%Y"),
            ).order_by('date')
        return AccountingEntry.objects.order_by('date')

    def get_context_data(self, **kwargs):
        context = super(AccountingEntriesView, self).get_context_data(**kwargs)
        all_contracts = Contract.objects.order_by('number').all()
        context['all_contracts'] = all_contracts
        contract_id = self.request.GET.get('contract_id')
        if contract_id:
            context['contract_id'] = int(contract_id)
        year = self.request.GET.get('year')
        if year:
            context['year'] = year
        from_date = self.request.GET.get('from')
        to_date = self.request.GET.get('to')
        if from_date and to_date:
            context['from'] = from_date
            context['to'] = to_date
        return context

    @staticmethod
    def new(request, *args, **kwargs):
        contract_id = kwargs['pk']
        contract = get_object_or_404(Contract, pk=contract_id)
        form = AccountingEntryForm(contract=contract)
        return render(request, 'form.html', {'form': form, 'action_url': reverse('dkapp:accounting_entries')})

    @staticmethod
    def filter(request):
        filter_args = {}
        contract_id = request.POST.get('contract_id')
        if contract_id:
            filter_args['contract_id'] = contract_id
        year = request.POST.get('year')
        if year:
            filter_args['year'] = year
        from_date = request.POST.get('from')
        to_date = request.POST.get('to')
        if from_date and to_date:
            filter_args['from'] = from_date
            filter_args['to'] = to_date
        filter_query_string = urllib.parse.urlencode(filter_args)
        return HttpResponseRedirect("?".join([reverse('dkapp:accounting_entries'), filter_query_string]))

    def post(self, request):
        contract_id = request.POST.get('contract')
        contract = get_object_or_404(Contract, pk=contract_id)
        form = AccountingEntryForm(request.POST, contract=contract)
        if form.is_valid():
            accounting_entry = form.save()
            return HttpResponseRedirect(reverse('dkapp:accounting_entry', args=(accounting_entry.id,)))

        return HttpResponseRedirect(reverse('dkapp:accounting_entries'))


class AccountingEntryView(generic.DetailView):
    model = AccountingEntry
    template_name = 'accounting_entries/detail.html'

    @staticmethod
    def edit(request, *args, **kwargs):
        accounting_entry_id = kwargs['pk']
        accounting_entry = get_object_or_404(AccountingEntry, pk=accounting_entry_id)
        form = AccountingEntryForm(instance=accounting_entry, contract=accounting_entry.contract)
        return render(request, 'form.html', {
            'form': form,
            'action_url': reverse('dkapp:accounting_entry', args=(accounting_entry.id,)),
        })

    def post(self, *args, **kwargs):
        accounting_entry_id = kwargs['pk']
        accounting_entry = get_object_or_404(AccountingEntry, pk=accounting_entry_id)
        form = AccountingEntryForm(
            self.request.POST,
            instance=accounting_entry,
            contract=accounting_entry.contract,
        )
        if form.is_valid():
            form.save()

        return HttpResponseRedirect(reverse('dkapp:accounting_entry', args=(accounting_entry.id,)))


class AccountingEntryDeleteView(generic.edit.DeleteView):
    template_name = 'object_confirm_delete.html'

    def get_object(self, *args, **kwargs):
        return get_object_or_404(AccountingEntry, pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('dkapp:accounting_entries')

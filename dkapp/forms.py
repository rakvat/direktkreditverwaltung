from django import forms
from .models import Contact, Contract, ContractVersion, AccountingEntry


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        exclude = ['updated_at', 'created_at']
        widgets = {
            'email': forms.EmailInput(),
            'remark': forms.Textarea(),
        }
        labels = {
            "first_name": "Vorname",
            "last_name": "Nachname",
            "address": "Adresse",
            "phone": "Telefonnummer",
            "email": "E-Mail",
            "iban": "IBAN",
            "bic": "BIC",
            "bank_name": "Bankname",
            "remark": "Bemerkung",
        }


class ContractForm(forms.ModelForm):
    # These are fields from contract_version that are added in addition to the fields
    # from the contract model as a first contract version is created when
    # creating a contract.
    start = forms.DateField(
        input_formats=['%d.%m.%Y'],
        label="Start des Vertrags (letzte Version des Vertrags)"
    )
    duration_months = forms.IntegerField(
        required=False,
        label="Laufzeit in Monaten (letzte Version des Vertrags)"
    )
    duration_years = forms.IntegerField(
        required=False,
        label=" * ODER * Laufzeit in Jahren (letzte Version des Vertrags)",
    )
    interest_rate = forms.FloatField(
        label="Zinssatz (Angabe in Prozent, letzte Version des Vertrags)"
    )

    class Meta:
        model = Contract
        exclude = ['updated_at', 'created_at']
        widgets = {
            'number': forms.NumberInput(),
            'comment': forms.Textarea(),
        }
        labels = {
            "number": "Nummer",
            "contact": "Kontakt/Vertragspartner_in",
            "comment": "Bemerkung",
            "category": "Kategorie",
        }

    def __init__(self, *args, **kwargs):
        contact_id = kwargs.pop('contact_id')
        super(ContractForm, self).__init__(*args, **kwargs)
        self.fields['start'].widget.attrs['placeholder'] = "DD.MM.YYYY"
        if contact_id:
            contact = Contact.objects.get(pk=contact_id)
            self.fields['contact'].initial = contact

    def save(self, commit=True):
        contract = super(ContractForm, self).save(commit=commit)
        contract_version = ContractVersion(
            contract_id=contract.id,
            start=self.cleaned_data['start'],
            duration_months=self.cleaned_data['duration_months'],
            duration_years=self.cleaned_data['duration_years'],
            interest_rate=self.cleaned_data['interest_rate'] / 100.0,
            version=1,  # first version of contract
        )
        if contract_version and (contract_version.duration_years or contract_version.duration_months):
            contract_version.save()

        return contract


class ContractVersionForm(forms.Form):
    start = forms.DateTimeField()
    duration_months = forms.IntegerField()
    duration_years = forms.IntegerField()
    interest_rate = forms.FloatField()


class AccountingEntryForm(forms.Form):
    date = forms.DateTimeField
    amount = forms.FloatField()

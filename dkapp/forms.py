from django import forms
from .models import Contact


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


class ContractForm(forms.Form):
    number = forms.IntegerField()
    comment = forms.CharField(required=False)
    category = forms.ChoiceField(choices=[('Privat', 'Privat'), ('Syndikat', 'Syndikat'), ('Dritte', 'Dritte')])
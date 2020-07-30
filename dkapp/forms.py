from django import forms
from .models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model=Contact
        fields=('first_name', 'last_name')
        labels = {
            "first_name": "Vorname",
        }


class ContractForm(forms.Form):
    number = forms.IntegerField()
    # contact = forms.ForeignKey(Contact, on_delete=models.CASCADE)
    comment = forms.CharField(required=False)
    category = forms.ChoiceField(choices=[('Privat', 'Privat'), ('Syndikat', 'Syndikat'), ('Dritte', 'Dritte')])

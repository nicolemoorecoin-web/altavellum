from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label='Name', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Name'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder':'Email'}))
    subject = forms.CharField(max_length=100, label='Subject', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Subject'}))
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder':'Create a message here', 'rows': 7, 'cols': 30,}),
        label='Create a message here'
    )
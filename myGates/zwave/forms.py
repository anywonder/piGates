from django import forms

class NewZWaveControllerForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput)
    location = forms.CharField(widget=forms.TextInput)
    ipaddress = forms.IPAddressField(widget=forms.TextInput)



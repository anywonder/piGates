from django import forms

class NewCameraForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput)
    location = forms.CharField(widget=forms.TextInput)
    ipaddress = forms.IPAddressField(widget=forms.TextInput)


class CameraSettingsForm(forms.Form):
    triggerdetectionlevel = forms.IntegerField(widget=forms.TextInput)
    detectionlevel = forms.IntegerField(widget=forms.TextInput, label='Detection Level')
    triggerdetectionlimit = forms.IntegerField(widget=forms.TextInput)
    sensitivity = forms.IntegerField(widget=forms.TextInput)

# class CameraSettingsForm(forms.Form):
#     subject = forms.CharField()
#     email = forms.EmailField(required=False)
#     message = forms.CharField(widget=forms.Textarea)

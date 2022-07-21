from django import forms
 
class UserForm(forms.Form):
    name = forms.CharField()
    age = forms.IntegerField()
    check1 = forms.ChoiceField(choices=((1, "English"), (2, "German"), (3, "French")), widget=forms.RadioSelect)

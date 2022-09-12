from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from .models import AdvUser, AllBackTests
from .strategies_list import Available_strategies
from .apps import user_registered

class UserForm(forms.Form):
    name = forms.CharField()
    age = forms.IntegerField()
    check1 = forms.ChoiceField(choices=((1, "English"), (2, "German"), (3, "French")), widget=forms.RadioSelect)

class ChangeUserInfoForm(forms.ModelForm):
    email = forms.EmailField(required= True, label= 'Email address')
    
    class Meta:
        model= AdvUser
        fields= ('username', 'email', 'first_name', 'last_name', 'send_messages')
        
class RegisterUserForm(forms.ModelForm):
    email = forms.EmailField(required= True, label= 'Email address')
    password1 = forms.CharField(label = 'Password', widget = forms.PasswordInput,
                               help_text = password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label = 'Password (again)', widget = forms.PasswordInput,
                               help_text = 'Enter the password again')

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1
    
    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError('Passwords do not match', code = 'password_mismatch')}
            raise ValidationError(errors)
            
    def save(self, commit = True):
        user = super().save(commit = False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()
        user_registered.send(RegisterUserForm, instance = user)
        return user
    
    class Meta:
        model= AdvUser
        fields= ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'send_messages')



strategies_value = Available_strategies.strategies_names_tuple #[('0', 'none')]
reports_value = [('0', 'none')]
#strategies_value = [('1', 'Strategy-1'), ('2', 'Strategy-2'), ('3', 'Strategy-3'), ('4', 'Strategy-4'), ('5', 'Strategy-5')]
#reports_value = [('1', 'Report-1'), ('2', 'Report-2'), ('3', 'Report-3'), ('4', 'Report-4'), ('5', 'Report-5')]

class ChoiseStrategyForm(forms.Form):
    f_strategies = forms.ChoiceField(label="Strategies:", initial='0', choices = strategies_value, required=True)
    f_text_log = forms.CharField(widget= forms.Textarea(attrs={'rows':'5', 'cols':90}), disabled = True, required=False)

class CreateReportForm(forms.Form):
    def __init__(self, data, *args, **kwargs):
#        try:
#            dynamic_choices = kwargs.pop('dynamic_choices')
#        except KeyError:
#            dynamic_choices = None # if normal form
#        super(CreateReportForm, self).__init__(*args, **kwargs)
        super().__init__(*args, **kwargs)
#        if dynamic_choices is not None:
        self.fields['f_reports'].choices = data #dynamic_choices
#        self.fields['f_reports'].initial = '0'
#        self.fields['f_reports'].queryset = data
       
    f_reports = forms.ChoiceField(label="Back test results:", initial='0', choices = reports_value, required=True)
#    f_reports = forms.ChoiceField()
    f_text_log = forms.CharField(widget= forms.Textarea(attrs={'rows':'5', 'cols':90}), disabled = True, required=False)

class BackTestForm(forms.Form):
#    f_strategies = forms.ChoiceField(label="Strategies:", initial='0', choices = strategies_value, required=True)
    f_strategies = forms.CharField(label="Strategy:", initial='none', disabled = True, required=True)
    f_reports = forms.ChoiceField(label="Test results:", initial='0', choices = reports_value, required=False)
    f_parts = forms.ChoiceField(label="Choise pairs part:", initial=1, choices=((1, "Part 1"), (2, "Part 2"), (3, "Part 3"), (4, "Part 4")), widget=forms.RadioSelect, required=False)
    
    f_series_len = forms.IntegerField(label="Series length (N):", initial=4, widget=forms.NumberInput( attrs={'size':'3'}), required=False)
    f_price_inc = forms.IntegerField(label="Price incriase in N candles (P):", initial=4, widget=forms.NumberInput( attrs={'size':'3'}), required=False)
    f_persent_same = forms.IntegerField(label="Persen of same candles (R):", initial=80, min_value=0, max_value=100, widget=forms.NumberInput( attrs={'size':'3'}), required=False)
    
    f_min_roi_time1 = forms.IntegerField(initial=0, min_value=0, max_value=60, widget=forms.NumberInput( attrs={'size':'3'}), disabled = True, required=False)
    f_min_roi_time2 = forms.IntegerField(initial=24, min_value=0, max_value=60, widget=forms.NumberInput( attrs={'size':'3'}), disabled = True, required=False)
    f_min_roi_time3 = forms.IntegerField(initial=30, min_value=0, max_value=60, widget=forms.NumberInput( attrs={'size':'3'}), disabled = True, required=False)
    f_min_roi_time4 = forms.IntegerField(initial=60, min_value=0, max_value=60, widget=forms.NumberInput( attrs={'size':'3'}), disabled = True, required=False)
    f_min_roi_value1 = forms.DecimalField(initial=4.5, min_value=0, max_value=100, decimal_places=1, widget=forms.NumberInput( attrs={'size':'3'}), required=False)
    f_min_roi_value2 = forms.DecimalField(initial=0, min_value=0, max_value=100, decimal_places=1, widget=forms.NumberInput( attrs={'size':'3'}), required=False)
    f_min_roi_value3 = forms.DecimalField(initial=0, min_value=0, max_value=100, decimal_places=1, widget=forms.NumberInput( attrs={'size':'3'}), required=False)
    f_min_roi_value4 = forms.DecimalField(initial=0, min_value=0, max_value=100, decimal_places=1, widget=forms.NumberInput( attrs={'size':'3'}), required=False)
    
#    f_roi_flags = forms.MultipleChoiceField(label="Choise pairs part:", initial=1, choices=((1, "ROI 1"), (2, "ROI 2"), (3, "ROI 3"), (4, "ROI 4")), widget=forms.CheckboxSelectMultiple, required=False)
    
    f_des_stop_loss = forms.DecimalField(label="Dsired Stop-loss value (S):", initial=0.5, decimal_places=1, widget=forms.NumberInput( attrs={'size':'3'}), required=False)
    f_stop_loss = forms.DecimalField(label="Stop-loss (after 0 min):", initial=3.0, decimal_places=1, widget=forms.NumberInput( attrs={'size':'3'}), required=False)
    f_my_stop_loss_time = forms.IntegerField(label="My Stop-loss (after [n] min):", initial=32,  min_value=0, max_value=60, widget=forms.NumberInput( attrs={'size':'3'}), required=False)
    f_my_stop_loss_value = forms.DecimalField(initial=0.1, min_value=0, max_value=100, decimal_places=1, widget=forms.NumberInput( attrs={'size':'3'}), required=False)
    
    f_movement_roi = forms.FloatField(label="Movement ROI (MR):", initial=2.5, min_value=0, max_value=100, widget=forms.NumberInput( attrs={'size':'3'}), required=False)
    
    f_text_log = forms.CharField(widget= forms.Textarea(attrs={'rows':'5', 'cols':90}), disabled = True, required=False)

#    def __init__(self, *args, **kwargs):
#         super(BackTestForm, self).__init__(*args, **kwargs)
    
#    class Meta:
#       model =  AllBackTests
#	   fields = ('f_strategies', 'f_reports', 'f_parts', 'f_series_len', 'f_price_inc', 'f_persent_same', 'f_roi_flags', 'f_min_roi_time1', 'f_min_roi_time2', 'f_min_roi_time3', 'f_min_roi_time4',
#                'f_min_roi_value1', 'f_min_roi_value2', 'f_min_roi_value3', 'f_min_roi_value4', 'f_movement_roi', 'f_des_stop_loss', 'f_stop_loss', 'f_my_stop_loss_time', 'f_my_stop_loss_value',
#                'f_text_log')

class TestBackTestForm(forms.ModelForm):
    class Meta:
        model = AllBackTests
        fields = '__all__'
        widgets = {'owner': forms.HiddenInput}


        

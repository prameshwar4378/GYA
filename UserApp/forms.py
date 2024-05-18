
from django import forms
from AdminApp.models import *

class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ['full_name', 'gender', 'dob', 'relation','phone_number']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            # 'phone_number': forms.CharField(attrs={'type': 'number'}),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and len(str(phone_number)) != 10:
            raise forms.ValidationError("Mobile number must be 10 digits.") 
        return phone_number
 
 

# class GuestSelectionTiketForm(forms.Form):
#     members = forms.ModelMultipleChoiceField(
#         queryset=Guest.objects.none(),  # Initial empty queryset
#         widget=forms.CheckboxSelectMultiple,
#         required=False
#     )

#     def __init__(self, user, *args, **kwargs):
#         super(GuestSelectionTiketForm, self).__init__(*args, **kwargs)
#         self.fields['members'].queryset = Guest.objects.filter(user=user)

from django import forms
from AdminApp.models import *

class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ['full_name', 'gender', 'dob', 'relation']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }
 
 

# class GuestSelectionTiketForm(forms.Form):
#     members = forms.ModelMultipleChoiceField(
#         queryset=Guest.objects.none(),  # Initial empty queryset
#         widget=forms.CheckboxSelectMultiple,
#         required=False
#     )

#     def __init__(self, user, *args, **kwargs):
#         super(GuestSelectionTiketForm, self).__init__(*args, **kwargs)
#         self.fields['members'].queryset = Guest.objects.filter(user=user)
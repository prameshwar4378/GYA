
from django import forms
from AdminApp.models import *

class FamilyMemberForm(forms.ModelForm):
    class Meta:
        model = FamilyMember
        fields = ['full_name', 'gender', 'age', 'relation']
 
 

class FamilyMemberSelectionTiketForm(forms.Form):
    members = forms.ModelMultipleChoiceField(
        queryset=FamilyMember.objects.none(),  # Initial empty queryset
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, user, *args, **kwargs):
        super(FamilyMemberSelectionTiketForm, self).__init__(*args, **kwargs)
        self.fields['members'].queryset = FamilyMember.objects.filter(user=user)
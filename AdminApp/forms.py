from django import forms
from .models import *
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404


GENDER = (
    ("Male", "Male"),
    ("Female", "Female")
)

class RegistrationForm(forms.ModelForm): 
    phone_number = forms.IntegerField(widget=forms.NumberInput(attrs={'type': 'number'}))
    full_name = forms.CharField(max_length=50)
    gender = forms.ChoiceField(choices=GENDER)  # Use ChoiceField for choices
    age = forms.IntegerField()  # Removed invalid max_length argument
     
    class Meta:
        model = User
        fields = ['email', ]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone_number'].required = True
        self.fields['full_name'].required = True
        self.fields['gender'].required = True
        self.fields['age'].required = True

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and len(str(phone_number)) != 10:
            raise forms.ValidationError("Mobile number must be 10 digits.")
        if OTP.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("A user with this mobile number already exists.")
        return phone_number

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False) 
        user.set_password("Pass@123")
        if commit:
            user.save()
            family_member = FamilyMember(
                user=user,
                name=self.cleaned_data['full_name'],
                mobile=user['phone_number'],  # assuming you want to use the same as phone_number
                gender=self.cleaned_data['gender'],
                age=self.cleaned_data['age'],
                relation=self.cleaned_data['relation']
            )
            family_member.save()
        return user



class ComiteeYearForm(forms.ModelForm):
    class Meta:
        model = ComiteeYear
        fields = [ 'year']
 
class ComiteeMemberForm(forms.ModelForm):
    class Meta:
        model = ComiteeMember
        fields = [ 'year',"image","name","position"]
 

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'start_time', 'end_time', 'organizer', 'status', 'capacity', 'category', 'url']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
 

class EventThumbnailForm(forms.ModelForm):
    class Meta:
        model = EventThumbnail
        fields = ['thumbnail']
 
 

class EventImagesBrochureForm(forms.ModelForm):
    class Meta:
        model = EventImagesBrochure
        fields = ['image', 'brochure']
        widgets = {
            'brochure': forms.FileInput(attrs={'accept': 'application/pdf'}),
        }

    def clean_brochure(self):
        brochure = self.cleaned_data.get('brochure', False)
        if brochure and not brochure.name.endswith('.pdf'):
            raise ValidationError("Only PDF files are accepted for the brochure.")
        return brochure

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        brochure = cleaned_data.get('brochure')
        if not image and not brochure:
            raise ValidationError("At least one of the fields (image or brochure) must be filled.")
        return cleaned_data



class PhotoGalleryForm(forms.ModelForm):
    class Meta:
        model = PhotoGallery
        fields = ['caption', 'image']
 
class EventTicketPriceForm(forms.ModelForm):
    class Meta:
        model = EventTicketPrice
        fields = ['min_age', 'max_age', 'price']
 
 
class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
 
class LoginUsingOTPForm(forms.Form):
    username = forms.CharField(label='Email / Mobile Number')
 
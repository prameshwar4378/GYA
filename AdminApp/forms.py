from django import forms
from .models import *
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib import messages


GENDER = (
    ("Male", "Male"),
    ("Female", "Female")
)

class RegistrationForm(forms.ModelForm): 
    phone_number = forms.IntegerField(widget=forms.NumberInput(attrs={'type': 'number'}))
    full_name = forms.CharField(max_length=50)
    gender = forms.ChoiceField(choices=GENDER)   
    dob = forms.DateField(widget=forms.NumberInput(attrs={'type': 'date'}),required=True)  

    class Meta:
        model = User
        fields = ['email', ]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone_number'].required = True
        self.fields['full_name'].required = True
        self.fields['gender'].required = True
        self.fields['dob'].required = True

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
            guests = Guest(
                user=user,
                name=self.cleaned_data['full_name'],
                mobile=user['phone_number'],  # assuming you want to use the same as phone_number
                gender=self.cleaned_data['gender'],
                dob=self.cleaned_data['dob'], 
                member_id=self.cleaned_data['member_id'], 
            )
            guests.save()
        return user


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    email = forms.EmailField(required=True, label="Email")
    phone_number = forms.CharField(max_length=15, required=True, label="Phone Number")

    class Meta:
        model = UserProfile
        fields = ['member_id', 'dob', 'gender']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(UserProfileForm, self).__init__(*args, **kwargs)
        
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['email'].initial = user.email
            try:
                otp = OTP.objects.get(user=user)
                self.fields['phone_number'].initial = otp.phone_number
            except OTP.DoesNotExist:
                self.fields['phone_number'].initial = ''

    def save(self, commit=True):
        user_profile = super(UserProfileForm, self).save(commit=False)
        user = user_profile.user
        
        user.first_name = self.cleaned_data['first_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            user_profile.save()
            otp, created = OTP.objects.get_or_create(user=user)
            otp.phone_number = self.cleaned_data['phone_number']
            otp.save()
        
        return user_profile
    

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
        fields = ['title', 'description', 'location', 'start_time', 'end_time', 'organizer', 'status', 'ticket_price', 'url']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
 

class EventThumbnailForm(forms.ModelForm):
    class Meta:
        model = EventThumbnail
        fields = ['thumbnail']
 

class EventTicketPriceForm(forms.ModelForm):
    class Meta:
        model = EventTicketPrice
        fields = ["member_price","guest_price"]
 

class UploadTicketFileForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["ticket_file"]
        labels={
            "ticket_file":"Upload Ticket"
        }
 


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


class VideoGalleryForm(forms.ModelForm):
    class Meta:
        model = VideoGallery
        fields = ['caption', 'video_link']


class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['content', 'is_active', 'url']
        
class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'thumbnail','date', 'is_active']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        } 

class NewsPhotosVideosForm(forms.ModelForm):
    class Meta:
        model = NewsPhotosVideos
        fields = ['news', 'image','video_link']
        
class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
 
class LoginUsingOTPForm(forms.Form):
    username = forms.CharField(label='Email / Mobile Number')
 
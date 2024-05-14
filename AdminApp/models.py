import random
import string
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
import threading
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError 
import random


class ComiteeYear(models.Model):
    year=models.CharField(max_length=20)
    def __str__(self):
       return self.year
 

class ComiteeMember(models.Model):
    year=models.ForeignKey(ComiteeYear, on_delete=models.CASCADE)
    image=models.ImageField(upload_to="ComiteeMembers/", height_field=None, width_field=None, max_length=300)
    name=models.CharField(max_length=50)
    position=models.CharField(max_length=50)
    def __str__(self):
       return self.year.year

GENDER = (
    ("Male", "Male"),
    ("Female", "Female")
)

class OTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    otp = models.CharField(max_length=6)
    phone_number = models.CharField(max_length=15, null=True,db_index=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    member_id = models.CharField(max_length=20, null=True, unique=True)
    dob = models.DateField(auto_now=False, auto_now_add=False)
    gender = models.CharField(max_length=50, choices=GENDER, null=True)
    is_member = models.BooleanField(default=False)
    paid_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    registration_date = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        if not self.member_id:
            last_member = UserProfile.objects.all().order_by('-member_id').first()
            if last_member.member_id:
                last_number = int(last_member.member_id.split('MBR')[1])
                new_number = last_number + 1
            else:
                new_number = 201
            self.member_id = f'MBR{new_number}'
        super().save(*args, **kwargs)

RELATION = (
    ("Self", "Self"),
    ("Mother", "Mother"),
    ("Father", "Father"),
    ("Son", "Son"),
    ("Daughter", "Daughter"),
    ("Brother", "Brother"),
    ("Sister", "Sister"),
    ("Grandfather", "Grandfather"),
    ("Grandmother", "Grandmother"),
    ("Grandson", "Grandson"),
    ("Granddaughter", "Granddaughter"),
    ("Uncle", "Uncle"),
    ("Aunt", "Aunt"),
    ("Nephew", "Nephew"),
    ("Niece", "Niece"),
    ("Cousin", "Cousin"),
)

class Guest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=50, choices=GENDER)
    dob = models.DateField(auto_now_add=False,auto_now=False)
    relation = models.CharField(max_length=50, choices=RELATION)
    phone_number = models.CharField(max_length=50, choices=RELATION)
 
    def __str__(self):
        return self.full_name

class Event(models.Model):
    STATUS_CHOICES = (
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=300)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    organizer =  models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='planned')
    url = models.URLField(blank=True, null=True)
    ticket_price = models.IntegerField(default=0)


    def __str__(self):
        return self.title


class EventTicketPrice(models.Model):
    event=models.ForeignKey(Event, on_delete=models.CASCADE,null=True)
    member_price=models.IntegerField(default=0)
    guest_price=models.IntegerField(default=0)
    def __str__(self):
        return f"{self.event.title} Ticket Price"

class Ticket(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    ticket_id=models.CharField(max_length=50)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    is_paid=models.BooleanField(default=False)
    booking_date=models.DateTimeField(auto_now=True)
    ticket_file=models.FileField(upload_to="Tickets/", max_length=1000,null=True,blank=True)
    paid_amount=models.IntegerField(default=0)

    class Meta:
        ordering = ['-booking_date']

    def __str__(self):
        return f"{self.event.title} Ticket"
    
    def save(self, *args, **kwargs):
        if not self.ticket_id:
            # Generate a ticket ID in the format TKT + 11 random digits
            self.ticket_id = 'TKT' + ''.join([str(random.randint(0, 9)) for _ in range(11)])
        super(Ticket, self).save(*args, **kwargs)


class BookingMembers(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    guests=models.ForeignKey(Guest, on_delete=models.CASCADE,null=True,blank=True)
    member=models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True) 
    def __str__(self):
        return f"{self.ticket.event.title} Booking Members"


class EventThumbnail(models.Model):
    event = models.OneToOneField("Event", on_delete=models.CASCADE)
    thumbnail = models.ImageField(upload_to="event_thumbnail/", blank=False, null=True)

    def __str__(self):
        return f"{self.event.title} Thumbnail"
    
class EventImagesBrochure(models.Model):
    event = models.ForeignKey("Event", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="event_images/", blank=True, null=True)
    brochure = models.FileField(upload_to="event_brochures/", blank=True, null=True)

    def __str__(self):
        return f"{self.event.title} Image and Brochure"
    


class PhotoGallery(models.Model):
    caption = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to="photo_gallery/")

    def __str__(self):
        return f"{self.caption} Image"
    


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
 
class OTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    otp = models.CharField(max_length=6)
    phone_number = models.CharField(max_length=15, null=True,db_index=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    is_member = models.BooleanField(default=False)
    paid_date=models.DateTimeField(auto_now=False, auto_now_add=True)

GENDER = (
    ("Male", "Male"),
    ("Female", "Female")
)

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

class FamilyMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=50, choices=GENDER)
    age = models.IntegerField()
    relation = models.CharField(max_length=50, choices=RELATION)
 
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
    capacity = models.IntegerField()
    category = models.CharField(max_length=100)
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

     
class EventTicketPrice(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    min_age = models.IntegerField()
    max_age = models.IntegerField()
    price = models.IntegerField()
    def __str__(self):
        return f"{self.event.title} Ticket Price"

class Ticket(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    ticket_id=models.CharField(max_length=50)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    is_paid=models.BooleanField(default=False)
    booking_date=models.DateTimeField(auto_now=True)

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
    family_member=models.ForeignKey(FamilyMember, on_delete=models.CASCADE)
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
    


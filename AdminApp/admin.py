from django.contrib import admin
from .models import *# Register your models here.

admin.site.register(ComiteeYear)
admin.site.register(ComiteeMember)
admin.site.register(PhotoGallery)
admin.site.register(Ticket)
admin.site.register(BookingMembers)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'start_time', 'end_time', 'organizer']

@admin.register(EventTicketPrice)
class EventTicketPriceAdmin(admin.ModelAdmin):
    list_display = ['event', 'min_age', 'max_age', 'price']
    def save_model(self, request, obj, form, change):
        obj.clean()
        super().save_model(request, obj, form, change)
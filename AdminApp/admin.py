from django.contrib import admin
from .models import *# Register your models here.

admin.site.register(ComiteeYear)
admin.site.register(ComiteeMember)
admin.site.register(PhotoGallery)
admin.site.register(Ticket)
admin.site.register(BookingMembers)
admin.site.register(Advertisement)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'start_time', 'end_time', 'organizer']
    list_filter = ('title', 'status')
    search_fields = ('title', 'status')
 


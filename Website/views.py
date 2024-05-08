from django.shortcuts import render,get_object_or_404
from AdminApp.models import *
# Create your views here.


def index(request): 
    event=Event.objects.select_related()
    if event.exists():
      event_exist=True
    else:
       event_exist=False

    return render(request,"index.html",{"events":event,"event_exist":event_exist})

 
def event_details(request,id):
    latest_events = Event.objects.select_related('eventthumbnail').order_by('-start_time')[:10]
    event_details = get_object_or_404(Event, id=id)
    event_images_or_brochure=EventImagesBrochure.objects.filter(event=event_details)
    return render(request, "website_event_details.html", {"letest_events":latest_events,"event_details": event_details,"event_images_or_brochure":event_images_or_brochure})


def about(request):
    return render(request,"index.html")


def commitee_members(request, id): 
    data=ComiteeMember.objects.filter(year=id)
    year=data.first()
    return render(request,"website_commitee_members.html",{"data":data,"year":year})



def photo_gallery(request): 
    images=PhotoGallery.objects.all().select_related()
    return render(request,"website_photo_gallery.html",{"images":images})


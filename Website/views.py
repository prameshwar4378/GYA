from django.shortcuts import render,get_object_or_404
from AdminApp.models import *
# Create your views here.


def index(request): 
    event=Event.objects.select_related()
    add=Advertisement.objects.all()
    news=News.objects.all()
    is_add_available=add.filter(is_active=True)
    if event.exists():
      event_exist=True
    else:
       event_exist=False
    return render(request,"index.html",{"news":news,"events":event,"event_exist":event_exist,"add":add,"is_add_available":is_add_available})

 
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


def news_details(request,id):
    # try:
        latest_news = News.objects.select_related().order_by('-id')[:10]
        for i in latest_news:
            print(i.thumbnail)
            
        news_details = get_object_or_404(News, id=id)
        news_photos=NewsPhotosVideos.objects.filter(image__isnull=False,news=news_details)
        return render(request, "website_news_details.html", {"latest_news":latest_news,"news_details": news_details,"news_photos":news_photos})
    # except Exception as e: 
    #     return render(request, "404.html", status=404)


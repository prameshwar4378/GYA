from django.shortcuts import render,get_object_or_404
from AdminApp.models import *
# Create your views here.


def index(request): 
    event=Event.objects.filter(is_publish=True).select_related()
    add=Advertisement.objects.all()
    news=News.objects.all()
    is_add_available=add.filter(is_active=True)
    if event.exists():
      event_exist=True
    else:
       event_exist=False
    return render(request,"index.html",{"news":news,"events":event,"event_exist":event_exist,"add":add,"is_add_available":is_add_available})

 
def event_details(request,id):
    latest_events = Event.objects.filter(is_publish=True).select_related('eventthumbnail').order_by('-start_time')[:10]
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

import re

def extract_video_id(embed_url):
    match = re.search(r"embed/([a-zA-Z0-9_-]+)", embed_url)
    if match:
        return match.group(1)
    return None

def news_details(request,id):
    # try:
        latest_news = News.objects.select_related().order_by('-id')[:10]
        news_details = get_object_or_404(News, id=id)
        
        photos_videos = NewsPhotosVideos.objects.filter(news=news_details) 
        video_data=[]
        for embed_link in photos_videos:
            embed_url= embed_link.video_link
            video_id=extract_video_id(embed_url)
            if video_id:
                video_data.append(
                    {"thumbnail_url":f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                    "video_url":f"https://www.youtube.com/embed/{video_id}",
                    "id":embed_link.id} 
                )

        news_photos=NewsPhotosVideos.objects.filter(image__isnull=False,news=news_details)
        return render(request, "website_news_details.html", {"latest_news":latest_news,"news_details": news_details,"news_photos":news_photos,'video_data': video_data})
    # except Exception as e: 
    #     return render(request, "404.html", status=404)


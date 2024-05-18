from django.urls import path
from Website.views import *
urlpatterns = [  path('commitee_members/<int:id>/', commitee_members, name="website_commitee_members"),
    path('photo_gallery/', photo_gallery, name="website_photo_gallery"),
    path('event_details/<int:id>', event_details, name='website_event_details'),
    path('news_details/<int:id>', news_details, name='website_news_details'),
]

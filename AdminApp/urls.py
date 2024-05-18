from django.urls import path
from AdminApp.views import *
urlpatterns = [
    path('dashboard/', admin_dashboard, name="admin_dashboard"),
    path('booking_list/', booking_list, name="admin_booking_list"),
    path('manage_booking/<int:id>/', manage_booking, name="admin_manage_booking"),
    path('delete_booking/<int:id>/', delete_booking, name="admin_delete_booking"),
    path('upload_ticket/', upload_ticket, name="admin_upload_ticket"),
    path('event_list/', event_list, name="admin_event_list"),
    path('comitee_year_list/', comitee_year_list, name="admin_comitee_year_list"),
    path('update_comitee_year/', update_comitee_year, name="admin_update_comitee_year"),
    path('delete_comitee_year/<int:id>', delete_comitee_year, name="admin_delete_comitee_year"),
    path('comitee_member_list/', comitee_member_list, name="admin_comitee_member_list"),
    path('update_comitee_member/', update_comitee_member, name="admin_update_comitee_member"),
    path('delete_comitee_member/<int:id>', delete_comitee_member, name="admin_delete_comitee_member"),

    path('create_event/', create_event, name="create_event"),
    path('update_event/<int:id>', update_event, name="update_event"),
    path('delete_event/<int:id>', delete_event, name="delete_event"),
    path('event_details/<int:id>', event_details, name="admin_event_details"),
    path('add_event_ticket_price/', add_event_ticket_price, name="admin_add_event_ticket_price"),
    path('custom_logout/', custom_logout, name="custom_logout"),

    path('delete_event_ticket_price/<int:id>', delete_event_ticket_price, name="admin_delete_event_ticket_price"),
    path('delete_event_brochure/<int:id>', delete_event_brochure, name="admin_delete_event_brochure"),
    path('delete_event_images/<int:id>', delete_event_images, name="admin_delete_event_images"),
    path('create_event_thumbnail/', create_event_thumbnail, name="create_event_thumbnail"),

    path('members_list/', members_list, name="admin_members_list"),
    path('member_details/<int:id>', member_details, name="admin_member_details"),
    path('update_member_profile/<int:id>', update_member_profile, name="admin_update_member_profile"),
    path('delete_member_user/<int:id>', delete_member_user, name="admin_delete_member_user"),

    path('photo_gallery_list/', photo_gallery_list, name="admin_photo_gallery_list"),
    path('create_photo_for_gallery/', create_photo_for_gallery, name="admin_create_photo_for_gallery"),
    path('delete_photo_from_gallery/<int:id>', delete_photo_from_gallery, name="admin_delete_photo_from_gallery"),
    
    path('advertisement_list/', advertisement_list, name="admin_advertisement_list"),
    path('create_advertisement/', create_advertisement, name="admin_create_advertisement"),
    path('update_advertisement/', update_advertisement, name="admin_update_advertisement"),
    path('delete_advertisement/<int:id>', delete_advertisement, name="admin_delete_advertisement"),

    path('news_list/', news_list, name='admin_news_list'),
    path('create_news/', create_news, name='admin_create_news'),
    path('update_news/<int:id>/', update_news, name='admin_update_news'),
    path('delete_news/<int:id>/', delete_news, name='admin_delete_news'),
    path('create_news_photos_videos/', create_news_photos_videos, name='admin_create_news_photos_videos'),
    path('news_details/<int:id>/', news_details, name='admin_news_details'),
    path('delete_news_photos/<int:id>/', delete_news_photos, name='admin_delete_news_photos'),
    path('delete_news_video/<int:id>/', delete_news_video, name='admin_delete_news_video'),


]

from django.urls import path
from UserApp.views import *
urlpatterns = [
    path('dashboard/', user_dashboard, name="user_dashboard"),
    path('family_member/', family_member, name="user_family_member"),
    path('user_create_family_member/', user_create_family_member, name="user_create_family_member"),
    path('update_family_member/', update_family_member, name='user_update_family_member'),
    path('delete_family_member/<int:id>', delete_family_member, name='user_delete_family_member'),
 
    path('events/', events, name='user_events'),
    path('event_details/<int:id>', event_details, name='user_event_details'),

    path('customize_family_member_for_booking/<int:id>', customize_family_member_for_booking, name='user_customize_family_member_for_booking'),
    path('ticket_overview/<int:id>', ticket_overview, name='user_ticket_overview'),

    path('delete_family_member_from_ticket/<int:id>', delete_family_member_from_ticket, name='user_delete_family_member_from_ticket'),
    path('add_family_member_in_ticket/', add_family_member_in_ticket, name='user_add_family_member_in_ticket'),
    path('bookings/', bookings, name='user_bookings'),
    path('delete_ticket/<int:id>', delete_ticket, name='user_delete_ticket'),
    path('pay_event_price/<int:id>', pay_event_price, name='user_pay_event_price'),
    
]

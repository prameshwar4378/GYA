from django.urls import path
from UserApp.views import *
urlpatterns = [
    path('dashboard/', user_dashboard, name="user_dashboard"),
    path('guests/', guests, name="user_guests"),
    path('user_create_guests/', user_create_guests, name="user_create_guests"),
    path('update_guests/', update_guests, name='user_update_guests'),
    path('delete_guests/<int:id>', delete_guests, name='user_delete_guests'),
 
    path('events/', events, name='user_events'),
    path('event_details/<int:id>', event_details, name='user_event_details'),

    path('event_ticket_prices/<int:id>', event_ticket_prices, name='user_event_ticket_prices'),
    path('ticket_overview/<int:id>', ticket_overview, name='user_ticket_overview'),
    path('get_member_details_for_booking/', get_member_details_for_booking, name='user_get_member_details_for_booking'),
 
    path('delete_member_and_guest_from_ticket/<int:id>', delete_member_and_guest_from_ticket, name='user_delete_member_and_guest_from_ticket'),
    path('add_guests_in_ticket/', add_guests_in_ticket, name='user_add_guests_in_ticket'),
    path('add_member_in_ticket/', add_member_in_ticket, name='user_add_member_in_ticket'),
    path('bookings/', bookings, name='user_bookings'),
    path('delete_ticket/<int:id>', delete_ticket, name='user_delete_ticket'),
    path('pay_event_price/', pay_event_price, name='user_pay_event_price'),
    
]

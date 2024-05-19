import django_filters
from django import forms
from .models import Ticket
from django.forms import DateInput

class Booking_List_Filter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        field_name='booking_date',
        lookup_expr='gte',
        widget=DateInput(attrs={'type': 'date'}),
        label='Start Date'
    )
    end_date = django_filters.DateFilter(
        field_name='booking_date',
        lookup_expr='lte',
        widget=DateInput(attrs={'type': 'date'}),
        label='End Date'
    )
    event = django_filters.CharFilter(
        field_name='event__title',  # Filter by event title
        lookup_expr='icontains',
        label='Event'
    ) 
    class Meta:
        model = Ticket
        fields = ['event', 'start_date', 'end_date', 'is_paid']

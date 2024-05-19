from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .forms import *
from django.db import IntegrityError, DatabaseError
from django.core.exceptions import ObjectDoesNotExist 
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.http import JsonResponse


def user_is_member(view_func):
    @wraps(view_func)
    @login_required  # Use the built-in login_required decorator
    def _wrapped_view(request, *args, **kwargs):
        user_profile = UserProfile.objects.filter(user=request.user).first()
        if user_profile and user_profile.is_member:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('/membership_payment')
    return _wrapped_view


    
@user_is_member    
@login_required
def user_dashboard(request):
    print(request.user)
    guests_count=Guest.objects.filter(user=request.user).count()
    participated_events=Ticket.objects.filter(user=request.user,is_paid=True).count()
    context={
        "guests_count":guests_count,
        "participated_events":participated_events,
    }
    return render(request,"user_dashboard.html",context)

   
@login_required
def guests(request):
    try:
        form = GuestForm()
        # Ensure only the user's Guests are fetched
        data = Guest.objects.filter(user=request.user).select_related().order_by("id")
        context = {
            "form": form,
            "data": data
        } 
        return render(request, "guests.html", context)
    except ObjectDoesNotExist:
        return render(request, "404.html")
    except Exception as e: 
        messages.error("getting 404 Error")
        return render(request, "404.html")

   
@login_required
def user_create_guests(request):
    if request.method == 'POST':
        form = GuestForm(request.POST)
        if form.is_valid():
            try:
                guests = form.save(commit=False)
                guests.user = request.user  # Assign the current user
                guests.save()
                messages.success(request, "Guest Created Successfully")
                return redirect('/user/guests')
            except (IntegrityError, DatabaseError) as e:
                messages.error(request, "There was an error saving the guest. Please try again.")
                return render(request, 'guests_create.html', {'form': form})
        else:
            data = Guest.objects.filter(user=request.user).select_related().order_by("id")
            messages.warning(request, "Enter valid information")
            return render(request, 'guests.html', {'form': form,'data':data})
    else:
        return redirect('/user/guests')
    

    
@login_required
def update_guests(request):
    if request.method == 'POST':
        guests_id = request.POST.get('txt_id')
        guests = get_object_or_404(Guest, id=guests_id)
        try:
            form = GuestForm(request.POST, instance=guests)
            if form.is_valid():
                form.save()
                messages.success(request, "Record Updated Successfully")
                return redirect("/user/guests")
            else:
                return render(request, 'update_guests.html', {'form': form})
        except (IntegrityError, DatabaseError) as e:
            messages.error(request, "There was a problem saving the update. Please try again.")
            return render(request, 'update_guests.html', {'form': form})
    return redirect("/user/guests")


@login_required
def delete_guests(request, id):
    try:
        with transaction.atomic():
            guests = Guest.objects.get(id=id)
            guests.delete()
            messages.success(request, "Guest deleted successfully.")
            return redirect("/user/guests")
    except ObjectDoesNotExist:
        # If the guest does not exist, handle the error
        messages.error(request, "Guest not found.")
        return render(request, '404.html', status=404)
    except IntegrityError:
        # Handle any potential integrity errors
        messages.error(request, "Database integrity error occurred while deleting the guest.")
        return render(request, '500.html', {'error': 'Integrity Error'}, status=500)
    except Exception as e:
        # Log the exception if needed and provide a user-friendly error page
        messages.error(request, f"An error occurred: {str(e)}")
        return render(request, '500.html', {'error': 'Unexpected Error'}, status=500)

 

@user_is_member    
@login_required
def events(request):
    try:
        events = Event.objects.filter(is_publish=True)
        return render(request, "user_events.html", {"data": events})
    except Exception as e:
        return render(request, "404.html", {
            "message": "An error occurred while retrieving events. Please try again later."
        }, status=500)


@user_is_member    
@login_required    
def event_details(request,id):
    try:
        latest_events = Event.objects.filter(is_publish=True).select_related('eventthumbnail').order_by('-start_time')[:10]
        event_details = get_object_or_404(Event, id=id)
        event_images_or_brochure=EventImagesBrochure.objects.filter(event=event_details)
        return render(request, "user_event_details.html", {"letest_events":latest_events,"event_details": event_details,"event_images_or_brochure":event_images_or_brochure})
    except Exception as e: 
        return render(request, "404.html", status=404)

@user_is_member    
@login_required
def event_ticket_prices(request, id):
    try:
        event = get_object_or_404(Event, id=id)
        try:
            event_price=get_object_or_404(EventTicketPrice,event=event)
        except Exception:
            EventTicketPrice.objects.create(event=event,member_price=0,guest_price=0)
            event_price=get_object_or_404(EventTicketPrice,event=event)

        if request.method == 'POST':
                ticket = Ticket.objects.create(user=request.user, event=event, is_paid=False)
                BookingMembers.objects.create(ticket=ticket,member=request.user)
                return redirect(f'/user/ticket_overview/{ticket.id}')
        return render(request, 'user_event_ticket_prices.html', { 
            "event_id": id, 
            "event": event,
            "event_price":event_price
        })

    except Exception as e: 
        return render(request, "404.html", status=404)
 
def get_member_details_for_booking(request):
    member_id = request.GET.get('member_id')
    user_profile = get_object_or_404(UserProfile, member_id=member_id)
    user = user_profile.user
    data = {'first_name': user.first_name}
    return JsonResponse(data)

@user_is_member    
@login_required
def ticket_overview(request, id):
    # Fetch the ticket and event details
    ticket = get_object_or_404(Ticket, id=id)
    event = get_object_or_404(Event, id=ticket.event.id)
    ticket_members = BookingMembers.objects.filter(ticket=ticket)
    event_price = EventTicketPrice.objects.get(event=event)

    # To get members with their pricing details
    guests_with_price = []
    member_with_price=[]
    total_price = 0  # Initialize the total price counter

    # Set to track IDs of members already in the ticket
    gests_ids_in_ticket = set()

    for i in ticket_members:
        if i.guests:
            gests_ids_in_ticket.add(i.guests.id)  # Collecting IDs of members already in the ticket
            price = event_price.guest_price 
            guests_with_price.append({
                'guest': i.guests,
                'price': price,
                "guest_id": i.id
            })
            total_price += price  # Accumulating the total price
            print("is Guest ")
        elif i.member:  # Handling the case where no price fits the age range
            price = event_price.member_price 
            member_with_price.append({
                'member': i.member,
                'price': price,
                "member_id":i.id
            })
            total_price += price  # Accumulating the total price
            print("is Member ")
 
    # Fetch only those Guests who are not yet added to this ticket
    available_guests = Guest.objects.filter(user=request.user).exclude(id__in=gests_ids_in_ticket)
    
    print(total_price)

    return render(request, 'user_ticket_overview.html', {
        "guests_with_price": guests_with_price,
        "member_with_price": member_with_price,
        "event": event,
        "total_price": total_price,
        "id": id,
        "available_guests": available_guests,  # Pass the available Guests to the template
        "ticket_id":id,
    })

@login_required    
def delete_member_and_guest_from_ticket(request,id):
        # Get the ticket id from the request
        member=get_object_or_404(BookingMembers,id=id)
        ticket_id=member.ticket.id
        member=member.delete()
        return redirect(f'/user/ticket_overview/{ticket_id}')  

@login_required    
def add_guests_in_ticket(request):
       if request.method=="POST":
          member=request.POST.get("cmb_member")
          ticket_id=request.POST.get("txt_ticket_id") 
          member_instance=get_object_or_404(Guest,id=member)
          ticket_instance=get_object_or_404(Ticket,id=ticket_id)
          BookingMembers.objects.create(ticket=ticket_instance,guests=member_instance)
       return redirect(f'/user/ticket_overview/{ticket_id}')    

@login_required    
def add_member_in_ticket(request):
       if request.method=="POST":
          member_id=request.POST.get("hidden_member_id")  
          ticket_id=request.POST.get("txt_ticket_id") 
          member_instance=get_object_or_404(UserProfile,member_id=member_id)
          ticket_instance=get_object_or_404(Ticket,id=ticket_id)
          if BookingMembers.objects.filter(ticket=ticket_instance,member=member_instance.user).exists():
                messages.warning(request,"Member alredy exist in the ticket")
                return redirect(f'/user/ticket_overview/{ticket_id}')    
          BookingMembers.objects.create(ticket=ticket_instance,member=member_instance.user)
       return redirect(f'/user/ticket_overview/{ticket_id}')    
                        
@user_is_member    
@login_required
def bookings(request):
    try:    
        tickets = Ticket.objects.filter(user=request.user).select_related()
        tickets_details = [] 
        for ticket in tickets:
            event = ticket.event
            ticket_members = BookingMembers.objects.filter(ticket=ticket)
            member_count = ticket_members.filter(member__isnull=False).count()
            guest_count = ticket_members.filter(guests__isnull=False).count()
            payment_status = True if ticket.is_paid else False
            
            # Calculate total price
            total_price = ticket.paid_amount
             
                
            tickets_details.append({
                'event': event.title,
                'member_count': member_count,
                'guest_count':guest_count,
                'payment_status': payment_status,
                'price': total_price,
                'ticket_file': ticket.ticket_file,
                'id': ticket.id,  # Store ticket ID for use in actions like Delete
                'ticket_id': ticket.ticket_id,  # Store ticket ID for use in actions like Delete
            })

        return render(request, "user_bookings.html", {'tickets_details': tickets_details})

    except Exception as e: 
        return render(request, "404.html", status=404)

# Delete a ticket
@login_required    
def delete_ticket(request,id):
    try:
        ticket=get_object_or_404(Ticket,id=id)
        ticket.delete()
        return redirect("/user/bookings")

    except Exception as e: 
        return render(request, "404.html", status=404)
       

@user_is_member    
@login_required
def pay_event_price(request):
    try:
        if request.method=="POST":
            id = request.POST.get('txt_id')
            amount=request.POST.get("txt_amount")
            print("Ticket id = ", id)
            print("Amount", amount)
            ticket = get_object_or_404(Ticket, id=id)
            if request.user != ticket.user:
                return redirect('404.html')  # Redirect to an error page or appropriate view
            ticket.is_paid = True
            ticket.paid_amount=amount
            ticket.save()
            messages.success(request,"Ticket booking Succefully...!")
        return redirect("/user/bookings")

    except Exception as e: 
        return render(request, "404.html", status=404)
    

@user_is_member    
@login_required
def generate_free_ticket(request,id):
    try:
        ticket = get_object_or_404(Ticket, id=id)
        if request.user != ticket.user:
            return render(request, "404.html", status=404)
        ticket.is_paid = True
        ticket.paid_amount=0
        ticket.save()
        messages.success(request,"Ticket booking Succefully...!")
        return redirect("/user/bookings")
    except Exception as e: 
        return render(request, "404.html", status=404)

        
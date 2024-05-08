from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .forms import *
from django.db import IntegrityError, DatabaseError
from django.core.exceptions import ObjectDoesNotExist 
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction

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
    family_member_count=FamilyMember.objects.filter(user=request.user).count()
    participated_events=Ticket.objects.filter(user=request.user,is_paid=True).count()
    context={
        "family_member_count":family_member_count,
        "participated_events":participated_events,
    }
    return render(request,"user_dashboard.html",context)

   
@login_required
def family_member(request):
    try:
        form = FamilyMemberForm()
        # Ensure only the user's family members are fetched
        data = FamilyMember.objects.filter(user=request.user).select_related().order_by("id")
        context = {
            "form": form,
            "data": data
        } 
        return render(request, "family_member.html", context)
    except ObjectDoesNotExist:
        return render(request, "404.html")
    except Exception as e: 
        messages.error("getting 404 Error")
        return render(request, "404.html")

   
@login_required
def user_create_family_member(request):
    if request.method == 'POST':
        form = FamilyMemberForm(request.POST)
        if form.is_valid():
            try:
                family_member = form.save(commit=False)
                family_member.user = request.user  # Assign the current user
                family_member.save()
                messages.success(request, "Family Member Created Successfully")
                return redirect('/user/family_member')
            except (IntegrityError, DatabaseError) as e:
                messages.error(request, "There was an error saving the family member. Please try again.")
                return render(request, 'family_member_create.html', {'form': form})
        else:
            return render(request, 'family_member.html', {'form': form})
    else:
        return redirect('/user/family_member')
    

    
@login_required
def update_family_member(request):
    if request.method == 'POST':
        family_member_id = request.POST.get('txt_id')
        family_member = get_object_or_404(FamilyMember, id=family_member_id)
        try:
            form = FamilyMemberForm(request.POST, instance=family_member)
            if form.is_valid():
                form.save()
                messages.success(request, "Record Updated Successfully")
                return redirect("/user/family_member")
            else:
                return render(request, 'update_family_member.html', {'form': form})
        except (IntegrityError, DatabaseError) as e:
            messages.error(request, "There was a problem saving the update. Please try again.")
            return render(request, 'update_family_member.html', {'form': form})
    return redirect("/user/family_member")


@login_required
def delete_family_member(request, id):
    try:
        with transaction.atomic():
            family_member = FamilyMember.objects.get(id=id)
            family_member.delete()
            messages.success(request, "Family member deleted successfully.")
            return redirect("/user/family_member")
    except ObjectDoesNotExist:
        # If the family member does not exist, handle the error
        messages.error(request, "Family member not found.")
        return render(request, '404.html', status=404)
    except IntegrityError:
        # Handle any potential integrity errors
        messages.error(request, "Database integrity error occurred while deleting the family member.")
        return render(request, '500.html', {'error': 'Integrity Error'}, status=500)
    except Exception as e:
        # Log the exception if needed and provide a user-friendly error page
        messages.error(request, f"An error occurred: {str(e)}")
        return render(request, '500.html', {'error': 'Unexpected Error'}, status=500)

 

@user_is_member    
@login_required
def events(request):
    try:
        # Assuming 'organizer' is a ForeignKey in Event
        # Replace 'organizer' with actual related field names you have in your Event model
        events = Event.objects.all()

        return render(request, "user_events.html", {"data": events})
    except Exception as e:
        # Optionally, log the exception details here, e.g., using Django's logging framework
        return render(request, "404.html", {
            "message": "An error occurred while retrieving events. Please try again later."
        }, status=500)


@user_is_member    
@login_required    
def event_details(request,id):
    try:
        latest_events = Event.objects.select_related('eventthumbnail').order_by('-start_time')[:10]
        event_details = get_object_or_404(Event, id=id)
        event_images_or_brochure=EventImagesBrochure.objects.filter(event=event_details)
        return render(request, "user_event_details.html", {"letest_events":latest_events,"event_details": event_details,"event_images_or_brochure":event_images_or_brochure})
    except Exception as e: 
        return render(request, "404.html", status=404)

@user_is_member    
@login_required
def customize_family_member_for_booking(request, id):
    try:
        event = get_object_or_404(Event, id=id)

        if request.method == 'POST':
            form = FamilyMemberSelectionTiketForm(request.user, request.POST)
            if form.is_valid():
                selected_members = form.cleaned_data['members']
                if not selected_members:
                    messages.warning(request, "At least one member is required")
                    return redirect(f'/user/customize_family_member_for_booking/{id}')

                ticket = Ticket.objects.create(user=request.user, event=event, is_paid=False)

                for member in selected_members:
                    BookingMembers.objects.create(ticket=ticket, family_member=member)

                return redirect(f'/user/ticket_overview/{ticket.id}')

        else:
            form = FamilyMemberSelectionTiketForm(request.user)

        return render(request, 'user_customize_family_member_for_booking.html', {
            'form': form, 
            "event_id": id, 
            "event": event
        })

    except Exception as e: 
        return render(request, "404.html", status=404)
 
@user_is_member    
@login_required
def ticket_overview(request, id):
    # Fetch the ticket and event details
    ticket = get_object_or_404(Ticket, id=id)
    event = get_object_or_404(Event, id=ticket.event.id)
    ticket_members = BookingMembers.objects.filter(ticket=ticket)

    # To get members with their pricing details
    members_with_price = []
    total_price = 0  # Initialize the total price counter

    # Set to track IDs of members already in the ticket
    member_ids_in_ticket = set()

    for member in ticket_members:
        member_ids_in_ticket.add(member.family_member.id)  # Collecting IDs of members already in the ticket
        try:
            event_price = EventTicketPrice.objects.get(
                event=event,
                min_age__lte=member.family_member.age,
                max_age__gte=member.family_member.age
            )
            price = event_price.price
        except EventTicketPrice.DoesNotExist:
            price = 0  # Handling the case where no price fits the age range

        members_with_price.append({
            'member': member.family_member,
            'price': price,
            "member_id": member.id
        })
        total_price += price  # Accumulating the total price

    # Fetch only those family members who are not yet added to this ticket
    available_family_members = FamilyMember.objects.filter(user=request.user).exclude(id__in=member_ids_in_ticket)
 
    return render(request, 'user_ticket_overview.html', {
        "members_with_price": members_with_price,
        "event": event,
        "total_price": total_price,
        "ticket_id": id,
        "available_family_members": available_family_members,  # Pass the available family members to the template
    })

def delete_family_member_from_ticket(request,id):
        # Get the ticket id from the request
        member=get_object_or_404(BookingMembers,id=id)
        ticket_id=member.ticket.id
        member=member.delete()
        return redirect(f'/user/ticket_overview/{ticket_id}')  

def add_family_member_in_ticket(request):
       if request.method=="POST":
          member=request.POST.get("cmb_member")
          ticket_id=request.POST.get("txt_ticket_id")
          print("Family Member", member)
          print("Ticket",ticket_id)
          member_instance=get_object_or_404(FamilyMember,id=member)
          ticket_instance=get_object_or_404(Ticket,id=ticket_id)
          BookingMembers.objects.create(ticket=ticket_instance,family_member=member_instance)
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
            member_count = ticket_members.count()
            payment_status = True if ticket.is_paid else False
            
            # Calculate total price
            total_price = 0
            for member in ticket_members:
                try:
                    event_price = EventTicketPrice.objects.get(
                        event=event, 
                        min_age__lte=member.family_member.age, 
                        max_age__gte=member.family_member.age
                    )
                    price = event_price.price
                except EventTicketPrice.DoesNotExist:
                    price = 0  # Decide what to do if no price is available
                    
                total_price += price
            tickets_details.append({
                'event': event.title,
                'member_count': member_count,
                'payment_status': payment_status,
                'price': total_price,
                'id': ticket.id,  # Store ticket ID for use in actions like Delete
                'ticket_id': ticket.ticket_id,  # Store ticket ID for use in actions like Delete
            })

        return render(request, "user_bookings.html", {'tickets_details': tickets_details})

    except Exception as e: 
        return render(request, "404.html", status=404)

# Delete a ticket
def delete_ticket(request,id):
    try:
        ticket=get_object_or_404(Ticket,id=id)
        ticket.delete()
        return redirect("/user/bookings")

    except Exception as e: 
        return render(request, "404.html", status=404)
       

@user_is_member    
@login_required
def pay_event_price(request, id):
    try:
        # Using get_object_or_404 ensures that a 404 error is returned if no Ticket is found
        ticket = get_object_or_404(Ticket, id=id)

        # Check if the user is allowed to pay for this ticket
        if request.user != ticket.user:
            return redirect('404.html')  # Redirect to an error page or appropriate view

        # Update the payment status of the ticket
        ticket.is_paid = True
        ticket.save()

        # Redirect to the bookings page after payment
        return redirect("/user/bookings")

    except Exception as e: 
        return render(request, "404.html", status=404)
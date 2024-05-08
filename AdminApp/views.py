from django.shortcuts import render
from .models import *
import threading
from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login,logout
from django.core.mail import send_mail
from .forms import *
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, DatabaseError
from django.db.models import Count
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# Create your views here.
def commitee_year_for_webiste_base(request):
    commitee_year = ComiteeYear.objects.select_related()
    return {
        'commitee_year': commitee_year,
    }

from django.core.mail import EmailMultiAlternatives



class EmailThread(threading.Thread):
    def __init__(self, subject, text_message, html_message, email_from, recipient_list):
        self.subject = subject
        self.text_message = text_message
        self.html_message = html_message
        self.email_from = email_from
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        # Create the email message with the text content
        email = EmailMultiAlternatives(
            self.subject,
            self.text_message,
            self.email_from,
            self.recipient_list
        )
        # Attach the HTML version
        email.attach_alternative(self.html_message, "text/html")
        # Send the email
        email.send()

def render_email_template(otp,template,user):
    user=get_object_or_404(User,id=user)
    context = {'otp': otp,"user":user}
    html_content = render_to_string(f'{template}', context)
    return html_content


def comitee_year_list(request):  
    if request.method == "POST":
        form = ComiteeYearForm(request.POST)
        if form.is_valid():
            form.save()  # More detailed error descriptions
            return redirect("/admin/comitee_year_list")
    else:
        form = ComiteeYearForm()
    session=ComiteeYear.objects.filter().select_related() 
    return render(request, 'admin_commitee_year.html', {'form': form,"session":session})


def update_comitee_year(request):
    if request.method == 'POST':
        year_id=request.POST.get("txt_year_id")
        year = get_object_or_404(ComiteeYear, id=year_id)  # Get the event data outside of the POST check
        form = ComiteeYearForm(request.POST, instance=year)
        if form.is_valid():
            form.save()
            messages.success(request, "Record Updated Successfully")
            return redirect("/admin/comitee_year_list") 
    else:
        form = ComiteeYearForm()  
    return render(request, 'admin_commitee_year.html', {'form': form})


def delete_comitee_year(request,id):
    ComiteeYear.objects.get(id=id).delete()
    return redirect("/admin/comitee_year_list")



def comitee_member_list(request):  
    if request.method == "POST":
        form = ComiteeMemberForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # More detailed error descriptions
            messages.success(request, "Member Added Succss")
            return redirect("/admin/comitee_member_list")
    else:
        form = ComiteeMemberForm()
    members=ComiteeMember.objects.filter().select_related() 
    return render(request, 'admin_commitee_member_list.html', {'form': form,"members":members})


def update_comitee_member(request):
    if request.method == 'POST':
        id=request.POST.get("txt_id")
        member = get_object_or_404(ComiteeMember, id=id)  # Get the event data outside of the POST check
        form = ComiteeMemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, "Record Updated Successfully")
            return redirect("/admin/comitee_member_list") 
    else:
        form = ComiteeYearForm()  
    return render(request, 'admin_commitee_member_list.html', {'form': form})


def delete_comitee_member(request,id):
    ComiteeMember.objects.get(id=id).delete()
    return redirect("/admin/comitee_member_list")


def register(request):  
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.first_name = form.cleaned_data['full_name']
            user.save()
            phone_number=form.cleaned_data['phone_number']
            full_name=form.cleaned_data['full_name']
            gender=form.cleaned_data['gender']
            age=form.cleaned_data['age']
            generate_otp = ''.join(random.choices('0123456789', k=6))

            OTP.objects.create(user=user,phone_number=phone_number,otp=generate_otp)
            FamilyMember.objects.create(user=user,full_name=full_name,gender=gender,age=age,relation="self")

            print(generate_otp)
            request.session['user_id_for_otp_verify'] = user.id

            subject = 'GYA - OTP Verification'
            template="email_verify_register_otp.html"
            html_message = render_email_template(generate_otp,template,user.id)
            text_message = strip_tags(html_message)
            email_from = 'prameshwar4378@gmail.com'
            recipient_list = [user.email] 
            email_thread = EmailThread(subject, text_message, html_message, email_from, recipient_list)
            email_thread.start()
 
            return redirect('/verify_otp')
        else:
            print("Form is not valid") 
            print(form.errors.as_data())  # More detailed error descriptions
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})



def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']  # Use the password from the form
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login Success")
                return redirect('/admin/dashboard/')
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid login details.")
    else:
        form = LoginForm()
        OTP_Login_Form=LoginUsingOTPForm()
    
    return render(request, 'login.html', {'form': form,'OTP_Login_Form':OTP_Login_Form})



def login_with_otp(request):
    if request.method == "POST":
        form = LoginUsingOTPForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username'] 
            # Check if username could be a phone number
            if username.isdigit() and len(username) in [10, 11, 12]:  # typical lengths for phone numbers
                try:
                    user_data = OTP.objects.filter(phone_number=username).exists()
                    if user_data:
                        user_data = OTP.objects.filter(phone_number=username).first()
                        request.session['user_id_for_otp_verify'] = user_data.user.id 
                        
                        generate_otp = ''.join(random.choices('0123456789', k=6))
                        OTP.objects.filter(phone_number=username).update(otp=generate_otp)
                        print(generate_otp)
                        
                        subject = 'GYA - OTP Verification'
                        template="email_verify_login_otp.html"
                        html_message = render_email_template(generate_otp,template,user_data.user.id)
                        text_message = strip_tags(html_message)
                        email_from = 'prameshwar4378@gmail.com'
                        recipient_list = [user_data.user.email]
                        print("This is test")
                        email_thread = EmailThread(subject, text_message, html_message, email_from, recipient_list)
                        email_thread.start()

                        return redirect('/verify_otp')
                    else:
                        messages.error(request, "No user found with this phone number.")
                        return redirect('/login')

                except ObjectDoesNotExist:
                    messages.error(request, "No user found with this phone number.")
                    return redirect('/login')

            # Check if username could be an email
            elif "@" in username and "." in username:  # basic check for email
                try:
                    user_data = User.objects.filter(email=username).exists()
                    if user_data:
                        user_data = User.objects.filter(email=username).first()
                        request.session['user_id_for_otp_verify'] = user_data.id 
                        generate_otp = ''.join(random.choices('0123456789', k=6))

                        if OTP.objects.filter(user=user_data):
                            OTP.objects.filter(user=user_data).update(otp=generate_otp)
                            print("OTP Available calling")
                        else:
                            OTP.objects.create(otp=generate_otp,user=user_data.id) 
                            print("OTP Not Available calling")

                        print(generate_otp)

                        subject = 'GYA - OTP Verification'
                        template="email_verify_login_otp.html"
                        context={"generate_otp":generate_otp}
                        html_message = render_email_template(generate_otp,template,user_data.id)
                        text_message = strip_tags(html_message)
                        email_from = 'prameshwar4378@gmail.com'
                        recipient_list = [user_data.email]
                        print("This is test")
                        email_thread = EmailThread(subject, text_message, html_message, email_from, recipient_list)
                        email_thread.start()
            
                        return redirect('/verify_otp')
 
                    else:
                        messages.error(request, "No user found with this email.")
                        return redirect('/login')

                except ObjectDoesNotExist:
                    messages.error(request, "No user found with this email.")
                    return redirect('/login')

            else:
                messages.error(request, "Invalid username format. Please enter a valid email or phone number.")
                return redirect('/login')
        return redirect('/login')
    return redirect('/login')
  

  
def verify_otp(request):
    if request.method == "POST":
        user_id = request.session.get('user_id_for_otp_verify')
        user_otp = request.POST.get('txt_otp')

        try:
            data = OTP.objects.get(user=user_id)
            
            if int(data.otp) == int(user_otp):
                print("OTP Verify Success")
                user = data.user
                user.backend = 'django.contrib.auth.backends.ModelBackend' 
                login(request, user)
                if data.user.is_superuser==True:
                    return redirect('/admin/dashboard/')
                else: 
                    return redirect('/user/dashboard/')
            else:
                print("OTP verification failed - Invalid OTP")
                messages.error(request, "Invalid OTP")
                return redirect('/verify_otp')

        except OTP.DoesNotExist:
            print("No OTP found for the user")
            messages.error(request, "No OTP found for this user.")
            return redirect('/verify_otp')
        except Exception as e:
            print(f"An error occurred: {e}")
            messages.error(request, "An error occurred while verifying the OTP. Please try again.")
            return redirect('/verify_otp')
    else:
        return render(request, 'verify_otp.html')
    

def custom_logout(request):
    logout(request)
    return redirect("/login")

def membership_payment(request):
    if request.method == "POST":
        txt_amount = request.POST.get("txt_amount")
        if not txt_amount:
            messages.warning(request, "Amount not found")
            return redirect("/user/dashboard")
        # Ensure UserProfile exists or create it, then set is_member to True
        UserProfile.objects.update_or_create(user=request.user, defaults={'is_member': True})
        return redirect("/user/dashboard")
    
    return render(request, 'membership_payment.html')




def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


def booking_list(request):
        tickets = Ticket.objects.order_by("-booking_date").select_related()
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
            
            user=ticket_members.first()
            print()
            tickets_details.append({
                'name':user.ticket.user.first_name,
                'event': event.title,
                'member_count': member_count,
                'payment_status': payment_status,
                'price': total_price,
                'id': ticket.id,  # Store ticket ID for use in actions like Delete
                'ticket_id': ticket.ticket_id,  # Store ticket ID for use in actions like Delete
                'booking_date': ticket.booking_date,  # Store ticket ID for use in actions like Delete
                'is_paid':ticket.is_paid,
            })

        return render(request, "admin_booking_list.html", {'tickets_details': tickets_details})



def members_list(request):
    data = FamilyMember.objects.filter(relation="self").annotate(
        total_members=Count('user__familymember')
    ).order_by("-id")
    context = {
        "data": data,
    }
    return render(request, 'admin_members_list.html', context)


def member_details(request,id):
    data = FamilyMember.objects.filter(user=id).select_related()
    context = {
        "data": data,
    }
    return render(request, 'admin_member_details.html', context)


def event_list(request):
    create_event_form = EventForm()
    data=Event.objects.all().select_related().order_by("-id")
    context={
        "create_event_form":create_event_form,
        "data":data,
    }
    return render(request, 'admin_event_list.html',context)


def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Event Created Success")
            return redirect('/admin/event_list')  # Assuming you have a URL named 'list' for listing events
    else:
            messages.warning(request,"Error Getting")
            return redirect('/admin/event_list')  # Assuming you have a URL named 'list' for listing events
 


def update_event(request, id):
    event_data = get_object_or_404(Event, id=id)  # Get the event data outside of the POST check
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event_data)
        if form.is_valid():
            form.save()
            messages.success(request, "Record Updated Successfully")
            return redirect("/admin/event_list")
        else:
            messages.error(request, "There was an error in the form. Please check your inputs.")
            return render(request, 'update_event.html', {'form': form})
    else:
        form = EventForm(instance=event_data)  # Initialize the form with the event instance data
    return render(request, 'update_event.html', {'form': form})

def delete_event(request,id):
    Event.objects.get(id=id).delete()
    return redirect("/admin/event_list")

def add_event_ticket_price(request):
    event_id = request.POST.get("txt_event_id") 
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = EventTicketPriceForm(request.POST)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.event = event
            new_form.save()
            messages.success(request, "Ticket Price Added Success.")
            return redirect(f"/admin/event_details/{event_id}")
        else:
            for field in form.errors:
                for error in form[field].errors:
                    messages.error(request, error)
            return redirect(f"/admin/event_details/{event_id}")
    else:
        messages.warning(request, "Only POST method is allowed for this operation.")
        return redirect(f"/admin/event_details/{event_id}")


def create_event_thumbnail(request):
    event_id = request.POST.get("txt_event_id")
    
    if request.method == 'POST':
        form = EventThumbnailForm(request.POST, request.FILES)
        if form.is_valid():
            thumbnail, created = EventThumbnail.objects.update_or_create(
                event_id=event_id,
                defaults={'thumbnail': form.cleaned_data.get('thumbnail')}
            )
            if created:
                messages.success(request, "Thumbnail created successfully.")
            else:
                messages.success(request, "Thumbnail updated successfully.")
            
            return redirect(f"/admin/event_details/{event_id}")
        else:
            messages.error(request, "Form is not valid. Please check the data provided.")
            return redirect(f"/admin/event_details/{event_id}")
    else:
        messages.warning(request, "Only POST method is allowed for this operation.")
        return redirect(f"/admin/event_details/{event_id}")
    

def event_details(request, id):
    event = get_object_or_404(Event, id=id)
    event_ticket_object=EventTicketPrice.objects.filter(event=event).select_related()
    images = EventImagesBrochure.objects.filter(event=event)
    imageform = EventImagesBrochureForm()
    thumbnail_form=EventThumbnailForm()
    event_tiket_price_form=EventTicketPriceForm()
    if request.method == 'POST':
        imageform = EventImagesBrochureForm(request.POST, request.FILES)
        if imageform.is_valid():
            new_image = imageform.save(commit=False)
            new_image.event = event  # Assuming EventImagesBrochure has a foreign key to Event
            new_image.save()
            messages.success(request, "Files uploaded successfully")
            return redirect(f"/admin/event_details/{id}")
        else:  
                for error in imageform.non_field_errors():
                    messages.error(request, error)
    else:
        imageform = EventImagesBrochureForm()

    return render(request, 'event_details.html', {'event_ticket_object':event_ticket_object,'event_tiket_price_form':event_tiket_price_form,'imageform': imageform,'thumbnail_form':thumbnail_form, 'data': event,"images":images})

def delete_event_brochure(request,id):
    event_brochure = EventImagesBrochure.objects.filter(id=id).first()
    if event_brochure.image:
       EventImagesBrochure.objects.filter(id=id).update(brochure="")
    else:
        EventImagesBrochure.objects.filter(id=id).delete()
    messages.success(request, "Files deleted successfully")
    return redirect(f"/admin/event_details/{event_brochure.event.id}")


def delete_event_images(request,id):
    event_image = EventImagesBrochure.objects.filter(id=id).first()
    if event_image.brochure:
       print("First Called")
       EventImagesBrochure.objects.filter(id=id).update(image="") 
    else:
       print("Second Called")
       EventImagesBrochure.objects.filter(id=id).delete()
    messages.success(request, "Files deleted successfully")
    return redirect(f"/admin/event_details/{event_image.event.id}")


def delete_event_ticket_price(request,id):
    event_brochure = EventTicketPrice.objects.filter(id=id).first()
    event_brochure.delete()
    messages.success(request, "Record deleted successfully")
    return redirect(f"/admin/event_details/{event_brochure.event.id}")


def photo_gallery_list(request): 
    data = PhotoGallery.objects.all()
    form = PhotoGalleryForm()
    return render(request, 'admin_photo_gallery_list.html', {'form': form, "data":data})


def create_photo_for_gallery(request):
    if request.method == 'POST':
        form = PhotoGalleryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,"Photo Added Success")
            return redirect('/admin/photo_gallery_list') 
        else:
            messages.error(request,"Form is not valid")
            return redirect('/admin/photo_gallery_list') 
             # Assuming you have a URL named 'list' for listing events
    else: 
            messages.error(request,"Form is not valid")
            return redirect('/admin/photo_gallery_list')  # Assuming you have a URL named 'list' for listing events


def delete_photo_from_gallery(request,id):
    PhotoGallery.objects.get(id=id).delete()
    return redirect("/admin/photo_gallery_list")




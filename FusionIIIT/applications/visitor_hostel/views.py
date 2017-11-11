from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import HttpResponseRedirect
from applications.visitor_hostel.models import *
from applications.visitor_hostel.forms import *
from datetime import date
import datetime
from django.contrib import messages
from applications.globals.models import *
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


def visitorhostel(request):

    context = {}
    # bookings here
    confirmed_bookings = Book_room.objects.filter(status = "Confirm")
    pending_bookings = Book_room.objects.filter(status = "Pending")
    cancelled_bookings = Book_room.objects.filter(status = "Cancel")

    # rooms info here
    all_rooms_status = Room_Status.objects.all()
    available_rooms = Room_Status.objects.filter(status="Available")
    booked_rooms = Room_Status.objects.filter(status = 'Booked')
    under_maintainence_rooms = Room_Status.objects.filter(status = 'UnderMaintenance')
    occupied_rooms = Room_Status.objects.filter(status = 'CheckedIn')

    # inventory data
    inventory = Inventory.objects.all()

    # rooms booked for a visitor
    # rooms_booked = Visitor_room.objects.filter()

    # to book meals
    guest_meals = Book_room.objects.filter(check_in__lte = datetime.datetime.today(),
                                            booking_to__gte = datetime.datetime.today())

    to_check_in = Book_room.objects.filter(status = "Confirm", check_in=None)

    cancelBookingForm = Book_room.objects.filter(status = "Confirm")

    book_room = Book_room.objects.filter(booking_from__lte=datetime.datetime.today())
    room_status = Room_Status.objects.filter(status='Booked').distinct()
    room_status1 = []
    print(room_status)
    for i in room_status:
        if i.book_room.booking_from<=datetime.date.today():
            room_status1.append(i.book_room)
    print(room_status1)
    checkInForm=[]
    for x in room_status1:
        if x not in checkInForm:
            checkInForm.append(x)
    print(checkInForm)

    room_status=Room_Status.objects.filter(status = "CheckedIn")
    book_room = Book_room.objects.all().filter(booking_to__gte=datetime.datetime.today())
    context1 = []
    for i in room_status:
        if i.book_room.booking_from<=datetime.date.today():
            context1.append(i.book_room)
            # print('Room', room_status)
    print(context1)
    checkOutForm=[]
    for x in context1:
        if x not in checkOutForm:
            checkOutForm.append(x)
    print(checkOutForm)

    edit_room_statusForm=Room_Status.objects.filter(Q(status="UnderMaintenance") | Q(status="Available"))

    return render(request, "vhModule/visitorhostel.html",
                  {'confirmed_bookings' : confirmed_bookings,
                   'pending_bookings' : pending_bookings,
                   'cancelled_bookings' : cancelled_bookings,
                   'all_rooms_status' : all_rooms_status,
                   'available_rooms' :available_rooms,
                   'booked_rooms' : booked_rooms,
                   'under_maintainence_rooms' : under_maintainence_rooms,
                   'occupied_rooms' : occupied_rooms,
                   'inventory' : inventory,
                   'guest_meals' : guest_meals,
                   'to_check_in' : to_check_in})


def vh_homepage(request):
    context = {}
    return render(request, "vhModule/vh_homepage.html", context)

@login_required(login_url='/accounts/login/')
def booking_request(request):
    user = get_object_or_404(User, username=request.user.username)

    if user :
        if request.method == 'POST' :
            if '0' in request.POST.get('status'):
                room_available = Room_Status.objects.filter(status="Available")
                if not room_available:
                    messages.success(request, 'no room available')
                    return HttpResponseRedirect('/visitorhostel/vh_homepage/')
                id = request.POST.get('0')
                book = Book_room.objects.filter(id=id).first()
                print(book)
                id = book.id
                print('book room', id)
                Book_room.objects.filter(id = id).update (status = "Confirm" )
                book_room = Book_room.objects.get(id=id)

                rooms=request.POST.getlist('room')

                for room in rooms:
                    room_id=Room.objects.all().filter(room_number=room).first()
                    print('room', room_id)
                    book_from = book_room.booking_from
                    book_to = book_room.booking_to
                    delta = (book_to - book_from).days
                    print(delta)
                    for i in range(delta):
                        date_1 = book_from+ datetime.timedelta(days=i)
                        p = Room_Status.objects.all().filter(room_id=room_id)
                        p = p[0]
                        p.date = date_1
                        p.status = 'Booked'
                        p.book_room = book
                        p.save()
                    #return HttpResponse('okay')
                messages.success(request, 'you allot room succesfully')
                return HttpResponseRedirect('/visitorhostel/vh_homepage/')

            elif 'cancel' in request.POST:
                print ("hello")
                id = request.POST.getlist('cancel')
                id = id[0]
                Book_room.objects.filter(id = id).update (status = "Cancel" )
                messages.success(request, 'succesfully cancelled')
                return HttpResponseRedirect('/visitorhostel/vh_homepage/')

            return HttpResponseRedirect('/visitorhostel/vh_homepage/')
        else :
            return HttpResponseRedirect('/visitorhostel/')

    else :
        messages.success(request, 'permission denied')
        return HttpResponseRedirect('/visitorhostel/')


@login_required(login_url='/accounts/login/')
def all_booking(request):
    user = get_object_or_404(User, username=request.user.username)

    if user:
        if request.method == 'POST' :
            print("hello")
            form = ViewBooking(request.POST)
            if form.is_valid:
                date_1=request.POST.getlist('date_from')[0]
                date_2=request.POST.getlist('date_to')[0]
                booking = Book_room.objects.exclude(Q(booking_to__lte=date_1)|Q( booking_from__gte=date_2) )
                print(booking)
                if not booking:
                    messages.success(request, 'No booking available in that date')
                    return HttpResponseRedirect('/visitorhostel/vh_homepage/')
                else :
                    return render(request, "vhModule/show_all_booking.html" , {'booking' : booking})
            return HttpResponseRedirect('/visitorhostel/vh_homepage/')
        else :
            return HttpResponseRedirect('/visitorhostel/')


@login_required(login_url='/accounts/login/')
def cancel_booked_booking(request):
    user = get_object_or_404(User, username=request.user.username)

    if user:
        if request.method == 'POST' :
            print("yes")
            id = request.POST.getlist('cancel')
            id = id[0]
            Book_room.objects.filter(id = id).update (status = "Cancel" )
            Room_Status.objects.filter(id=id).update(status = "Available",id='')
            messages.success(request, 'cancelled successfully ')
            context = Book_room.objects.filter(status ="Confirm")
            return render(request, "vhModule/cancel_booked_room.html" , { 'context' : context})
        else :
            return HttpResponseRedirect('/visitorhostel/')


@login_required(login_url='/accounts/login/')
def check_in(request):
    user = get_object_or_404(User, username=request.user.username)
    c=ExtraInfo.objects.all().filter(user=user)

    if user:
        if request.method =='POST' :
            id=request.POST.getlist('checkedin')
            id=id[0]
            #print(id)
            messages.success(request, 'check in succesfully')
            Book_room.objects.all().filter(id=id).update(check_in=datetime.datetime.today())
            Room_Status.objects.filter(book_room=id).update(status="CheckedIn")
            # code
            book_room = Book_room.objects.all().filter(booking_from__lte=datetime.datetime.today())
            room_status = Room_Status.objects.all().filter(status='Booked')
            context1 = []
            for i in room_status:
                if i.book_room.booking_from<=datetime.date.today():
                    context1.append(i.book_room)
            # print('Room', room_status)
            print(context1)
            context=[]
            for x in context1:
                if x not in context:
                    context.append(x)
            print(context)

            if not context:
                messages.success(request, 'No booking available')
                return HttpResponseRedirect('/visitorhostel/vh_homepage/')
            return render(request, "vhModule/checkin1.html" , { 'context' : context})

        else :
            return HttpResponseRedirect('/visitorhostel/')


@login_required(login_url='/accounts/login/')
def check_out(request):
    user = get_object_or_404(User, username=request.user.username)
    c=ExtraInfo.objects.all().filter(user=user)

    #####st=str(c.designation)
    #print(st)
    if user:
        if request.method =='POST' :
            id=request.POST.getlist('checkout')
            print(id)
            id=id[0]
            book_room=id
            book_room=Book_room.objects.all().filter(id=id)
            book_room=book_room[0]
            Book_room.objects.all().filter(id=id).update(check_out=datetime.datetime.today())
            print(type(book_room),"booktoom1")
            days=(datetime.date.today() - book_room.check_in).days
            v_id=book_room.visitor
            category=book_room.visitor_category
            person=book_room.person_count
            room_bill=0

            book_room=Book_room.objects.filter(id=id)
            if category =='A':
                room_bill=0
            elif category== 'B':
                for i in book_room:
                    room_status=Room_Status.objects.all().filter(book_room=i)
                    for i in room_status:
                        if i.room_id.room_type=='SingleBed':
                            room_bill=room_bill+days*400
                        else :
                            room_bill=room_bill+days*500
            elif category=='C':
                for i in book_room:
                    room_status=Room_Status.objects.all().filter(book_room=i)
                    for i in room_status:
                        if i.room_id.room_type=='SingleBed':
                            room_bill=room_bill+days*800
                        else :
                            room_bill=room_bill+days*1000
            else:
                for i in book_room:
                    room_status=Room_Status.objects.all().filter(book_room=i)
                    for i in room_status:
                        if i.room_id.room_type=='SingleBed':
                            room_bill=room_bill+days*1400
                        else :
                            room_bill=room_bill+days*1600

            mess_bill=0
            meal=Meal.objects.all().filter(visitor=v_id).distinct()
            print(meal)
            for m in meal:
                mess_bill1=0
                if m.morning_tea==True:
                    mess_bill1=mess_bill1+ m.persons*10
                    print(mess_bill1)
                if m.eve_tea==True:
                    mess_bill1=mess_bill1+m.persons*10
                if m.breakfast==True:
                    mess_bill1=mess_bill1+m.persons*50
                if m.lunch==True:
                    mess_bill1=mess_bill1+m.persons*100
                if m.dinner==True:
                    mess_bill1=mess_bill1+m.persons*100

                if mess_bill1==m.persons*270:
                    mess_bill=mess_bill+225*m.persons
                else:
                        mess_bill=mess_bill + mess_bill1
            print(type(v_id))
            print(book_room[0])
            Room_Status.objects.filter(book_room=book_room[0]).update(status="Available",book_room='')
            total_bill=mess_bill + room_bill
            context = {'v_id':v_id,'visitor':v_id.visitor_name,'mess_bill':mess_bill,'room_bill':room_bill, 't_bill':total_bill}
            print(context)
            return render(request, "vhModule/payment1.html" , { 'context' : context})
        else :
            return HttpResponseRedirect('/visitorhostel/')


@login_required(login_url='/accounts/login/')
def meal_book(request):
    user = get_object_or_404(User, username=request.user.username)
    c=ExtraInfo.objects.all().filter(user=user)

    if user:
        if request.method == "POST":

            id=request.POST.get('pk')
            visitor=Visitor.objects.filter(id=id)
            print(visitor)
            id=visitor[0]
            date_1=datetime.datetime.today

            if 1 in food:
                m_tea=True
            else:
                m_tea=False

            if 4 in food:
                e_tea=True
            else:
                e_tea=False


            if 2 in food:
                breakfast=True
            else:
                breakfast=False


            if 3 in food:
                lunch=True
            else:
                lunch=False


            if 5 in food:
                dinner=True
            else:
                dinner=False

            if person:
                person=request.POST('numberofpeople')
            else:
                person = 1

            Meal.objects.create(visitor=id,
                                morning_tea=m_tea,
                                eve_tea=e_tea,
                                meal_date=date_1,
                                breakfast=breakfast,
                                lunch=lunch,
                                dinner=dinner,
                                persons=person)

            return HttpResponseRedirect('/visitorhostel/')
        else:
            return HttpResponseRedirect('/visitorhostel/')


@login_required(login_url='/accounts/login/')
def bill_generation(request):
    user = get_object_or_404(User, username=request.user.username)
    c=ExtraInfo.objects.all().filter(user=user)

    #####st=str(c.designation)
    #print(st)
    if user:
        if request.method == 'POST':
            v_id=request.POST.getlist('visitor')[0]
            print(v_id,"abc")

            meal_bill=request.POST.getlist('mess_bill')[0]
            room_bill=request.POST.getlist('room_bill')[0]
            status=request.POST.getlist('status')[0]
            if status=="True":
                st=True
            else:
                st=False

            user = get_object_or_404(User, username=request.user.username)
            c=ExtraInfo.objects.filter(user=user)
            visitor=Visitor.objects.filter(visitor_phone=v_id)
            print(visitor,"asd")
            visitor=visitor[0]
            visitor_bill=Visitor_bill.objects.create(visitor=visitor,caretaker=user,meal_bill=meal_bill, room_bill=room_bill,payment_status=st)
            messages.success(request, 'guest check out successfully')
            return HttpResponseRedirect('/visitorhostel/vh_homepage/')

        else:
            return HttpResponseRedirect('/visitorhostel/')


@login_required(login_url='/accounts/login/')
def Room_availabity(request):
    user = get_object_or_404(User, username=request.user.username)
    print(user)
    if user:
        if request.method == 'POST':
            form=RoomAvailability(request.POST)
            if form.is_valid:
                date_1=request.POST.getlist('date_from')[0]
                date_2=request.POST.getlist('date_to')[0]
                context =[]
                room_status=Room_Status.objects.filter(status="Available")
                for i in room_status:
                    b=Room.objects.filter(room_id=i.room_id.room_id)
                    context.append(b)

                id=Book_room.objects.all().filter(booking_from__gte=date_2)
                for i in id:
                    room_status=Room_Status.objects.all().filter(id=i.id)
                    for i in room_status:
                        b=Room.objects.filter(room_id=i.room_id.room_id)
                        context.append(b)

                id=Book_room.objects.all().filter(booking_to__lte=date_1)
                for i in id:
                    room_status=Room_Status.objects.all().filter(id=i.id)
                    for i in room_status:
                        b=Room.objects.filter(room_id=i.room_id.room_id)
                        context.append(b)
                print("hii")
                return render(request,"vhModule/checkavailabilty11.html",{'context':context})
        else:
            return HttpResponseRedirect('/visitorhostel/')


@login_required(login_url='/accounts/login/')
def BookaRoom(request):
    user = get_object_or_404(User, username=request.user.username)
    if user:
        if request.method=='POST':
            print("book a room")
            name=request.POST.get('name')
            mob=request.POST.get('phone')
            email=request.POST.get('email')
            address=request.POST.get('address')
            country=request.POST.get('country')
            visitor=Visitor.objects.create(intender=user,
                                           visitor_name=name,
                                           visitor_email=email,
                                           visitor_phone=mob,
                                           visitor_address=address,
                                           nationality=country)
            persons=request.POST.get('numberofpeople')
            category=request.POST.get('category')
            purpose=request.POST.get('purposeofvisit')
            date_1=request.POST.get('booking_from')
            date_2=request.POST.get('booking_to')
            book_room=Book_room.objects.create(visitor=visitor,
                                               visitor_category=category,
                                               purpose=purpose,
                                               booking_to=date_2,
                                               booking_from=date_1)
            return HttpResponseRedirect('/visitorhostel/')
        else:
            return HttpResponseRedirect('/visitorhostel/')

def add_to_inventory(request):
    return HttpResponseRedirect('/visitorhostel/')


def edit_room_status(request):
    if request.method == 'POST':
        room=request.POST.get('change')
        room=Room.objects.filter(room_number=room)[0]
        Room_Status.objects.filter(room_id=room).update(status="UnderMaintenance")
        return HttpResponseRedirect('/visitorhostel/')
    else:
        return HttpResponseRedirect('/visitorhostel/')

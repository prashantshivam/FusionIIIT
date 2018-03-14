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
from .forms import InventoryForm

@login_required(login_url='/accounts/login/')
def visitorhostel(request):

    # intenders
    intenders = User.objects.all()
    user = request.user
    user_detail=UserDetail.objects.get(name=user)
    user_designation=user_detail.designation
    available_rooms = {}
    # bookings for intender view
    if (user_designation == "Intender") :
        all_bookings = BookingDetail.objects.all()
        pending_bookings = BookingDetail.objects.filter(status = "Pending", intender=user)
        active_bookings = BookingDetail.objects.filter(status = "Confirmed", intender=user)
        print (active_bookings, "active")

        visitors = {}
        for booking in active_bookings:
            temp = range(2, booking.person_count + 1)
            visitors[booking.id] = temp

        inactive_bookings = BookingDetail.objects.filter(Q(status = "Cancelled") | Q(status = "Rejected") | Q(status="Complete"), intender=user)
        canceled_bookings = BookingDetail.objects.filter(status = "Canceled", intender=user)
        rejected_bookings = BookingDetail.objects.filter(status = 'Rejected', intender=user)
    else:  # booking for caretaker and incharge view
        all_bookings = BookingDetail.objects.all()
        pending_bookings = BookingDetail.objects.filter(status = "Pending")
        active_bookings = BookingDetail.objects.filter(Q(status = "Confirmed") | Q(status = "CheckedIn"))

        visitors = {}
        for booking in active_bookings:
            temp = range(2, booking.person_count + 1)
            visitors[booking.id] = temp

        inactive_bookings = BookingDetail.objects.filter(Q(status = "Cancelled") | Q(status = "Rejected") | Q(status="Complete"))
        canceled_bookings = BookingDetail.objects.filter(status = "Canceled")
        rejected_bookings = BookingDetail.objects.filter(status = 'Rejected')

        for booking in pending_bookings:
            booking_from = booking.booking_from
            booking_to = booking.booking_to
            temp = booking_details(booking_from, booking_to)
            available_rooms[booking.id] = temp
    #print (available_rooms)

    # inventory data
    inventory = Inventory.objects.all()
    inventory_bill = InventoryBill.objects.all()

    # to book meals

    active_visitors = {}
    for booking in active_bookings:
        if booking.status == 'CheckedIn':
            for visitor in booking.visitor.all():
                active_visitors[booking.id] = visitor

    # edit_room_statusForm=RoomStatus.objects.filter(Q(status="UnderMaintenance") | Q(status="Available"))

    previous_visitors = VisitorDetail.objects.all()

    # ------------------------------------------------------------------------------------------------------------------------------
    bills = {}

    for booking in active_bookings:
        if booking.status == 'CheckedIn':
            rooms = booking.rooms.all()
            days = (datetime.date.today() - booking.check_in).days
            category = booking.visitor_category
            person = booking.person_count

            room_bill=0

            if category =='A':
                room_bill=0
            elif category== 'B':
                for i in rooms:
                    if i.room_type=='SingleBed':
                        room_bill=room_bill+days*400
                    else :
                        room_bill=room_bill+days*500
            elif category=='C':
                for i in rooms:
                    if i.room_type=='SingleBed':
                        room_bill=room_bill+days*800
                    else :
                        room_bill=room_bill+days*1000
            else:
                for i in rooms:
                    if i.room_type=='SingleBed':
                        room_bill=room_bill+days*1400
                    else :
                        room_bill=room_bill+days*1600

            mess_bill = 0

            total_bill = mess_bill + room_bill

            bills[booking.id] = {'mess_bill':mess_bill,'room_bill':room_bill, 'total_bill':total_bill}

    # -------------------------------------------------------------------------------------------------------------------------------

    return render(request, "vhModule/visitorhostel.html",
                  {'all_bookings' : all_bookings,
                   'inactive_bookings' : inactive_bookings,
                   'pending_bookings' : pending_bookings,
                   'active_bookings' : active_bookings,
                   'canceled_bookings' : canceled_bookings,
                   'bills' : bills,
                   # 'all_rooms_status' : all_rooms_status,
                   'available_rooms' :available_rooms,
                   # 'booked_rooms' : booked_rooms,
                   # 'under_maintainence_rooms' : under_maintainence_rooms,
                   # 'occupied_rooms' : occupied_rooms,
                   'inventory' : inventory,
                   'inventory_bill' : inventory_bill,
                   'active_visitors' : active_visitors,
                   'intenders' : intenders,
                   'user' : user,
                   'visitors' : visitors,
                   'previous_visitors' : previous_visitors,
                   'user_designation': user_designation})

# Get methods for bookings

@login_required(login_url='/accounts/login/')
def get_booking_requests(request):
    if request.method == 'POST':
        pending_bookings = BookingDetail.objects.filter(status = "Pending")

        return render(request, "vhModule/visitorhostel.html", {'pending_bookings' : pending_bookings})
    else:
        return HttpResponseRedirect('/visitorhostel/')

@login_required(login_url='/accounts/login/')
def get_active_bookings(request):
    if request.method == 'POST':
        active_bookings = BookingDetail.objects.filter(status = "Confirmed")

        return render_to_response(request, "vhModule/visitorhostel.html", {'active_bookings' : active_bookings})
    else:
        return HttpResponseRedirect('/visitorhostel/')

@login_required(login_url='/accounts/login/')
def get_inactive_bookings(request):
    if request.method == 'POST':
        inactive_bookings = BookingDetail.objects.filter(Q(status = "Cancelled") | Q(status = "Rejected") | Q(status="Complete"))

        return render(request, "vhModule/visitorhostel.html", {'inactive_bookings' : inactive_bookings})
    else:
        return HttpResponseRedirect('/visitorhostel/')

# Method for making booking request

@login_required(login_url='/accounts/login/')
def get_booking_form(request):
    if request.method == 'POST':
        intenders = User.objects.all()
        return render(request, "vhModule/visitorhostel.html", {'intenders' : intenders})
    else:
        return HttpResponseRedirect('/visitorhostel/')

@login_required(login_url='/accounts/login/')
def request_booking(request):
    if request.method == 'POST':
        intender = request.POST.get('intender')
        user = User.objects.get(id=intender)
        booking_id = "VH"+str(datetime.datetime.now())
        category = request.POST.get('category')
        person_count=request.POST.get('number-of-people')
        if person_count:
            person_count = person_count
        else:
            person_count = 1
        purpose_of_visit=request.POST.get('purpose-of-visit')
        booking_from=request.POST.get('booking_from')
        booking_to=request.POST.get('booking_to')
        BookingDetail.objects.create(purpose=purpose_of_visit,
                                       intender=user,
                                       booking_from=booking_from,
                                       booking_to=booking_to,
                                       visitor_category=category,
                                       person_count=person_count)

        return HttpResponseRedirect('/visitorhostel/')
    else:
        return HttpResponseRedirect('/visitorhostel/')

@login_required(login_url='/accounts/login/')
def confirm_booking(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking-id')
        intender = request.POST.get('intender'),
        category=request.POST.get('category')
        purpose=request.POST.get('purpose')
        booking_from=request.POST.get('booking_from')
        booking_to=request.POST.get('booking_to')
        person_count=request.POST.get('numberofpeople')
        rooms=request.POST.getlist('rooms')
        print (rooms)
        booking = BookingDetail.objects.get(id=booking_id)
        bd = BookingDetail.objects.get(id=booking_id)
        bd.status = 'Confirmed'
        bd.category = category
        for room in rooms:
            room_object = RoomDetail.objects.get(id = int(room))
            bd.rooms.add(room_object)
        bd.save()
        return HttpResponseRedirect('/visitorhostel/')
    else:
        return HttpResponseRedirect('/visitorhostel/')

@login_required(login_url='/accounts/login/')
def cancel_booking(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking-id')
        remark = request.POST.get('remark')
        BookingDetail.objects.filter(id=booking_id).update(status='Cancelled', remark=remark)
        return HttpResponseRedirect('/visitorhostel/')
    else:
        return HttpResponseRedirect('/visitorhostel/')

@login_required(login_url='/accounts/login/')
def reject_booking(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking-id')
        remark = request.POST.get('remark')
        BookingDetail.objects.filter(id=booking_id).update(status="Rejected", remark=remark)
        return HttpResponseRedirect('/visitorhostel/')
    else:
        return HttpResponseRedirect('/visitorhostel/')


@login_required(login_url='/accounts/login/')
def check_in(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking-id')
        visitor_name=request.POST.get('name')
        print (visitor_name, "fNJBG")
        visitor_phone=request.POST.get('phone')
        visitor_email=request.POST.get('email')
        visitor_address=request.POST.get('address')
        check_in_date=datetime.date.today()
        visitor = VisitorDetail.objects.create(visitor_phone=visitor_phone,visitor_name=visitor_name,visitor_email=visitor_email,visitor_address=visitor_address)
        try:
            bd = BookingDetail.objects.get(id=booking_id)
            bd.status = "CheckedIn"
            bd.check_in = check_in_date
            bd.visitor.add(visitor)
            bd.save()
        except:
            return HttpResponse('/visitorhostel/')
        return HttpResponse('/visitorhostel/')
    else:
        return HttpResponse('/visitorhostel/')

@login_required(login_url='/accounts/login/')
def check_out(request):
    user = get_object_or_404(User, username=request.user.username)
    c=ExtraInfo.objects.all().filter(user=user)

    if user:
        if request.method =='POST' :
            id=request.POST.get('id')
            print (id)
            booking = BookingDetail.objects.get(id=id)
            visitor_info=booking.visitor.all()
            i=visitor_info[0]
            rooms=booking.rooms.all()
            BookingDetail.objects.filter(id=id).update(check_out=datetime.datetime.today())
            days=(datetime.date.today() - booking.check_in).days
            category=booking.visitor_category
            person=booking.person_count
            for room in rooms:
                RoomDetail.objects.filter(id=room.id).update(room_status='Available')

            # for visitors in visitor_info:


            room_bill=0

            if category =='A':
                room_bill=0
            elif category== 'B':
                for i in rooms:
                    if i.room_type=='SingleBed':
                        room_bill=room_bill+days*400
                    else :
                        room_bill=room_bill+days*500
            elif category=='C':
                for i in rooms:
                    if i.room_type=='SingleBed':
                        room_bill=room_bill+days*800
                    else :
                        room_bill=room_bill+days*1000
            else:
                for i in rooms:
                    if i.room_type=='SingleBed':
                        room_bill=room_bill+days*1400
                    else :
                        room_bill=room_bill+days*1600

            mess_bill=0
            #meal=Meal.objects.all().filter(visitor=v_id).distinct()
            #print(meal)
            #for m in meal:
                # mess_bill1=0
                # if m.morning_tea==True:
                #     mess_bill1=mess_bill1+ m.persons*10
                #     print(mess_bill1)
                # if m.eve_tea==True:
                #     mess_bill1=mess_bill1+m.persons*10
                # if m.breakfast==True:
                #     mess_bill1=mess_bill1+m.persons*50
                # if m.lunch==True:
                #     mess_bill1=mess_bill1+m.persons*100
                # if m.dinner==True:
                #     mess_bill1=mess_bill1+m.persons*100
                #
                # if mess_bill1==m.persons*270:
                #     mess_bill=mess_bill+225*m.persons
                # else:
                #         mess_bill=mess_bill + mess_bill1
            # print(type(v_id))
            # print(book_room[0])
            #RoomStatus.objects.filter(book_room=book_room[0]).update(status="Available",book_room='')
            total_bill=mess_bill + room_bill

            context = {'mess_bill':mess_bill,'room_bill':room_bill, 'total_bill':total_bill}
            print(context)
            return render(request, "vhModule/visitorhostel.html" , { 'context' : context,'visitor_info': visitor_info,'rooms':rooms})
        else :
            return HttpResponseRedirect('/visitorhostel/')


@login_required(login_url='/accounts/login/')
def record_meal(request):
    user = get_object_or_404(User, username=request.user.username)
    c=ExtraInfo.objects.all().filter(user=user)

    if user:
        if request.method == "POST":

            id=request.POST.get('pk')
            booking_id = request.POST.get('booking')
            booking = BookingDetail.objects.get(id = booking_id)
            visitor=VisitorDetail.objects.get(id=id)
            date_1=datetime.datetime.now()
            food=request.POST.getlist('food[]')
            print(food)
            # print(request.POST)
            if '1' in food:
                m_tea=True
            else:
                m_tea=False

            if '4' in food:
                e_tea=True
            else:
                e_tea=False


            if '2' in food:
                breakfast=True
            else:
                breakfast=False


            if '3' in food:
                lunch=True
            else:
                lunch=False


            if '5' in food:
                dinner=True
            else:
                dinner=False

            if request.POST.get('numberofpeople'):
                person=request.POST.get('numberofpeople')
            else:
                person = 1

            MealRecord.objects.create(visitor=visitor,
                                booking=booking,
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
            return HttpResponseRedirect('/visitorhostel/')

        else:
            return HttpResponseRedirect('/visitorhostel/')


@login_required(login_url='/accounts/login/')
def room_availabity(request):
    if request.method == 'POST':
        date_1=request.POST.get('start_date')
        date_2=request.POST.get('end_date')
        available_rooms = booking_details(date_1, date_2)
        return render(request,"vhModule/room-availability.html",{'available_rooms':available_rooms})
    else:
        return HttpResponseRedirect('/visitorhostel/')



def add_to_inventory(request):
    if request.method=='POST':
        item_name=request.POST.get('item_name')
        bill_number=request.POST.get('bill_number')
        quantity=(request.POST.get('quantity'))
        print (quantity)
        cost=request.POST.get('cost')
        consumable=request.POST.get('consumable')
        # if(Inventory.objects.get(item_name = item_name)):
        #     Inventory.objects.filter(item_name=item_name).update(quantity=quantity,consumable=consumable)
        # else:
        Inventory.objects.create(item_name=item_name,quantity=quantity,consumable=consumable)

        item_name_key = Inventory.objects.get(item_name=item_name)
        InventoryBill.objects.create(item_name=item_name_key,bill_number=bill_number,cost=cost)
        return HttpResponseRedirect('/visitorhostel/')
    else:
        return HttpResponseRedirect('/visitorhostel/')


def update_inventory(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        quantity = request.POST.get('quantity')

        Inventory.objects.filter(id=id).update(quantity=quantity)
        return HttpResponseRedirect('/visitorhostel/')
    else:
        return HttpResponseRedirect('/visitorhostel/')


def edit_room_status(request):
    if request.method == 'POST':
        room_number = request.POST.get('room_number')
        room_status = request.POST.get('room_status')
        room=RoomDetail.objects.get(room_number=room_number)
        RoomDetail.objects.filter(room_id=room).update(status=room_status)
        return HttpResponseRedirect('/visitorhostel/')
    else:
        return HttpResponseRedirect('/visitorhostel/')


def booking_details(date1, date2):

    booking= BookingDetail.objects.filter(Q(status="Confirmed") | Q(booking_from__lte=date1, booking_to__gte=date1) | Q(booking_from__gte=date1,
booking_to__lte=date2) | Q(booking_from__lte=date2, booking_to__gte=date2))
    booked_rooms = []
    for booking in booking:
        for room in booking.rooms.all():
            booked_rooms.append(room)

    available_rooms = []
    all_rooms = RoomDetail.objects.all()
    for room in all_rooms:
        if room not in booked_rooms:
            available_rooms.append(room)

    return available_rooms

import datetime

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render

from applications.visitor_hostel.forms import MealBooking, ViewBooking

from .models import Book_room, Meal, Room, Room_Status, Visitor


def visitorhostel(request):
    context = {}
    return render(request, "vhModule/visitorhostel.html", context)


def vh_homepage(request):
    context = {}
    return render(request, "vhModule/vh_homepage.html", context)


def booking_request(request):
    if request.method == 'POST':
        if 'confirm' in request.POST:
            room_available = Room_Status.objects.filter(status="Available")
            if not room_available:
                messages.success(request, 'no room available')
                return HttpResponseRedirect('/visitorhostel/vh_homepage/')
            br_id = request.POST.getlist('confirm')
            print(br_id)
            br_id = br_id[0]
            book = Book_room.objects.filter(br_id=br_id).first()
            br_id = book.br_id
            print('book room', br_id)
            Book_room.objects.filter(br_id=br_id).update(status="Confirm")
            book_room = Book_room.objects.get(br_id=br_id)

            rooms = request.POST.getlist('room')

            for room in rooms:
                room_id = Room.objects.filter(room_number=room).first()
                print('room', room_id)
                book_from = book_room.booking_from
                book_to = book_room.booking_to
                delta = (book_to - book_from).days
                print(delta)
                for i in range(delta):
                    date_1 = book_from + datetime.timedelta(days=i)
                    p = Room_Status.objects.all().filter(room_id=room_id)
                    p = p[0]
                    p.date = date_1
                    p.status = 'Booked'
                    p.br_id = book
                    p.save()

            messages.success(request, 'you allot room succesfully')
            return HttpResponseRedirect('/visitorhostel/vh_homepage/')

        elif 'cancel' in request.POST:
            messages.success(request, 'succesfully cancelled')
            return HttpResponseRedirect('/visitorhostel/vh_homepage/')

        return HttpResponseRedirect('/visitorhostel/vh_homepage/')

    else:
        context = Book_room.objects.filter(status="Pending")
        room = Room_Status.objects.filter(status="Available")
        if not context:
            messages.success(request, 'No new request')
            return HttpResponseRedirect('/visitorhostel/vh_homepage/')
        return render(request, "vhModule/vh_view_booking_request.html",
                      {'context': context, 'room': room})


def view_booking(request):
    if request.method == 'POST':
        form = ViewBooking(request.POST)
        if form.is_valid():
            date_1 = request.POST.getlist('date_from')[0]
            # print(date_1)
            booking = Book_room.objects.filter(booking_from__gte=date_1)
            print(booking)
            if not booking:
                messages.success(request, 'No booking available in that date')
                return HttpResponseRedirect('/visitorhostel/vh_homepage/')
            else:
                return render(request, "vhModule/show_all_booking.html", {'booking': booking})
        return HttpResponseRedirect('/visitorhostel/vh_homepage/')
    else:
        form = ViewBooking()
        return render(request, "vhModule/input_booking_date.html", {'form': form})


def cancel_booked_booking(request):
    if request.method == 'POST':
        print("yes")
        br_id = request.POST.getlist('cancel')[0]
        Book_room.objects.filter(br_id=br_id).update(status="Cancel")
        Room_Status.objects.filter(br_id=br_id).update(status="Available")
        messages.success(request, 'cancelled successfully')
        context = Book_room.objects.filter(status="Confirm")
        return render(request, "vhModule/cancel_booked_room.html", {'context': context})
    else:
        context = Book_room.objects.filter(status="Confirm")
        print(context)
        if not context:
            messages.success(request, 'No confirm booking available')
            return HttpResponseRedirect('/visitorhostel/vh_homepage/')
        return render(request, "vhModule/cancel_booked_room.html", {'context': context})


def check_in(request):
    if request.method == 'POST':
        br_id = request.POST.getlist('checkedin')[0]
        print(br_id)
        messages.success(request, 'check in succesfully')
        Book_room.objects.filter(br_id=br_id).update(check_in=datetime.datetime.today())
        print(datetime.datetime.today())
        Room_Status.objects.filter(br_id=br_id).update(status="CheckedIn")

        book_room = Book_room.objects.filter(booking_from__lte=datetime.datetime.today())
        room_status = Room_Status.objects.filter(status='Booked')
        context1 = []
        for i in room_status:
            if i.br_id.booking_from <= datetime.date.today():
                context1.append(i.br_id)
        # print('Room', room_status)
        print(context1)
        context = []
        for x in context1:
            if x not in context:
                context.append(x)
        print(context)

        if not context:
            messages.success(request, 'No booking available')
            return HttpResponseRedirect('/visitorhostel/vh_homepage/')
        return render(request, "vhModule/checkin1.html", {'context': context})

    else:
        book_room = Book_room.objects.filter(booking_from__lte=datetime.datetime.today())
        room_status = Room_Status.objects.filter(status='Booked').distinct()
        context1 = []
        for i in room_status:
            if i.br_id.booking_from <= datetime.date.today():
                context1.append(i.br_id)
        # print('Room', room_status)
        print(context1)
        context = []
        for x in context1:
            if x not in context:
                context.append(x)
            # if i.br_id in b_room:
            # r_status.append(i)
        print(context)

        # return HttpResponse('okay')
        # context = Book_room.objects.filter(br_id__in=Room_Status.objects.filter(status = "Booked")
        # , booking_from__gte=datetime.datetime.today())
        # print(context)
        if not context:
            messages.success(request, 'No booking available')
            return HttpResponseRedirect('/visitorhostel/vh_homepage/')
        return render(request, "vhModule/checkin1.html", {'context': context})


def check_out(request):
    if request.method == 'POST':
        br_id = request.POST.getlist('checkout')[0]
        book_room = Book_room.objects.filter(br_id=br_id)
        book_room = book_room[0]
        # Book_room.objects.all().filter(br_id=br_id).update(check_out=datetime.datetime.today())
        # Room_Status.objects.filter(br_id=br_id).update(status="Available",date='',br_id='')
        print(book_room)
        days = (datetime.date.today() - book_room.check_in).days
        v_id = book_room.visitor_id
        category = book_room.visitor_category
        person = book_room.person_count
        room_bill = 0
        if category == 'A':
            room_bill = 0
        elif category == 'B':
            room_bill = days*400*(person/2) + days*500*(person % 2)
        elif category == 'C':
            room_bill = days*800*(person/2) + days*1000*(person % 2)
        else:
            room_bill = days*1400*(person/2) + days*1600*(person % 2)

        mess_bill = 0
        meal = Meal.objects.all().filter(visitor_id=v_id).distinct()
        print(meal)
        for m in meal:
            mess_bill1 = 0
            if m.morning_tea:
                mess_bill1 = mess_bill1 + m.persons*10
                print(mess_bill1)
            if m.eve_tea:
                mess_bill1 = mess_bill1 + m.persons*10
            if m.breakfast:
                mess_bill1 = mess_bill1 + m.persons*50
            if m.lunch:
                mess_bill1 = mess_bill1 + m.persons*100
            if m.dinner:
                mess_bill1 = mess_bill1 + m.persons*100

            if mess_bill1 == m.persons*270:
                mess_bill = mess_bill+225*m.persons
            else:
                mess_bill = mess_bill + mess_bill1

        print(v_id)
        total_bill = mess_bill + room_bill
        context = {'v_id': v_id,
                   'visitor': v_id.visitor_name,
                   'mess_bill': mess_bill,
                   'room_bill': room_bill,
                   't_bill': total_bill}
        print(context)
        return render(request, "vhModule/payment1.html", {'context': context})

    else:
        room_status = Room_Status.objects.filter(status="CheckedIn")
        book_room = Book_room.objects.filter(booking_to__lte=datetime.datetime.today())
        context1 = []
        for i in room_status:
            if i.br_id.booking_from <= datetime.date.today():
                context1.append(i.br_id)
        # print('Room', room_status)
        print(context1)
        context = []
        for x in context1:
            if x not in context:
                context.append(x)
        print(context)
        if not context:
            messages.success(request, 'No guest checked in currently')
            return HttpResponseRedirect('/visitorhostel/vh_homepage/')
        return render(request, "vhModule/checkout1.html", {'context': context})


def meal_book(request):
    if request.method == "POST":
        form = MealBooking(request.POST)
        if form.is_valid():
            br_id = request.POST.getlist('visitor_id')
            print(br_id)
            br_id = br_id[0]
            visitor = Visitor.objects.filter(visitor_id=br_id)
            print(visitor)
            br_id = visitor[0]
            date_1 = request.POST.getlist('date')
            if not date_1:
                form = MealBooking
                messages.success(request, 'No guest checked in currently')
                return HttpResponseRedirect('/visitorhostel/bookingmea1.html/')
            else:
                date_1 = date_1[0]

            m_tea = request.POST.getlist('morning_tea')
            if m_tea:
                m_tea = True
            else:
                m_tea = False

            e_tea = request.POST.getlist('eve_tea')
            if e_tea:
                e_tea = True
            else:
                e_tea = False

            breakfast = request.POST.getlist('breakfast')
            if breakfast:
                breakfast = True
            else:
                breakfast = False

            lunch = request.POST.getlist('lunch')
            if lunch:
                lunch = True
            else:
                lunch = False

            dinner = request.POST.getlist('dinner')
            if dinner:
                dinner = True
            else:
                dinner = False

            # person = request.POST.getlist('persons')[0]
            Meal.objects.create(visitor_id=br_id,
                                morning_tea=m_tea,
                                eve_tea=e_tea,
                                meal_date=date_1,
                                breakfast=breakfast,
                                lunch=lunch,
                                dinner=dinner)
            print("ok")

        messages.success(request, 'No guest checked in currently')
        return HttpResponseRedirect('/visitorhostel/vh_homepage/')

    else:
        form = MealBooking
        return render(request, "vhModule/bookingmea1.html", {'form': form})


def bill_generation(request):
    if request.method == 'POST':
        v_id = request.POST.getlist('visitor')[0]
        v_id = Visitor.objects.filter(visitor_id=v_id)[0]
        # meal_bill = request.POST.getlist('mess_bill')[0]
        # room_bill = request.POST.getlist('room_bill')[0]
        # status = request.POST.getlist('status')[0]
        # if status:
        #     st = True
        # else:
        #     st = False
        # visitor_bill = Visitor_bill.objects.create(visitor_id=v_id,
        #                                            meal_bill=meal_bill,
        #                                            room_bill=room_bill,
        #                                            status=st)
        messages.success(request, 'guest check out successfully')
    else:
        messages.success(request, 'No user selected')
        return HttpResponseRedirect('/visitorhostel/vh_homepage/')


def Room_availabity(request):
    if request.method == 'POST':
        print("room availability")
    else:
        context = []
        room_status = Room_Status.objects.filter(status="Available")
        for i in room_status:
            b = Room.objects.filter(room_id=i.room_id.room_id)
            context.append(b)
        return render(request, "vhModule/checkavailabilty11.html", {'context': context})

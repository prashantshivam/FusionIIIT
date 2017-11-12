from django.conf.urls import url

from . import views

app_name = 'visitorhostel'

urlpatterns = [

    url(r'^$', views.visitorhostel, name='visitorhostel'),
    url(r'^vh_booking_request/' , views.booking_request , name ='booking_request'),
    url(r'^view_booking/', views.all_booking, name = 'view_all_booking'),
    url(r'^cancel_booking/', views.cancel_booked_booking, name = 'cancel_booking'),
    url(r'^checkin/', views.check_in, name = 'guest check in'),
    url(r'^checkout/', views.check_out, name = 'guest check out'),
    url(r'^bookmeal/', views.meal_book, name = 'meal booking'),
    url(r'^bill/', views.bill_generation, name = 'bill_generation'),
    url(r'^check_availability/', views.Room_availabity, name = 'Room_availabity'),
    url(r'^bookaroom/', views.BookaRoom, name = 'room booking'),
    url(r'^add-to-inventory/', views.add_to_inventory, name = 'add_to_inventory'),
    url(r'^update-inventory/', views.update_inventory, name = 'update_inventory'),
    url(r'^edit-room-status/', views.edit_room_status, name = 'edit_room_status'),
    url(r'^booking-details/', views.booking_details, name = 'booking_details'),

]

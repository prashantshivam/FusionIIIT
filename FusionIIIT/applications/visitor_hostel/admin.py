from django.contrib import admin

from .models import (Booking, Inventory, Meal, RoomDetail, Visitor, Bill,
                     RoomStatus, InventoryBill)

admin.site.register(Visitor)
admin.site.register(Booking)
admin.site.register(Bill)
admin.site.register(RoomDetail)
admin.site.register(Meal)
admin.site.register(Inventory)
admin.site.register(RoomStatus)
admin.site.register(InventoryBill)


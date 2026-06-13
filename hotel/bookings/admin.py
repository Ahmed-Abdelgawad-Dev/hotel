from django.contrib import admin
from .models import BookingCart, Booking, BookingVersion, BookingRoom

@admin.register(BookingCart)
class BookingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'room_type', 'check_in', 'check_out', 'status', 'expires_at')
    list_filter = ('status', 'room_type')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_ref', 'guest', 'room_type', 'check_in', 'check_out', 'total_price', 'status')
    list_filter = ('status', 'source', 'room_type')
    search_fields = ('booking_ref', 'guest__first_name', 'guest__last_name', 'guest__email')

@admin.register(BookingVersion)
class BookingVersionAdmin(admin.ModelAdmin):
    list_display = ('booking', 'version_number', 'reason', 'created_at')
    list_filter = ('reason',)

@admin.register(BookingRoom)
class BookingRoomAdmin(admin.ModelAdmin):
    list_display = ('booking', 'room', 'assigned_at')

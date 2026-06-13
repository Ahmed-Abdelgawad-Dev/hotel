import django.db.models as M
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import timedelta
from hotel.core.models import TimestampedModel

class BookingCart(TimestampedModel):
    session_key = M.CharField(max_length=40, db_index=True)
    room_type = M.ForeignKey('rooms.RoomType', on_delete=M.PROTECT)
    meal_plan = M.ForeignKey('inventory.MealPlan', on_delete=M.PROTECT)
    check_in = M.DateField()
    check_out = M.DateField()
    adults = M.PositiveSmallIntegerField(default=1)
    children = M.PositiveSmallIntegerField(default=0)
    total_price = M.DecimalField(max_digits=10, decimal_places=2, help_text='Computed at creation; locked')
    price_breakdown = M.JSONField(default=list, help_text='Night-by-night rate detail')
    status = M.CharField(max_length=10, choices=[('active', 'Active'), ('expired', 'Expired'), ('converted', 'Converted')], default='active')
    expires_at = M.DateTimeField()
    locked_at = M.DateTimeField(null=True, blank=True, help_text='Set when guest enters payment flow - prevents expiry race')
    class Meta: indexes = [M.Index(fields=['status', 'expires_at']), M.Index(fields=['session_key'])]
    def __str__(s): return 'Cart #{}: {} {} -> {}'.format(s.id, s.room_type, s.check_in, s.check_out)
    def save(self, *a, **kw):
        if not self.expires_at: self.expires_at = timezone.now() + timedelta(minutes=20)
        super().save(*a, **kw)

class Booking(TimestampedModel):
    booking_ref = M.CharField(max_length=40, unique=True, blank=True)
    guest = M.ForeignKey('guests.Guest', on_delete=M.PROTECT, related_name='bookings', null=True, blank=True)
    room_type = M.ForeignKey('rooms.RoomType', on_delete=M.PROTECT)
    meal_plan = M.ForeignKey('inventory.MealPlan', on_delete=M.PROTECT)
    check_in = M.DateField(help_text='Point-in-time snapshot (latest)')
    check_out = M.DateField(help_text='Point-in-time snapshot (latest)')
    adults = M.PositiveSmallIntegerField(default=1)
    children = M.PositiveSmallIntegerField(default=0)
    total_price = M.DecimalField(max_digits=10, decimal_places=2)
    price_breakdown = M.JSONField(default=list)
    status = M.CharField(max_length=20, choices=[('pending_payment', 'Pending Payment'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled'), ('no_show', 'No Show'), ('completed', 'Completed')], default='pending_payment')
    special_requests = M.TextField(blank=True)
    source = M.CharField(max_length=20, choices=[('web', 'Web'), ('extranet', 'Extranet'), ('channel_manager', 'Channel Manager')], default='web')
    cart = M.OneToOneField(BookingCart, on_delete=M.SET_NULL, null=True, blank=True, related_name='booking')
    current_version = M.PositiveIntegerField(default=1)
    modification_policy = M.CharField(max_length=10, choices=[('flexible', 'Flexible'), ('moderate', 'Moderate'), ('strict', 'Strict')], default='moderate')
    class Meta: ordering = ['-created_at']; indexes = [M.Index(fields=['status', 'check_in']), M.Index(fields=['booking_ref']), M.Index(fields=['guest'])]
    def __str__(s): return 'Booking {} -- {}'.format(s.booking_ref or s.id, s.guest)
    def save(self, *a, **kw):
        if not self.booking_ref: self.booking_ref = 'HTL-' + get_random_string(10).lower()
        super().save(*a, **kw)
    @property
    def nights(self): return (self.check_out - self.check_in).days

class BookingVersion(TimestampedModel):
    booking = M.ForeignKey(Booking, on_delete=M.CASCADE, related_name='versions')
    version_number = M.PositiveIntegerField()
    check_in = M.DateField(); check_out = M.DateField()
    adults = M.PositiveSmallIntegerField(); children = M.PositiveSmallIntegerField()
    meal_plan = M.ForeignKey('inventory.MealPlan', on_delete=M.PROTECT)
    total_price = M.DecimalField(max_digits=10, decimal_places=2)
    price_breakdown = M.JSONField(default=list)
    reason = M.CharField(max_length=20, choices=[('initial', 'Initial'), ('guest_request', 'Guest Request'), ('hotel_initiated', 'Hotel Initiated'), ('no_show', 'No-Show'), ('system', 'System')])
    modified_by = M.ForeignKey('users.User', on_delete=M.SET_NULL, null=True, blank=True)
    notes = M.TextField(blank=True)
    changes_summary = M.JSONField(default=dict, blank=True)
    class Meta: unique_together = ('booking', 'version_number'); ordering = ['version_number']
    def __str__(s): return '{} v{}'.format(s.booking.booking_ref, s.version_number)

class BookingRoom(M.Model):
    booking = M.ForeignKey(Booking, on_delete=M.CASCADE, related_name='assigned_rooms')
    room = M.ForeignKey('rooms.Room', on_delete=M.PROTECT)
    assigned_at = M.DateTimeField(auto_now_add=True)
    assigned_by = M.ForeignKey('users.User', on_delete=M.SET_NULL, null=True, blank=True)
    class Meta: unique_together = ('booking', 'room')
    def __str__(s): return '{} -> Room {}'.format(s.booking.booking_ref, s.room.room_number)

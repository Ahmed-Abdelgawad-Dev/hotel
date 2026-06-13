from django.db import models as M
from hotel.core.models import TimestampedModel

class Payment(TimestampedModel):
    booking = M.OneToOneField('bookings.Booking', on_delete=M.CASCADE, related_name='payment')
    stripe_payment_intent_id = M.CharField(max_length=100, unique=True, blank=True, null=True)
    stripe_checkout_session_id = M.CharField(max_length=100, unique=True, blank=True, null=True)
    amount = M.DecimalField(max_digits=10, decimal_places=2)
    currency = M.CharField(max_length=3, default='EUR')
    status = M.CharField(max_length=15, choices=[('pending','Pending'),('processing','Processing'),('succeeded','Succeeded'),('failed','Failed'),('refunded','Refunded')], default='pending')
    stripe_raw_response = M.JSONField(default=dict, blank=True)
    class Meta: ordering = ['-created_at']
    def __str__(s): return 'Payment for ' + str(s.booking) + ' - ' + s.status

class Refund(TimestampedModel):
    payment = M.ForeignKey(Payment, on_delete=M.PROTECT, related_name='refunds')
    stripe_refund_id = M.CharField(max_length=100, unique=True)
    amount = M.DecimalField(max_digits=10, decimal_places=2)
    reason = M.TextField(blank=True)
    status = M.CharField(max_length=15, choices=[('pending','Pending'),('succeeded','Succeeded'),('failed','Failed')], default='pending')
    created_by = M.ForeignKey('users.User', on_delete=M.SET_NULL, null=True, blank=True)
    def __str__(s): return 'Refund #{} for {} - {}'.format(s.id, s.payment, s.amount)

class WebhookEvent(TimestampedModel):
    stripe_event_id = M.CharField(max_length=100, unique=True)
    event_type = M.CharField(max_length=100)
    payload = M.JSONField(default=dict)
    processed = M.BooleanField(default=False)
    error_message = M.TextField(blank=True)
    class Meta: ordering = ['-created_at']
    def __str__(s): return s.event_type + (' (processed)' if s.processed else ' (pending)')

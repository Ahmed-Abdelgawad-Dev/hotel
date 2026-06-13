from django.db import models as M
from hotel.core.models import TimestampedModel, PublishedModel

class EmailTemplate(TimestampedModel, PublishedModel):
    name = M.SlugField(max_length=100, unique=True)
    subject = M.CharField(max_length=300)
    html_body = M.TextField()
    text_body = M.TextField()
    class Meta: ordering = ['name']
    def __str__(s): return s.name

class EmailLog(TimestampedModel):
    recipient_email = M.EmailField()
    template_name = M.CharField(max_length=100)
    booking = M.ForeignKey('bookings.Booking', on_delete=M.SET_NULL, null=True, blank=True)
    status = M.CharField(max_length=10, choices=[('queued','Queued'),('sent','Sent'),('failed','Failed')], default='queued')
    error_message = M.TextField(blank=True)
    sent_at = M.DateTimeField(null=True, blank=True)
    class Meta: ordering = ['-created_at']
    def __str__(s): return 'Email to {} - {}'.format(s.recipient_email, s.status)

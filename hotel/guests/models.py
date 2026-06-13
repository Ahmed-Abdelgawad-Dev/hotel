import django.db.models as M
from hotel.core.models import TimestampedModel

class Guest(TimestampedModel):
    first_name = M.CharField(max_length=100)
    last_name = M.CharField(max_length=100)
    email = M.EmailField(unique=True, db_index=True, help_text='Used for lookup/dedup')
    phone = M.CharField(max_length=30, blank=True)
    country = M.CharField(max_length=2, help_text='ISO 3166-1 alpha-2')
    marketing_consent = M.BooleanField(default=False, help_text='GDPR: marketing consent')
    gdpr_erasure_requested = M.BooleanField(default=False, help_text='Soft anonymisation flag')
    class Meta: ordering = ['last_name', 'first_name']; indexes = [M.Index(fields=['email'])]
    def __str__(s): return '{} {} ({})'.format(s.first_name, s.last_name, s.email)
    @property
    def full_name(s): return '{} {}'.format(s.first_name, s.last_name)

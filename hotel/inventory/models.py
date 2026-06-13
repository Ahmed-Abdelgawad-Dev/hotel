import django.db.models as M
from django.db.models import Q, F
from django.core.validators import MinValueValidator
from decimal import Decimal
from hotel.core.models import TimestampedModel, PublishedModel

class Season(TimestampedModel):
    name = M.CharField(max_length=100)
    start_date = M.DateField()
    end_date = M.DateField()
    priority = M.PositiveSmallIntegerField(default=1, help_text='Higher = evaluated first when ranges overlap')
    class Meta: ordering = ['-priority', 'start_date']
    def __str__(s): return '{} (priority {})'.format(s.name, s.priority)

class MealPlan(TimestampedModel, PublishedModel):
    code = M.CharField(max_length=5, unique=True, primary_key=True)
    name = M.CharField(max_length=100)
    description = M.TextField(help_text='Used on the booking review page')
    includes_items = M.TextField(blank=True, help_text='Bullet list of inclusions')
    class Meta: ordering = ['code']
    def __str__(s): return '{} -- {}'.format(s.code, s.name)

class RateRule(TimestampedModel, PublishedModel):
    room_type = M.ForeignKey('rooms.RoomType', on_delete=M.PROTECT, related_name='rate_rules')
    meal_plan = M.ForeignKey(MealPlan, on_delete=M.PROTECT, related_name='rate_rules')
    season = M.ForeignKey(Season, on_delete=M.PROTECT, null=True, blank=True, help_text='NULL = applies outside any season')
    price_per_night = M.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    min_nights = M.PositiveSmallIntegerField(default=1)
    max_nights = M.PositiveSmallIntegerField(null=True, blank=True, default=None, help_text='NULL = no maximum')
    days_of_week_mask = M.PositiveSmallIntegerField(default=0b1111111, help_text='7-bit bitmask (bit 0 = Monday)')
    class Meta: indexes = [M.Index(fields=['room_type', 'meal_plan', 'season']), M.Index(fields=['room_type', 'meal_plan', 'is_active'])]
    def __str__(s):
        sn = s.season.name if s.season else 'Year-round'
        return '{}/{} -- {} = {}'.format(s.room_type, s.meal_plan, sn, s.price_per_night)

class InventoryAllotment(M.Model):
    room_type = M.ForeignKey('rooms.RoomType', on_delete=M.PROTECT, related_name='allotments')
    date = M.DateField()
    total_rooms = M.PositiveSmallIntegerField(default=1, help_text='Managed by extranet')
    rooms_on_hold = M.PositiveSmallIntegerField(default=0)
    rooms_sold = M.PositiveSmallIntegerField(default=0)
    class Meta:
        unique_together = ('room_type', 'date')
        ordering = ['date']
        indexes = [M.Index(fields=['date'])]
        constraints = [M.CheckConstraint(condition=Q(rooms_on_hold__lte=F('total_rooms') - F('rooms_sold')), name='allotment_not_overbooked')]
        verbose_name = 'Inventory Allotment'
    def __str__(s): return '{} on {}: {} available'.format(s.room_type, s.date, s.available)
    @property
    def available(self): return self.total_rooms - self.rooms_on_hold - self.rooms_sold
    @property
    def is_available(self): return self.available >= 1

class StopSell(M.Model):
    room_type = M.ForeignKey('rooms.RoomType', on_delete=M.PROTECT, related_name='stop_sells')
    start_date = M.DateField()
    end_date = M.DateField()
    reason = M.CharField(max_length=200)
    created_by = M.ForeignKey('users.User', on_delete=M.SET_NULL, null=True, blank=True)
    created_at = M.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-start_date']
    def __str__(s): return 'Stop-sell: {} {} -> {}'.format(s.room_type, s.start_date, s.end_date)

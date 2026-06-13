from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional
from django.db import transaction, models
from django.utils import timezone
from django.core.cache import cache

@dataclass
class AllotmentData:
    date: date
    total_rooms: int
    rooms_on_hold: int
    rooms_sold: int

    @property
    def available(self):
        return self.total_rooms - self.rooms_on_hold - self.rooms_sold

    @property
    def is_available(self):
        return self.available >= 1

@dataclass
class RateRuleData:
    date: date
    price_per_night: Decimal
    season_name: Optional[str] = None
    min_nights: int = 1
    max_nights: Optional[int] = None

class AllotmentRepository(ABC):
    @abstractmethod
    def get_for_date_range(self, room_type_id, start_date, end_date, for_update=False): ...
    @abstractmethod
    def increment_hold(self, room_type_id, start_date, end_date): ...
    @abstractmethod
    def decrement_hold(self, room_type_id, start_date, end_date): ...
    @abstractmethod
    def move_hold_to_sold(self, room_type_id, start_date, end_date): ...
    @abstractmethod
    def release_sold(self, room_type_id, start_date, end_date): ...

class PricingRepository(ABC):
    @abstractmethod
    def get_rate_for_night(self, room_type_id, meal_plan_id, night_date): ...
    @abstractmethod
    def get_all_rates_for_stay(self, room_type_id, meal_plan_id, check_in, check_out): ...

class DjangoAllotmentRepository(AllotmentRepository):
    def get_for_date_range(self, room_type_id, start_date, end_date, for_update=False):
        from .models import InventoryAllotment
        qs = InventoryAllotment.objects.filter(
            room_type_id=room_type_id, date__gte=start_date, date__lt=end_date
        ).order_by("date")
        if for_update:
            qs = qs.select_for_update()
        return [AllotmentData(date=a.date, total_rooms=a.total_rooms,
                              rooms_on_hold=a.rooms_on_hold, rooms_sold=a.rooms_sold) for a in qs]

    @transaction.atomic
    def increment_hold(self, room_type_id, start_date, end_date):
        from .models import InventoryAllotment
        InventoryAllotment.objects.filter(
            room_type_id=room_type_id, date__gte=start_date, date__lt=end_date
        ).select_for_update().update(rooms_on_hold=models.F("rooms_on_hold") + 1)

    @transaction.atomic
    def decrement_hold(self, room_type_id, start_date, end_date):
        from .models import InventoryAllotment
        InventoryAllotment.objects.filter(
            room_type_id=room_type_id, date__gte=start_date, date__lt=end_date
        ).select_for_update().update(rooms_on_hold=models.F("rooms_on_hold") - 1)

    @transaction.atomic
    def move_hold_to_sold(self, room_type_id, start_date, end_date):
        from .models import InventoryAllotment
        InventoryAllotment.objects.filter(
            room_type_id=room_type_id, date__gte=start_date, date__lt=end_date
        ).select_for_update().update(
            rooms_on_hold=models.F("rooms_on_hold") - 1,
            rooms_sold=models.F("rooms_sold") + 1,
        )

    @transaction.atomic
    def release_sold(self, room_type_id, start_date, end_date):
        from .models import InventoryAllotment
        InventoryAllotment.objects.filter(
            room_type_id=room_type_id, date__gte=start_date, date__lt=end_date
        ).select_for_update().update(rooms_sold=models.F("rooms_sold") - 1)

class DjangoPricingRepository(PricingRepository):
    def get_rate_for_night(self, room_type_id, meal_plan_id, night_date):
        from .models import RateRule, Season
        season = Season.objects.filter(
            start_date__lte=night_date, end_date__gte=night_date
        ).order_by("-priority").first()
        rule = RateRule.objects.filter(
            room_type_id=room_type_id, meal_plan_id=meal_plan_id,
            season=season, is_active=True
        ).first()
        if not rule:
            rule = RateRule.objects.filter(
                room_type_id=room_type_id, meal_plan_id=meal_plan_id,
                season__isnull=True, is_active=True
            ).first()
        if not rule:
            return None
        return RateRuleData(
            date=night_date, price_per_night=rule.price_per_night,
            season_name=season.name if season else None,
            min_nights=rule.min_nights, max_nights=rule.max_nights,
        )

    def get_all_rates_for_stay(self, room_type_id, meal_plan_id, check_in, check_out):
        nights = (check_out - check_in).days
        rates = []
        for i in range(nights):
            night_date = check_in + timedelta(days=i)
            rate = self.get_rate_for_night(room_type_id, meal_plan_id, night_date)
            if rate:
                rates.append(rate)
        return rates

class PricingCache:
    VERSION_KEY = "pricing:version"

    @classmethod
    def get_version(cls):
        return cache.get_or_set(cls.VERSION_KEY, 1, timeout=None)

    @classmethod
    def bump_version(cls):
        try:
            cache.incr(cls.VERSION_KEY)
        except ValueError:
            cache.set(cls.VERSION_KEY, 2, timeout=None)

    @classmethod
    def make_key(cls, room_type_id, meal_plan_id, check_in, check_out):
        return f"pricing:v{cls.get_version()}:{room_type_id}:{meal_plan_id}:{check_in}:{check_out}"

class AvailabilityService:
    def __init__(self, allotment_repo=None):
        self.allotment_repo = allotment_repo or DjangoAllotmentRepository()

    def check_range(self, room_type_id, check_in, check_out):
        allotments = self.allotment_repo.get_for_date_range(room_type_id, check_in, check_out)
        if not allotments:
            return False
        return all(a.is_available for a in allotments)

class PricingService:
    def __init__(self, pricing_repo=None):
        self.pricing_repo = pricing_repo or DjangoPricingRepository()

    def calculate(self, room_type_id, meal_plan_id, check_in, check_out):
        cache_key = PricingCache.make_key(room_type_id, meal_plan_id, check_in, check_out)
        cached = cache.get(cache_key)
        if cached is not None:
            return Decimal(str(cached))
        rates = self.pricing_repo.get_all_rates_for_stay(room_type_id, meal_plan_id, check_in, check_out)
        if not rates:
            return Decimal("0")
        total = sum(r.price_per_night for r in rates)
        cache.set(cache_key, str(total), 300)
        return total

    def get_breakdown(self, room_type_id, meal_plan_id, check_in, check_out):
        rates = self.pricing_repo.get_all_rates_for_stay(room_type_id, meal_plan_id, check_in, check_out)
        return [{"date": r.date.isoformat(), "price": str(r.price_per_night), "season": r.season_name} for r in rates]

class InventoryService:
    def __init__(self, allotment_repo=None):
        self.allotment_repo = allotment_repo or DjangoAllotmentRepository()

    @transaction.atomic
    def place_hold_and_create_cart(self, room_type, meal_plan, check_in, check_out,
                                   adults, children, total_price, price_breakdown, session_key):
        from hotel.bookings.models import BookingCart
        allotments = self.allotment_repo.get_for_date_range(
            room_type.id, check_in, check_out, for_update=True
        )
        for a in allotments:
            if not a.is_available:
                raise ValueError(f"No availability on {a.date}")
        self.allotment_repo.increment_hold(room_type.id, check_in, check_out)
        cart = BookingCart.objects.create(
            session_key=session_key, room_type=room_type, meal_plan=meal_plan,
            check_in=check_in, check_out=check_out, adults=adults, children=children,
            total_price=total_price, price_breakdown=price_breakdown,
            expires_at=timezone.now() + timedelta(minutes=20), status="active",
        )
        return cart

    @transaction.atomic
    def confirm_booking(self, cart):
        self.allotment_repo.move_hold_to_sold(cart.room_type_id, cart.check_in, cart.check_out)

    @transaction.atomic
    def release_hold(self, room_type_id, start_date, end_date):
        self.allotment_repo.decrement_hold(room_type_id, start_date, end_date)

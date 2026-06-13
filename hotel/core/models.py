"""Core abstract base models for the entire project."""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


# ──────────────────────────────────────────────
# Abstract Base Classes (design.md §3.0)
# ──────────────────────────────────────────────

class TimestampedModel(models.Model):
    """Adds created_at and updated_at fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class OrderedModel(models.Model):
    """Adds sort_order field and ordering."""
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ["sort_order"]


class PublishedModel(models.Model):
    """Adds is_active and published_at fields for content publishing."""
    is_active = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


# ──────────────────────────────────────────────
# Legacy models (to be replaced by new apps)
# ──────────────────────────────────────────────

class RoomCategory(models.TextChoices):
    STANDARD = "standard", "Standard"
    SUPERIOR = "superior", "Superior"
    DELUXE = "deluxe", "Deluxe"
    FAMILY = "family", "Family"


class Room(models.Model):
    category = models.CharField(
        max_length=20,
        choices=RoomCategory.choices,
        default=RoomCategory.STANDARD,
        db_index=True,
    )
    size_sqm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("32.00"))],
        help_text="Room size in square metres",
    )
    max_adults = models.PositiveSmallIntegerField(default=2)
    max_children = models.PositiveSmallIntegerField(default=2)
    max_capacity = models.PositiveSmallIntegerField(default=5)
    bed_type = models.CharField(
        max_length=50,
        choices=[
            ("single", "Single"),
            ("double", "Double"),
            ("twin", "Twin"),
            ("king", "King"),
            ("queen", "Queen"),
        ],
    )
    extra_beds_allowed = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category"]
        verbose_name = "Room"
        verbose_name_plural = "Rooms"

    def __str__(self):
        return f"{self.get_category_display()}"

    @property
    def max_occupancy(self):
        return self.max_adults + self.max_children


class RoomImage(models.Model):
    """Additional gallery images for a room."""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="rooms/gallery/")
    thumbnail = models.ImageField(upload_to="rooms/thumbnails/", blank=True, null=True)
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Image for {self.room} (#{self.order})"

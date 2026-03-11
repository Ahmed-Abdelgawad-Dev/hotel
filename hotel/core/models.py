from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class RoomCategory(models.TextChoices):
    STANDARD = "standard", "Standard"
    SUPERIOR = "superior", "Superior"
    DELUXE = "deluxe", "Deluxe"
    FAMILY = "family", "Family"


class Room(models.Model):
    # Identity
    category = models.CharField(
        max_length=20,
        choices=RoomCategory.choices,
        default=RoomCategory.STANDARD,
        db_index=True,
    )

    # Physical details
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

    # Content
    description = models.TextField(blank=True)

    # Status
    is_available = models.BooleanField(default=True, db_index=True)
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category"]
        verbose_name = "Room"
        verbose_name_plural = "Rooms"

    def __str__(self):
        return f"{self.get_category_display()} — Room {self.room_number}"

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

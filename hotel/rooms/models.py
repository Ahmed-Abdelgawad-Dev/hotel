import django.db.models as M
from hotel.core.models import OrderedModel, PublishedModel, TimestampedModel
from io import BytesIO
from django.core.files.base import ContentFile

class RoomType(TimestampedModel, OrderedModel, PublishedModel):
    name = M.CharField(max_length=50)
    slug = M.SlugField(max_length=60, unique=True)
    short_description = M.CharField(max_length=200, help_text='Used in listing cards')
    full_description = M.TextField(help_text='Used on detail page')
    max_capacity = M.PositiveSmallIntegerField(default=2)
    max_adults = M.PositiveSmallIntegerField(default=2)
    max_children = M.PositiveSmallIntegerField(default=2)
    size_sqm = M.DecimalField(max_digits=5, decimal_places=1)
    view_type = M.CharField(max_length=20, choices=[('garden', 'Garden'), ('pool', 'Pool'), ('terrace', 'Terrace'), ('balcony', 'Balcony')], default='garden')
    base_price_per_night = M.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Fallback when no RateRule exists')
    class Meta: ordering = ['sort_order']; verbose_name = 'Room Type'; verbose_name_plural = 'Room Types'
    def __str__(s): return s.name

class Amenity(TimestampedModel):
    name = M.CharField(max_length=100)
    icon_class = M.CharField(max_length=50)
    category = M.CharField(max_length=20, choices=[('tech', 'Tech'), ('bathroom', 'Bathroom'), ('comfort', 'Comfort'), ('food', 'Food & Drink')], default='comfort')
    class Meta: verbose_name_plural = 'Amenities'; ordering = ['category', 'name']
    def __str__(s): return s.name

class RoomTypeAmenity(M.Model):
    room_type = M.ForeignKey(RoomType, on_delete=M.CASCADE)
    amenity = M.ForeignKey(Amenity, on_delete=M.CASCADE)
    is_highlighted = M.BooleanField(default=False, help_text='Show prominently on listing cards')
    class Meta: unique_together = ('room_type', 'amenity'); verbose_name_plural = 'Room Type Amenities'

class RoomTypeImage(TimestampedModel, OrderedModel):
    room_type = M.ForeignKey(RoomType, on_delete=M.CASCADE, related_name='images')
    image = M.ImageField(upload_to='rooms/types/')
    caption = M.CharField(max_length=200, blank=True)
    alt_text = M.CharField(max_length=200, help_text='Required for accessibility/SEO')
    is_hero = M.BooleanField(default=False, help_text='The primary card/header image')
    MAX_WIDTH = 1920; MAX_HEIGHT = 1080; JPEG_QUALITY = 85
    class Meta: ordering = ['sort_order']
    def __str__(s): return 'Image for ' + str(s.room_type)
    def save(self, *a, **kw): self._process_image(); super().save(*a, **kw)
    def _process_image(self):
        if not self.image: return
        try: from PIL import Image
        except ImportError: return
        img = Image.open(self.image)
        if img.mode in ('RGBA', 'P'): img = img.convert('RGB')
        img.thumbnail((self.MAX_WIDTH, self.MAX_HEIGHT), Image.LANCZOS)
        buf = BytesIO()
        img.save(buf, format='JPEG', quality=self.JPEG_QUALITY, optimize=True)
        fn = self.image.name.split('/')[-1]
        if not fn.lower().endswith('.jpg'): fn = fn.rsplit('.', 1)[0] + '.jpg'
        self.image.save(fn, ContentFile(buf.getvalue()), save=False)
        buf.close()

class Room(TimestampedModel):
    room_type = M.ForeignKey(RoomType, on_delete=M.CASCADE, related_name='rooms')
    room_number = M.CharField(max_length=10)
    floor = M.PositiveSmallIntegerField()
    internal_notes = M.TextField(blank=True, help_text='Staff-only notes')
    is_active = M.BooleanField(default=True, help_text='Out-of-service flag')
    class Meta: ordering = ['room_number']; indexes = [M.Index(fields=['room_type', 'is_active'])]
    def __str__(s): return '{} -- Room {}'.format(s.room_type.name, s.room_number)

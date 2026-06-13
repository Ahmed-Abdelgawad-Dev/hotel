from django.db import models as M
from hotel.core.models import TimestampedModel, OrderedModel, PublishedModel

class SiteSettings(TimestampedModel):
    hotel_name = M.CharField(max_length=200, default='Luxury Hotel')
    tagline = M.CharField(max_length=300, blank=True)
    address = M.TextField(blank=True)
    phone = M.CharField(max_length=30, blank=True)
    email = M.EmailField(blank=True)
    booking_terms_url = M.URLField(blank=True)
    privacy_policy_url = M.URLField(blank=True)
    google_maps_embed_url = M.URLField(blank=True)
    facebook_url = M.URLField(blank=True)
    instagram_url = M.URLField(blank=True)
    whatsapp_number = M.CharField(max_length=30, blank=True)
    class Meta: verbose_name = 'Site Settings'; verbose_name_plural = 'Site Settings'
    def save(self, *a, **kw): self.pk = 1; super().save(*a, **kw)
    @classmethod
    def load(cls): obj, _ = cls.objects.get_or_create(pk=1); return obj
    def __str__(s): return s.hotel_name

class HeroSlide(TimestampedModel, OrderedModel, PublishedModel):
    headline = M.CharField(max_length=200)
    subheadline = M.CharField(max_length=300, blank=True)
    image = M.ImageField(upload_to='hero/')
    image_alt = M.CharField(max_length=200)
    cta_text = M.CharField(max_length=80, blank=True)
    cta_url = M.CharField(max_length=200, blank=True)
    def __str__(s): return s.headline

class GalleryImage(TimestampedModel, OrderedModel, PublishedModel):
    image = M.ImageField(upload_to='gallery/')
    caption = M.CharField(max_length=200, blank=True)
    alt_text = M.CharField(max_length=200)
    category = M.CharField(max_length=20, choices=[('rooms','Rooms'),('dining','Dining'),('spa','Spa'),('events','Events'),('pool','Pool'),('exterior','Exterior')])
    def __str__(s): return 'Gallery: ' + s.category

class Offer(TimestampedModel, PublishedModel):
    title = M.CharField(max_length=200)
    slug = M.SlugField(max_length=220, unique=True)
    teaser = M.CharField(max_length=300)
    description = M.TextField()
    image = M.ImageField(upload_to='offers/')
    valid_from = M.DateField(null=True, blank=True)
    valid_to = M.DateField(null=True, blank=True)
    discount_percent = M.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    min_nights = M.PositiveSmallIntegerField(default=1)
    room_types = M.ManyToManyField('rooms.RoomType', blank=True)
    def __str__(s): return s.title

class DiningVenue(TimestampedModel, OrderedModel, PublishedModel):
    name = M.CharField(max_length=200)
    slug = M.SlugField(max_length=220, unique=True)
    description = M.TextField()
    cuisine_type = M.CharField(max_length=100)
    dress_code = M.CharField(max_length=100, blank=True)
    opening_hours = M.TextField(blank=True)
    capacity = M.PositiveSmallIntegerField(null=True, blank=True)
    image = M.ImageField(upload_to='dining/')
    gallery = M.ManyToManyField(GalleryImage, blank=True)
    def __str__(s): return s.name

class SpaService(TimestampedModel):
    name = M.CharField(max_length=200)
    category = M.CharField(max_length=20, choices=[('massage','Massage'),('facial','Facial'),('body','Body'),('wellness','Wellness')])
    description = M.TextField()
    duration_minutes = M.PositiveSmallIntegerField()
    price = M.DecimalField(max_digits=10, decimal_places=2)
    image = M.ImageField(upload_to='spa/')
    is_featured = M.BooleanField(default=False)
    def __str__(s): return '{} ({}min)'.format(s.name, s.duration_minutes)

class MeetingRoom(TimestampedModel):
    name = M.CharField(max_length=200)
    capacity_theatre = M.PositiveSmallIntegerField(default=0)
    capacity_classroom = M.PositiveSmallIntegerField(default=0)
    capacity_boardroom = M.PositiveSmallIntegerField(default=0)
    size_sqm = M.DecimalField(max_digits=5, decimal_places=1)
    description = M.TextField()
    image = M.ImageField(upload_to='meetings/')
    amenities_list = M.TextField(blank=True)
    def __str__(s): return s.name

class Activity(TimestampedModel):
    name = M.CharField(max_length=200)
    description = M.TextField()
    duration = M.CharField(max_length=100)
    difficulty = M.CharField(max_length=15, choices=[('easy','Easy'),('moderate','Moderate'),('challenging','Challenging')])
    image = M.ImageField(upload_to='activities/')
    is_featured = M.BooleanField(default=False)
    class Meta: verbose_name_plural = 'Activities'
    def __str__(s): return s.name

class Review(TimestampedModel):
    guest_display_name = M.CharField(max_length=100)
    country = M.CharField(max_length=2)
    star_rating = M.PositiveSmallIntegerField(default=5)
    body = M.TextField()
    stay_date = M.DateField()
    is_approved = M.BooleanField(default=False)
    is_featured = M.BooleanField(default=False)
    booking = M.ForeignKey('bookings.Booking', on_delete=M.SET_NULL, null=True, blank=True)
    source = M.CharField(max_length=15, choices=[('website','Website'),('tripadvisor','TripAdvisor'),('google','Google')], default='website')
    def __str__(s): return '{} - {} star'.format(s.guest_display_name, s.star_rating)

class NewsletterSubscriber(TimestampedModel):
    email = M.EmailField(unique=True)
    is_active = M.BooleanField(default=True)
    source = M.CharField(max_length=50, default='footer_form')
    ip_address = M.GenericIPAddressField(null=True, blank=True)
    def __str__(s): return s.email

from django.contrib import admin
from .models import (
    SiteSettings, HeroSlide, GalleryImage, Offer, DiningVenue,
    SpaService, MeetingRoom, Activity, Review, NewsletterSubscriber,
)

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Hotel Info', {'fields': ('hotel_name', 'tagline', 'address', 'phone', 'email')}),
        ('URLs', {'fields': ('booking_terms_url', 'privacy_policy_url', 'google_maps_embed_url')}),
        ('Social', {'fields': ('facebook_url', 'instagram_url', 'whatsapp_number')}),
    )

@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('headline', 'sort_order', 'is_active')
    list_filter = ('is_active',)

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('category', 'caption', 'sort_order', 'is_active')
    list_filter = ('is_active', 'category')

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'discount_percent', 'valid_from', 'valid_to', 'is_active')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(DiningVenue)
class DiningVenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'cuisine_type', 'sort_order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(SpaService)
class SpaServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'duration_minutes', 'price', 'is_featured')

@admin.register(MeetingRoom)
class MeetingRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity_theatre', 'size_sqm')

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'difficulty', 'duration', 'is_featured')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('guest_display_name', 'star_rating', 'is_approved', 'is_featured', 'source')
    list_filter = ('is_approved', 'is_featured', 'source', 'star_rating')

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'source', 'created_at')
    list_filter = ('is_active', 'source')


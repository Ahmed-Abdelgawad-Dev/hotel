from django.contrib import admin
from .models import RoomType, Amenity, RoomTypeAmenity, RoomTypeImage, Room

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'max_capacity', 'view_type', 'is_active', 'sort_order')
    list_filter = ('is_active', 'view_type')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'icon_class')
    list_filter = ('category',)

@admin.register(RoomTypeImage)
class RoomTypeImageAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'is_hero', 'sort_order')
    list_filter = ('is_hero',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'room_number', 'floor', 'is_active')
    list_filter = ('is_active', 'room_type')
    search_fields = ('room_number',)

admin.site.register(RoomTypeAmenity)

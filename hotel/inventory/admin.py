from django.contrib import admin
from .models import Season, MealPlan, RateRule, InventoryAllotment, StopSell

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'priority')
    ordering = ('-priority', 'start_date')

@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_active')

@admin.register(RateRule)
class RateRuleAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'meal_plan', 'season', 'price_per_night', 'min_nights', 'is_active')
    list_filter = ('is_active', 'room_type', 'meal_plan')

@admin.register(InventoryAllotment)
class InventoryAllotmentAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'date', 'total_rooms', 'rooms_on_hold', 'rooms_sold')
    list_filter = ('room_type',)
    search_fields = ('room_type__name',)

@admin.register(StopSell)
class StopSellAdmin(admin.ModelAdmin):
    list_display = ('room_type', 'start_date', 'end_date', 'reason')

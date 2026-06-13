from django.contrib import admin
from .models import Guest

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'country', 'marketing_consent')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('country', 'marketing_consent', 'gdpr_erasure_requested')

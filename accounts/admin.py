from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from.models import User, Address

# Register your models here.


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ['recipient_name', 'address_line1', 'address_line2', 'state', 'phone', 'is_default']

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'phone','first_name', 'last_name', 'is_staff', 'is_active']
    search_fields = ['username', 'email']
    fieldsets = BaseUserAdmin.fieldsets + (("Contact", {'fields': ('phone',)}),)
    addFieldsets = BaseUserAdmin.add_fieldsets + ('Contact', {'fields': ('phone','first_name', 'last_name', 'email',)}),
    inlines = [AddressInline]

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['recipient_name', 'line1', 'line2', 'state', 'phone', 'is_default']
    list_filter = ['state', 'is_default']
    search_fields = ['state', 'recipient_name', 'phone']
    readonly_fields = ['user']
    autocomplete_fields = ['user']
    # list_display_links = ['user']
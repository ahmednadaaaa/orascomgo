from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Driver, Merchant


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'phone', 'user_type', 'is_verified', 'created_at']
    list_filter = ['user_type', 'is_verified', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'phone', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone', 'address', 'profile_picture', 'is_verified')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone', 'email')
        }),
    )


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['user', 'vehicle_type', 'status', 'rating', 'total_deliveries']
    list_filter = ['vehicle_type', 'status']
    search_fields = ['user__username', 'user__phone', 'license_number']
    readonly_fields = ['total_deliveries', 'rating']
    
    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('Vehicle Info', {
            'fields': ('vehicle_type', 'license_number', 'license_image', 'vehicle_registration')
        }),
        ('Status', {
            'fields': ('status', 'current_latitude', 'current_longitude')
        }),
        ('Statistics', {
            'fields': ('rating', 'total_deliveries', 'areas')
        }),
    )


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'business_type', 'user', 'area', 'is_approved', 'created_at']
    list_filter = ['business_type', 'is_approved', 'created_at']
    search_fields = ['business_name', 'user__username', 'business_phone', 'business_email']
    actions = ['approve_merchants']
    
    def approve_merchants(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} merchants approved successfully")
    approve_merchants.short_description = "Approve selected merchants"


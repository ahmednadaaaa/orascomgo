from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderStatusHistory


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['status', 'notes', 'created_at', 'created_by']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['tracking_number', 'customer_name', 'status_badge', 'service_type', 
                    'from_area', 'to_area', 'total_price', 'created_at']
    list_filter = ['status', 'service_type', 'from_area', 'to_area', 'payment_method', 'created_at']
    search_fields = ['tracking_number', 'customer_name', 'customer_phone', 'delivery_address']
    readonly_fields = ['tracking_number', 'base_price', 'total_price', 'created_at', 'updated_at']
    inlines = [OrderStatusHistoryInline]
    
    fieldsets = (
        ('Tracking Info', {
            'fields': ('tracking_number', 'status')
        }),
        ('Customer Info', {
            'fields': ('customer', 'customer_name', 'customer_phone')
        }),
        ('Location Info', {
            'fields': ('from_area', 'to_area', 'pickup_address', 'delivery_address')
        }),
        ('Package Info', {
            'fields': ('weight', 'service_type', 'notes')
        }),
        ('Pricing & Payment', {
            'fields': ('base_price', 'total_price', 'payment_method', 'is_paid')
        }),
        ('Assignment', {
            'fields': ('driver',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'pickup_time', 'delivery_time', 'estimated_delivery')
        }),
        ('Rating', {
            'fields': ('customer_rating', 'customer_review')
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'confirmed': '#2196F3',
            'picked_up': '#9C27B0',
            'in_transit': '#FF9800',
            'out_for_delivery': '#FF5722',
            'delivered': '#4CAF50',
            'cancelled': '#F44336',
            'failed': '#9E9E9E',
        }
        color = colors.get(obj.status, '#757575')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 5px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'



from django.db import models
from django.conf import settings
import random
import string

def generate_tracking_number():
    return ''.join(random.choices(string.digits, k=6))

class Order(models.Model):
    AREA_CHOICES = (
        ('capital', 'العاصمة'),
        ('salmiya', 'السالمية'),
        ('farwaniya', 'الفروانية'),
        ('hawalli', 'حولي'),
        ('jahra', 'الجهراء'),
        ('ahmadi', 'الأحمدي'),
    )
    
    SERVICE_TYPE_CHOICES = (
        ('ultra', 'فوري (أقل من نصف ساعة)'),
        ('super', 'فائق السرعة (أقل من ساعة)'),
        ('express1', 'سريع جداً (1-3 ساعات)'),
        ('normal1', 'سريع (3-6 ساعات)'),
        ('normal2', 'عادي (6-12 ساعة)'),
        ('normal3', 'اقتصادي (12-18 ساعة)'),
        ('normal4', 'قياسي (18-24 ساعة)'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'قيد الانتظار'),
        ('confirmed', 'تم التأكيد'),
        ('picked_up', 'تم الاستلام'),
        ('in_transit', 'في الطريق'),
        ('out_for_delivery', 'خرج للتسليم'),
        ('delivered', 'تم التوصيل'),
        ('cancelled', 'ملغى'),
        ('failed', 'فشل التوصيل'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('cod', 'الدفع عند الاستلام'),
        ('knet', 'KNET'),
    )
    
    # Basic Info
    tracking_number = models.CharField(max_length=10, unique=True, default=generate_tracking_number)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  # بدل CASCADE علشان لو الضيف مش موجود، مايحصلش error
        null=True,                   # يسمح بقيم فارغة للضيف
        blank=True,                  # يسمح بالفراغ في الفورم
        related_name='orders'
    )
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    
    # Location Info
    from_area = models.CharField(max_length=50, choices=AREA_CHOICES)
    to_area = models.CharField(max_length=50, choices=AREA_CHOICES)
    pickup_address = models.TextField(blank=True)
    delivery_address = models.TextField()
    
    # Package Info
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES)
    notes = models.TextField(blank=True)
    
    # Pricing
    base_price = models.DecimalField(max_digits=8, decimal_places=3)
    total_price = models.DecimalField(max_digits=8, decimal_places=3)
    
    # Payment
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    is_paid = models.BooleanField(default=False)
    
    # Status & Assignment
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    driver = models.ForeignKey('accounts.Driver', on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pickup_time = models.DateTimeField(null=True, blank=True)
    delivery_time = models.DateTimeField(null=True, blank=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    
    # Rating
    customer_rating = models.IntegerField(null=True, blank=True)
    customer_review = models.TextField(blank=True)
    
    def __str__(self):
        return f"Order #{self.tracking_number} - {self.customer_name}"
    
    def calculate_price(self):
        """Calculate order price based on weight, distance, and service type"""
        base_price = 2.5  # KWD
        weight_price = float(self.weight) * 0.5
        
        service_multipliers = {
            'ultra': 2.5,
            'super': 2.0,
            'express1': 1.5,
            'normal1': 1.0,
            'normal2': 0.9,
            'normal3': 0.8,
            'normal4': 0.7,
        }
        
        service_multiplier = service_multipliers.get(self.service_type, 1.0)
        distance_multiplier = 1.3 if self.from_area != self.to_area else 1.0
        
        total = (base_price + weight_price) * service_multiplier * distance_multiplier
        return round(total, 3)
    
    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.calculate_price()
            self.base_price = self.total_price
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=30, choices=Order.STATUS_CHOICES)
    notes = models.TextField(blank=True)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.order.tracking_number} - {self.get_status_display()}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Order Status Histories'

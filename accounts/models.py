from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('driver', 'Driver'),
        ('merchant', 'Merchant'),
        ('admin', 'Admin'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} - {self.get_user_type_display()}"
    
    class Meta:
        ordering = ['-created_at']


class Driver(models.Model):
    VEHICLE_CHOICES = (
        ('motorcycle', 'Motorcycle'),
        ('car', 'Car'),
        ('van', 'Van'),
    )
    
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('offline', 'Offline'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES)
    license_number = models.CharField(max_length=50)
    license_image = models.ImageField(upload_to='licenses/')
    vehicle_registration = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    total_deliveries = models.IntegerField(default=0)
    areas = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return f"Driver: {self.user.username}"
    
    class Meta:
        ordering = ['-rating']


class Merchant(models.Model):
    BUSINESS_TYPE_CHOICES = (
        ('restaurant', 'Restaurant'),
        ('instagram', 'Instagram Business'),
        ('home-business', 'Home Business'),
        ('ecommerce', 'E-commerce'),
        ('retail', 'Retail Store'),
        ('wholesale', 'Wholesale'),
        ('other', 'Other'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='merchant_profile')
    business_name = models.CharField(max_length=200)
    business_type = models.CharField(max_length=30, choices=BUSINESS_TYPE_CHOICES)
    business_phone = models.CharField(max_length=15)
    business_email = models.EmailField(blank=True)
    business_address = models.TextField()
    area = models.CharField(max_length=100)
    website = models.URLField(blank=True, null=True)
    instagram = models.CharField(max_length=100, blank=True)
    expected_orders_per_month = models.IntegerField(default=0)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.business_name
    
    class Meta:
        ordering = ['-created_at']

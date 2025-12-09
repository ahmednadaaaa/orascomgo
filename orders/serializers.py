from rest_framework import serializers
from .models import Order, OrderStatusHistory
from accounts.serializers import UserSerializer, DriverSerializer

class OrderSerializer(serializers.ModelSerializer):
    customer_details = UserSerializer(source='customer', read_only=True)
    driver_details = DriverSerializer(source='driver', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    service_type_display = serializers.CharField(source='get_service_type_display', read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['tracking_number', 'customer', 'base_price', 'total_price', 
                            'created_at', 'updated_at']
    
    def create(self, validated_data):
        user = self.context['request'].user
        if user.is_authenticated:
            validated_data['customer'] = user  # لو المستخدم مسجل دخول
        else:
            validated_data['customer'] = None  # لو الضيف، حط None
        return super().create(validated_data)


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = OrderStatusHistory
        fields = '__all__'
        read_only_fields = ['created_at', 'created_by']


class OrderTrackingSerializer(serializers.ModelSerializer):
    """Simplified serializer for public tracking"""
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = ['tracking_number', 'status', 'status_display', 'from_area', 'to_area',
                  'created_at', 'estimated_delivery', 'status_history']

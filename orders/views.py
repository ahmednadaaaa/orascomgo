from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Order, OrderStatusHistory
from .serializers import OrderSerializer, OrderStatusHistorySerializer, OrderTrackingSerializer

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]  
        return [IsAuthenticated()]


    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        elif user.user_type == 'driver':
            return Order.objects.filter(driver__user=user)
        elif user.user_type == 'merchant':
            return Order.objects.filter(customer=user)
        return Order.objects.filter(customer=user)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        if not new_status:
            return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = new_status
        order.save()
        
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            notes=notes,
            created_by=request.user
        )
        
        if new_status == 'picked_up':
            order.pickup_time = timezone.now()
        elif new_status == 'delivered':
            order.delivery_time = timezone.now()
        
        order.save()
        
        return Response({'message': 'Order status updated successfully'})
    
    @action(detail=True, methods=['post'])
    def assign_driver(self, request, pk=None):
        order = self.get_object()
        driver_id = request.data.get('driver_id')
        
        if not driver_id:
            return Response({'error': 'Driver ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        from accounts.models import Driver
        driver = get_object_or_404(Driver, id=driver_id)
        
        order.driver = driver
        order.status = 'confirmed'
        order.save()
        
        OrderStatusHistory.objects.create(
            order=order,
            status='confirmed',
            notes=f'Driver assigned: {driver.user.get_full_name()}',
            created_by=request.user
        )
        
        return Response({'message': 'Driver assigned successfully'})
    
    @action(detail=True, methods=['post'])
    def rate_order(self, request, pk=None):
        order = self.get_object()
        
        if order.customer != request.user:
            return Response({'error': 'You can only rate your own orders'}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        rating = request.data.get('rating')
        review = request.data.get('review', '')
        
        if not rating or rating < 1 or rating > 5:
            return Response({'error': 'Rating must be between 1 and 5'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        order.customer_rating = rating
        order.customer_review = review
        order.save()
        
        if order.driver:
            driver = order.driver
            driver.total_deliveries += 1

            total_ratings = Order.objects.filter(
                driver=driver, 
                customer_rating__isnull=False
            ).count()
            avg_rating = Order.objects.filter(
                driver=driver, 
                customer_rating__isnull=False
            ).aggregate(models.Avg('customer_rating'))['customer_rating__avg']
            driver.rating = avg_rating
            driver.save()
        
        return Response({'message': 'Order rated successfully'})


@api_view(['GET'])
@permission_classes([AllowAny])
def track_order(request, tracking_number):
    """Public endpoint to track order by tracking number"""
    order = get_object_or_404(Order, tracking_number=tracking_number)
    serializer = OrderTrackingSerializer(order)
    return Response(serializer.data)







ACTIVE_STATUSES = [
    'pending', 'confirmed', 'picked_up', 
    'in_transit', 'out_for_delivery', 'delivered'
]

@api_view(['GET'])
@permission_classes([AllowAny])
def track_order(request, tracking_number):
    """
    Public endpoint to track order by tracking number.
    يعرض الطلب فقط لو حالته ضمن ACTIVE_STATUSES.
    """
    order = get_object_or_404(Order, tracking_number=tracking_number, status__in=ACTIVE_STATUSES)
    serializer = OrderTrackingSerializer(order)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def track_by_phone(request, phone):
    """
    Public endpoint to track orders by customer phone.
    يعرض الطلبات فقط لو حالتها ضمن ACTIVE_STATUSES.
    """
    orders = Order.objects.filter(
        customer_phone=phone,
        status__in=ACTIVE_STATUSES
    ).order_by('-created_at')

    serializer = OrderTrackingSerializer(orders, many=True)
    return Response(serializer.data)
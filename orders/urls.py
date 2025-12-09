from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, track_order, track_by_phone

router = DefaultRouter()
router.register('', OrderViewSet, basename='order')

urlpatterns = [
    path('track/<str:tracking_number>/', track_order, name='track-order'),
    path('track-by-phone/<str:phone>/', track_by_phone, name='track-by-phone'),

    path('', include(router.urls)),
    
    
    ]
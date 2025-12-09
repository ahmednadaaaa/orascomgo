from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, 
    LoginView, 
    logout_view, 
    UserProfileView,
    change_password,
    driver_register_view,
    merchant_register_view,
    DriverViewSet, 
    MerchantViewSet
)

router = DefaultRouter()
router.register('drivers', DriverViewSet, basename='driver')
router.register('merchants', MerchantViewSet, basename='merchant')

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('change-password/', change_password, name='change-password'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # Driver & Merchant Registration (من الموقع)
    path('register/driver/', driver_register_view, name='driver_register'),
    path('register/merchant/', merchant_register_view, name='merchant_register'),
    
    # Router
    path('', include(router.urls)),
]
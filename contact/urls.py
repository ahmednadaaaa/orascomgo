# contact/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import contact_us_view, ContactMessageViewSet

router = DefaultRouter()
router.register('messages', ContactMessageViewSet, basename='contact_message')

urlpatterns = [
    path('', contact_us_view, name='contact_us'),
    path('', include(router.urls)),  
]
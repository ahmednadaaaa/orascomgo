from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),  # تغيير حسب اسم تطبيقك
    path('api/', include('accounts.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/tracking/', include('tracking.urls')),
    path('api/contact/', include('contact.urls')),
    # الصفحات الرئيسية
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('login.html', TemplateView.as_view(template_name='login.html'), name='login_page'),
    path('signup.html', TemplateView.as_view(template_name='signup.html')),
    path('profile.html', TemplateView.as_view(template_name='profile.html'), name='profile_page'),    

    path('change-password.html', TemplateView.as_view(template_name='change-password.html')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage
from .serializers import ContactMessageSerializer
import json

class ContactMessageViewSet(viewsets.ModelViewSet):
    """Admin يقدر يشوف ويرد على الرسائل"""
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        if self.request.user.is_staff:
            return ContactMessage.objects.all()
        return ContactMessage.objects.none()


@api_view(['POST'])
@permission_classes([AllowAny])
def contact_us_view(request):
    """استقبال رسائل التواصل من الموقع"""
    try:
        # طباعة البيانات المستقبلة للتشخيص
        print(f"Request data: {request.data}")
        
        name = request.data.get('name', '').strip()
        phone = request.data.get('phone', '').strip()
        subject = request.data.get('subject', '').strip()
        message = request.data.get('message', '').strip()

        print(f"Extracted: name={name}, phone={phone}, subject={subject}, message={message}")

        # Validation
        if not name:
            return Response(
                {'error': 'الاسم مطلوب'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not phone:
            return Response(
                {'error': 'رقم الهاتف مطلوب'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not subject:
            return Response(
                {'error': 'الموضوع مطلوب'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not message:
            return Response(
                {'error': 'الرسالة مطلوبة'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # التحقق من صيغة رقم الهاتف
        if len(phone) < 8:
            return Response(
                {'error': 'رقم الهاتف يجب أن يكون 8 أرقام على الأقل'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not phone.isdigit():
            return Response(
                {'error': 'رقم الهاتف يجب أن يحتوي على أرقام فقط'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # إنشاء الرسالة
        contact = ContactMessage.objects.create(
            name=name,
            phone=phone,
            subject=subject,
            message=message
        )

        print(f"Message created with ID: {contact.id}")

        # إرسال بريد إلى Admin
        try:
            send_mail(
                subject=f"رسالة جديدة من {name}",
                message=f"""
الاسم: {name}
رقم الهاتف: {phone}
الموضوع: {subject}

الرسالة:
{message}

---
تم الاستقبال في: {contact.created_at}
رابط الرد: {settings.SITE_URL}/admin/contact/contactmessage/{contact.id}/change/
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False
            )
            print("Email sent successfully")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")

        return Response({
            'message': '✅ تم استقبال رسالتك بنجاح! سنتواصل معك قريباً',
            'id': contact.id,
            'phone': phone
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(f"Error in contact_us_view: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'حدث خطأ: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        

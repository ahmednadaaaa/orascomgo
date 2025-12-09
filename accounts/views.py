# views.py - معدّل حسب models بتاعتك
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, authenticate
from .serializers import (UserSerializer, RegisterSerializer, LoginSerializer, 
                          DriverSerializer, MerchantSerializer)
from .models import Driver, Merchant

User = get_user_model()

# ===== Register View =====
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.get(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)

# ===== Login View =====
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Login successful'
        })

# ===== Logout View =====
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logout successful'})
    except:
        return Response({'error': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)

# ===== User Profile View =====
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

# ===== Driver Registration View (من الموقع) =====
@api_view(['POST'])
@permission_classes([AllowAny])
def driver_register_view(request):
    """استقبال طلب تسجيل المندوب من الموقع"""
    try:
        full_name = request.data.get('full_name')
        phone = request.data.get('phone')
        email = request.data.get('email')
        work_areas = request.data.get('work_areas')  # Should be JSON list
        vehicle_type = request.data.get('vehicle_type')
        license_number = request.data.get('license_number')
        license_image = request.FILES.get('license_image')
        message = request.data.get('message')

        # التحقق من البيانات المطلوبة
        if not all([full_name, phone, email, vehicle_type, license_number]):
            return Response(
                {'error': 'جميع الحقول المطلوبة مفقودة'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # التحقق من أن الهاتف فريد
        if User.objects.filter(phone=phone).exists():
            return Response(
                {'error': 'رقم الهاتف مسجل بالفعل'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # إنشاء User أولاً
        # استخراج الاسم الأول والأخير
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        user = User.objects.create_user(
            username=phone,  # استخدم الهاتف كاسم مستخدم
            email=email,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            user_type='driver'
        )

        # إنشاء Driver Profile
        import json
        try:
            work_areas_list = json.loads(work_areas) if isinstance(work_areas, str) else work_areas
        except:
            work_areas_list = []

        driver = Driver.objects.create(
            user=user,
            vehicle_type=vehicle_type,
            license_number=license_number,
            license_image=license_image,
            areas=work_areas_list
        )

        # إنشاء Token
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'message': 'تم إرسال طلبك بنجاح! سنتواصل معك قريباً',
            'id': driver.id,
            'user_id': user.id,
            'token': token.key
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ===== Merchant Registration View (من الموقع) =====
@api_view(['POST'])
@permission_classes([AllowAny])
def merchant_register_view(request):
    """استقبال طلب تسجيل التاجر من الموقع"""
    try:
        business_name = request.data.get('business_name')
        phone = request.data.get('phone')
        email = request.data.get('email')
        website_instagram = request.data.get('website_instagram')
        business_type = request.data.get('business_type')
        area = request.data.get('area')
        expected_orders = request.data.get('expected_orders')
        message = request.data.get('message')

        # التحقق من البيانات المطلوبة
        if not all([business_name, phone, email, business_type, area]):
            return Response(
                {'error': 'جميع الحقول المطلوبة مفقودة'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # التحقق من أن الهاتف فريد
        if User.objects.filter(phone=phone).exists():
            return Response(
                {'error': 'رقم الهاتف مسجل بالفعل'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # إنشاء User أولاً
        user = User.objects.create_user(
            username=phone,  # استخدم الهاتف كاسم مستخدم
            email=email,
            phone=phone,
            first_name=business_name,
            user_type='merchant'
        )

        # إنشاء Merchant Profile
        merchant = Merchant.objects.create(
            user=user,
            business_name=business_name,
            business_type=business_type,
            business_phone=phone,
            business_email=email,
            business_address='',  # سيتم ملؤه لاحقاً
            area=area,
            website=website_instagram if website_instagram.startswith('http') else '',
            instagram=website_instagram if not website_instagram.startswith('http') else '',
            expected_orders_per_month=int(expected_orders) if expected_orders else 0,
            is_approved=False
        )

        # إنشاء Token
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'message': 'تم إرسال طلبك بنجاح! سنتواصل معك قريباً',
            'id': merchant.id,
            'user_id': user.id,
            'token': token.key
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ===== Change Password View =====
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not old_password or not new_password:
        return Response(
            {'error': 'Old and new passwords are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    if not user.check_password(old_password):
        return Response(
            {'error': 'Old password is incorrect'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(new_password) < 8:
        return Response(
            {'error': 'New password must be at least 8 characters'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    user.set_password(new_password)
    user.save()
    return Response({'message': 'Password changed successfully'})

# ===== Driver ViewSet =====
class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Driver.objects.all()
        try:
            return Driver.objects.filter(user=self.request.user)
        except:
            return Driver.objects.none()

# ===== Merchant ViewSet =====
class MerchantViewSet(viewsets.ModelViewSet):
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Merchant.objects.all()
        try:
            return Merchant.objects.filter(user=self.request.user)
        except:
            return Merchant.objects.none()
        

def logout_page(request):
    return render(request, 'logout.html')
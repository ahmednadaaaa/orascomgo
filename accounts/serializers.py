# serializers.py - أضف دي
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework.authtoken.models import Token
from .models import Driver, Merchant

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'first_name', 'last_name', 
                  'user_type', 'address', 'profile_picture', 'is_verified', 'created_at']
        read_only_fields = ['id', 'is_verified', 'created_at']

class DriverSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Driver
        fields = '__all__'

class MerchantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Merchant
        fields = '__all__'

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password', 'password_confirm', 
                  'first_name', 'last_name', 'user_type']
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user

class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)
    def validate(self, data):
        phone = data.get('phone')
        password = data.get('password')
        if phone and password:
            try:
                user = User.objects.get(phone=phone)
                user = authenticate(username=user.username, password=password)
            except User.DoesNotExist:
                raise serializers.ValidationError('Invalid credentials')
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            data['user'] = user
        else:
            raise serializers.ValidationError('Must include phone and password')
        return data
from rest_framework import serializers
from .models import ContactMessage

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'phone', 'subject', 'message', 'status', 'reply', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'reply', 'created_at', 'updated_at']


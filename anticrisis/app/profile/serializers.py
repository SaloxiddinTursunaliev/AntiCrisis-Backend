from rest_framework import serializers
from django.contrib.auth.models import User
from ..models2 import BusinessProfile, BusinessType

class BusinessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessType
        fields = ['id', 'name', 'description']  # Adjust fields as necessary

class BusinessProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessProfile
        fields = '__all__'  # Include all fields from BusinessProfile

class UserProfileSerializer(serializers.ModelSerializer):
    business_profile = BusinessProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'business_profile']
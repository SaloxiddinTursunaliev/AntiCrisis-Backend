from rest_framework import serializers
from django.contrib.auth.models import User
from ..models2 import Profile, BusinessType

class BusinessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessType
        fields = ['id', 'name', 'description']  # Adjust fields as necessary

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'  # Include all fields from Profile

class UserProfileSerializer(serializers.ModelSerializer):
    business_profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'business_profile']
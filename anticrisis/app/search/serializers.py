from rest_framework import serializers
from ..models2 import BusinessProfile

class BusinessProfileSearchSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')  # Assuming user is a ForeignKey in BusinessProfile

    class Meta:
        model = BusinessProfile
        fields = ['id', 'business_name', 'avatar_picture', 'about', 'username']
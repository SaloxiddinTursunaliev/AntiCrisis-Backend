from rest_framework import serializers
from ..models2 import Profile

class ProfileSearchSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')  # Assuming user is a ForeignKey in Profile

    class Meta:
        model = Profile
        fields = ['id', 'business_name', 'avatar_url', 'about', 'username']
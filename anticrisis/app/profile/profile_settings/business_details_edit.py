from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from ...models2 import Profile
from rest_framework.permissions import IsAuthenticated
import os

User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'username',
            'business_name',
            'avatar_url',
            'banner_url',
            'about',
            'phone',
            'email',
            'website',
            'address',
            'location_coordinates'
        ]

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def business_details_edit(request):
    try:
        profile = request.user.profile

        if request.method == 'GET':
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'POST':
            serializer = ProfileSerializer(profile, data=request.data, partial=True)  # Allow partial updates
            if serializer.is_valid():
                serializer.save()  # Save the updated profile
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Profile.DoesNotExist:
        return Response({'error': 'Profile does not exist.'}, status=status.HTTP_404_NOT_FOUND)
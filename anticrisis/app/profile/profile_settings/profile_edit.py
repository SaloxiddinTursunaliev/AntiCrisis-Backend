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
        fields = ['banner_url', 'avatar_url', 'username', 'business_name']

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def profile_edit(request):
    try:
        profile = request.user.profile # .profile is the related name for the Profile model
        # This is better than querying manually like:
        # Profile.objects.get(user=request.user)
        # because it's: cleaner, faster (if already cached) and more Django-idiomatic.

        if request.method == 'GET':
            response_data = {
                'banner_url': request.build_absolute_uri(profile.banner_url.url) if profile.banner_url else None,
                'avatar_url': request.build_absolute_uri(profile.avatar_url.url) if profile.avatar_url else None,
                'username': request.user.username,
                'business_name': profile.business_name
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
        elif request.method == 'POST':
            serializer = ProfileSerializer(profile, data=request.data, partial=True)  # Allow partial updates
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Profile.DoesNotExist:
        return Response({'error': 'Profile does not exist.'}, status=status.HTTP_404_NOT_FOUND)
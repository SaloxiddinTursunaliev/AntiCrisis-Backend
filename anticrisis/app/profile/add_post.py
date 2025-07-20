from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from ..models2 import Post
from django.contrib.auth.models import User

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['description', 'post_image', 'likes_count', 'created_at']

@api_view(['GET', 'POST'])  # Allow GET and POST methods
@permission_classes([IsAuthenticated])
def profile_posts(request, username):
    if request.method == 'GET':
        try:
            # Retrieve user by ID
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        offset = int(request.query_params.get('offset', 0))  # Default to 0 if not provided
        page_size = int(request.query_params.get('pageSize', 20))  # Default to 20 if not provided}

        posts = Post.objects.filter(
            business_profile=user.business_profile
        )[offset:offset + page_size]  # Apply offset and limit

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(business_profile=request.user.business_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
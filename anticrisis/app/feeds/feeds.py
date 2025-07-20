from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from ..models2 import Post

class PostSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    business_name = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['description', 'post_image', 'likes_count', 'created_at', 'username', 'business_name']

    def get_username(self, obj):
        return obj.business_profile.user.username  # Adjust based on your model relationships

    def get_business_name(self, obj):
        return obj.business_profile.name  # Assumes the business name is stored in the business profile

@api_view(['GET'])  # Allow GET method
@permission_classes([IsAuthenticated])
def get_feeds(request):
    # Pagination parameters
    offset = int(request.query_params.get('offset', 0))  # Default to 0 if not provided
    page_size = int(request.query_params.get('pageSize', 20))  # Default to 20 if not provided

    # Get the user's following list (assuming a ManyToMany relationship)
    following_users = request.user.following.all()  # Adjust according to your model

    # Retrieve posts from the users that the authenticated user follows
    posts = Post.objects.filter(business_profile__user__in=following_users)[offset:offset + page_size]

    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
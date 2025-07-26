from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from ..models2 import Post, Follow

class PostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    business_name = serializers.CharField(source='user.profile.business_name', read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'description', 'post_image', 'likes_count', 'created_at',
            'username', 'business_name', 'avatar_url'
        ]

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.user.profile.avatar_url:
            return request.build_absolute_uri(obj.user.profile.avatar_url.url)
        return None
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_feeds(request):
    try:
        offset = int(request.query_params.get('offset', 0))
        page_size = int(request.query_params.get('pageSize', 20))
    except ValueError:
        return Response({'error': 'Invalid offset or pageSize'}, status=status.HTTP_400_BAD_REQUEST)

    following_ids = list(
        Follow.objects
        .filter(follower_id=request.user.id)
        .values_list('following_id', flat=True)
    )

    if not following_ids:
        return Response([], status=status.HTTP_200_OK)

    posts = (
        Post.objects
        .filter(user_id__in=following_ids)
        .select_related('user', 'user__profile')
        .only(
            'id', 'description', 'post_image', 'likes_count', 'created_at',
            'user_id', 'user__username',
            'user__profile__business_name', 'user__profile__avatar_url'
        )
        .order_by('-created_at')
        [offset:offset + page_size]
    )

    serializer = PostSerializer(posts, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)
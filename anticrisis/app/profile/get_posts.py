from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..models2 import Post
from django.contrib.auth.models import User

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def profile_posts(request, username):
    if request.method == 'GET':
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        offset = int(request.query_params.get('offset', 0))
        page_size = int(request.query_params.get('pageSize', 20))

        posts = Post.objects.filter(
            user=user
        ).only(
            'id', 'description', 'post_image', 'likes_count', 'created_at'
        ).order_by('-created_at')[offset:offset + page_size]

        data = []
        for p in posts:
            data.append({
                'description': p.description,
                'post_image': request.build_absolute_uri(p.post_image.url) if p.post_image else None,
                'likes_count': p.likes_count,
                'created_at': p.created_at.isoformat(),
            })

        return Response(data, status=status.HTTP_200_OK)
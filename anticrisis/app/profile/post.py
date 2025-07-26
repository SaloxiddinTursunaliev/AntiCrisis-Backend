from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils.timezone import now
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from ..models2 import Post

MAX_IMAGE_SIZE_MB = 5

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def post(request):
    if request.method == 'GET':
        # Fetch user's posts
        user = request.user
        posts = Post.objects.filter(user=user).order_by('-created_at')
        serialized_posts = [{
            'id': post.id,
            'description': post.description,
            'post_image': request.build_absolute_uri(post.post_image.url) if post.post_image else None,
            'likes_count': post.likes_count,
            'created_at': post.created_at.isoformat(),
        } for post in posts]
        return Response(serialized_posts, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        user = request.user
        description = request.data.get('description')  # allow None or empty
        image = request.FILES.get('post_image')

        if image:
            content_type = image.content_type or ''
            if not content_type.startswith("image/"):
                return Response({'error': 'Uploaded file must be an image.'}, status=status.HTTP_400_BAD_REQUEST)
            if image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
                return Response({'error': f'Image must be under {MAX_IMAGE_SIZE_MB}MB.'}, status=status.HTTP_400_BAD_REQUEST)

        post = Post.objects.create(
            user=user,
            description=description or '',
            post_image=image,
            created_at=now()  # Only if override auto_now_add
        )

        return Response({
            'id': post.id,
            'description': post.description,
            'post_image': request.build_absolute_uri(post.post_image.url) if post.post_image else None,
            'likes_count': post.likes_count,
            'created_at': post.created_at.isoformat(),
        }, status=status.HTTP_201_CREATED)

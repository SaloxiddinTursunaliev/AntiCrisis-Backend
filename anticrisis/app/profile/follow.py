from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404

from ..models2 import Profile, Follow

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def follow_user(request, username):
    # Fetch profile and prefetch associated user in one query
    business_profile_to_follow = get_object_or_404(
        Profile.objects.select_related('user'),
        user__username=username
    )

    follower_user = request.user
    following_user = business_profile_to_follow.user

    if follower_user == following_user:
        return Response({'error': 'You cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'POST':
        with transaction.atomic():
            follow, created = Follow.objects.select_for_update().get_or_create(
                follower=follower_user,
                following=following_user
            )

            if not created:
                return Response({'message': 'You are already following this business profile'}, status=status.HTTP_400_BAD_REQUEST)

            # Update counts using F expressions atomically
            Profile.objects.filter(user=follower_user).update(followings_count=F('followings_count') + 1)
            Profile.objects.filter(user=following_user).update(followers_count=F('followers_count') + 1)

        return Response(
            {'message': f'You are now following {business_profile_to_follow.business_name}'},
            status=status.HTTP_201_CREATED
        )

    elif request.method == 'DELETE':
        with transaction.atomic():
            deleted, _ = Follow.objects.filter(
                follower=follower_user,
                following=following_user
            ).delete()

            if not deleted:
                return Response({'message': 'You are not following this business profile'}, status=status.HTTP_400_BAD_REQUEST)

            # Decrement counters
            Profile.objects.filter(user=follower_user).update(followings_count=F('followings_count') - 1)
            Profile.objects.filter(user=following_user).update(followers_count=F('followers_count') - 1)

        return Response(
            {'message': f'You have unfollowed {business_profile_to_follow.business_name}'},
            status=status.HTTP_204_NO_CONTENT
        )

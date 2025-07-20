from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..models2 import BusinessProfile, Follow

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def follow_user(request, username):
    # Retrieve the business profile to follow/unfollow
    try:
        business_profile_to_follow = BusinessProfile.objects.get(user__username=username)
    except BusinessProfile.DoesNotExist:
        return Response({'error': 'Business profile not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        # Attempt to create follow relationship
        follow, created = Follow.objects.get_or_create(
            follower=request.user.business_profile,
            following=business_profile_to_follow
        )

        if not created:
            return Response({'message': 'You are already following this business profile'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': f'You are now following {business_profile_to_follow.business_name}'}, status=status.HTTP_201_CREATED)

    elif request.method == 'DELETE':
        # Attempt to delete follow relationship
        try:
            follow = Follow.objects.get(
                follower=request.user.business_profile,
                following=business_profile_to_follow
            )
            follow.delete()
            return Response({'message': f'You have unfollowed {business_profile_to_follow.business_name}'}, status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response({'message': 'You are not following this business profile'}, status=status.HTTP_400_BAD_REQUEST)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from ..models2 import Profile, UserBusinessType, Follow

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request, username):
    """
    Returns a user's business profile along with business types and follow status.
    Optimized for minimal DB load and fast serialization.
    """
    viewer_user = request.user

    try:
        # Optimized user + profile join
        user = User.objects.select_related('profile').only(
            'id', 'username',
            'profile__id', 'profile__user_id',
            'profile__business_name', 'profile__avatar_url',
            'profile__banner_url', 'profile__followers_count',
            'profile__followings_count', 'profile__discounts_received_count',
            'profile__discounts_used_count', 'profile__about',
            'profile__phone', 'profile__email',
            'profile__website', 'profile__address',
            'profile__location_coordinates'
        ).get(username=username)

        profile = user.profile

    except (User.DoesNotExist, Profile.DoesNotExist):
        return Response({'detail': 'User or business profile not found'}, status=status.HTTP_404_NOT_FOUND)

    # Manual serialization for maximum performance
    profile_data = {
        'id': profile.id,
        'business_name': profile.business_name,
        'banner_url': request.build_absolute_uri(profile.banner_url.url) if profile.banner_url else None,
        'avatar_url': request.build_absolute_uri(profile.avatar_url.url) if profile.avatar_url else None,
        'followers_count': profile.followers_count,
        'followings_count': profile.followings_count,
        'discounts_received_count': profile.discounts_received_count,
        'discounts_used_count': profile.discounts_used_count,
        'about': profile.about,
        'phone': profile.phone,
        'email': profile.email,
        'website': profile.website,
        'address': profile.address,
        'location_coordinates': profile.location_coordinates,
        'linked_profiles': list(profile.linked_profiles.values_list('id', flat=True)[:5]),
    }

    # Fetch related business types efficiently
    business_type_tuples = UserBusinessType.objects.select_related('business_type').filter(
        user=user
    ).values_list(
        'business_type__id', 'business_type__name', 'business_type__description'
    )
    # business_type_tuples = BusinessType.objects.filter(
    #     userbusinesstype__user_id=user.id
    # ).values_list('id', 'name', 'description')
        
    # include them in Redis
    business_types = [
        {'id': i, 'name': n, 'description': d}
        for i, n, d in business_type_tuples
    ] # maybe do not include desc

    # Efficient follow check (EXISTS query)
    is_following = Follow.objects.filter(
        follower=viewer_user,
        following=user
    ).exists()

    # Final response
    response_data = {
        'id': user.id,
        'username': user.username,
        'profile': profile_data,
        'business_types': business_types,
        'is_following': is_following,
    }

    return Response(response_data, status=status.HTTP_200_OK)

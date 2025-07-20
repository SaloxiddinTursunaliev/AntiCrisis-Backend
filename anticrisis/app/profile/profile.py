# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from ..models2 import BusinessProfile, BusinessType, BusinessProfileType, Discount, Follow
from .serializers import UserProfileSerializer, BusinessTypeSerializer
from django.db.models import Avg

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request, username):
    try:
        # Retrieve user by ID
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        # Retrieve the business profile associated with the user
        business_profile = BusinessProfile.objects.get(user=user)
    except BusinessProfile.DoesNotExist:
        return Response({'error': 'Business profile not found'}, status=status.HTTP_404_NOT_FOUND)

    # Serialize user profile data
    user_profile_data = UserProfileSerializer(user).data

    #######################################################

     # Retrieve the business types associated with the user's business profile
    business_profile_types = BusinessProfileType.objects.filter(profile=business_profile)
    business_types = BusinessType.objects.filter(id__in=business_profile_types.values_list('business_type', flat=True))

    # Serialize the specified business types
    business_types_serialized = BusinessTypeSerializer(business_types, many=True).data

    # Add business types to the user profile data
    user_profile_data['business_types'] = business_types_serialized

    #######################################################
    
    # Get followers count from the Follow model
    followers_count = Follow.objects.filter(following=business_profile).count()
    user_profile_data['followers_count'] = followers_count

    #######################################################

    # Get followings count from the Follow model
    followings_count = Follow.objects.filter(follower=business_profile).count()
    user_profile_data['followings_count'] = followings_count

    #######################################################
    
    # Check if the requester user is following the business profile
    is_following = Follow.objects.filter(follower=request.user.business_profile, following=business_profile).exists()
    user_profile_data['is_following'] = is_following

    #######################################################

    # Get average discount percentage
    discounts = Discount.objects.filter(issuer=business_profile)
    if discounts.exists():
        average_discount = discounts.aggregate(Avg('percentage'))['percentage__avg']
    else:
        average_discount = 0  # Default value if there are no discounts

    user_profile_data['average_discount_percentage'] = average_discount

    #######################################################

    return Response(user_profile_data, status=status.HTTP_200_OK)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models2 import BusinessProfile
from .serializers import BusinessProfileSearchSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_business_by_id(request, business_id):
    try:
        # Retrieve the business profile by ID
        business_profile = BusinessProfile.objects.get(id=business_id)
    except BusinessProfile.DoesNotExist:
        return Response({'error': 'Business profile not found'}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the business profile data
    serialized_data = BusinessProfileSearchSerializer(business_profile).data
    
    return Response(serialized_data, status=status.HTTP_200_OK)
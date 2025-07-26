from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models2 import Profile
from .serializers import ProfileSearchSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_business_by_id(request, business_id):
    try:
        # Use select_related to avoid extra query on `user`
        profile = Profile.objects.select_related('user').get(id=business_id)
    except Profile.DoesNotExist:
        return Response({'error': 'Business profile not found'}, status=status.HTTP_404_NOT_FOUND)

    serialized_data = ProfileSearchSerializer(profile).data
    
    return Response(serialized_data, status=status.HTTP_200_OK)

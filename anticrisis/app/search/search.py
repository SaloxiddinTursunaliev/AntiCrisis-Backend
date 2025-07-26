from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from ..models2 import Profile
from .serializers import ProfileSearchSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_businesses(request):
    query = request.query_params.get('q', None)  # Query parameter for search
    offset = int(request.query_params.get('offset', 0))  # Default to 0 if not provided
    page_size = int(request.query_params.get('pageSize', 20))  # Default to 20 if not provided

    if query:
        # # Filter business profiles where the business name starts with the query
        # business_profiles = Profile.objects.filter(
        #     Q(business_name__istartswith=query)
        # )

        # Use LIKE for more flexible searching
        business_profiles = Profile.objects.filter(
            business_name__icontains=query
        )[offset:offset + page_size]  # Apply offset and limit

        serializer = ProfileSearchSerializer(business_profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Please provide a search query (q)'}, status=status.HTTP_400_BAD_REQUEST)
    
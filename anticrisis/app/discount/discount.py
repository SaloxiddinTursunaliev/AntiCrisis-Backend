from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from ..models2 import Discount, BusinessProfile
from django.shortcuts import get_object_or_404
from django.db.models import Q

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ['id', 'recipient', 'percentage', 'redeem_limit']  # Include relevant fields

    def create(self, validated_data):
        issuer = self.context['issuer']  # Get issuer from context
        return Discount.objects.create(issuer=issuer, **validated_data)

class BusinessProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessProfile
        fields = ['business_name', 'avatar_picture']  # Include relevant fields

class DiscountWithRecipientSerializer(serializers.ModelSerializer):
    recipient_details = BusinessProfileSerializer(source='recipient', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Discount
        fields = ['id', 'recipient', 'percentage', 'redeem_limit', 'redeem_used', 'created_at', 'recipient_details']

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def discount(request):
    if request.method == 'GET':
        query = request.query_params.get('q', None)  # Query parameter for search
        offset = int(request.query_params.get('offset', 0))  # Default to 0 if not provided
        page_size = int(request.query_params.get('pageSize', 20))  # Default to 20 if not provided
        
        # Handle fetching discounts
        business_profile = request.user.business_profile
        discount_type = request.query_params.get('type')

        # Initialize the queryset based on discount type
        if discount_type == 'issued':
            discounts = Discount.objects.filter(issuer=business_profile)
        elif discount_type == 'received':
            discounts = Discount.objects.filter(recipient=business_profile)
        else:
            return Response({'error': 'Invalid discount type specified.'}, status=status.HTTP_400_BAD_REQUEST)

        # Apply the search filter if a query is provided
        if query:
            # Filter based on business name (assuming a related field)
            discounts = discounts.filter(Q(recipient__business_name__icontains=query) | 
                                         Q(issuer__business_name__icontains=query))

        # Paginate the results
        discounts = discounts[offset:offset + page_size]

        # Serialize and return the response
        serializer = DiscountWithRecipientSerializer(discounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Handle creating a discount
        try:
            issuer = request.user.business_profile
        except BusinessProfile.DoesNotExist:
            return Response({'error': 'Business profile not found'}, status=status.HTTP_404_NOT_FOUND)

        recipient_user_id = request.data.get('recipient')
        if not recipient_user_id:
            return Response({'error': 'Recipient user ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        recipient_profile = get_object_or_404(BusinessProfile, user_id=recipient_user_id)

        data = {
            'recipient': recipient_profile.id,
            'percentage': request.data.get('percentage'),
            'redeem_limit': request.data.get('redeem_limit'),
        }

        serializer = DiscountSerializer(data=data, context={'issuer': issuer})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
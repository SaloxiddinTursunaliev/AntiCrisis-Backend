from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from ..models2 import Discount, BusinessProfile
from django.shortcuts import get_object_or_404

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ['id', 'recipient', 'percentage', 'redeem_limit']  # Include relevant fields

    def create(self, validated_data):
        issuer = self.context['issuer']  # Get issuer from context
        return Discount.objects.create(issuer=issuer, **validated_data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def discount(request):
    if request.method == 'GET':
        # Handle fetching discounts
        business_profile = request.user.business_profile
        discount_type = request.query_params.get('type')

        if discount_type == 'issued':
            discounts = Discount.objects.filter(issuer=business_profile)
        elif discount_type == 'received':
            discounts = Discount.objects.filter(recipient=business_profile)
        else:
            return Response({'error': 'Invalid discount type specified.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DiscountSerializer(discounts, many=True)
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
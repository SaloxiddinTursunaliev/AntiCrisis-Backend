from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q, F
from decimal import Decimal, InvalidOperation
from django.db import transaction
from ..models2 import Discount, Profile, User


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def discounts(request):
    user = request.user
    q = request.query_params.get('q', '')
    offset = int(request.query_params.get('offset', 0))
    page_size = int(request.query_params.get('pageSize', 20))
    discount_type = request.query_params.get('type')

    if discount_type == 'issued':
        queryset = Discount.objects.filter(issuer=user)
    elif discount_type == 'received':
        queryset = Discount.objects.filter(recipient=user)
    else:
        return Response({'error': 'Invalid discount type specified.'}, status=status.HTTP_400_BAD_REQUEST)

    if q:
        queryset = queryset.filter(
            Q(issuer__profile__business_name__icontains=q) |
            Q(recipient__profile__business_name__icontains=q)
        )

    queryset = (
        queryset
        .select_related('recipient__profile')
        .only(
            'id', 'recipient_id', 'percentage', 'redeem_limit', 'redeem_used', 'created_at',
            'recipient__profile__business_name', 'recipient__profile__avatar_url'
        )
        .order_by('-created_at')
        [offset:offset + page_size]
    )

    data = [
        {
            'id': d.id,
            'recipient': d.recipient_id,
            'percentage': str(d.percentage),
            'redeem_limit': str(d.redeem_limit),
            'redeem_used': str(d.redeem_used),
            'created_at': d.created_at.isoformat(),
            'recipient_details': {
                'business_name': d.recipient.profile.business_name,
                'avatar_url': request.build_absolute_uri(d.recipient.profile.avatar_url.url)
                if d.recipient.profile.avatar_url else None,
            }
        }
        for d in queryset
    ]

    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def discount_add(request):
    user = request.user
    try:
        recipient_id = int(request.data['recipient'])
        percentage = Decimal(request.data['percentage'])
        redeem_limit = Decimal(request.data['redeem_limit'])
    except (KeyError, ValueError, InvalidOperation):
        return Response({'error': 'Invalid input format.'}, status=status.HTTP_400_BAD_REQUEST)

    if not (0 < percentage <= 100):
        return Response({'error': 'Percentage must be between 1 and 100.'}, status=status.HTTP_400_BAD_REQUEST)

    if user.id == recipient_id:
        return Response({'error': 'Cannot issue discount to yourself.'}, status=status.HTTP_400_BAD_REQUEST)

    recipient = get_object_or_404(User.objects.only('id', 'username'), id=recipient_id)

    discount = Discount.objects.create(
        issuer=user,
        recipient=recipient,
        percentage=percentage,
        redeem_limit=redeem_limit,
    )

    # Efficient F-expression update to avoid read-modify-write overhead
    Profile.objects.filter(user=recipient).update(discounts_received_count=F('discounts_received_count') + 1)

    return Response({
        'id': discount.id,
        'issuer': user.username,
        'recipient': recipient.username,
        'percentage': str(discount.percentage),
        'redeem_limit': str(discount.redeem_limit),
        'created_at': discount.created_at.isoformat(),
    }, status=status.HTTP_201_CREATED)

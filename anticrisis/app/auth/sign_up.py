from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from ..models2 import Profile
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import login

User = get_user_model()  # Use the custom user model

class UserSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'business_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        business_name = validated_data.pop('business_name')
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        # Create the Profile instance
        Profile.objects.create(user=user, business_name=business_name)
        
        return user

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)

            # Log the user in
            login(request, user)

            return Response({
                'token': token.key,
                'id':user.id,
                'username': user.username,
                # 'business_name': user.business_profile.business_name,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# {
#     "username": "testuser",
#     "email": "test@example.com",
#     "password": "yourpassword",
#     "business_name": "Business Name"
# }
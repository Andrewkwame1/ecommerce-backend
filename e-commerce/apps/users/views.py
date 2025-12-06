from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta

from .models import User, Address, EmailVerificationToken, PasswordResetToken
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    AddressSerializer, PasswordChangeSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)
from .tasks import send_verification_email, send_password_reset_email
from utils.pagination import StandardPagination


class UserRegistrationView(APIView):
    """User registration endpoint"""
    
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Create email verification token
            token = EmailVerificationToken.objects.create(
                user=user,
                expires_at=timezone.now() + timedelta(days=1)
            )
            
            # Send verification email asynchronously
            send_verification_email.delay(user.id, str(token.token))
            
            return Response({
                'message': 'User registered successfully. Please check your email to verify your account.',
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """User login endpoint"""
    
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Login successful',
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_verified': user.is_verified
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """User logout endpoint"""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    """Email verification endpoint"""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, token):
        try:
            verification_token = EmailVerificationToken.objects.get(token=token)
            
            if verification_token.is_expired():
                return Response(
                    {'error': 'Verification token has expired'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = verification_token.user
            user.is_verified = True
            user.save(update_fields=['is_verified'])  # Update only this field
            
            # Delete the used token
            verification_token.delete()
            
            return Response({
                'message': 'Email verified successfully'
            }, status=status.HTTP_200_OK)
            
        except EmailVerificationToken.DoesNotExist:
            return Response(
                {'error': 'Invalid verification token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class PasswordChangeView(APIView):
    """Password change endpoint for authenticated users"""
    
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save(update_fields=['password'])  # Update only password field
            
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """Request password reset endpoint"""
    
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Create password reset token (or update existing one)
                token, created = PasswordResetToken.objects.get_or_create(
                    user=user,
                    defaults={'expires_at': timezone.now() + timedelta(hours=1)}
                )
                
                if not created:
                    # Update expiry for existing token
                    token.expires_at = timezone.now() + timedelta(hours=1)
                    token.is_used = False
                    token.save(update_fields=['expires_at', 'is_used'])
                
                # Send password reset email asynchronously
                send_password_reset_email.delay(user.id, str(token.token))
                
            except User.DoesNotExist:
                pass  # Don't reveal if email exists
            
            return Response({
                'message': 'If the email exists, a password reset link has been sent.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """Confirm password reset endpoint"""
    
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                token = PasswordResetToken.objects.get(token=serializer.validated_data['token'])
                
                if token.is_expired():
                    return Response(
                        {'error': 'Reset token has expired or been used'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                user = token.user
                user.set_password(serializer.validated_data['new_password'])
                user.save(update_fields=['password'])
                
                # Mark token as used
                token.is_used = True
                token.save(update_fields=['is_used'])
                
                return Response({
                    'message': 'Password reset successfully'
                }, status=status.HTTP_200_OK)
                
            except PasswordResetToken.DoesNotExist:
                return Response(
                    {'error': 'Invalid reset token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user


class AddressListCreateView(generics.ListCreateAPIView):
    """List and create addresses with pagination"""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer
    pagination_class = StandardPagination
    
    def get_queryset(self):
        # Prevent errors during schema generation with AnonymousUser
        if getattr(self, 'swagger_fake_view', False):
            return Address.objects.none()
        
        # Filter by user and order by default address first, then by creation date
        return Address.objects.filter(
            user=self.request.user
        ).order_by('-is_default', '-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete address"""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
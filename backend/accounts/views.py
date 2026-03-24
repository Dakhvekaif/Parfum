"""
Auth views: register, login (JWT), profile, change password, admin customer list.
"""

from django.contrib.auth import authenticate, get_user_model
from django.db.models import Count, Max, Sum
from rest_framework import filters, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from parfum.permissions import IsAdmin
from parfum.throttles import AuthRateThrottle

from .serializers import (
    ChangePasswordSerializer,
    CustomerSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ — Create a new account."""

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens immediately
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Account created successfully.",
                "user": UserSerializer(user).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """POST /api/auth/login/ — Authenticate and get JWT tokens."""

    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        if user is None:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"error": "Account is deactivated."},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Login successful.",
                "user": UserSerializer(user).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            }
        )


from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings

class GoogleLoginView(APIView):
    """POST /api/auth/google/ — Authenticate with Google ID token."""
    
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        from .serializers import GoogleLoginSerializer
        serializer = GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["id_token"]

        try:
            # Specify the CLIENT_ID of the app that accesses the backend if needed, 
            # but usually verifying without specifying client_id is okay for simple setups, 
            # though it's safer to provide it if available.
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request())
            
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            email = idinfo['email']
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')

        except ValueError:
            return Response(
                {"error": "Invalid Google token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Find or create user
        user = User.objects.filter(email=email).first()
        if not user:
            from django.utils.crypto import get_random_string
            user = User.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=get_random_string(32),
                auth_provider='google'
            )
        else:
            if not user.is_active:
                return Response(
                    {"error": "Account is deactivated."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if getattr(user, 'auth_provider', '') != 'google':
                user.auth_provider = 'google'
                user.save(update_fields=['auth_provider'])

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Google Login successful.",
                "user": UserSerializer(user).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """POST /api/auth/logout/ — Blacklist the refresh token."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logged out successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"error": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ProfileView(generics.RetrieveUpdateAPIView):
    """GET/PUT /api/auth/profile/ — View/update own profile."""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """POST /api/auth/change-password/ — Change password."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return Response({"message": "Password changed successfully."})


class AdminCustomerListView(generics.ListAPIView):
    """GET /api/admin/customers/ — List all customers with order stats."""

    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "email", "phone", "city"]
    ordering_fields = ["date_joined", "first_name", "orders_count", "total_spent"]
    ordering = ["-date_joined"]

    def get_queryset(self):
        return User.objects.filter(role="customer").annotate(
            orders_count=Count("orders"),
            total_spent=Sum("orders__total_amount"),
            last_order_date=Max("orders__created_at"),
        )


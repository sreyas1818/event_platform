from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    SignupSerializer,
    VerifyEmailSerializer,
    LoginSerializer
)
from .models import UserProfile, EmailOTP

from .utils import generate_otp
class SignupView(APIView):

    def post(self, request):

        serializer = SignupSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        role = serializer.validated_data['role']

        if User.objects.filter(email=email).exists():

            return Response(
                {
                    "detail": "Email already registered",
                    "code": "email_already_exists"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        UserProfile.objects.create(
            user=user,
            role=role
        )

        otp = generate_otp()


        EmailOTP.objects.create(
            email=email,
            otp=otp
        )

        send_mail(
            subject='Verify Email',
            message=f'Your OTP is {otp}',
            from_email='sreyas593@gmail.com',
            recipient_list=[email]
        )

        return Response(
            {
                "message":
                "Signup successful. OTP sent."
            },
            status=201
        )

class VerifyEmailView(APIView):

    def post(self, request):

        serializer = VerifyEmailSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        otp_record = EmailOTP.objects.filter(
            email=email
        ).first()

        if not otp_record:

            return Response(
                {
                    "detail": "OTP not found",
                    "code": "otp_not_found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if otp_record.attempts >= 5:

            return Response(
                {
                    "detail":
                    "Maximum OTP attempts exceeded",
                    "code":
                    "otp_locked"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if timezone.now() > (
            otp_record.created_at +
            timedelta(minutes=5)
        ):

            otp_record.delete()

            return Response(
                {
                    "detail": "OTP expired",
                    "code": "otp_expired"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp_record.otp != otp:

            otp_record.attempts += 1

            otp_record.save()

            return Response(
                {
                    "detail": "Invalid OTP",
                    "code": "invalid_otp",
                    "attempts_left":
                    5 - otp_record.attempts
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.get(
            email=email
        )

        profile = UserProfile.objects.get(
            user=user
        )

        profile.is_verified = True

        profile.save()

        otp_record.delete()

        return Response(
            {
                "message":
                "Email verified successfully"
            },
            status=status.HTTP_200_OK
        )
        
class LoginView(APIView):

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:

            user = User.objects.get(
                email=email
            )

        except User.DoesNotExist:

            return Response(
                {
                    "detail": "Invalid credentials",
                    "code": "invalid_credentials"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(password):

            return Response(
                {
                    "detail": "Invalid credentials",
                    "code": "invalid_credentials"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        profile = UserProfile.objects.get(
            user=user
        )

        if not profile.is_verified:

            return Response(
                {
                    "detail": "Verify email first",
                    "code": "email_not_verified"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        refresh = RefreshToken.for_user(
            user
        )

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }
        )

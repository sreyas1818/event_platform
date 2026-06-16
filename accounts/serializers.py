from rest_framework import serializers


class SignupSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField(
        min_length=8,
        write_only=True
    )

    role = serializers.ChoiceField(
        choices=[
            'SEEKER',
            'FACILITATOR'
        ]
    )

class VerifyEmailSerializer(serializers.Serializer):

    email = serializers.EmailField()

    otp = serializers.CharField(
        max_length=6
    )

class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True
    )
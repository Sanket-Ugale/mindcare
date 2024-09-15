from rest_framework import serializers
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from .models import *
User=get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields=['email','password']

    def create(self,validated_data):
        user=User.objects.create(email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class verifyOTPSerializer(serializers.Serializer):
    # class Meta:
    #     model = User
    #     fields=['email','otp']
    email=serializers.EmailField()
    otp=serializers.CharField()

class forgotPasswordSerializer(serializers.Serializer):
        email=serializers.EmailField()

class resetPasswordSerializer(serializers.Serializer):
        email=serializers.EmailField()
        otp=serializers.CharField()
        resetToken=serializers.CharField()
        password=serializers.CharField()
        confirmPassword=serializers.CharField()

        def validate(self, data):
            if data['password']!=data['confirmPassword']:
                raise serializers.ValidationError('Password and confirm password not matched')

            if not len(data['password'])>7:
                raise serializers.ValidationError('Password length should be greater than or equal to 8')
            return data
 
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields='__all__'

class MentorProfileSerializer(serializers.ModelSerializer): 
    class Meta:
        model = MentorProfile
        fields='__all__'
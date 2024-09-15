from django.shortcuts import render
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .serializers import *
import json
import random
import string
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.http.response import HttpResponse
from .models import *
from mindcare.celery import app
from .serializers import *
# from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .task import sendEmailTask, sendForgotEmailTask, sendScheduleEmailTask
from django_celery_beat.models import PeriodicTask,CrontabSchedule,IntervalSchedule
from datetime import datetime, timedelta
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from pathlib import Path
# import google.generativeai as genai
from django.db.models import Q

# Create your views here.
User=get_user_model()

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    def post(self, request):
        try:
            # Get the refresh token from the request data
            refresh_token = request.data.get("refresh")

            # Check if the refresh token is provided
            print(f"refresh_token {refresh_token}")
            if not refresh_token:
                return Response({"error": "Refresh token not provided."}, status=status.HTTP_300_MULTIPLE_CHOICES)

            # Blacklist the refresh token
            print(f" check blacklist {RefreshToken.check_blacklist}")
            token = RefreshToken(refresh_token)
            print(f" check blacklist {RefreshToken.check_blacklist}")
            print(f"TOKEN {token}")
            token.blacklist()


            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)

# Create your views here.
@api_view(['POST'])
def sign_in(request):
    try:
        data=request.data
        email=data.get('email')
        password=data.get('password')
        user = authenticate(username=email, password=password)
        if user:
            if user.verification_status=='pending':
                return Response({"message":"Account Not Verified"})
            if user.is_user==False:
                user.is_user=True
                user.save()
            # token, _ = Token.objects.get_or_create(user=user)
            refresh = RefreshToken.for_user(user)
            return Response({
            # "token":str(token_obj),
            # "payload":serializer.data,
                "user":str(user),
            "message":"Login Success",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            },
            status=status.HTTP_302_FOUND)
            # return Response({
            #     'token':str(token)
            # },status=status.HTTP_200_OK)
        else:
            return Response({
                'message':'Invalid Credentials'
                },
                status=status.HTTP_404_NOT_FOUND
                )
    except Exception as e:
        print(e)
        return Response({
            'message':'Something went wrong'
            },
            status=status.HTTP_400_BAD_REQUEST
            )

# Timer function to call invalidate password task after 5 min
def callInvalidateOTP(email):
    print("INVALIDATE OTP CALLED ✅ 🦋")
    randomNum=random.randint(0,99999999)
    hour=datetime.now().hour
    minutes=datetime.now().minute+10
    # what if someone using this function at **:59 minutes 
    if minutes>59:
        hour=hour+1
        minutes=minutes-59
        print("TIME: ")
        print(str(hour)+":"+str(minutes))
    schedule, created = CrontabSchedule.objects.get_or_create(
        hour=hour,
        minute=minutes,
        )
    task = PeriodicTask.objects.create(
        crontab=schedule,
        name='schedule_Invalidate_otp_task_'+str(randomNum),
        task='authenticate.task.invalidateOTP', 
        kwargs=json.dumps({"email":email,"name":'schedule_Invalidate_otp_task_'+str(randomNum)}),
        )#[email]['schedule_Invalidate_otp_task_'+str(randomNum)]
    return HttpResponse('timer start of 10min to invalidate otp')

class sign_up(APIView):
    def post(self, request):
        serializer=UserSerializer(data=request.data)
        if not serializer.is_valid():
            user=User.objects.get(email=serializer.data['email'])

            if user.otp_validity == False and user.verification_status == "pending":
                try:
                    if user.is_user==False:
                        user.is_user=True
                    email=user.email
                    sendEmailTask.delay(email)
                    user.otp_validity=True
                    refresh = RefreshToken.for_user(user)
                    custom_expiration_time = datetime.utcnow() + timedelta(days=7)
                    refresh.expires = custom_expiration_time
                    user.save()
                    callInvalidateOTP(email)                                      
                except:
                    return Response(
                        serializer.errors
                        # {
                        #     # "message":"Something went wrong in",
                        #     "error":serializer.errors
                        #     },
                            # status=status.HTTP_400_BAD_REQUEST
                            )
                return Response({
                    # "payload":serializer.data,
                    "message":"OTP send on "+serializer.data['email']+" Successfully.",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    },
                    status=status.HTTP_302_FOUND
                    )
                # print(email)
                # callInvalidateOTP(email)
            return Response({
                    "error":serializer.errors
                    },
                    status=status.HTTP_403_FORBIDDEN
                    )
        # "message":"Some thing went wrong",
        try:
            email=serializer.validated_data['email']
            print(email)
            # send_otp_via_email(serializer.data['email'])
            print("✅✅✅✅")
            # app.send_task('authentication.task.sendEmailTask', args=[email], kwargs={})
            # authentication.task.sendEmailTask.delay(email)
            sendEmailTask.delay(email)
            # print(result.get())
        except Exception as e:
            return Response(
                {
                    "message":"Something went wrong",
                    "error":str(e)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                    )
        serializer.save()
        user=User.objects.get(email=serializer.data['email'])
        user.otp_validity=True
        user.is_user =True
        # token_obj, _=Token.objects.get_or_create(user=user)
        refresh = RefreshToken.for_user(user)
        custom_expiration_time = datetime.utcnow() + timedelta(days=7)
        refresh.expires = custom_expiration_time
        user.save()
        callInvalidateOTP(email)
        
        return Response({
            # "token":str(token_obj),
            # "payload":serializer.data,
            "message":"OTP send on "+serializer.data['email']+" Successfully.",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            },
            status=status.HTTP_302_FOUND)

class forgot_password(APIView):
    def post(self, request):
        serializer=forgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "message":"Invalid Input",
                "error":serializer.errors
                },
                status=status.HTTP_403_FORBIDDEN
                )
        email=serializer.data['email']
        user=User.objects.filter(email=email)
        if not user.exists():
            return Response({
                "message":"User not found"
                },
                status=status.HTTP_404_NOT_FOUND
                )
        try:    
            # send_otp_via_email(serializer.data['email'])
            sendForgotEmailTask.delay(email)
        except:
            return Response({
                "message":"Something went wrong",
                "error":serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
                )
        # serializer.save()
        resetToken=''.join(random.choices(string.ascii_lowercase +
                             string.digits, k=50))
        user=user.first()
        user.verification_status = "reset"
        user.otp_validity=True
        user.resetToken=str(resetToken)
        print(str(resetToken))
        user.save()
        user=User.objects.get(email=serializer.data['email'])
        email=user.email

        callInvalidateOTP(email)
        # token_obj, _=Token.objects.get_or_create(user=user)
        # refresh = RefreshToken.for_user(user)
        
        return Response({
            # "token":str(token_obj),
            # "payload":serializer.data,
            "message":"OTP send on "+serializer.data['email']+" Successfully.",
            "resetToken":str(resetToken)
            # "refresh": str(refresh),
            # "access": str(refresh.access_token),
            },
            status=status.HTTP_302_FOUND)   

class reset_password(APIView):
    def post(self,request):
        serializer=resetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "message":"Invalid Input",
                "error":serializer.errors
                },
                status=status.HTTP_403_FORBIDDEN
                )
        email=serializer.data['email']
        resetToken=serializer.data['resetToken']
        user=User.objects.filter(email=email)

        if not user.exists():
            return Response({
                "message":"User not found",
            },status=status.HTTP_404_NOT_FOUND
            )
        
        user=user.first() 

        if not user.resetToken==resetToken:
            return Response({
                "message":"Invalid Rest Token",
            },status=status.HTTP_404_NOT_FOUND
            )
        
        if serializer.data['otp']!=user.otp:
            return Response({
                "message":"Invalid OTP",
            },
            )
        if user.email==email and user.resetToken==resetToken and user.verification_status=='reset':
            user.resetToken='none'
            user.otp_validity=False
            user.verification_status='verified'
            user.set_password(serializer.data['password'])
            user.save()
            return Response({
                    "message":"Password changed Successfully"
                    },
                    status=status.HTTP_202_ACCEPTED
                    )
        
class verify_OTP(APIView):
    def post(self,request):
        print("IN verifyOTP field 🔢")
        try:
            data=request.data
            serializer=verifyOTPSerializer(data=data)
            if serializer.is_valid():
            # if True:
                email=serializer.data['email']
                otp=serializer.data['otp']
                user=User.objects.filter(email=email)
                if not user.exists():
                    return Response({
                        "message":"User not found"
                        },
                        status=status.HTTP_404_NOT_FOUND
                        )
                if user[0].otp != otp:
                    return Response({
                        "message":"Invalid OTP"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                        )
                if user.first().verification_status == "verified":
                    return Response({
                        "message":"Account already verified"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                        )
                user=user.first()
                user.otp_validity=False
                user.verification_status = "verified"
                user.save()
                return Response({
                    "message":"Account verified Successfully"
                    },
                    status=status.HTTP_200_OK
                    )
        except Exception as e:
            return Response({
                "ERROR":str(e)
                },
                status=status.HTTP_200_OK
                )    
        
# Create your views here.
@api_view(['POST'])
def mentor_sign_in(request):
    try:
        data=request.data
        email=data.get('email')
        password=data.get('password')
        user = authenticate(username=email, password=password)
        if user:
            if user.verification_status=='pending':
                return Response({"message":"Account Not Verified"})
            if user.is_doctor==False:
                user.is_doctor=True
                user.save()
            # token, _ = Token.objects.get_or_create(user=user)
            refresh = RefreshToken.for_user(user)
            return Response({
            # "token":str(token_obj),
            # "payload":serializer.data,
                "user":str(user),
            "message":"Login Success",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            },
            status=status.HTTP_302_FOUND)
            # return Response({
            #     'token':str(token)
            # },status=status.HTTP_200_OK)
        else:
            return Response({
                'message':'Invalid Credentials'
                },
                status=status.HTTP_404_NOT_FOUND
                )
    except Exception as e:
        print(e)
        return Response({
            'message':'Something went wrong'
            },
            status=status.HTTP_400_BAD_REQUEST
            )



class mentor_sign_up(APIView):
    def post(self, request):
        serializer=UserSerializer(data=request.data)
        if not serializer.is_valid():
            user=User.objects.get(email=serializer.data['email'])

            if user.otp_validity == False and user.verification_status == "pending":
                try:
                    if user.is_doctor==False:
                        user.is_doctor=True
                    email=user.email
                    sendEmailTask.delay(email)
                    user.otp_validity=True
                    refresh = RefreshToken.for_user(user)
                    custom_expiration_time = datetime.utcnow() + timedelta(days=7)
                    refresh.expires = custom_expiration_time
                    user.save()
                    callInvalidateOTP(email)                                      
                except:
                    return Response(
                        serializer.errors
                        # {
                        #     # "message":"Something went wrong in",
                        #     "error":serializer.errors
                        #     },
                            # status=status.HTTP_400_BAD_REQUEST
                            )
                return Response({
                    # "payload":serializer.data,
                    "message":"OTP send on "+serializer.data['email']+" Successfully.",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    },
                    status=status.HTTP_302_FOUND
                    )
                # print(email)
                # callInvalidateOTP(email)
            return Response({
                    "error":serializer.errors
                    },
                    status=status.HTTP_403_FORBIDDEN
                    )
        # "message":"Some thing went wrong",
        try:
            email=serializer.validated_data['email']
            print(email)
            # send_otp_via_email(serializer.data['email'])
            print("✅✅✅✅")
            # app.send_task('authentication.task.sendEmailTask', args=[email], kwargs={})
            # authentication.task.sendEmailTask.delay(email)
            sendEmailTask.delay(email)
            # print(result.get())
        except Exception as e:
            return Response(
                {
                    "message":"Something went wrong",
                    "error":str(e)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                    )
        serializer.save()
        user=User.objects.get(email=serializer.data['email'])
        user.otp_validity=True
        user.is_doctor =True
        # token_obj, _=Token.objects.get_or_create(user=user)
        refresh = RefreshToken.for_user(user)
        custom_expiration_time = datetime.utcnow() + timedelta(days=7)
        refresh.expires = custom_expiration_time
        user.save()
        callInvalidateOTP(email)
        
        return Response({
            # "token":str(token_obj),
            # "payload":serializer.data,
            "message":"OTP send on "+serializer.data['email']+" Successfully.",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            },
            status=status.HTTP_302_FOUND)

class UserProfileAPIView(APIView):
    # authentication_classes=[JWTAuthentication]
    # permission_classes=[IsAuthenticated]
    def get(self, request):
        user_profile_id = request.data.get('user_profile_id')
        if user_profile_id is 0:
            return Response({"detail": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)
        try: 
            if user_profile_id:
                user_profile = UserProfile.objects.filter(user_profile_id=user_profile_id).first()
                if user_profile:
                    serializer = UserProfileSerializer(user_profile)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({"detail": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                mentor_profiles = UserProfile.objects.all()
                serializer = UserProfileSerializer(mentor_profiles, many=True)
                return Response({"payload":serializer.data})
        except Exception as e:
            print(f"ERROR: {e}")
            return Response({"detail": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            existing_profile = UserProfile.objects.filter(user_id=user_id).first()

            if existing_profile:
                # Update existing profile
                serializer = UserProfileSerializer(existing_profile, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            else:
                # Create new profile
                serializer.save()

            return Response({"message":"Profile Updated Successfully", "payload":serializer.data}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MentorProfileAPIView(APIView):
    # authentication_classes=[JWTAuthentication]
    # permission_classes=[IsAuthenticated]
    def get(self, request):
        mentor_profile_id = request.data.get('mentor_profile_id')
        if mentor_profile_id is 0:
            return Response({"detail": "Mentor profile not found"}, status=status.HTTP_404_NOT_FOUND)
        try: 
            if mentor_profile_id:
                mentor_profile = MentorProfile.objects.filter(mentor_profile_id=mentor_profile_id).first()
                if mentor_profile:
                    serializer = MentorProfileSerializer(mentor_profile)
                    return Response({"payload":serializer.data})
                else:
                    return Response({"detail": "Mentor profile not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                mentor_profiles = MentorProfile.objects.all()
                serializer = MentorProfileSerializer(mentor_profiles, many=True)
                return Response({"payload":serializer.data})
        except Exception as e:
            return Response({"detail": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = MentorProfileSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            existing_profile = MentorProfile.objects.filter(user_id=user_id).first()

            if existing_profile:
                # Update existing profile
                serializer = MentorProfileSerializer(existing_profile, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            else:
                # Create new profile
                serializer.save()

            return Response({"message":"Profile Updated Successfully", "payload":serializer.data}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
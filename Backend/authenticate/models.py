from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from .manager import UserManager

# Create your models here.
class User(AbstractUser):
    username=None
    email=models.EmailField(unique=True)
    verification_status=models.CharField(max_length=20,default='pending')
    # verification_slug=models.CharField(max_length=100,null=True)
    otp =models.CharField(max_length=6, null=True)
    otp_validity =models.BooleanField(default=False)
    is_user=models.BooleanField(default=True)
    is_doctor=models.BooleanField(default=False)
    resetToken=models.CharField(max_length=50,default="none")

    USERNAME_FIELD= 'email'
    REQUIRED_FIELDS=[]
    objects=UserManager()


class UserProfile(models.Model):
    user_profile_id=models.AutoField(primary_key=True)
    user_id=models.ForeignKey(User,on_delete=models.CASCADE)
    image=models.ImageField(upload_to='profile_pics',default='default.jpg')
    birthDate=models.DateField(default=timezone.now)
    gender=models.CharField(max_length=10,null=True)
    phone_number= models.CharField(max_length=10,null=True)
    name=models.CharField(max_length=30)
    age=models.IntegerField(default=18)
    height=models.IntegerField(default=150)
    weight=models.IntegerField(default=50)
    # health_report=models.FileField(upload_to='health_reports',default='default.jpg')

class MentorProfile(models.Model):
    mentor_profile_id=models.AutoField(primary_key=True)
    # image, name, age, height, weight, mentor queue size, rating, experience, specialization, serviceStatus=ready to accept appointments, not accepting appointments, verified by MindCare
    user_id=models.ForeignKey(User,on_delete=models.CASCADE)
    image=models.ImageField(upload_to='profile_pics',default='default.jpg')
    name=models.CharField(max_length=30)
    age=models.IntegerField(default=18)
    birthDate=models.DateField(default=timezone.now)
    gender=models.CharField(max_length=10,null=True)
    phone_number= models.CharField(max_length=10,null=True)
    about=models.TextField(null=True, blank=True)
    location=models.CharField(max_length=100,null=True, blank=True)
    availibility=models.CharField(max_length=100, null=True, blank=True, default='Monday - Friday 10:00 AM - 6:00 PM')
    # height=models.IntegerField(default=150)
    # weight=models.IntegerField(default=50)
    # health_report=models.FileField(upload_to='health_reports',default='default.jpg')
    rating=models.IntegerField(default=0)
    experience=models.IntegerField(default=0)
    specialization=models.CharField(max_length=30)
    serviceStatus=models.BooleanField(default=False)
    mentor_queue_size=models.IntegerField(default=0)
    verified=models.BooleanField(default=False)

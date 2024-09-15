from datetime import timezone
from django.db import models
from authenticate.models import *

class Appointment(models.Model):
    appointmentStatus=(
        ('pending','pending'),
        ('accepted','accepted'),
        ('rejected','rejected'),
    )
    user_profile_id=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    mentor_profile_id=models.ForeignKey(MentorProfile,on_delete=models.CASCADE)
    schedule_date=models.DateTimeField(default=timezone.now)
    appointment_token=models.TextField(null=True, blank=True)
    # schedule_time=models.TimeField(default=timezone.now)
    # schedule_day=models.CharField(max_length=10)
    status=models.CharField(max_length=10,choices=appointmentStatus,default='pending')
    scheduled_on=models.DateTimeField(default=timezone.now)

class Sprint(models.Model):
    status_choices=(
        ('pending','pending'),
        ('completed','completed'),
    )
    sprint_id=models.AutoField(primary_key=True)
    user_profile_id=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    sprint_no=models.IntegerField(default=0)
    start_date=models.DateTimeField(default=timezone.now)
    end_date=models.DateTimeField(default=timezone.now)
    Scenario_analysis=models.IntegerField(default=0)
    Quiz_analysis=models.IntegerField(default=0)
    Wearable_analysis=models.IntegerField(default=0)
    Facesoul_analysis=models.IntegerField(default=0)
    Chat_analysis=models.IntegerField(default=0)
    status=models.CharField(max_length=10,choices=status_choices,default='pending')


class Chat(models.Model):
    user_profile_id=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    message=models.TextField()
    response=models.TextField(null=True)
    # time=models.TimeField(default=timezone.time)
    date=models.DateTimeField(auto_now_add=True)

class QuizQuestion(models.Model):
    # user_profile_id=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    question=models.TextField()
    # scale=models.IntegerField(default=0)
    # result=models.IntegerField(default=0)
    # timestamp=models.DateTimeField(auto_now_add=True)

class QuizResult(models.Model):
    user_profile_id=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    question_id=models.ForeignKey(QuizQuestion,on_delete=models.CASCADE)
    answer=models.TextField()
    timestamp=models.DateTimeField(auto_now_add=True)

class Wearable(models.Model):
    user_profile_id=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    heart_rate=models.IntegerField(default=0)
    steps=models.IntegerField(default=0)
    blood_pressure=models.IntegerField(default=0)
    sleep=models.IntegerField(default=0)
    activity=models.IntegerField(default=0)
    timestamp=models.DateTimeField(auto_now_add=True)

class ScenarioQuestion(models.Model):
    user_profile_id=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    scenario1_image=models.ImageField(upload_to='media/scenario/', default='media/scenario/default.jpg')
    scenario1_label=models.CharField(max_length=100,null=True)
    scenario1_description=models.TextField(null=True)
    scenario2_image=models.ImageField(upload_to='media/scenario/', default='media/scenario/default.jpg')
    scenario2_label=models.CharField(max_length=100,null=True)
    scenario2_description=models.TextField(null=True)

class ScenarioResult(models.Model):
    user_profile_id=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    ScenarioQuestion_id=models.ForeignKey(ScenarioQuestion,on_delete=models.CASCADE)
    result=models.IntegerField(default=0)
    timestamp=models.DateTimeField(auto_now_add=True)

class Facesoul(models.Model):
    user_profile_id=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    image=models.ImageField(upload_to='media/facesoul/')
    analysis=models.CharField(max_length=1000)
    timestamp=models.DateTimeField(auto_now_add=True)

class Task(models.Model):
    user_profile_id=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    title=models.CharField(max_length=100)
    description=models.TextField()
    link=models.URLField(max_length=200)
    timestamp=models.DateTimeField(auto_now_add=True)

class Analysis(models.Model):
    user_profile_id=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    report=models.TextField()
    score=models.IntegerField(default=0)
    conclusion=models.CharField(max_length=1000)

class Notification(models.Model):
    user_profile_id=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    title=models.CharField(max_length=100)
    description=models.CharField(max_length=1000)
    link=models.CharField(max_length=1000)
    status=models.CharField(max_length=10,default='pending')
    send=models.CharField(max_length=10,default='pending')

class ContactUs(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField(max_length=100)
    message=models.CharField(max_length=1000)
    phone=models.IntegerField()
    date=models.DateField(default=timezone.now)
    time=models.TimeField(default=timezone.now)

class Feedback(models.Model):
    user_profile_id=models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    feedback=models.CharField(max_length=1000)
    rating=models.IntegerField(default=0)
    date=models.DateField(default=timezone.now)
    time=models.TimeField(default=timezone.now)

class FAQ(models.Model):
    question=models.CharField(max_length=1000)
    answer=models.CharField(max_length=1000)

class Articles(models.Model):
    title=models.CharField(max_length=100)
    description=models.TextField()
    image=models.ImageField(upload_to='media/articles/')
    timestamp=models.DateTimeField(auto_now_add=True)

class Music(models.Model):
    title=models.CharField(max_length=100)
    description=models.TextField(null = True)
    link=models.URLField(max_length=200, null = True, blank=True)
    audio_image=models.ImageField(upload_to='media/music/')
    audio_file=models.FileField(upload_to='media/music/')
    timestamp=models.DateTimeField(auto_now_add=True)

class Storie(models.Model):
    title=models.CharField(max_length=100)
    description=models.TextField(null = True)
    link=models.URLField(max_length=200, null = True, blank=True)
    image=models.ImageField(upload_to='media/stories/')
    timestamp=models.DateTimeField(auto_now_add=True)

class Quote(models.Model):
    quote=models.TextField()
    author=models.CharField(max_length=100)
    timestamp=models.DateTimeField(auto_now_add=True)
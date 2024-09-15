from rest_framework import serializers
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from .models import *
User=get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields='__all__'

class MentorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorProfile
        fields='__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields='__all__'


class ChatSerializer(serializers.ModelSerializer):  
    class Meta:
        model = Chat
        fields='__all__'

class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields='__all__'

class QuizResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizResult
        fields='__all__'

class WearableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wearable
        fields='__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields='__all__'

class ScenarioResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScenarioResult
        fields='__all__'

class ScenarioQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScenarioQuestion
        fields='__all__'

class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields='__all__'

class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields='__all__'

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields='__all__'

class FacesoulSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facesoul
        fields='__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields='__all__'

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields='__all__'

class ArticlesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articles
        fields='__all__'

class StorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storie
        fields='__all__'

class MusicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Music
        fields='__all__'

class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields='__all__'


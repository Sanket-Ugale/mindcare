from . import views
from django.urls import path

urlpatterns = [
    path('api/appointments/<appointmentId>', views.AppointmentAPIView.as_view()),
    path('api/weareables/', views.WearableAPIView.as_view()),
    path('api/notifications/', views.NotificationAPIView.as_view()),
    path('api/scenarioresult/', views.ScenarioResultAPIView.as_view()),
    path('api/scenarioquestion/', views.ScenarioQuestionAPIView.as_view()),
    path('api/chats/', views.ChatAPIView.as_view()),
    path('api/quizquestion/', views.QuizQuestionAPIView.as_view()),
    path('api/quizresult/', views.QuizResultAPIView.as_view()),
    path('api/analysis/', views.AnalysisAPIView.as_view()),
    path('api/tasks/', views.TaskAPIView.as_view()),
    path('api/contactus/', views.ContactUsAPIView.as_view()),
    # path('api/sprints/', views.SprintAPIView.as_view()),
    path('chatAnalysis/', views.ChatAnalysis.as_view()), 
    path('', views.index),
    path('genai_chat_api/', views.genai_chat_api),
    path('getAppointmentToken/', views.AppointmentTokenAPIView.as_view()),
    # path('getQuizResult/', views.GetQuizResultAPIView.as_view()),
    path('api/quotes/', views.QuoteAPIView.as_view()),
    path('api/music/', views.MusicAPIView.as_view()),
    path('api/storie/', views.StorieAPIView.as_view()),
    path('api/articles/', views.ArticlesAPIView.as_view()),
    path('api/feedback/', views.FeedbackAPIView.as_view()),
    path('api/faq/', views.FAQAPIView.as_view()),

]

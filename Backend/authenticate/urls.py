from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('user/signIn/', views.sign_in),
    path('user/signUp/', views.sign_up.as_view()),
    path('user/signOut/', views.LogoutView.as_view()),
    path('mentor/signIn/', views.mentor_sign_in),
    path('mentor/signUp/', views.mentor_sign_up.as_view()),
    # path('mentor/signOut/', views.m),
    path('forgotPassword/', views.forgot_password.as_view()),
    path('resetPassword/', views.reset_password.as_view()),
    path('verifyOTP/', views.verify_OTP.as_view()),
    path('user/profile/', views.UserProfileAPIView.as_view()),
    path('mentor/profile/', views.MentorProfileAPIView.as_view()),
]
if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)


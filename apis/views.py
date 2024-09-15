import random
import string
import time
import os
import uuid
from django.http import JsonResponse
from django.shortcuts import render
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from asgiref.sync import async_to_sync, sync_to_async
# Create your views here.
import google.generativeai as genai
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from textblob import TextBlob
# from django.http import HttpRequest
from agora_token_builder import RtcTokenBuilder
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API'))
model = genai.GenerativeModel('gemini-pro')
    
class AppointmentTokenAPIView(APIView):
    def post(self, request):
        appId =os.getenv('AGORA_APPID')
        appCertificate = os.getenv('APP_CERTIFICATE')
        
        channelName = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(50))
        if not channelName:
            return Response({'error': 'Missing channel parameter'}, status=status.HTTP_400_BAD_REQUEST)

        uid = random.randint(1, 230)
        expirationTimeInSeconds = 3600
        currentTimeStamp = int(time.time())
        privilegeExpiredTs = currentTimeStamp + expirationTimeInSeconds
        role = 1

        token = RtcTokenBuilder.buildTokenWithUid(appId, appCertificate, channelName, uid, role, privilegeExpiredTs)

        return Response({'token': token, 'uid': uid, 'channel': channelName})

class ChatAnalysis(APIView):
    def get(self, request):
        url = 'https://127.0.0.1:8000/api/chats/'

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return Response({'error': f"Error: Unable to fetch data. {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = response.json()
        combined_text = ' '.join([entry['message'] + ' ' + entry['response'] for entry in data])
        blob = TextBlob(combined_text)

        return Response({
                'sentiment_polarity': blob.sentiment.polarity,
                'sentiment_subjectivity': blob.sentiment.subjectivity
            }, status=status.HTTP_200_OK)
    
def genai_chat_api(request):
    try:
        message = request.data.get('message')  # Assuming 'message' is the key for your data
        chat = model.start_chat()
        response = chat.send_message(f"if the below question is related to mental health or emotional or related to humans and feelings then only return the response and if question is negative emotions and feelings try to give postive and motivational response, also provide response if question is funny and introductory like hii hello, for any other question return 'I can't help you in that case, I am hear to assest you with mental health' only this sentence. show that you are only trained for mental health for below question please follow the above instructions to respond to the below question question: {message}")
        return Response({"response": response.text})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@csrf_exempt
async def genai_chat(message):
    try:
      # Assuming 'message' is the key for your data
        chat = model.start_chat()
        response = await chat.send_message(f"if the below question is related to mental health or emotional or related to humans and feelings then only return the response and if question is negative emotions and feelings try to give postive and motivational response, for any other question return 'I can't help you in that case' only this sentence. show that you are only trained for mental health for below question please follow the above instructions to respond to the below question question: {message}")
        return response.text
    except Exception as e:
        pass
        # return str(e)
def index(request):
    return render(request,'home.html')

class AppointmentAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self, request, appointmentId):
        try:
            appointment = Appointment.objects.filter(id=appointmentId)
            serializer = AppointmentSerializer(appointment, many=True)
            if serializer.data is None or serializer.data == []:
                return Response({"message":"No appointment found"})
            return Response({"payload":serializer.data})
        except Exception as e:
            return Response({"message":str(e)})

    def post(self, request, appointmentId):
        print(appointmentId)
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        pk=request.data['pk']
        appointment = Appointment.objects.get(pk=pk)
        serializer = AppointmentSerializer(appointment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        pk=request.data['pk']
        appointment = Appointment.objects.get(pk=pk)
        serializer = AppointmentSerializer(appointment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        pk=request.data['pk']
        appointment = Appointment.objects.get(pk=pk)
        appointment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ChatAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self, request):
        chat = Chat.objects.all()
        serializer = ChatSerializer(chat, many=True)
        return Response(serializer.data)
    def post(self, request):
        message = request.data.get('message')  # Assuming 'message' is the key for your data
        chat = model.start_chat()
        response = chat.send_message(f"""if the below question is related to mental health or emotional or related to humans or for entertainment or if user asking for jokes tell him positive jokes or normal talk like best friend and feelings then only return the response 
                                     and if question is negative emotions and feelings try to give postive and motivational response, 
                                     also provide response if question introductory like hii, hello, 
                                     for any other question return 'I am hear to assest you with mental health' this sentence. 
                                     show that you are only trained for mental health for below question please follow the above instructions to respond to the below question 
                                     question: {message}""")
        request.data['response'] = response.text
        serializer = ChatSerializer(data=request.data)
        # message = request.data['message']
        print(response.text)
        if serializer.is_valid():
            serializer.response = response.text
            # serializer.message=request.data['message']
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        pk=request.data['pk']
        chat = Chat.objects.get(pk=pk)
        serializer = ChatSerializer(chat, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        pk=request.data['pk']
        chat = Chat.objects.get(pk=pk)
        serializer = ChatSerializer(chat, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        pk=request.data['pk']
        chat = Chat.objects.get(pk=pk)
        chat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class QuizQuestionAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self, request):
        quiz = QuizQuestion.objects.all()
        serializer = QuizQuestionSerializer(quiz, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = QuizQuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        print(request.data)
        # Extract the array of quiz data from the request
        quiz_data = request.data

        # Initialize an empty dictionary to store the updated quiz objects
        updated_quizzes = {}

        # Iterate over each quiz data object in the array
        for quiz in quiz_data:
            pk = quiz['question_id']
            quiz_obj = QuizQuestion.objects.get(pk=pk)
            serializer = QuizQuestionSerializer(quiz_obj, data=quiz)
            if serializer.is_valid():
                # Save the updated quiz object and add it to the dictionary
                serializer.save()
                updated_quizzes[pk] = serializer.data
            else:
                # If the serializer is not valid, add an error message to the dictionary
                updated_quizzes[pk] = {'error': serializer.errors}

        # Return the dictionary of updated quiz objects
        if updated_quizzes:
            return Response(updated_quizzes)
        else:
            # If no quiz objects were updated, return a 400 Bad Request response
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        pk=request.data['pk']
        quiz = QuizQuestion.objects.get(pk=pk)
        serializer = QuizQuestionSerializer(quiz, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        pk=request.data['pk']
        quiz = QuizQuestion.objects.get(pk=pk)
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class QuizResultAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self, request):
        quiz = QuizResult.objects.all()
        serializer = QuizResultSerializer(quiz, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data
        if isinstance(data, list):  # check if data is a list of dictionaries
            responses = []
            for item in data:
                serializer = QuizResultSerializer(data=item)
                if serializer.is_valid():
                    serializer.save()
                    responses.append(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(responses, status=status.HTTP_201_CREATED)
        else:
            serializer = QuizResultSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        pk=request.data['pk']
        quiz = QuizResult.objects.get(pk=pk)
        serializer = QuizResultSerializer(quiz, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        pk=request.data['pk']
        quiz = QuizResult.objects.get(pk=pk)
        serializer = QuizResultSerializer(quiz, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        pk=request.data['pk']
        quiz = QuizResult.objects.get(pk=pk)
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class WearableAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self, request):
        wearable = Wearable.objects.all()
        serializer = WearableSerializer(wearable, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WearableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        pk=request.data['pk']
        wearable = Wearable.objects.get(pk=pk)
        serializer = WearableSerializer(wearable, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        pk=request.data['pk']
        wearable = Wearable.objects.get(pk=pk)
        serializer = WearableSerializer(wearable, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        pk=request.data['pk']
        wearable = Wearable.objects.get(pk=pk)
        wearable.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ScenarioResultAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self, request):
        scenario = ScenarioResult.objects.all()
        serializer = ScenarioResultSerializer(scenario, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ScenarioResultSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def put(self, request):
    #     pk=request.data['pk']
    #     scenario = ScenarioResult.objects.get(pk=pk)
    #     serializer = ScenarioResultSerializer(scenario, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def patch(self, request):
    #     pk=request.data['pk']
    #     scenario = ScenarioResult.objects.get(pk=pk)
    #     serializer = ScenarioResultSerializer(scenario, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request):
    #     pk=request.data['pk']
    #     scenario = ScenarioResult.objects.get(pk=pk)
    #     scenario.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    
class ScenarioQuestionAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self, request):
        scenario = ScenarioQuestion.objects.all()
        serializer = ScenarioQuestionSerializer(scenario, many=True)
        return Response(serializer.data)

    # def post(self, request):
    #     serializer = ScenarioQuestionSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def put(self, request):
    #     pk=request.data['pk']
    #     scenario = ScenarioQuestion.objects.get(pk=pk)
    #     serializer = ScenarioQuestionSerializer(scenario, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def patch(self, request):
    #     pk=request.data['pk']
    #     scenario = ScenarioQuestion.objects.get(pk=pk)
    #     serializer = ScenarioQuestionSerializer(scenario, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request):
    #     pk=request.data['pk']
    #     scenario = ScenarioQuestion.objects.get(pk=pk)
    #     scenario.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    
class FacesoulAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self, request):
        facesoul = Facesoul.objects.all()
        serializer = FacesoulSerializer(facesoul, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FacesoulSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def put(self, request):
    #     pk=request.data['pk']
    #     facesoul = Facesoul.objects.get(pk=pk)
    #     serializer = FacesoulSerializer(facesoul, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def patch(self, request):
    #     pk=request.data['pk']
    #     facesoul = Facesoul.objects.get(pk=pk)
    #     serializer = FacesoulSerializer(facesoul, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request):
    #     pk=request.data['pk']
    #     facesoul = Facesoul.objects.get(pk=pk)
    #     facesoul.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)

class TaskAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self, request):
        task = Task.objects.all()
        serializer = TaskSerializer(task, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        pk=request.data['pk']
        task = Task.objects.get(pk=pk)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        pk=request.data['pk']
        task = Task.objects.get(pk=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        pk=request.data['pk']
        task = Task.objects.get(pk=pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AnalysisAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self, request):
        analysis = Analysis.objects.all()
        serializer = AnalysisSerializer(analysis, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AnalysisSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        pk=request.data['pk']
        analysis = Analysis.objects.get(pk=pk)
        serializer = AnalysisSerializer(analysis, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        pk=request.data['pk']
        analysis = Analysis.objects.get(pk=pk)
        serializer = AnalysisSerializer(analysis, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        pk=request.data['pk']
        analysis = Analysis.objects.get(pk=pk)
        analysis.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class NotificationAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self, request):
        notification = Notification.objects.all()
        serializer = NotificationSerializer(notification, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        pk=request.data['pk']
        notification = Notification.objects.get(pk=pk)
        serializer = NotificationSerializer(notification, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        pk=request.data['pk']
        notification = Notification.objects.get(pk=pk)
        serializer = NotificationSerializer(notification, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        pk=request.data['pk']
        notification = Notification.objects.get(pk=pk)
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ContactUsAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self, request):
        contactus = ContactUs.objects.all()
        serializer = ContactUsSerializer(contactus, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ContactUsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        pk=request.data['pk']
        contactus = ContactUs.objects.get(pk=pk)
        serializer = ContactUsSerializer(contactus, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        pk=request.data['pk']
        contactus = ContactUs.objects.get(pk=pk)
        serializer = ContactUsSerializer(contactus, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        pk=request.data['pk']
        contactus = ContactUs.objects.get(pk=pk)
        contactus.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)    
    
class FeedbackAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    # def get(self, request):
    #     feedback = Feedback.objects.all()
    #     serializer = FeedbackSerializer(feedback, many=True)
    #     return Response(serializer.data)

    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def put(self, request):
    #     pk=request.data['pk']
    #     feedback = Feedback.objects.get(pk=pk)
    #     serializer = FeedbackSerializer(feedback, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def patch(self, request):
    #     pk=request.data['pk']
    #     feedback = Feedback.objects.get(pk=pk)
    #     serializer = FeedbackSerializer(feedback, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request):
    #     pk=request.data['pk']
    #     feedback = Feedback.objects.get(pk=pk)
    #     feedback.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


class FAQAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self, request):
        faq = FAQ.objects.all()
        serializer = FAQSerializer(faq, many=True)
        return Response(serializer.data)

    # def post(self, request):
    #     serializer = FAQSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def put(self, request):
    #     pk=request.data['pk']
    #     faq = FAQ.objects.get(pk=pk)
    #     serializer = FAQSerializer(faq, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def patch(self, request):
    #     pk=request.data['pk']
    #     faq = FAQ.objects.get(pk=pk)
    #     serializer = FAQSerializer(faq, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request):
    #     pk=request.data['pk']
    #     faq = FAQ.objects.get(pk=pk)
    #     faq.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)

class QuoteAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self, request):
        quote = Quote.objects.all()
        serializer = QuoteSerializer(quote, many=True)
        return Response(serializer.data)

    
class MusicAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self, request):
        music = Music.objects.all()
        serializer = MusicSerializer(music, many=True)
        return Response(serializer.data)
    
class StorieAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self, request):
        storie = Storie.objects.all()
        serializer = StorieSerializer(storie, many=True)
        return Response(serializer.data)
    
class ArticlesAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self, request):
        articles = Articles.objects.all()
        serializer = ArticlesSerializer(articles, many=True)
        return Response(serializer.data)
    

    
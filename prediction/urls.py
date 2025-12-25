from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('predict/', views.predict, name='predict'),
    path('chat/', views.chat, name='chat'),
    path('chat/api/', views.chat_api, name='chat_api'),
]

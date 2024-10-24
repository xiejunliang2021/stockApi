from django.contrib import admin
from django.urls import path
from .views import LoginView, RegistrView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('register/', RegistrView.as_view()),

]

from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings

from . import views

app_name= 'users'

urlpatterns = [
    path('', LoginView.as_view(template_name="users/login.html"),name="login"),
    path('logout/', views.logoutUser,name="logout"),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
]



from django.urls import path 
from . import views

app_name = 'posts'

urlpatterns = [
    path('create/<int:pk>/', views.create_post, name='create_post'),
    path('', views.student_report_list, name='student_report_list'),
    path('reports/<int:report_id>/pdf/', views.generate_student_report_pdf, name='generate_student_report_pdf'),
    
]
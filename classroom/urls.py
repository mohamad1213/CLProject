from django.urls import path 
from . import views

app_name = 'classroom'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('api/gender-data/', views.get_gender_data, name='get_gender_data'),
    path('api/discussion-activity/', views.get_discussion_activity, name='get_discussion_activity'),
    path('api/monthly-discussion-activity/', views.get_monthly_discussion_activity, name='monthly_discussion_activity'),
    path('classroom/', views.home, name='home'),
    path('tentang/', views.tentang, name='tentang'),
    path('classroom/view/<int:document_id>/', views.view_document, name='view_document'),
    path('create/', views.create_classroom, name = 'create_classroom'),
    path('join/', views.join_classroom, name = 'join_classroom'),
    path('open/<int:pk>/', views.open_classroom, name = 'open_classroom'),
    path('classroom/<int:pk>/update/', views.update_classroom, name='update_classroom'),
    path('<int:pk>', views.delete_classroom, name = 'delete_classroom'),
    path('<int:pk>/members', views.members, name = 'members_classroom'),
    path('assignment/<int:pk>/student_work', views.student_work, name = 'student_work'),
    path('assignment/', views.assignment, name = 'assignment'),
    path('assignment/create', views.assignment_create, name = 'assignment_create'),
    path('assignment/<int:pk>/update/', views.assignment_update, name='assignment_update'),
    path('assignment/<int:pk>', views.assignment_submit, name = 'assignment_submit'),
    path('assignment/<int:pk>/turnin/', views.turnin, name = 'turnin'),
    path('assignment/<int:pk>/unsubmit/', views.unsubmit, name = 'unsubmit'),
    path('assignment/<int:pk>/unsubmit_file/', views.unsubmit_file, name = 'unsubmit_file'),
    path('todo/', views.todo, name = 'todo'),
    path('toreview/', views.toreview, name = 'toreview'),
    path('<int:pk>/classwork/', views.classwork, name = 'classwork'),
]
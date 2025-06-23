from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from posts.models import Post
from comments.models import Comment
from django.utils import timezone
import sweetify
from django.urls import reverse_lazy
from itertools import chain
from .models import Classroom,Topic,ClassroomTeachers
from posts.models import Assignment,SubmittedAssignment,AssignmentFile, Attachment
from .forms import ClassroomCreationForm,JoinClassroomForm, PostForm, AssignmentFileForm, AssignmentCreateForm
from comments.forms import CommentCreateForm, PrivateCommentForm
from comments.models import PrivateComment
import pytz
from django.contrib.auth.models import User, Group
from django.db.models import Count, Q
from collections import defaultdict
from users.models import Profile
from django.http import JsonResponse
import json
from calendar import month_name
now_utc = timezone.now()
tz_indonesia = pytz.timezone('Asia/Jakarta')
now_indonesia = now_utc.astimezone(tz_indonesia)
import random

def tentang(request):
    return render(request, 'classroom/tentang.html')
def get_random_color():
    colors = [
        '#FF5733', '#33FF57', '#3357FF', '#F333FF', '#33FFF5',
        '#F5FF33', '#FF33A2', '#A233FF', '#33FFB8', '#FFC733'
    ]
    return random.choice(colors)

@login_required
def home(requests):
    teaching_classes = set([classroom.classroom for classroom in requests.user.classroomteachers_set.all()])
    classrooms = set(requests.user.classroom_set.all()).union(teaching_classes)
    classroom_form = ClassroomCreationForm()
    classroom_colors = {classroom: get_random_color() for classroom in classrooms}
    join_classroom_form = JoinClassroomForm()
    
    context = {
        'classrooms' : classrooms,
        'classroom_form': classroom_form,
        'join_classroom_form':join_classroom_form,
        'classroom_colors': classroom_colors
    }
    return render(requests, 'classroom/home.html', context)
@login_required
def get_discussion_activity(request):
    # Menghitung jumlah post dan komentar untuk setiap bulan
    monthly_counts = {
        "Jan": {"posts": 0, "comments": 0},
        "Feb": {"posts": 0, "comments": 0},
        "Mar": {"posts": 0, "comments": 0},
        "Apr": {"posts": 0, "comments": 0},
        "May": {"posts": 0, "comments": 0},
        "Jun": {"posts": 0, "comments": 0},
        "Jul": {"posts": 0, "comments": 0},
        "Aug": {"posts": 0, "comments": 0},
        "Sep": {"posts": 0, "comments": 0},
        "Oct": {"posts": 0, "comments": 0},
        "Nov": {"posts": 0, "comments": 0},
        "Dec": {"posts": 0, "comments": 0},
    }
    
    # Ambil post pengguna yang terbaru
    latest_posts = Post.objects.filter(created_by=request.user, created_at__year=timezone.now().year).order_by('-created_at')
    
    for post in latest_posts:
        month = post.created_at.strftime("%b")
        monthly_counts[month]["posts"] += 1
        monthly_counts[month]["comments"] += post.post_comment_count
    
    # Format data untuk JSON response
    months = list(monthly_counts.keys())
    posts_data = [monthly_counts[month]["posts"] for month in months]
    comments_data = [monthly_counts[month]["comments"] for month in months]
    
    data = {
        'months': months,
        'posts_data': posts_data,
        'comments_data': comments_data,
    }
    
    return JsonResponse(data)
@login_required
def get_monthly_discussion_activity(request):
    # Inisialisasi data untuk menyimpan jumlah post dan komentar per bulan
    monthly_activity = []

    # Mengambil daftar nama-nama bulan dalam bahasa Inggris
    months = list(month_name)[1:]

    # Iterasi untuk setiap bulan dalam setahun
    for month in range(1, 13):
        # Mengambil posts yang dibuat pada bulan dan tahun tertentu
        posts = Post.objects.filter(created_by=request.user, created_at__month=month, created_at__year=timezone.now().year)
        
        # Menghitung jumlah posts
        posts_count = posts.count()

        # Menghitung jumlah komentar untuk semua posts pada bulan tersebut
        comments_count = sum(post.comment_set.count() for post in posts)

        # Menambahkan data ke dalam list
        monthly_activity.append({
            'month': months[month - 1],  # Mendapatkan nama bulan berdasarkan indeks
            'posts_count': posts_count,
            'comments_count': comments_count,
        })

    # Mengembalikan data dalam format JSON
    return JsonResponse(monthly_activity, safe=False)
@login_required
def get_gender_data(request):
    gender_data = Profile.objects.values('gender').annotate(count=Count('gender'))
    
    gender_counts = {
        'M': 0,
        'F': 0,
    }
    
    for data in gender_data:
        gender_counts[data['gender']] = data['count']
    print(gender_counts)

    return JsonResponse(gender_counts)
@login_required
def dashboard(request):
    teaching_classes = set([classroom.classroom for classroom in request.user.classroomteachers_set.all()])
    classrooms = set(request.user.classroom_set.all()).union(teaching_classes)
    total_classrooms = len(classrooms)

    classrooms_with_user_count = Classroom.objects.annotate(total_users=Count('users'))
    group_siswa_classrooms = classrooms_with_user_count.filter(users__groups__name='siswa').distinct().count()

    siswa_group = Group.objects.get(name='siswa')
    latest_users = User.objects.filter(groups=siswa_group).order_by('-date_joined')[:10]

    user_profiles = []
    for user in latest_users:
        classrooms = user.classroom_set.all()
        classroom_names = [classroom.name for classroom in classrooms]

        try:
            profile_image = user.profile.image.url if user.profile.image else None
        except AttributeError:
            profile_image = None

        user_info = {
            "nama": user.username,
            "gambar": profile_image,
            "classrooms": classroom_names
        }
        user_profiles.append(user_info)
    user_classrooms = request.user.classroom_set.all()

    # Jika pengguna tidak memiliki kelas yang diikuti, atur latest_posts kosong
    if not user_classrooms.exists():
        latest_posts = []
    else:
        user_topics = Topic.objects.filter(classroom__in=user_classrooms)
        # Filter postingan-postingan yang terkait dengan kelas-kelas yang diikuti pengguna
        # latest_posts = Post.objects.filter(topic__in=user_topics).select_related('created_by').prefetch_related('comment_set').order_by('-created_at')[:5]
        
    latest_posts = Post.objects.filter(created_by=request.user).select_related('created_by').prefetch_related('comment_set').order_by('-created_at')[:5]
    siswa_group = Group.objects.get(name="siswa")
    
    # Dapatkan semua pengguna yang ada dalam grup "siswa"
    siswa_users = User.objects.filter(groups=siswa_group)
    recent_comments_private = PrivateComment.objects.filter(user__in=siswa_users).select_related('user', 'assignment').order_by('-created_at')[:5]
    print(recent_comments_private)
    user = User.objects.get(username=request.user)
    total_posting = Post.objects.filter(created_by=user).count()
    total_submit = SubmittedAssignment.objects.filter(user=request.user, status='completed').count()
    total_tugas_guru = Assignment.objects.count()

    all_assignments = []
    for classroom in classrooms:
        assignments = Assignment.objects.filter(topic__classroom=classroom)
        all_assignments.extend(assignments)

    classrooms = request.user.classroom_set.all()
    topics = []
    for classroom in classrooms:
        topics.extend(list(classroom.topic_set.all()))

    assignments = []
    for topic in topics:
        assignments.extend(list(topic.assignment_set.all()))

    completed_assignments = []  # List for completed assignments
    pending_assignments = []  # List for pending (in progress) assignments
    for assignment in assignments:
        if not assignment.is_turnedin(request.user):
            pending_assignments.append(assignment)

    total_tugas = SubmittedAssignment.objects.filter(user=request.user, status='completed').count()
    comment = Comment.objects.filter(user=user)

    context = {
        'total_classrooms': total_classrooms,
        'total_submit': total_submit,
        'total_posting': total_posting,
        'total_tugas_guru': total_tugas_guru,
        'total_tugas': total_tugas,
        'comment': comment,
        'recent_task': pending_assignments,
        'total_siswa': pending_assignments,
        'total_student': group_siswa_classrooms,
        'user_profiles': user_profiles,
        'latest_posts':latest_posts,
        'recent_comments_private':recent_comments_private,
    }

    return render(request, 'classroom/beranda.html', context)
@login_required
def create_classroom(request):
    if request.method == 'POST':
        form = ClassroomCreationForm(request.POST)
        if form.is_valid(): 
            name = form.cleaned_data.get('name')
            description = form.cleaned_data.get('description')
            classroom = Classroom(name=name, description=description, created_by=request.user)
            classroom.save()
            classroom.classroom_code = classroom.name[:4] + str(classroom.id)
            classroom.save()
            topic = Topic(name = 'General' , classroom = classroom)
            topic.save()
            classroom_teachers = ClassroomTeachers(classroom = classroom, teacher=request.user)
            classroom_teachers.save()
            sweetify.success(request, f'Kelas {name} Berhasil dibuat !')
            return redirect('/classroom/')
        else:
            sweetify.error(request, f'Kelas tidak dapat dibuat :(')
            sweetify.error(request, form.errors)
    return redirect('classroom:home')

@login_required
def join_classroom(request):
    if request.method == 'POST':
        print('fORM vaLID')
        form = JoinClassroomForm(request.POST)
        if form.is_valid(): 
            classroom = Classroom.objects.filter(classroom_code = form.cleaned_data.get('code')).first()
            if classroom:
                classroom.users.add(request.user)
                request.user.classroom_set.add(classroom)
                sweetify.success(request, f'Anda telah ditambahkan {classroom.name}')
            else:
                sweetify.error(request, f'Terjadi kesalahan saat menambahkan Anda ke dalam kelas')
        else:
            sweetify.success(request, f'Berhasil menambahkan Anda ke dalam kelas')
    return redirect('classroom:home')

@login_required
def open_classroom(request,pk):
    classroom = get_object_or_404(Classroom,pk = pk)
    topics = classroom.topic_set.all()
    contents = []
    for topic in topics:
        contents.extend(list(topic.post_set.all()))
        contents.extend(list(topic.assignment_set.all()))
    
    contents.sort(key = lambda x: x.created_at)
    post_form = PostForm()
    comment_form = CommentCreateForm()
    teacher = classroom.classroomteachers_set.all()

    context = {
        'classroom' : classroom,
        'contents': reversed(contents),
        'post_form': post_form,
        'comment_form': comment_form,
        'teachers': classroom.classroomteachers_set.all(),
        'students': classroom.users.all(),
    }

    return render(request, 'classroom/classroom.html', context)
def update_classroom(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    if request.method == 'POST':
        form = ClassroomCreationForm(request.POST, instance=classroom)
        if form.is_valid():
            form.save()
            return redirect('classroom:home', pk=classroom.pk)
    else:
        form = ClassroomCreationForm(instance=classroom)
    return render(request, 'classroom/home.html', {'cok': form})

@login_required
def view_document(request, document_id):
    document = Post.objects.get(id=document_id)
    return render(request, 'classroom/classroom.html', {'document': document})
@login_required
def delete_classroom(requests):
    context = {
        'title' : 'Classroom',
    }
    return render(requests, 'base.html', context)


@login_required
def members(request, classroom_code):
    classroom = get_object_or_404(Classroom, classroom=classroom_code)
    context = {
        'teachers': classroom.classroomteachers_set.all(),
        'students': classroom.users.all(),
    }
    print(context)
    return render(request, 'classroom/members.html', context)
@login_required
def assignment(request):
    assignment = Assignment.objects.all()
    completed_tasks_count = Assignment.objects.filter(status='selesai', due_date__lte=now_indonesia).count()
    onprogress_tasks_count = Assignment.objects.filter(status=Assignment.onprogress, due_date__lte=now_indonesia).count()
    print(f"Assignment {completed_tasks_count}: status={onprogress_tasks_count}")
    context = {
        'assignment':assignment,
        'completed_tasks_count': completed_tasks_count,
        'onprogress_tasks_count': onprogress_tasks_count,
    }
    return render(request, 'classroom/assigments.html', context)
@login_required
def assignment_create(request):
    if request.method == 'POST':
        form = AssignmentCreateForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            topic = get_object_or_404(Topic, pk=int(form.cleaned_data['topics']))
            due_date = form.cleaned_data['due_date']
            if due_date > now_indonesia:
                status = Assignment.onprogress
            else:
                status = Assignment.completed
            
            # status = Assignment.onprogress if form.cleaned_data['due_date'] > timezone.now() else Assignment.completed
            assignment = Assignment(
                title = form.cleaned_data['title'],
                description = form.cleaned_data['description'],
                created_by = request.user,
                topic = topic,
                due_date = form.cleaned_data['due_date'],
                status = status,
            )
            assignment.save()
            files = request.FILES.getlist('file_field')
            for f in files:
                Attachment.objects.create(assignment = assignment,files=f)
            sweetify.success(request, f'Tugas berhasil dibuat')
            return redirect('classroom:open_classroom', topic.classroom.pk)
        else:
            sweetify.error(request, f'Tugas gagal dibuat: {form.errors.as_text()}')
    else:
        form = AssignmentCreateForm(request.user)
    context = {'form':form}
    return render(request, 'classroom/assignment_create.html', context)

@login_required
def assignment_update(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    
    if request.method == 'POST':
        form = AssignmentCreateForm(request.user, request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            topic = get_object_or_404(Topic, pk=int(form.cleaned_data['topics']))
            due_date = form.cleaned_data['due_date']
            now_indonesia = timezone.now()  # Ensure this is set correctly
            
            if due_date > now_indonesia:
                status = Assignment.onprogress
            else:
                status = Assignment.completed
            
            assignment.title = form.cleaned_data['title']
            assignment.description = form.cleaned_data['description']
            assignment.topic = topic
            assignment.due_date = due_date
            assignment.marks = form.cleaned_data['points']
            assignment.status = status
            assignment.save()

            # Update attachments
            files = request.FILES.getlist('file_field')
            for f in files:
                Attachment.objects.create(assignment=assignment, files=f)
            
            sweetify.success(request, 'Tugas berhasil diperbarui.')
            return redirect('classroom:open_classroom', topic.classroom.pk)
        else:
            sweetify.error(request, f'Tugas gagal diperbarui: {form.errors.as_text()}')
    else:
        form = AssignmentCreateForm(request.user, instance=assignment)
    existing_attachments = Attachment.objects.filter(assignment=assignment)
    return render(request, 'classroom/assignment_update.html', {'form': form, 'existing_attachments':existing_attachments})
@login_required
def assignment_submit(request, pk):
    if request.method=='POST':
        assignment = get_object_or_404(Assignment,pk=pk)
        submitted_assignment = assignment.submittedassignment_set.filter(user=request.user).first()
        if not submitted_assignment:
            submitted_assignment = SubmittedAssignment.objects.create(assignment = assignment, user = request.user)
        files = request.FILES.getlist('file_field')
        print(files)
        for f in files:
            AssignmentFile.objects.create(submitted_assignment = submitted_assignment,files=f)

        assignment.status = Assignment.completed
        assignment.save()
    form = AssignmentFileForm()
    private_comment_form = PrivateCommentForm()
    assignment = get_object_or_404(Assignment, pk=pk)
    submit_assignment = assignment.submittedassignment_set.filter(user=request.user)
    classroom_teachers = list(map(lambda teaches: teaches.teacher, assignment.topic.classroom.classroomteachers_set.all()))
    print(classroom_teachers)
    is_teacher = request.user in classroom_teachers
    print(is_teacher)
    if submit_assignment:
        submit_assignment = submit_assignment.first()
        assignment_files = submit_assignment.assignmentfile_set.all()
    else: assignment_files = None


    context = {
        'assignment': assignment,
        'attachments': assignment.attachment_set.all(),
        'submitted_assignment': submit_assignment,
        'assignment_files': assignment_files,
        'form':form,
        'private_comment_form': private_comment_form,
        'is_teacher': is_teacher,
    }
    return render(request, 'classroom/assignment_submit.html', context)

@login_required
def turnin(request,pk):
    if request.method == 'POST':
        assignment = get_object_or_404(Assignment,pk=pk)
        submitted_assignment = assignment.submittedassignment_set.filter(user = request.user).first()
        if not submitted_assignment:
            submitted_assignment = SubmittedAssignment.objects.create(assignment = assignment, user = request.user)
        submitted_assignment.turned_in = True 
        submitted_assignment.status = 'Selesai'
        submitted_assignment.save()
        sweetify.success(request, f'Tugas telah diselesaikan')
        return redirect('classroom:assignment_submit', pk)

@login_required
def unsubmit(request,pk):
    if request.method == 'POST':
        assignment = get_object_or_404(Assignment,pk=pk)
        submitted_assignment = assignment.submittedassignment_set.filter(user = request.user).first()
        submitted_assignment.turned_in = False  
        submitted_assignment.save()
        
    return redirect('classroom:assignment_submit', pk)

@login_required
def unsubmit_file(request, pk):
    if request.method == 'POST':
        assignment_file = get_object_or_404(AssignmentFile, pk=pk)
        assignment_pk = assignment_file.submitted_assignment.assignment.pk
        if assignment_file.submitted_assignment.user == request.user:
            if assignment_file.submitted_assignment.turned_in:
                submitted_assignment = assignment_file.submitted_assignment
                submitted_assignment.turned_in = False  
                submitted_assignment.save()
            assignment_file.delete()
        return redirect('classroom:assignment_submit', assignment_pk)

@login_required
def todo(request):
    submitted_assignments = SubmittedAssignment.objects.filter(user=request.user).order_by('-id')
    classrooms = request.user.classroom_set.all()
    topics = []
    for classroom in classrooms:
        topics.extend(list(classroom.topic_set.all()))
    assignments = []
    for topic in topics:
        assignments.extend(list(topic.assignment_set.all().order_by('-id')))
    filtered_assignments = []
    for assignment in assignments:
        if not assignment.is_turnedin(request.user):
            filtered_assignments.append(assignment)
    context = {'assignments': filtered_assignments,'submitted_assignments':submitted_assignments}
    return render(request, 'classroom/todo.html', context)


@login_required
def toreview(request):
    classrooms = request.user.classroomteachers_set.all()
    classrooms = list(map(lambda x: x.classroom, classrooms))
    topics = []
    for classroom in classrooms:
        topics.extend(classroom.topic_set.all())
    assignments = []
    for topic in topics:
        assignments.extend(topic.assignment_set.all())
    context = {'assignments': reversed(assignments)}
    return render(request, 'classroom/toreview.html', context)


@login_required
def classwork(request, pk):
    classroom = get_object_or_404(Classroom,pk=pk)
    assignments = []
    for topic in classroom.topic_set.all():
        assignments.extend(list(topic.assignment_set.all()))
    
    context = {'assignments':assignments}
    return render(request, 'classroom/classwork.html', context)

def student_work(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    context = {'assignment': assignment}
    return render(request, 'classroom/student_work.html', context)



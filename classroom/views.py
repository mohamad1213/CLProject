from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from posts.models import Post
from comments.models import Comment
from django.utils import timezone
import sweetify
from itertools import chain
from .models import Classroom,Topic,ClassroomTeachers
from posts.models import Assignment,SubmittedAssignment,AssignmentFile, Attachment
from .forms import ClassroomCreationForm,JoinClassroomForm, PostForm, AssignmentFileForm, AssignmentCreateForm
from comments.forms import CommentCreateForm, PrivateCommentForm
import pytz
from django.contrib.auth.models import User, Group
now_utc = timezone.now()
tz_indonesia = pytz.timezone('Asia/Jakarta')
now_indonesia = now_utc.astimezone(tz_indonesia)
@login_required
def home(requests):
    teaching_classes = set([classroom.classroom for classroom in requests.user.classroomteachers_set.all()])
    classrooms = set(requests.user.classroom_set.all()).union(teaching_classes)
    classroom_form = ClassroomCreationForm()
    join_classroom_form = JoinClassroomForm()
    
    context = {
        'classrooms' : classrooms,
        'classroom_form': classroom_form,
        'join_classroom_form':join_classroom_form
    }
    return render(requests, 'classroom/home.html', context)
@login_required
def dashboard(requests):
    teaching_classes = set([classroom.classroom for classroom in requests.user.classroomteachers_set.all()])
    classrooms = set(requests.user.classroom_set.all()).union(teaching_classes)
    total_classrooms = len(classrooms)
    user = User.objects.get(username=requests.user)
    total_posting = Post.objects.filter(created_by=user).count()
    total_submit = SubmittedAssignment.objects.filter(user=requests.user, status='completed').count()
    total_tugas_guru = Assignment.objects.count()
    all_assignments = []
    for classroom in classrooms:
        assignments = Assignment.objects.filter(topic__classroom=classroom)
        all_assignments.extend(assignments)
    classrooms = requests.user.classroom_set.all()
    topics = []
    for classroom in classrooms:
        topics.extend(list(classroom.topic_set.all()))
    assignments = []
    for topic in topics:
        assignments.extend(list(topic.assignment_set.all()))
    completed_assignments = []  # List for completed assignments
    pending_assignments = []  # List for pending (in progress) assignments
    for assignment in assignments:
        submitted_assignment = assignment.submittedassignment_set.filter(user=requests.user).first()
        if submitted_assignment:
            status = submitted_assignment.status
            if status == 'completed':
                completed_assignments.append(assignment)
            else:
                pending_assignments.append(assignment)
        else:
            pending_assignments.append(assignment)
    all_classrooms = Classroom.objects.all()

# Menghitung total siswa dari semua kelas
    total_students = User.objects.filter(users__in=all_classrooms).count()

    total_tugas_siswa = len(pending_assignments)
    comment = Comment.objects.filter(user=user)
    total_tugas = SubmittedAssignment.objects.filter(user=requests.user, status='completed').count()
    context = {
        'total_classrooms' : total_classrooms,
        'total_submit' : total_submit,
        'total_posting' : total_posting,
        'total_tugas_guru' : total_tugas_guru,
        'total_tugas_siswa' : total_tugas_siswa,
        'total_tugas' : total_tugas,
        'comment' : comment,
        'recent_task' : pending_assignments,
    }
    print(total_students)
    return render(requests, 'classroom/beranda.html', context)
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
            sweetify.success(request, f'Classroom {name} created !')
            return redirect('/classroom/')
        else:
            sweetify.error(request, f'Classroom Could not be created :(')
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
                request.user.classroom_set.add(classroom)
                sweetify.success(request, f'You are added in {classroom.name}')
            else:
                sweetify.success(request, f'Error adding you to the classroom')
        else:
            sweetify.success(request, f'Error adding you to the classroom')
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

    context = {
        'classroom' : classroom,
        'contents': reversed(contents),
        'post_form': post_form,
        'comment_form': comment_form,
    }

    return render(request, 'classroom/classroom.html', context)
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
def members(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    context = {
        'teachers': classroom.classroomteachers_set.all(),
        'students': classroom.users.all(),
    }
    return render(request, 'classroom/members.html', context)
@login_required
def assignment(request):
    assignment = Assignment.objects.all()
    completed_tasks_count = Assignment.objects.filter(status='completed', due_date__lte=now_indonesia).count()
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
        submitted_assignment.status = 'completed'
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
    submitted_assignments = SubmittedAssignment.objects.filter(user=request.user)
    classrooms = request.user.classroom_set.all()
    topics = []
    for classroom in classrooms:
        topics.extend(list(classroom.topic_set.all()))
    assignments = []
    for topic in topics:
        assignments.extend(list(topic.assignment_set.all()))
    filtered_assignments = []
    # for assignment in assignments:
    #     if not assignment.is_turnedin(request.user):
    #         filtered_assignment.append(assignment)
    for assignment in assignments:
        submitted_assignment = assignment.submittedassignment_set.filter(user=request.user).first()
        if submitted_assignment:
            status = submitted_assignment.status
        else:
            status = 'pending'
        filtered_assignments.append({
            'assignment': assignment,
            'status': status
        })
    context = {'assignments': filtered_assignments}
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



from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Assignment, Post,Resource,StudentReport, SubmittedAssignment
from classroom.models import Classroom,Topic
from classroom.forms import PostForm
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .forms import StudentReportForm

@login_required
def create_post(request, pk):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            classroom = get_object_or_404(Classroom,pk = pk)
            topic = classroom.topic_set.first()
            title = form.cleaned_data.get('title')
            description = form.cleaned_data.get('description')
            files = request.FILES.getlist('file_field')
            post = Post.objects.create(title=title,description=description,created_by=request.user, topic = topic)
            for f in files:
                Resource.objects.create(post = post,files=f)
            
            messages.success(request, f'Post Created {title}')
        else:
            messages.danger(request, f'Cannot create post')
    
    return redirect('classroom:open_classroom', pk)

# views.py


@login_required
def student_report_list(request):
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
    context = {'assignments': filtered_assignments,'reports':submitted_assignments,}
    return render(request, 'student_report_list.html',context)
@login_required
def generate_student_report_pdf(request, report_id):
    report = StudentReport.objects.get(pk=report_id)
    if request.user.groups.filter(name='guru').exists():  # Check if user belongs to 'guru' group
        template_path = 'reportpdf.html'
        context = {'report': report}
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'filename="student_report_{report_id}.pdf"'
        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('PDF generation error')
        return response
    else:
        return HttpResponse('Unauthorized access')

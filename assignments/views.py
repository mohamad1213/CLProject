from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from posts.models import SubmittedAssignment,Assignment
from classroom.models import Classroom
from comments.forms import PrivateCommentForm
from .forms import GradeStudentForm

@login_required
def view_grades(request,pk):
    test = SubmittedAssignment.objects.all()
    for u in test:
        output = {
            "assignment" : u.assignment,
            "user" : u.user,
            "turned_in" : u.turned_in,
            "grade" : u.grade,
            "is_reviewed" : u.is_reviewed,
        }
        print(output)
    assignment = get_object_or_404(Assignment,pk=pk)
    submitted_assignments = assignment.submittedassignment_set.all()
    context = {
        'submitted_assignments':submitted_assignments,
        'assignment':assignment,
        'output':output,
    }
    return render(request, 'assignments/view_grades.html', context)

@login_required
def grade(request,pk):
    submit_assignment = get_object_or_404(SubmittedAssignment, pk=pk)
    if request.method == 'POST':
        grade_form = GradeStudentForm(request.POST)
        if grade_form.is_valid():
            grade = grade_form.cleaned_data.get('grade')
            submit_assignment.is_reviewed = True
            submit_assignment.grade = grade 
            submit_assignment.save()
        else:
            print('not valid')
    else:
        grade_form = GradeStudentForm() 
            
    assignment_files = submit_assignment.assignmentfile_set.all()
    context = {
        'submit_assignment':submit_assignment,
        'assignment_files':assignment_files,
        'grade_form':grade_form,
    }
    return render(request, 'assignments/grade.html', context)
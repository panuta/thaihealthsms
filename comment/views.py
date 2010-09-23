# -*- encoding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from forms import *
from models import *

from domain.models import Program, Project, Activity
from report.models import Report, ReportSubmission
from kpi.models import DomainKPISchedule
from budget.models import BudgetSchedule

from comment import functions as comment_functions

from helper import utilities
from helper.shortcuts import render_response, render_page_response, access_denied

def view_project_comments(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    
    if request.method == 'POST':
        if 'submit_comment_button' in request.POST:
            form = PostCommentForm(request.POST)
            
            if form.is_valid():
                comment_functions.post_comment_for('project', project_id, form.cleaned_data['comment_message'], request.user.get_profile())
                messages.success(request, 'เพิ่มความคิดเห็นเรียบร้อย')
                return redirect('view_project_comments', project_id)
            
        elif 'submit_reply_button' in request.POST:
            comment_id = request.POST['comment_id']
            message = request.POST['comment_message']
            
            comment = get_object_or_404(Comment, pk=comment_id)
            if message:
                comment_functions.post_reply_comment_for(comment, 'project', project_id, message, request.user.get_profile())
                return redirect('view_project_comments', project_id)
        
    else:
        form = PostCommentForm()
    
    comments = comment_functions.get_comments_for('project', project_id, request.user.get_profile(), mark_as_read=True)
    return render_page_response(request, 'comments', 'page_program/project_comments.html', {'project':project, 'comments':comments, 'form':form})

def view_activity_comments(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    
    if request.method == 'POST':
        if 'submit_comment_button' in request.POST:
            form = PostCommentForm(request.POST)
            
            if form.is_valid():
                comment_functions.post_comment_for('activity', activity_id, form.cleaned_data['comment_message'], request.user.get_profile())
                messages.success(request, 'เพิ่มความคิดเห็นเรียบร้อย')
                return redirect('view_activity_comments', activity_id)
            
        elif 'submit_reply_button' in request.POST:
            comment_id = request.POST['comment_id']
            message = request.POST['comment_message']
            
            comment = get_object_or_404(Comment, pk=comment_id)
            if message:
                comment_functions.post_reply_comment_for(comment, 'activity', activity_id, message, request.user.get_profile())
                messages.success(request, 'ตอบกลับความคิดเห็นเรียบร้อย')
                return redirect('view_activity_comments', activity_id)
        
    else:
        form = PostCommentForm()
    
    comments = comment_functions.get_comments_for('activity', activity_id, request.user.get_profile(), mark_as_read=True)
    return render_page_response(request, 'comments', 'page_program/activity_comments.html', {'activity':activity, 'comments':comments, 'form':form})

def view_report_comments_by_submission(request, submission_id):
    submission = get_object_or_404(ReportSubmission, pk=submission_id)
    return redirect('view_report_comments', submission.program.id, submission.report.id, utilities.format_dateid(submission.schedule_date))

def view_report_comments(request, program_id, report_id, schedule_dateid):
    program = get_object_or_404(Program, pk=program_id)
    report = get_object_or_404(Report, pk=report_id)
    schedule_date = utilities.convert_dateid_to_date(schedule_dateid)
    
    try:
        submission = ReportSubmission.objects.get(program=program, report=report, schedule_date=schedule_date)
    except:
        submission = ReportSubmission(program=program, report=report, schedule_date=schedule_date)
    
    if request.method == 'POST':
        if 'submit_comment_button' in request.POST:
            form = PostCommentForm(request.POST)
            
            if form.is_valid():
                if not submission.id: submission.save()
                comment_functions.post_comment_for('report', submission.id, form.cleaned_data['comment_message'], request.user.get_profile())
                messages.success(request, 'เพิ่มความคิดเห็นเรียบร้อย')
                return redirect('view_report_comments', program_id=program.id, report_id=report.id, schedule_dateid=schedule_dateid)
            
        elif 'submit_reply_button' in request.POST:
            comment_id = request.POST['comment_id']
            message = request.POST['comment_message']
            
            comment = get_object_or_404(Comment, pk=comment_id)
            if message:
                comment_functions.post_reply_comment_for(comment, 'report', submission.id, message, request.user.get_profile())
                messages.success(request, 'ตอบกลับความคิดเห็นเรียบร้อย')
                return redirect('view_report_comments', program_id=program.id, report_id=report.id, schedule_dateid=schedule_dateid)
        
    else:
        form = PostCommentForm()
    
    if submission.id:
        comments = comment_functions.get_comments_for('report', submission.id, request.user.get_profile(), mark_as_read=True)
    else:
        comments = []
    
    return render_page_response(request, 'comments', 'page_report/report_comments.html', {'submission':submission, 'comments':comments, 'form':form})

def view_kpi_comments(request, schedule_id):
    schedule = get_object_or_404(DomainKPISchedule, pk=schedule_id)
    
    if request.method == 'POST':
        if 'submit_comment_button' in request.POST:
            form = PostCommentForm(request.POST)
            
            if form.is_valid():
                comment_functions.post_comment_for('kpi', schedule_id, form.cleaned_data['comment_message'], request.user.get_profile())
                messages.success(request, 'เพิ่มความคิดเห็นเรียบร้อย')
                return redirect('view_kpi_comments', schedule_id)
            
        elif 'submit_reply_button' in request.POST:
            comment_id = request.POST['comment_id']
            message = request.POST['comment_message']
            
            comment = get_object_or_404(Comment, pk=comment_id)
            if message:
                comment_functions.post_reply_comment_for(comment, 'kpi', schedule_id, message, request.user.get_profile())
                messages.success(request, 'ตอบกลับความคิดเห็นเรียบร้อย')
                return redirect('view_kpi_comments', schedule_id)
        
    else:
        form = PostCommentForm()
    
    comments = comment_functions.get_comments_for('kpi', schedule_id, request.user.get_profile(), mark_as_read=True)
    return render_page_response(request, 'comments', 'page_kpi/kpi_comments.html', {'schedule':schedule, 'comments':comments, 'form':form})

def view_budget_comments(request, schedule_id):
    schedule = get_object_or_404(BudgetSchedule, pk=schedule_id)
    
    if request.method == 'POST':
        if 'submit_comment_button' in request.POST:
            form = PostCommentForm(request.POST)
            
            if form.is_valid():
                comment_functions.post_comment_for('budget', schedule_id, form.cleaned_data['comment_message'], request.user.get_profile())
                messages.success(request, 'เพิ่มความคิดเห็นเรียบร้อย')
                return redirect('view_budget_comments', schedule_id)
            
        elif 'submit_reply_button' in request.POST:
            comment_id = request.POST['comment_id']
            message = request.POST['comment_message']
            
            comment = get_object_or_404(Comment, pk=comment_id)
            if message:
                comment_functions.post_reply_comment_for(comment, 'budget', schedule_id, message, request.user.get_profile())
                messages.success(request, 'ตอบกลับความคิดเห็นเรียบร้อย')
                return redirect('view_budget_comments', schedule_id)
        
    else:
        form = PostCommentForm()
    
    comments = comment_functions.get_comments_for('budget', schedule_id, request.user.get_profile(), mark_as_read=True)
    return render_page_response(request, 'comments', 'page_kpi/budget_comments.html', {'schedule':schedule, 'comments':comments, 'form':form})
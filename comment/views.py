# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from models import *
from domain.models import Project, Activity
from report.models import ReportSubmission
from kpi.models import DomainKPISchedule
from budget.models import BudgetSchedule

from helper.shortcuts import render_response, render_page_response, access_denied

def view_project_comments(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render_page_response(request, 'comments', 'page_program/project_comments.html', {'project':project, })

def view_activity_comments(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    return render_page_response(request, 'comments', 'page_program/activity_comments.html', {'activity':activity, })

def view_report_comments(request, program_id, report_id, schedule_date):
    submission = get_object_or_404(ReportSubmission, pk=submission_id)
    return render_page_response(request, 'comments', 'page_program/report_comments.html', {'submission':submission, })

def view_kpi_comments(request, schedule_id):
    schedule = get_object_or_404(DomainKPISchedule, pk=schedule_id)
    return render_page_response(request, 'comments', 'page_kpi/kpi_comments.html', {'schedule':schedule, })

def view_budget_comments(request, schedule_id):
    schedule = get_object_or_404(BudgetSchedule, pk=schedule_id)
    return render_page_response(request, 'comments', 'page_kpi/budget_comments.html', {'schedule':schedule, })
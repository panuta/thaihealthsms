# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from models import *
from domain.models import MasterPlan, Program

from helper.shortcuts import render_response, render_page_response, access_denied

@login_required
def view_master_plan_manage_report(request, master_plan_ref_no):
    master_plan = get_object_or_404(MasterPlan, ref_no=master_plan_ref_no)
    return render_page_response(request, 'report', 'page_sector/manage_master_plan/manage_report.html', {'master_plan':master_plan, })

@login_required
def view_program_reports(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    return render_page_response(request, 'reports', 'page_program/program_reports.html', {'program':program, })

@login_required
def view_report_overview(request, submission_id):
    submission = get_object_or_404(ReportSubmission, pk=submission_id)
    return render_page_response(request, 'overview', 'page_program/report_overview.html', {'submission':submission, })
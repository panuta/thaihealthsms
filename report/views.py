# -*- encoding: utf-8 -*-
import os
from datetime import datetime, date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect

from forms import *
from models import *

from report import functions as report_functions

from domain.models import MasterPlan, Program

from helper import utilities, permission
from helper.shortcuts import render_response, render_page_response, access_denied

#
# MASTER PLAN MANAGEMENT
#

@login_required
def view_master_plan_manage_program_report(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    master_plan = program.plan.master_plan
    today = date.today()
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    if request.method == 'POST':
        form = MasterPlanProgramReportsForm(request.POST, master_plan=master_plan)
        if form.is_valid():
            reports_before = [report_program.report for report_program in ReportAssignment.objects.filter(program=program, is_active=True)]
            reports_after = form.cleaned_data['reports']
            
            cancel_reports = set(reports_before) - set(reports_after)
            
            # Cancel Reports
            for cancel_report in cancel_reports:
                report_program = ReportAssignment.objects.get(report=cancel_report, program=program)
                report_program.is_active = False
                report_program.save()
            
            # Add New Reports
            new_reports = set(reports_after) - set(reports_before)
            for new_report in new_reports:
                report_program, created = ReportAssignment.objects.get_or_create(report=new_report, program=program)
                
                if not created:
                    report_program.is_active = True
                    report_program.save()
            
            messages.success(request, 'เลือกรายงานเรียบร้อย')
            return redirect('view_master_plan_manage_organization', (program.plan.master_plan.ref_no))
        
    else:
        form = MasterPlanProgramReportsForm(master_plan=master_plan, initial={'reports':[report_program.report.id for report_program in ReportAssignment.objects.filter(program=program, is_active=True)]})
    
    has_reports = Report.objects.filter(master_plan=master_plan).count() > 0
    return render_page_response(request, 'organization', 'page_sector/manage_master_plan/manage_program_report.html', {'master_plan':master_plan, 'program':program, 'form':form, 'has_reports':has_reports})

@login_required
def view_master_plan_manage_report(request, master_plan_ref_no):
    master_plan = get_object_or_404(MasterPlan, ref_no=master_plan_ref_no)
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    reports = Report.objects.filter(master_plan=master_plan).order_by('created')
    
    for report in reports:
        # NOTE ON DELETING REPORT:
        # Not allow to delete report if there's still project using this report (ReportProject model)
        # or some report submission has been submitted (state is not NO_ACTIVITY or EDITING_ACTIVITY)
        
        report.program_count = ReportAssignment.objects.filter(report=report, is_active=True).count()
        submission_count = ReportSubmission.objects.filter(report=report).exclude(Q(state=NO_ACTIVITY) | Q(state=EDITING_ACTIVITY)).count()
        report.removable = not report.program_count and not submission_count
    
    return render_page_response(request, 'report', 'page_sector/manage_master_plan/manage_report.html', {'master_plan':master_plan, 'reports':reports})

@login_required
def view_master_plan_manage_report_add_report(request, master_plan_ref_no):
    master_plan = get_object_or_404(MasterPlan, ref_no=master_plan_ref_no)
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    if request.method == 'POST':
        report_due_type = REPORT_DUE_TYPE[request.POST.get('report_due_type')]
        
        form = MasterPlanReportForm(request.POST)
        if form.is_valid():
            report_name = form.cleaned_data['name']
            need_approval = form.cleaned_data['need_approval']
            
            notify_before = form.cleaned_data['notify_before']
            notify_before_days = form.cleaned_data['notify_before_days'] if notify_before else 0
            if not notify_before_days: notify_before_days = 0
            
            notify_due = form.cleaned_data['notify_due']
            
            report = Report.objects.create(master_plan=master_plan, due_type=report_due_type, name=report_name, need_approval=need_approval, need_checkup=True, created_by=request.user.get_profile(), notify_days_before=notify_before_days, notify_at_due=notify_due)
            
            if report_due_type == REPORT_DUE_DATES:
                for due_date in request.POST.getlist('due_dates'):
                    if due_date:
                        (dyear, dmonth, ddate) = due_date.split('-')
                        ReportDueDates.objects.create(report=report, due_date=date(int(dyear), int(dmonth), int(ddate)))
                
            elif report_due_type == REPORT_REPEAT_DUE:
                cycle_length = form.cleaned_data['cycle_length']
                monthly_date = form.cleaned_data['monthly_date']
                
                schedule_start = report_functions.generate_report_schedule_start(True, monthly_date)
                ReportDueRepeatable.objects.create(report=report, schedule_start=schedule_start, schedule_cycle=3, schedule_cycle_length=cycle_length, schedule_monthly_date=monthly_date)
            
            messages.success(request, 'เพิ่มหัวเรื่องรายงานเรียบร้อย')
            return utilities.redirect_or_back('view_master_plan_manage_report', (master_plan.ref_no), request)
        
        # To re-populate the form when error occured
        report = Report(due_type=report_due_type)
        if report_due_type == REPORT_DUE_DATES:
            due_dates = []
            for due_date in request.POST.getlist('due_dates'):
                if due_date:
                        (dyear, dmonth, ddate) = due_date.split('-')
                        due_dates.append(ReportDueDates(due_date=date(int(dyear), int(dmonth), int(ddate))))
            
            report.due_dates = due_dates
            
    else:
        report = Report(due_type=REPORT_NO_DUE_DATE)
        form = MasterPlanReportForm()
    
    return render_page_response(request, 'report', 'page_sector/manage_master_plan/manage_report_modify_report.html', {'master_plan':master_plan, 'report':report, 'form':form})

@login_required
def view_master_plan_manage_report_edit_report(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    master_plan = report.master_plan
    if not master_plan: raise Http404
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    if request.method == 'POST':
        report_due_type = REPORT_DUE_TYPE[request.POST.get('report_due_type')]
        
        form = MasterPlanReportForm(request.POST)
        if form.is_valid():
            report.name = form.cleaned_data['name']
            report.need_approval = form.cleaned_data['need_approval']
            
            notify_before = form.cleaned_data['notify_before']
            report.notify_days_before = form.cleaned_data['notify_before_days'] if notify_before else 0
            if not report.notify_days_before: report.notify_days_before = 0
            
            report.notify_at_due = form.cleaned_data['notify_due']
            
            ReportDueRepeatable.objects.filter(report=report).delete()
            ReportDueDates.objects.filter(report=report).delete()
            ReportSubmission.objects.filter(report=report, state=NO_ACTIVITY).delete()
            
            report.due_type = report_due_type
            
            if report_due_type == REPORT_DUE_DATES:
                for due_date in request.POST.getlist('due_dates'):
                    if due_date:
                        (dyear, dmonth, ddate) = due_date.split('-')
                        ReportDueDates.objects.create(report=report, due_date=date(int(dyear), int(dmonth), int(ddate)))
                
            elif report_due_type == REPORT_REPEAT_DUE:
                cycle_length = form.cleaned_data['cycle_length']
                monthly_date = form.cleaned_data['monthly_date']
                
                schedule_start = report_functions.generate_report_schedule_start(True, monthly_date)
                ReportDueRepeatable.objects.create(report=report, schedule_start=schedule_start, schedule_cycle=3, schedule_cycle_length=cycle_length, schedule_monthly_date=monthly_date)
                
            report.save()
            
            messages.success(request, 'แก้ไขหัวเรื่องรายงานเรียบร้อย')
            return redirect('view_master_plan_manage_report', (master_plan.ref_no))

    else:
        if not report.notify_days_before:
            notify_before = False
            notify_days_before = ''
        else:
            notify_before = True
            notify_days_before = report.notify_days_before
        
        if report.due_type == REPORT_REPEAT_DUE:
            report_repeatable = ReportDueRepeatable.objects.get(report=report)
            cycle_length = report_repeatable.schedule_cycle_length
            monthly_date = report_repeatable.schedule_monthly_date
        else:
            cycle_length = ''
            monthly_date = ''
        
        form = MasterPlanReportForm(initial={
            'name': report.name,
            'need_approval': report.need_approval,
            'cycle_length': cycle_length,
            'monthly_date': monthly_date,
            'notify_before': notify_before,
            'notify_before_days': notify_days_before,
            'notify_due': report.notify_at_due,
        })
    
    if report.due_type == REPORT_DUE_DATES:
        report.due_dates = ReportDueDates.objects.filter(report=report).order_by('due_date')
    else:
        report.due_dates = []
    
    return render_page_response(request, 'report', 'page_sector/manage_master_plan/manage_report_modify_report.html', {'master_plan':master_plan, 'report':report, 'form':form})

@login_required
def view_master_plan_manage_report_delete_report(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    master_plan = report.master_plan
    if not master_plan: raise Http404
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    program_count = ReportAssignment.objects.filter(report=report, is_active=True).count()
    submission_count = ReportSubmission.objects.filter(report=report).exclude(Q(state=NO_ACTIVITY) | Q(state=EDITING_ACTIVITY)).count()
    if not program_count and not submission_count:
        ReportDueRepeatable.objects.filter(report=report).delete()
        ReportDueDates.objects.filter(report=report).delete()
        ReportSubmission.objects.filter(report=report).delete()
        report.delete()
        messages.success(request, 'ลบหัวเรื่องรายงานเรียบร้อย')
    else:
        messages.error(request, 'ไม่สามารถลบหัวเรื่องรายงาน เนื่องจากยังมีแผนงานผูกอยู่ หรือมีรายงานที่ส่งไปแล้ว')
        
    return redirect('view_master_plan_manage_report', (master_plan.ref_no))

#
# PROGRAM REPORTS
#

@login_required
def view_program_reports(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    
    """
    if kpi_year:
        year_number = int(year) - 543
    else:
        year_number = utilities.master_plan_current_year_number(program.plan.master_plan)
    
    utilities.master_plan_current_year_span(program.plan.master_plan)
    
    submissions = ReportSubmission.objects.filter(program=program).filter(Q(state=APPROVED_ACTIVITY) | (Q(state=SUBMITTED_ACTIVITY) & (Q(report__need_approval=False) | Q(report__need_checkup=False)))).order_by('-schedule_date')
    """
    
    # TODO Categorize by year and report type
    
    submissions = ReportSubmission.objects.filter(program=program).filter(Q(state=APPROVED_ACTIVITY) | (Q(state=SUBMITTED_ACTIVITY) & (Q(report__need_approval=False) | Q(report__need_checkup=False)))).order_by('-schedule_date')
    
    return render_page_response(request, 'reports', 'page_program/program_reports.html', {'program':program, 'submissions':submissions})

#
# PROGRAM REPORTS - SEND
#

@login_required
def view_program_reports_send_list(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    
    reports = []
    for assignment in ReportAssignment.objects.filter(program=program, is_active=True):
        report = assignment.report
        report.counter = report_functions.get_sending_report_count(program, report)
        reports.append(report)
    
    return render_page_response(request, 'reports', 'page_program/program_reports_send.html', {'program':program, 'reports':reports})

@login_required
def view_program_reports_send_report(request, program_id, report_id):
    program = get_object_or_404(Program, id=program_id)
    report = get_object_or_404(Report, id=report_id)
    submissions = report_functions.get_sending_report(program, report)
    return render_page_response(request, 'reports', 'page_program/program_reports_send_report.html', {'program':program, 'report':report, 'submissions':submissions})

#
# PROGRAM REPORTS - MANAGE
#

@login_required
def view_program_reports_manage_report(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    
    assignments = ReportAssignment.objects.filter(program=program, is_active=True)
    reports_from_master_plan = []
    reports_from_program = []
    
    for assignment in assignments:
        if assignment.report.master_plan:
            reports_from_master_plan.append(assignment.report)
        else:
            report = assignment.report
            report.removable = ReportSubmission.objects.filter(report=report).exclude(Q(state=NO_ACTIVITY) | Q(state=EDITING_ACTIVITY)).count() == 0
            reports_from_program.append(report)
    
    return render_page_response(request, 'reports', 'page_program/program_reports_manage.html', {'program':program, 'reports_from_master_plan':reports_from_master_plan, 'reports_from_program':reports_from_program})

@login_required
def view_program_reports_manage_report_add_report(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    
    if request.method == 'POST':
        report_due_type = REPORT_DUE_TYPE[request.POST.get('report_due_type')]
        
        form = ProgramReportForm(request.POST)
        if form.is_valid():
            report_name = form.cleaned_data['name']
            need_checkup = form.cleaned_data['need_checkup']
            need_approval = form.cleaned_data['need_approval']
            
            notify_before = form.cleaned_data['notify_before']
            notify_before_days = form.cleaned_data['notify_before_days'] if notify_before else 0
            if not notify_before_days: notify_before_days = 0
            
            notify_due = form.cleaned_data['notify_due']
            
            report = Report.objects.create(program=program, due_type=report_due_type, name=report_name, need_approval=need_approval, need_checkup=need_checkup, created_by=request.user.get_profile(), notify_days_before=notify_before_days, notify_at_due=notify_due)
            
            if report_due_type == REPORT_DUE_DATES:
                for due_date in request.POST.getlist('due_dates'):
                    if due_date:
                        (dyear, dmonth, ddate) = due_date.split('-')
                        ReportDueDates.objects.create(report=report, due_date=date(int(dyear), int(dmonth), int(ddate)))
                
            elif report_due_type == REPORT_REPEAT_DUE:
                cycle_length = form.cleaned_data['cycle_length']
                monthly_date = form.cleaned_data['monthly_date']
                
                schedule_start = report_functions.generate_report_schedule_start(True, monthly_date)
                ReportDueRepeatable.objects.create(report=report, schedule_start=schedule_start, schedule_cycle=3, schedule_cycle_length=cycle_length, schedule_monthly_date=monthly_date)
                
            ReportAssignment.objects.create(report=report, program=program)
            
            messages.success(request, 'เพิ่มหัวเรื่องรายงานเรียบร้อย')
            return redirect('view_program_reports_manage_report', (program.id))

    # To re-populate the form when error occured
        report = Report(due_type=report_due_type)
        if report_due_type == REPORT_DUE_DATES:
            due_dates = []
            for due_date in request.POST.getlist('due_dates'):
                if due_date:
                        (dyear, dmonth, ddate) = due_date.split('-')
                        due_dates.append(ReportDueDates(due_date=date(int(dyear), int(dmonth), int(ddate))))
            
            report.due_dates = due_dates
            
    else:
        report = Report(due_type=REPORT_NO_DUE_DATE)
        form = ProgramReportForm()
        
    return render_page_response(request, 'reports', 'page_program/program_reports_modify_report.html', {'program':program, 'form':form, 'report':report})

@login_required
def view_program_reports_manage_report_edit_report(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    
    if report.master_plan:
        messages.error(request, 'ไม่สามารถแก้ไขรายงานของแผนหลักได้จากหน้านี้')
        return redirect('view_program_reports_manage_report', (program.id))
    
    program = report.program
    
    if request.method == 'POST':
        report_due_type = REPORT_DUE_TYPE[request.POST.get('report_due_type')]
        
        form = ProgramReportForm(request.POST)
        if form.is_valid():
            report.name = form.cleaned_data['name']
            report.need_checkup = form.cleaned_data['need_checkup']
            report.need_approval = form.cleaned_data['need_approval']
            
            notify_before = form.cleaned_data['notify_before']
            report.notify_before_days = form.cleaned_data['notify_before_days'] if notify_before else 0
            if not report.notify_before_days: report.notify_before_days = 0
            
            report.notify_at_due = form.cleaned_data['notify_due']
            
            ReportDueRepeatable.objects.filter(report=report).delete()
            ReportDueDates.objects.filter(report=report).delete()
            ReportSubmission.objects.filter(report=report, state=NO_ACTIVITY).delete()
            
            report.due_type = report_due_type
            
            if report_due_type == REPORT_DUE_DATES:
                for due_date in request.POST.getlist('due_dates'):
                    if due_date:
                        (dyear, dmonth, ddate) = due_date.split('-')
                        ReportDueDates.objects.create(report=report, due_date=date(int(dyear), int(dmonth), int(ddate)))
                
            elif report_due_type == REPORT_REPEAT_DUE:
                cycle_length = form.cleaned_data['cycle_length']
                monthly_date = form.cleaned_data['monthly_date']
                
                schedule_start = report_functions.generate_report_schedule_start(True, monthly_date)
                ReportDueRepeatable.objects.create(report=report, schedule_start=schedule_start, schedule_cycle=3, schedule_cycle_length=cycle_length, schedule_monthly_date=monthly_date)
                
            report.save()
            
            messages.success(request, 'แก้ไขหัวเรื่องรายงานเรียบร้อย')
            return redirect('view_program_reports_manage_report', (program.id))
            
    else:
        if not report.notify_days_before:
            notify_before = False
            notify_days_before = ''
        else:
            notify_before = True
            notify_days_before = report.notify_days_before
        
        if report.due_type == REPORT_REPEAT_DUE:
            report_repeatable = ReportDueRepeatable.objects.get(report=report)
            cycle_length = report_repeatable.schedule_cycle_length
            monthly_date = report_repeatable.schedule_monthly_date
        else:
            cycle_length = ''
            monthly_date = ''
        
        form = ProgramReportForm(initial={
            'name': report.name,
            'need_checkup': report.need_checkup,
            'need_approval': report.need_approval,
            'cycle_length': cycle_length,
            'monthly_date': monthly_date,
            'notify_before': notify_before,
            'notify_before_days': notify_days_before,
            'notify_due': report.notify_at_due,
        })
    
    if report.due_type == REPORT_DUE_DATES:
        report.due_dates = ReportDueDates.objects.filter(report=report).order_by('due_date')
    else:
        report.due_dates = []
    
    return render_page_response(request, 'reports', 'page_program/program_reports_modify_report.html', {'program':program, 'form':form, 'report':report})

@login_required
def view_program_reports_manage_report_delete_report(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    
    if report.master_plan:
        messages.error(request, 'ไม่สามารถแก้ไขรายงานของแผนหลักได้จากหน้านี้')
        return redirect('view_program_reports_manage_report', (program.id))
    
    program = report.program
    
    if ReportSubmission.objects.filter(report=report).exclude(Q(state=NO_ACTIVITY) | Q(state=EDITING_ACTIVITY)).count() == 0:
        ReportDueRepeatable.objects.filter(report=report).delete()
        ReportDueDates.objects.filter(report=report).delete()
        ReportSubmission.objects.filter(report=report).delete()
        ReportAssignment.objects.filter(report=report).delete()
        report.delete()
        
        messages.success(request, 'ลบหัวเรื่องรายงานเรียบร้อย')
    else:
        messages.error(request, 'ไม่สามารถลบรอบการส่งรายงานที่มีการส่งรายงานไปแล้วได้')
    
    return redirect('view_program_reports_manage_report', (program.id))

@login_required
def view_report_overview(request, program_id, report_id, schedule_dateid):
    program = get_object_or_404(Program, pk=program_id)
    report = get_object_or_404(Report, pk=report_id)
    schedule_date = utilities.convert_dateid_to_date(schedule_dateid)
    
    try:
        submission = ReportSubmission.objects.get(program=program, report=report, schedule_date=schedule_date)
    except:
        submission = ReportSubmission(program=program, report=report, schedule_date=schedule_date)
    
    if request.method == 'POST':
        submit_type = request.POST.get('submit')
        
        if submit_type == 'submit-file':
            if not permission.access_obj(request.user, 'report submission edit', submission):
                return access_denied(request)
            
            if not submission.id: submission.save()
            
            file_response = ReportSubmissionFileResponse.objects.create(submission=submission, uploaded_by=request.user.get_profile())
            
            # Uploading directory
            uploading_directory = "%s/%d/%d/" % (settings.REPORT_SUBMIT_FILE_PATH, submission.report.id, submission.id)
            if not os.path.exists(uploading_directory): os.makedirs(uploading_directory)
            
            # Uploading file
            uploading_file = request.FILES['uploading_file']
            (file_name, separator, file_ext) = uploading_file.name.rpartition('.')
            
            if not file_name:
                file_name = file_ext
                file_ext = ''
            else:
                file_ext = '.%s' % file_ext
            
            unique_filename = '%s%s' % (file_name, file_ext)
            
            unique_filename = '%s%s' % (file_name, file_ext)
            if os.path.isfile('%s%s' % (uploading_directory, unique_filename.encode('utf-8'))):
                # Duplicated filename
                suffix_counter = 1
                
                while os.path.isfile('%s%s(%d)%s' % (uploading_directory, file_name, suffix_counter, file_ext)):
                    suffix_counter = suffix_counter + 1
                    
                unique_filename = '%s(%d)%s' % (file_name, suffix_counter, file_ext)
                
            file_response.filename = unique_filename
            file_response.save()
            
            destination = open(uploading_directory + unique_filename.encode('utf-8'), 'wb')
            for chunk in request.FILES['uploading_file'].chunks(): destination.write(chunk)
            destination.close()
            
            submission.state = EDITING_ACTIVITY
            submission.save()
        
        elif submit_type == 'submit-text':
            if not permission.access_obj(request.user, 'report submission edit', submission):
                return access_denied(request)
            
            text = request.POST.get("text")
            
            if not submission.id: submission.save()
            
            try:
                text_response = ReportSubmissionTextResponse.objects.get(submission=submission)
            except ReportSubmissionTextResponse.DoesNotExist:
                text_response = ReportSubmissionTextResponse.objects.create(submission=submission, submitted_by=request.user.get_profile())
                
            text_response.text = text
            text_response.save()
            
            submission.state = EDITING_ACTIVITY if text else NO_ACTIVITY
            submission.save()
            
        elif submit_type == 'submit-report':
            if not permission.access_obj(request.user, 'report submission submit', submission):
                return access_denied(request)
            
            submission.state = SUBMITTED_ACTIVITY
            submission.submitted_on = datetime.now()
            submission.approval_on = None
            submission.save()
            
        elif submit_type == 'approve-report':
            if not permission.access_obj(request.user, 'report submission approve', submission):
                return access_denied(request)
            
            submission.state = APPROVED_ACTIVITY
            submission.approval_on = datetime.now()
            submission.save()
            
        elif submit_type == 'reject-report':
            if not permission.access_obj(request.user, 'report submission approve', submission):
                return access_denied(request)
            
            submission.state = REJECTED_ACTIVITY
            submission.approval_on = datetime.now()
            submission.save()
        
        return redirect('view_report_overview', program_id=program.id, report_id=report.id, schedule_dateid=schedule_dateid)
    
    current_date = date.today()
    
    if (submission.state == NO_ACTIVITY or submission.state == EDITING_ACTIVITY) and submission.schedule_date < current_date:
        submission.status_code = 'overdue'
    elif submission.state == NO_ACTIVITY or submission.state == EDITING_ACTIVITY:
        submission.status_code = 'not_submitted'
    elif submission.state == SUBMITTED_ACTIVITY and not submission.report.need_approval:
        submission.status_code = 'submitted'
    elif submission.state == SUBMITTED_ACTIVITY and submission.report.need_approval:
        submission.status_code = 'waiting'
    elif submission.state == APPROVED_ACTIVITY:
        submission.status_code = 'approved'
    elif submission.state == REJECTED_ACTIVITY:
        submission.status_code = 'rejected'
    
    submission.allow_modifying = submission.status_code in ('overdue', 'not_submitted', 'rejected')
    
    try:
        submission.text_response = ReportSubmissionTextResponse.objects.get(submission=submission)
    except ReportSubmissionTextResponse.DoesNotExist:
        submission.text_response = ''
        
    submission.files = ReportSubmissionFileResponse.objects.filter(submission=submission)
    
    return render_page_response(request, 'overview', 'page_report/report_overview.html', {'submission':submission, 'REPORT_SUBMIT_FILE_URL':settings.REPORT_SUBMIT_FILE_URL})

@login_required
def view_report_related_data(request, program_id, report_id, schedule_dateid):
    program = get_object_or_404(Program, pk=program_id)
    report = get_object_or_404(Report, pk=report_id)
    schedule_date = utilities.convert_dateid_to_date(schedule_dateid)
    
    try:
        submission = ReportSubmission.objects.get(program=program, report=report, schedule_date=schedule_date)
    except:
        submission = ReportSubmission(program=program, report=report, schedule_date=schedule_date)
    
    return render_page_response(request, 'related', 'page_report/report_related_data.html', {'submission':submission})
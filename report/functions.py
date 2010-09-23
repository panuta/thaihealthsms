# -*- encoding:utf-8 -*-
import calendar
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from django.db.models import Q
from django.db.models import Min, Max
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.conf import settings

from accounts.models import *
from domain.models import *
from report.models import *

from helper import utilities, permission

def looping_earlier_report_schedule(report, funct):
    current_date = date.today()
    
    if report.due_type == REPORT_REPEAT_DUE:
        repeatable = ReportDueRepeatable.objects.get(report=report)
        
        next_date = repeatable.schedule_start
        while next_date < current_date:
            funct.__call__(report, next_date)
            next_date = _get_next_schedule(next_date, repeatable)
    
    elif report.due_type == REPORT_DUE_DATES:
        for due_date in ReportDueDates.objects.filter(report=report, due_date__lt=current_date):
            funct.__call__(report, due_date.due_date)

# For creating report
def generate_report_schedule_start(start_now, schedule_monthly_date):
    current_date = date.today()
    first_day, last_day = calendar.monthrange(current_date.year, current_date.month)
    
    schedule_monthly_date = int(schedule_monthly_date)
    
    if schedule_monthly_date == 0: schedule_monthly_date = last_day
    
    if start_now:
        schedule_start = date(current_date.year, current_date.month, schedule_monthly_date)
    else:
        if current_date.month == 12:
            schedule_start = date(current_date.year+1, 1, schedule_monthly_date)
        else:
            schedule_start = date(current_date.year, current_date.month+1, schedule_monthly_date)
    
    return schedule_start

def get_program_warning_report_count(program):
    """
    Purpose:
    - get late report submission count
    - get rejected report submission count
    
    Return:
    tuple of late count and rejected count
    """
    
    late_submissions = []
    
    def print_something(report, due_date):
        try:
            submission = ReportSubmission.objects.get(report=report, program=program, schedule_date=due_date)    
        except ReportSubmission.DoesNotExist:
            submission = ReportSubmission(report=report, program=program, schedule_date=due_date)
        
        if submission.state == NO_ACTIVITY or submission.state == EDITING_ACTIVITY:
            late_submissions.append(submission)
    
    for assignment in ReportAssignment.objects.filter(program=program, is_active=True):
        report = assignment.report
        looping_earlier_report_schedule(report, print_something)
    
    rejected_submission_count = ReportSubmission.objects.filter(program=program, state=REJECTED_ACTIVITY).count()
    
    return (len(late_submissions), rejected_submission_count)

def get_reports_for_program_reports_page(program, start_date, end_date, include_warning=False):
    submissions = ReportSubmission.objects.filter(program=program, schedule_date__gte=start_date, schedule_date__lte=end_date).filter(Q(state=APPROVED_ACTIVITY) | (Q(state=SUBMITTED_ACTIVITY) & (Q(report__need_approval=False) | Q(report__need_checkup=False)))).order_by('-schedule_date')
    late_submissions = []
    rejected_submissions = []
    
    if include_warning:
        def print_something(report, due_date):
            try:
                submission = ReportSubmission.objects.get(report=report, program=program, schedule_date=due_date)    
            except ReportSubmission.DoesNotExist:
                submission = ReportSubmission(report=report, program=program, schedule_date=due_date)
            
            if submission.state == NO_ACTIVITY or submission.state == EDITING_ACTIVITY:
                late_submissions.append(submission)
        
        for assignment in ReportAssignment.objects.filter(program=program, is_active=True):
            report = assignment.report
            looping_earlier_report_schedule(report, print_something)
        
        rejected_submissions = [submission for submission in ReportSubmission.objects.filter(program=program, state=REJECTED_ACTIVITY)]
        
    submissions = list(submissions)
    submissions.sort(key=lambda item:item.schedule_date, reverse=True)
    late_submissions.sort(key=lambda item:item.schedule_date, reverse=False)
    rejected_submissions.sort(key=lambda item:item.schedule_date, reverse=False)
    
    return (submissions, late_submissions, rejected_submissions)

#
# SEND REPORT PAGE
#

def get_sending_report_count(program, report):
    """
    Return number of report
    - Rejected report count
    - Overdue report count
    - Waiting approval report count
    """
    current_date = date.today()
    
    overdue_count = 0
    if report.due_type == REPORT_REPEAT_DUE:
        repeatable = ReportDueRepeatable.objects.get(report=report)
        
        next_date = repeatable.schedule_start
        while next_date < current_date:
            try:
                submission = ReportSubmission.objects.get(report=report, program=program, schedule_date=next_date)
                if submission.state == NO_ACTIVITY or submission.state == EDITING_ACTIVITY:
                    overdue_count = overdue_count + 1
            except ReportSubmission.DoesNotExist:
                overdue_count = overdue_count + 1
            
            next_date = _get_next_schedule(next_date, repeatable)
    
    elif report.due_type == REPORT_DUE_DATES:
        for due_date in ReportDueDates.objects.filter(report=report, due_date__lt=current_date):
            try:
                submission = ReportSubmission.objects.get(report=report, program=program, schedule_date=due_date.due_date)
                if submission.state == NO_ACTIVITY or submission.state == EDITING_ACTIVITY:
                    overdue_count = overdue_count + 1
            except ReportSubmission.DoesNotExist:
                overdue_count = overdue_count + 1
    
    rejected_count = ReportSubmission.objects.filter(report=report, program=program, state=REJECTED_ACTIVITY).count()
    
    if report.need_approval:
        waiting_count = ReportSubmission.objects.filter(report=report, program=program, state=SUBMITTED_ACTIVITY).count()
    else:
        waiting_count = 0
    
    return {'rejected':rejected_count, 'overdue':overdue_count, 'waiting':waiting_count}

def get_sending_report(program, report):
    """
    Return reports that
    - Next due reports (by settings.REPORT_DISPLAY_ADVANCED_SCHEDULES)
    - Rejected reports
    - Overdue reports
    - Waiting for approval reports
    """
    current_date = date.today()
    
    submissions = []
    if report.due_type == REPORT_REPEAT_DUE:
        repeatable = ReportDueRepeatable.objects.get(report=report)
        
        next_date = repeatable.schedule_start
        while next_date < current_date:
            try:
                submission = ReportSubmission.objects.get(report=report, program=program, schedule_date=next_date)
            except:
                submission = ReportSubmission(report=report, program=program, schedule_date=next_date)
            
            if submission.state == NO_ACTIVITY or submission.state == EDITING_ACTIVITY:
                submission.this_is = 'overdue'
                submissions.append(submission)
            
            next_date = _get_next_schedule(next_date, repeatable)
        
        if report.need_approval:
            for submission in ReportSubmission.objects.filter(report=report, program=program, state=SUBMITTED_ACTIVITY):
                submission.this_is = 'waiting'
                submissions.append(submission)
        
        for submission in ReportSubmission.objects.filter(report=report, program=program, state=REJECTED_ACTIVITY):
            submission.this_is = 'rejected'
            submissions.append(submission)
        
        advanced_submission_count = 0
        while settings.REPORT_DISPLAY_ADVANCED_SCHEDULES > advanced_submission_count:
            try:
                submission = ReportSubmission.objects.get(report=report, program=program, schedule_date=next_date)
            except:
                submission = ReportSubmission(report=report, program=program, schedule_date=next_date)
            
            if submission.state == NO_ACTIVITY or submission.state == EDITING_ACTIVITY:
                submission.this_is = 'nextdue'
                submissions.append(submission)
                advanced_submission_count = advanced_submission_count + 1
            
            next_date = _get_next_schedule(next_date, repeatable)
        
        submissions.sort(key=lambda item:item.schedule_date, reverse=False)
    
    elif report.due_type == REPORT_DUE_DATES:
        advanced_submission_count = 0
        
        for due_date in ReportDueDates.objects.filter(report=report).order_by('due_date'):
            try:
                submission = ReportSubmission.objects.get(report=report, program=program, schedule_date=due_date.due_date)
            except:
                submission = ReportSubmission(report=report, program=program, schedule_date=due_date.due_date)
            
            if (submission.state == NO_ACTIVITY or submission.state == EDITING_ACTIVITY) and due_date.due_date < current_date:
                submission.this_is = 'overdue'
                submissions.append(submission)
                
            elif report.need_approval and submission.state == SUBMITTED_ACTIVITY:
                submission.this_is = 'waiting'
                submissions.append(submission)
                
            elif submission.state == REJECTED_ACTIVITY:
                submission.this_is = 'rejected'
                submissions.append(submission)
                
            elif (submission.state == NO_ACTIVITY or submission.state == EDITING_ACTIVITY) and settings.REPORT_DISPLAY_ADVANCED_SCHEDULES > advanced_submission_count:
                advanced_submission_count = advanced_submission_count + 1
                submission.this_is = 'nextdue'
                submissions.append(submission)
    
    return submissions

# END -- SEND REPORT PAGE

def get_reports_for_edit_reference(program):
    reports = []
    for assignment in ReportAssignment.objects.filter(program=program, is_active=True):
        report = assignment.report
        report.submissions = ReportSubmission.objects.filter(program=program, report=report).filter(Q(state=APPROVED_ACTIVITY) | (Q(state=SUBMITTED_ACTIVITY) & (Q(report__need_approval=False) | Q(report__need_checkup=False)))).order_by('-schedule_date')
        
        if report.submissions:
            reports.append(report)
    
    return reports

#
# REPORT NOTIFICATION
#

def submission_notification():
    current_date = date.today()
    site = Site.objects.get_current()
    email_datatuple = list()
    
    user_notifies = {}
    for report in Report.objects.all():
        for report_assignment in ReportAssignment.objects.filter(report=report, is_active=True):
            program = report_assignment.program
            
            atdue = []
            beforedue = []
            
            if report.due_type == REPORT_REPEAT_DUE:
                repeatable = ReportDueRepeatable.objects.get(report=report)
                next_date = repeatable.schedule_start
                while next_date < current_date:
                    submission, created = ReportSubmission.objects.get_or_create(report=report,
                                            program=program, schedule_date=next_date)
                    next_date = _get_next_schedule(next_date, repeatable)
                
                if next_date == current_date and report.notify_at_due:
                    # ADD --> atdue
                    submission, created = ReportSubmission.objects.get_or_create(report=report,
                                            program=program, schedule_date=next_date)
                    atdue.append(submission)
                
                if report.notify_days_before:
                    days_pass = (next_date - current_date).days
                    while days_pass <= report.notify_days_before:
                        if next_date - timedelta(days=report.notify_days_before) == current_date:
                            submission, created = ReportSubmission.objects.get_or_create(report=report,
                                program=program, schedule_date=next_date-timedelta(days=report.notify_days_before))
                            if submission.state == NO_ACTIVITY or submission.state == EDITING_ACTIVITY:
                                # ADD --> beforedue
                                beforedue.append(submission)
                        next_date = _get_next_schedule(next_date, repeatable)
                        days_pass = (next_date - current_date).days
                
            elif report.due_type == REPORT_DUE_DATES:
                for due_date in ReportDueDates.objects.filter(report=report):
                    if due_date.due_date == current_date and report.notify_at_due:
                        # ADD --> atdue
                        submission, created = ReportSubmission.objects.get_or_create(report=report,
                                                program=program, schedule_date=due_date.due_date)
                        atdue.append(submission)
                    
                    if due_date.due_date - timedelta(days=report.notify_days_before) == current_date:
                        submission, created = ReportSubmission.objects.get_or_create(report=report,
                                                program=program, schedule_date=due_date.due_date)
                        if submission.state == NO_ACTIVITY or submission.state == EDITING_ACTIVITY:
                            # ADD --> beforedue
                            beforedue.append(submission)
            
            if atdue or beforedue:
                user_notifies = _populate_user_notification(user_notifies,
                                    _who_to_notify(program), atdue, beforedue)
    
    if user_notifies:
        email_datatuple = []
        
        for user in user_notifies.keys():
            atdue_submissions = user_notifies[user]['atdue']
            beforedue_submissions = user_notifies[user]['beforedue']
            
            # Sending Email
            email_subject = render_to_string('email/notify_report_subject.txt',
                                {'program': program}).strip(' \n\t')
            email_message = render_to_string('email/notify_report_message.txt',
                                {'site': site,
                                 'atdue_submissions': atdue_submissions,
                                 'beforedue_submissions': beforedue_submissions}).strip(' \n\t')

            email_datatuple.append((email_subject, email_message,
                                    settings.SYSTEM_NOREPLY_EMAIL, [user.user.email]))
        
        send_mass_mail(email_datatuple, fail_silently=True)

def _populate_user_notification(user_notifies, users, atdue, beforedue):
    for user in users:
        if not user in user_notifies:
            user_notifies[user] = {'atdue':[], 'beforedue':[]}
            
        for submission in atdue:
            user_notifies[user]['atdue'].append(submission)
        
        for submission in beforedue:
            user_notifies[user]['beforedue'].append(submission)
    
    return user_notifies

def _who_to_notify(program):
    responsibilities = UserRoleResponsibility.objects.filter(role__name='program_manager', programs__in=(program,))
    users = set()
    for responsibility in responsibilities:
        users.add(responsibility.user)
    return users
# END -- REPORT NOTIFICATION

# NOTE: Only for monthly
def _get_next_schedule(current_schedule, repeatable):
    month = current_schedule.month + repeatable.schedule_cycle_length
    
    if month > 12:
            month = month - 12
            year = current_schedule.year + 1
    else:
        year = current_schedule.year
    
    if repeatable.schedule_monthly_date == 0:
        first_day, last_day = calendar.monthrange(year, month)
        day = last_day
    else:
        day = current_schedule.day
    
    return date(year, month, day)

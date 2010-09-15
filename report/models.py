from django.contrib.auth.models import User
from django.db import models

# Report due date type
REPORT_NO_DUE_DATE = 1
REPORT_REPEAT_DUE = 2
REPORT_DUE_DATES = 3

# Report Activity
NO_ACTIVITY = 0
EDITING_ACTIVITY = 5
SUBMITTED_ACTIVITY = 1
APPROVED_ACTIVITY = 2
REJECTED_ACTIVITY = 3
CANCELLED_ACTIVITY = 4

class Report(models.Model):
    master_plan = models.ForeignKey('domain.MasterPlan', null=True) # Report Owner's Master Plan
    program = models.ForeignKey('domain.Program', null=True) # Report Owner's Program
    due_type = models.IntegerField(default=REPORT_NO_DUE_DATE)
    
    name = models.CharField(max_length=500)
    need_checkup = models.BooleanField(default=False) # Need to be report to one who has report_checkup permission
    need_approval = models.BooleanField(default=False) # Need approval from one who has report_approval permission
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.UserAccount')
    
    notify_days_before = models.IntegerField(default=0)
    notify_at_due = models.BooleanField(default=False)

class ReportDueRepeatable(models.Model):
    report = models.ForeignKey('Report', primary_key=True)
    schedule_start = models.DateField()
    schedule_cycle = models.IntegerField(default=3) # 1:Daily, 2:Weekly, 3:Monthly, 4:Yearly
    schedule_cycle_length = models.IntegerField(default=1)
    schedule_monthly_date = models.IntegerField(default=1) # 0 is end of month

class ReportDueDates(models.Model):
    report = models.ForeignKey('Report')
    due_date = models.DateField()


class ReportAssignment(models.Model):
    report = models.ForeignKey('Report')
    program = models.ForeignKey('domain.Program')
    is_active = models.BooleanField(default=True)


class ReportSubmission(models.Model):
    report = models.ForeignKey('Report')
    program = models.ForeignKey('domain.Program')
    schedule_date = models.DateField()
    submitted_on = models.DateTimeField(null=True)
    state = models.IntegerField(default=NO_ACTIVITY)
    approval_on = models.DateTimeField(null=True)

class ReportSubmissionTextResponse(models.Model):
    submission = models.ForeignKey('ReportSubmission', primary_key=True)
    text = models.TextField()
    submitted = models.DateTimeField(auto_now_add=True)
    submitted_by = models.ForeignKey('accounts.UserAccount')

class ReportSubmissionFileResponse(models.Model):
    submission = models.ForeignKey('ReportSubmission')
    filename = models.CharField(max_length=512)
    uploaded = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey('accounts.UserAccount')

class ReportSubmissionReference(models.Model):
    submission = models.ForeignKey('ReportSubmission')
    project = models.ForeignKey('domain.Project', null=True)
    kpi_schedule = models.ForeignKey('kpi.DomainKPISchedule', null=True)
    budget_schedule = models.ForeignKey('budget.BudgetSchedule', null=True)
    description = models.CharField(max_length=1000, blank=True)
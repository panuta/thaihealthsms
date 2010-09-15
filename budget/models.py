from django.db import models

class BudgetSchedule(models.Model):
    program = models.ForeignKey('domain.Program')
    grant_budget = models.IntegerField(default=0)
    claim_budget = models.IntegerField(default=0)
    schedule_on = models.DateField()
    claimed_on = models.DateField(null=True)
    remark = models.CharField(max_length=1000, blank=True)

class BudgetScheduleRevision(models.Model):
    schedule = models.ForeignKey('BudgetSchedule')
    grant_budget = models.IntegerField()
    claim_budget = models.IntegerField()
    schedule_on = models.DateField()
    revised = models.DateTimeField(auto_now_add=True)
    revised_by = models.ForeignKey('accounts.UserAccount')

class BudgetScheduleReference(models.Model):
    schedule = models.ForeignKey('BudgetSchedule', related_name='schedule')
    project = models.ForeignKey('domain.Project', null=True)
    report_submission = models.ForeignKey('report.ReportSubmission', null=True)
    description = models.CharField(max_length=1000, blank=True)
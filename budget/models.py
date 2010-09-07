from django.db import models

class BudgetSchedule(models.Model):
    program = models.ForeignKey('domain.Program')
    grant_budget = models.IntegerField(default=0)
    claim_budget = models.IntegerField(default=0)
    schedule_on = models.DateField()
    claimed_on = models.DateField()

class BudgetScheduleRevision(models.Model):
    schedule = models.ForeignKey('BudgetSchedule')
    grant_budget = models.IntegerField()
    claim_budget = models.IntegerField()
    schedule_on = models.DateField()
    revised = models.DateTimeField(auto_now_add=True)
    revised_by = models.ForeignKey('accounts.UserAccount')
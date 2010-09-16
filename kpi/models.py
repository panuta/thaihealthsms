from django.db import models

class DomainKPICategory(models.Model):
    master_plan = models.ForeignKey('domain.MasterPlan', null=True)
    program = models.ForeignKey('domain.Program', null=True)
    name = models.CharField(max_length=300)

class DomainKPI(models.Model):
    master_plan = models.ForeignKey('domain.MasterPlan', null=True)
    plan = models.ForeignKey('domain.Plan', null=True)
    program = models.ForeignKey('domain.Program', null=True)
    category = models.ForeignKey('DomainKPICategory', null=True)
    ref_no = models.CharField(max_length=100)
    name = models.CharField(max_length=1000)
    abbr_name = models.CharField(max_length=200, default='')
    year = models.IntegerField(default=0) # gregorian calendar year
    unit_name = models.CharField(max_length=300)

    class Meta:
        ordering = ['id']

class DomainKPISchedule(models.Model):
    kpi = models.ForeignKey('DomainKPI')
    program = models.ForeignKey('domain.Program', null=True)
    target = models.IntegerField()
    result = models.IntegerField()
    quarter = models.IntegerField() # 1-4
    quarter_year = models.IntegerField() # gregorian calendar year
    remark = models.CharField(max_length=1000, blank=True)

class DomainKPIScheduleReference(models.Model):
    schedule = models.ForeignKey('DomainKPISchedule', related_name='schedule')
    project = models.ForeignKey('domain.Project', null=True)
    kpi_schedule = models.ForeignKey('DomainKPISchedule', null=True, related_name='kpi_schedule_source') # NOT CURRENTLY USED
    report_submission = models.ForeignKey('report.ReportSubmission', null=True)
    description = models.CharField(max_length=1000, blank=True)

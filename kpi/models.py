from django.db import models

class DomainKPIType(models.Model):
    of_master_plan = models.ForeignKey('domain.MasterPlan', null=True)
    of_program = models.ForeignKey('domain.Program', null=True)
    name = models.CharField(max_length=300)

class DomainKPI(models.Model):
    ref_no = models.CharField(max_length=100)
    name = models.CharField(max_length=1000)
    abbr_name = models.CharField(max_length=200, default='')
    year = models.CharField(max_length=30, default='')
    unit_name = models.CharField(max_length=300)
    type = models.ForeignKey('DomainKPIType', null=True)
    of_master_plan = models.ForeignKey('domain.MasterPlan', null=True)
    of_plan = models.ForeignKey('domain.Plan', null=True)
    of_program = models.ForeignKey('domain.Program', null=True)

class DomainKPISchedule(models.Model):
    kpi = models.ForeignKey('DomainKPI')
    target = models.IntegerField()
    result = models.IntegerField()
    quarter = models.IntegerField() # 1-4
    quarter_year = models.IntegerField() # gregorian calendar year

class DomainKPIScheduleSource(models.Model):
    schedule = models.ForeignKey('DomainKPISchedule', related_name='schedule')
    from_project = models.ForeignKey('domain.Project', null=True)
    from_kpi_schedule = models.ForeignKey('DomainKPISchedule', null=True, related_name='kpi_schedule_source')
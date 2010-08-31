from django.db import models

class Sector(models.Model):
    ref_no = models.IntegerField()
    name = models.CharField(max_length=500)

class MasterPlan(models.Model):
    ref_no = models.IntegerField()
    name = models.CharField(max_length=500)

class SectorMasterPlan(models.Model):
    sector = models.ForeignKey('Sector')
    master_plan = models.ForeignKey('MasterPlan')

class Plan(models.Model):
    master_plan = models.ForeignKey('MasterPlan')
    ref_no = models.CharField(max_length=100)
    name = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)

class Program(models.Model):
    plan = models.ForeignKey('Plan')
    ref_no = models.CharField(max_length=100)
    contract_no = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=500)
    abbr_name = models.CharField(max_length=200, blank=True)
    manager_name = models.CharField(max_length=300, blank=True)
    description = models.CharField(max_length=1000, blank=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    status = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

class Project(models.Model):
    """
    if plan is present, this project is under the plan's master_plan.
    if program is present, this project is under the program.
    """
    
    plan = models.ForeignKey('Plan', null=True)
    program = models.ForeignKey('Program', null=True)
    ref_no = models.CharField(max_length=100)
    contract_no = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=500)
    abbr_name = models.CharField(max_length=200, null=True)
    description = models.CharField(max_length=1000, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    status = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.UserAccount')

class Activity(models.Model):
    project = models.ForeignKey('Project')
    ref_no = models.CharField(max_length=100)
    name = models.CharField(max_length=500)
    description = models.CharField(max_length=1000, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.UserAccount')
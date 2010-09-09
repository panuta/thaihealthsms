from django.contrib.auth.models import User, Group
from django.db import models

class UserAccount(models.Model):
    user = models.ForeignKey(User, unique=True)
    firstname = models.CharField(max_length=300)
    lastname = models.CharField(max_length=300)
    random_password = models.CharField(max_length=30, null=True)

class UserRoleResponsibility(models.Model):
    user = models.ForeignKey('UserAccount')
    role = models.ForeignKey(Group)
    sectors = models.ManyToManyField('domain.Sector', null=True)
    programs = models.ManyToManyField('domain.Program', null=True)

class RoleDetails(models.Model):
    NO_LEVEL = 0
    SECTOR_LEVEL = 1 # e.g. Sector Manager, Sector Manager Assistant
    PROGRAM_LEVEL = 2 # e.g. Program Manager, Program Manager Assistant
    
    role = models.OneToOneField(Group)
    name = models.CharField(max_length=512)
    level = models.IntegerField(default=SECTOR_LEVEL) # Use to determine usre's role either in sector layer or program layer

class AdminPermission(models.Model):
    permission = models.CharField(max_length=300)

class UserPermission(models.Model):
    role = models.ForeignKey(Group)
    permission = models.CharField(max_length=300)
    only_responsible = models.BooleanField(default=True)

class PermissionName(models.Model):
    permission = models.CharField(max_length=300, unique=True)
    name = models.CharField(max_length=1000)
    description = models.CharField(max_length=1000, default='')
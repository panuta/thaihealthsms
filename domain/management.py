# -*- encoding: utf-8 -*-

# Signal after syncdb
from datetime import datetime, date, timedelta

from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

from accounts.models import *
from domain.models import *
from budget.models import *
from kpi.models import *

import calendar
import random

def after_syncdb(sender, **kwargs):

    """
    THIS IS REAL PRODUCTION CODE
    """
    
    # Site Information ###############
    Site.objects.all().update(domain=settings.WEBSITE_ADDRESS, name=settings.WEBSITE_ADDRESS)
    
    # User Roles ##################
    sector_manager_role, created = Group.objects.get_or_create(name='sector_manager')
    RoleDetails.objects.get_or_create(role=sector_manager_role, name='ผู้อำนวยการสำนัก', level=RoleDetails.SECTOR_LEVEL)
    
    sector_manager_assistant_role, created = Group.objects.get_or_create(name='sector_manager_assistant')
    RoleDetails.objects.get_or_create(role=sector_manager_assistant_role, name='ผู้ช่วยผู้อำนวยการสำนัก', level=RoleDetails.SECTOR_LEVEL)
    
    sector_specialist_role, created = Group.objects.get_or_create(name='sector_specialist')
    RoleDetails.objects.get_or_create(role=sector_specialist_role, name='นักวิชาการบริหารแผนงาน', level=RoleDetails.SECTOR_LEVEL)
    
    program_manager_role, created = Group.objects.get_or_create(name='program_manager')
    RoleDetails.objects.get_or_create(role=program_manager_role, name='ผู้จัดการแผนงาน', level=RoleDetails.PROGRAM_LEVEL)
    
    program_manager_assistant_role, created = Group.objects.get_or_create(name='program_manager_assistant')
    RoleDetails.objects.get_or_create(role=program_manager_assistant_role, name='ผู้ช่วยผู้จัดการแผนงาน', level=RoleDetails.PROGRAM_LEVEL)
    
    # Administrator ##################
    admins = settings.ADMINS
    
    from django.core.mail import send_mail
    
    for admin in admins:
        try:
            User.objects.get(username=admin[0])
            
        except User.DoesNotExist:
            #random_password = User.objects.make_random_password()
            random_password = '1q2w3e4r'
            admin_user = User.objects.create_user(admin[0], admin[1], random_password)
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.save()
            
            #email_render_dict = {'username':admin[0], 'password':random_password, 'settings':settings, 'site_name':settings.WEBSITE_ADDRESS}
            #email_subject = render_to_string('email/create_admin_subject.txt', email_render_dict)
            #email_message = render_to_string('email/create_admin_message.txt', email_render_dict)
            
            #send_mail(email_subject, email_message, settings.SYSTEM_NOREPLY_EMAIL, [admin[1]])
            
            admin_account = admin_user.get_profile()
            admin_account.firstname = admin[0]
            admin_account.lastname = ''
            admin_account.save()
    
    # Sector ##################
    sector1, created = Sector.objects.get_or_create(ref_no=1, name='สำนักสนับสนุนการสร้างสุขภาวะและลดปัจจัยเสี่ยงหลัก')
    sector2, created = Sector.objects.get_or_create(ref_no=2, name='สำนักสนับสนุนการสร้างสุขภาวะและลดปัจจัยเสี่ยงรอง')
    sector3, created = Sector.objects.get_or_create(ref_no=3, name='สำนักสนับสนุนการสร้างสุขภาวะในพื้นที่ชุมชน')
    sector4, created = Sector.objects.get_or_create(ref_no=4, name='สำนักสนับสนุนการเรียนรู้และสุขภาวะองค์กร')
    sector5, created = Sector.objects.get_or_create(ref_no=5, name='สำนักรณรงค์สื่อสารสาธารณะและสังคม')
    sector6, created = Sector.objects.get_or_create(ref_no=6, name='สำนักสนับสนุนโครงการเปิดรับทั่วไป')
    sector7, created = Sector.objects.get_or_create(ref_no=7, name='สำนักสนับสนุนการพัฒนาระบบสุขภาพและบริการสุขภาพ')
    sector8, created = Sector.objects.get_or_create(ref_no=8, name='สำนักพัฒนายุทธศาสตร์ แผนและสมรรถนะ')
    sector9, created = Sector.objects.get_or_create(ref_no=9, name='สำนักพัฒนาวิชาการ')
    
    # Master Plan ##################
    master_plan1, created  = MasterPlan.objects.get_or_create(ref_no=1, name="แผนควบคุมการบริโภคยาสูบ")
    master_plan2, created  = MasterPlan.objects.get_or_create(ref_no=2, name="แผนควบคุมการบริโภคเครื่องดื่มแอลกอฮอล์")
    master_plan3, created  = MasterPlan.objects.get_or_create(ref_no=3, name="แผนสนับสนุนการป้องกันอุบัตเหตุทางถนนและอุบัติภัย")
    master_plan4, created  = MasterPlan.objects.get_or_create(ref_no=4, name="แผนควบคุมปัจจัยเสี่ยงทางสุขภาพ")
    master_plan5, created  = MasterPlan.objects.get_or_create(ref_no=5, name="แผนสุขภาวะประชากรกลุ่มเฉพาะ")
    master_plan6, created  = MasterPlan.objects.get_or_create(ref_no=6, name="แผนสุขภาวะชุมชน")
    master_plan7, created  = MasterPlan.objects.get_or_create(ref_no=7, name="แผนสุขภาวะเด็ก เยาวชน และครอบครัว")
    master_plan8, created  = MasterPlan.objects.get_or_create(ref_no=8, name="แผนสร้างเสริมสุขภาวะในองค์กร")
    master_plan9, created  = MasterPlan.objects.get_or_create(ref_no=9, name="แผนส่งเสริมการออกกำลังกายและกีฬาเพื่อสุขภาพ")
    master_plan10, created  = MasterPlan.objects.get_or_create(ref_no=10, name="แผนสื่อสารการตลาดเพื่อสังคม")
    master_plan11, created  = MasterPlan.objects.get_or_create(ref_no=11, name="แผนสนับสนุนโครงสร้างทั่วไปและนวัตกรรม")
    master_plan12, created  = MasterPlan.objects.get_or_create(ref_no=12, name="แผนสนับสนุนการสร้างเสริมสุขภาพผ่านระบบบริการสุขภาพ")
    master_plan13, created  = MasterPlan.objects.get_or_create(ref_no=13, name="แผนพัฒนาระบบและกลไกสนับสนุนเพื่อการสร้างเสริมสุขภาพ")
    
    SectorMasterPlan.objects.get_or_create(sector=sector1, master_plan=master_plan1)
    SectorMasterPlan.objects.get_or_create(sector=sector1, master_plan=master_plan2)
    SectorMasterPlan.objects.get_or_create(sector=sector1, master_plan=master_plan3)
    SectorMasterPlan.objects.get_or_create(sector=sector2, master_plan=master_plan4)
    SectorMasterPlan.objects.get_or_create(sector=sector2, master_plan=master_plan5)
    SectorMasterPlan.objects.get_or_create(sector=sector3, master_plan=master_plan6)
    SectorMasterPlan.objects.get_or_create(sector=sector4, master_plan=master_plan7)
    SectorMasterPlan.objects.get_or_create(sector=sector4, master_plan=master_plan8)
    SectorMasterPlan.objects.get_or_create(sector=sector5, master_plan=master_plan9)
    SectorMasterPlan.objects.get_or_create(sector=sector5, master_plan=master_plan10)
    SectorMasterPlan.objects.get_or_create(sector=sector6, master_plan=master_plan11)
    SectorMasterPlan.objects.get_or_create(sector=sector7, master_plan=master_plan12)
    SectorMasterPlan.objects.get_or_create(sector=sector7, master_plan=master_plan13)
    SectorMasterPlan.objects.get_or_create(sector=sector8, master_plan=master_plan13)
    SectorMasterPlan.objects.get_or_create(sector=sector9, master_plan=master_plan13)
    
    #
    # Permission ##################
    #
    
    PermissionName.objects.get_or_create(permission='master_plan manage', name='จัดการแผนหลัก')
    
    # KPI
    PermissionName.objects.get_or_create(permission='program kpi edit target', name='แก้ไขตัวเลขคาดการณ์ตัวชี้วัด')
    PermissionName.objects.get_or_create(permission='program kpi edit result', name='แก้ไขตัวเลขผลที่เกิดของตัวชี้วัด')
    
    # BUDGET
    PermissionName.objects.get_or_create(permission='program budget edit grant', name='แก้ไขตัวเลขคาดการณ์การเบิกจ่าย')
    PermissionName.objects.get_or_create(permission='program budget edit claim', name='แก้ไขตัวเลขเบิกจ่ายจริง')
    
    # REPORT
    PermissionName.objects.get_or_create(permission='report submission edit', name='แก้ไขรายงาน')
    PermissionName.objects.get_or_create(permission='report submission submit', name='ส่งรายงาน')
    PermissionName.objects.get_or_create(permission='report submission approve', name='รับรองรายงาน')
    
    AdminPermission.objects.get_or_create(permission='master_plan manage')
    
    
    
    # FOR SECTOR MANAGER
    UserPermission.objects.get_or_create(permission='program kpi edit target', role=sector_manager_role, only_responsible=True)
    UserPermission.objects.get_or_create(permission='program kpi edit result', role=sector_manager_role, only_responsible=True)
    
    UserPermission.objects.get_or_create(permission='program budget edit grant', role=sector_manager_role, only_responsible=True)
    UserPermission.objects.get_or_create(permission='program budget edit claim', role=sector_manager_role, only_responsible=True)
    
    UserPermission.objects.get_or_create(permission='master_plan manage', role=sector_manager_role, only_responsible=True)
    UserPermission.objects.get_or_create(permission='report submission approve', role=sector_manager_role, only_responsible=True)
    
    # FOR SECTOR MANAGER ASSISTANT
    UserPermission.objects.get_or_create(permission='program kpi edit target', role=sector_manager_assistant_role, only_responsible=True)
    UserPermission.objects.get_or_create(permission='program kpi edit result', role=sector_manager_assistant_role, only_responsible=True)
    
    UserPermission.objects.get_or_create(permission='program budget edit grant', role=sector_manager_assistant_role, only_responsible=True)
    UserPermission.objects.get_or_create(permission='program budget edit claim', role=sector_manager_assistant_role, only_responsible=True)
    
    UserPermission.objects.get_or_create(permission='master_plan manage', role=sector_manager_assistant_role, only_responsible=True)
    UserPermission.objects.get_or_create(permission='report submission approve', role=sector_manager_assistant_role, only_responsible=True)
    
    # FOR SECTOR SPECIALIST
    UserPermission.objects.get_or_create(permission='program kpi edit target', role=sector_specialist_role, only_responsible=True)
    UserPermission.objects.get_or_create(permission='program kpi edit result', role=sector_specialist_role, only_responsible=True)
    
    UserPermission.objects.get_or_create(permission='program budget edit target', role=sector_specialist_role, only_responsible=True)
    UserPermission.objects.get_or_create(permission='program budget edit result', role=sector_specialist_role, only_responsible=True)
    
    UserPermission.objects.get_or_create(permission='master_plan manage', role=sector_specialist_role, only_responsible=True)
    UserPermission.objects.get_or_create(permission='report submission approve', role=sector_specialist_role, only_responsible=True)
    
    # FOR PROGRAM MANAGER
    UserPermission.objects.get_or_create(permission='report submission edit', role=program_manager_role, only_responsible=True)
    UserPermission.objects.get_or_create(permission='report submission submit', role=program_manager_role, only_responsible=True)
    
    # FOR PROGRAM MANAGER ASSISTANT
    UserPermission.objects.get_or_create(permission='report submission edit', role=program_manager_assistant_role, only_responsible=True)
    UserPermission.objects.get_or_create(permission='report submission submit', role=program_manager_assistant_role, only_responsible=True)
    
    """
    END HERE
    """

    """
    BELOW CODE IS FOR PROTOTYPE-PURPOSE ONLY
    """
    
    plan1, created = Plan.objects.get_or_create(master_plan=master_plan1, ref_no="101", name="Sample Plan 1")
    plan2, created = Plan.objects.get_or_create(master_plan=master_plan1, ref_no="102", name="Sample Plan 2")
    
    program101_01, created = Program.objects.get_or_create(plan=plan1, ref_no="101-01", name="Sample Program 1")
    program101_02, created = Program.objects.get_or_create(plan=plan1, ref_no="101-02", name="Sample Program 2")
    program102_01, created = Program.objects.get_or_create(plan=plan2, ref_no="102-01", name="Sample Program 3")
    program102_02, created = Program.objects.get_or_create(plan=plan2, ref_no="102-02", name="Sample Program 4")
    
    # INITIAL USER LIST
    try:
        sector_manager_user = User.objects.get(username='sector')
        sector_manager_user_account = sector_manager_user.get_profile()
    except User.DoesNotExist:
        sector_manager_user = User.objects.create_user('sector', 'panuta@gmail.com', 'password')
        sector_manager_user.save()
        
        sector_manager_user_account = sector_manager_user.get_profile()
        sector_manager_user_account.firstname = 'Sector'
        sector_manager_user_account.lastname = 'Manager'
        sector_manager_user_account.save()
        
        sector_manager_user.groups.add(sector_manager_role)
        responsibility = UserRoleResponsibility.objects.create(user=sector_manager_user_account, role=sector_manager_role)
        responsibility.sectors.add(sector1)
    
    try:
        User.objects.get(username='assistant')
    except User.DoesNotExist:
        user = User.objects.create_user('assistant', 'panuta@gmail.com', 'password')
        user.save()
        
        user_account = user.get_profile()
        user_account.firstname = 'Manager'
        user_account.lastname = 'Assistant'
        user_account.save()
        
        user.groups.add(sector_manager_assistant_role)
        responsibility = UserRoleResponsibility.objects.create(user=user_account, role=sector_manager_assistant_role)
        responsibility.sectors.add(sector1)
        responsibility.programs.add(program101_01)
        responsibility.programs.add(program102_01)
    
    try:
        User.objects.get(username='program')
    except User.DoesNotExist:
        user = User.objects.create_user('program', 'panuta@gmail.com', 'password')
        user.save()
        
        user_account = user.get_profile()
        user_account.firstname = 'Project'
        user_account.lastname = 'Manager'
        user_account.save()
        
        user.groups.add(program_manager_role)
        responsibility = UserRoleResponsibility.objects.create(user=user_account, role=program_manager_role)
        responsibility.programs.add(program101_01)
    
    try:
        User.objects.get(username='program_assistant')
    except User.DoesNotExist:
        user = User.objects.create_user('program_assistant', 'panuta@gmail.com', 'password')
        user.save()
        
        user_account = user.get_profile()
        user_account.firstname = 'Project'
        user_account.lastname = 'Assistant'
        user_account.save()
        
        user.groups.add(program_manager_assistant_role)
        responsibility = UserRoleResponsibility.objects.create(user=user_account, role=program_manager_assistant_role)
        responsibility.programs.add(program101_01)
    
    
    
    project_001, created = Project.objects.get_or_create(program=program101_01, ref_no='001', contract_no='REF001', name='Project 001', abbr_name='PRJ001', created_by=sector_manager_user_account)
    
from django.db.models.signals import post_syncdb
post_syncdb.connect(after_syncdb, dispatch_uid="domain.management")



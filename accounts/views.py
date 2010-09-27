# -*- encoding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.utils import simplejson

from accounts.forms import *
from accounts.models import *

from domain.models import SectorMasterPlan, Plan, Program
from report.models import ReportSubmission, SUBMITTED_ACTIVITY

from comment import functions as comment_functions
from report import functions as report_functions

from helper import permission
from helper.shortcuts import render_response

# NOTE: Use this method to create UserAccount object after django.auth.User object is created
def user_post_save_callback(sender, instance, created, *args, **kwargs):
    if created: UserAccount.objects.create(user=instance)

from django.contrib.auth.views import login
from django.contrib.auth import REDIRECT_FIELD_NAME

# NOTE: Determine if the user has logged in for the first time
def hooked_login(request, template_name='registration/login.html', redirect_field_name=REDIRECT_FIELD_NAME):
    response = login(request, template_name, redirect_field_name)

    if request.user.is_authenticated():
        if not request.user.is_superuser and request.user.get_profile().random_password:
            request.session['first_time_login'] = True
            return redirect('/accounts/first_time/')
        else:
            request.session['first_time_login'] = False
        
    return response

@login_required
def view_first_time_login(request):
    if request.user.is_authenticated():
        if request.user.is_superuser or (not request.user.is_superuser and not request.user.get_profile().random_password):
            return redirect('/')
        
    if request.method == 'POST':
        form = ChangeFirstTimePasswordForm(request.POST)
        if form.is_valid():
            password1 = form.cleaned_data['password1']
            password2 =form.cleaned_data['password2']
            
            user = request.user
            user.set_password(password1)
            user.save()
            
            user_account = user.get_profile()
            user_account.random_password = ''
            user_account.save()
            
            next = request.POST.get('next')
            if not next: next = '/'
            return redirect(next)
        
    else:
        form = ChangeFirstTimePasswordForm()
        
    next = request.GET.get('next', '')
    return render_response(request, "registration/first_time_login.html", {'form':form, 'next':next})

#
# HOMEPAGE
#

def view_user_homepage(request):
    if not request.user.is_authenticated():
        return redirect('/accounts/login/')
    else:
        roles = request.user.groups.all()
        if roles:
            responsibilities = UserRoleResponsibility.objects.filter(user=request.user.get_profile())
            
            if roles[0].name == 'sector_manager':
                return _view_sector_manager_homepage(request, roles, responsibilities)
            
            elif roles[0].name == 'sector_manager_assistant':
                return _view_sector_manager_assistant_homepage(request, roles, responsibilities)
            
            elif roles[0].name == 'sector_specialist':
                return _view_sector_manager_assistant_homepage(request, roles, responsibilities)
            
            elif roles[0].name == 'program_manager':
                return _view_program_manager_homepage(request, roles, responsibilities)
            
            elif roles[0].name == 'program_manager_assistant':
                return _view_program_manager_assistant_homepage(request, roles, responsibilities)
            
            else:
                return _view_general_homepage(request, roles, responsibilities)
            
        if request.user.is_superuser:
            return redirect('view_administration')
        
        raise Http404

def _view_sector_manager_homepage(request, roles, responsibilities):
    return redirect('view_sector_overview', (responsibilities[0].sectors.all()[0].id))

def _view_sector_manager_assistant_homepage(request, roles, responsibilities):
    primary_role = roles[0]
    
    primary_sector = responsibilities[0].sectors.all()[0]
    primary_master_plans = [smp.master_plan for smp in SectorMasterPlan.objects.filter(sector=responsibilities[0].sectors.all()[0])]
    
    responsible_programs = responsibilities[0].programs.all()
    
    # Report
    for program in responsible_programs:
        program.approving_submissions = ReportSubmission.objects.filter(program=program, report__need_checkup=True, state=SUBMITTED_ACTIVITY)
        (late_report_count, rejected_report_count) = report_functions.get_program_warning_report_count(program)
        program.late_report_count = late_report_count
        program.rejected_report_count = rejected_report_count
    
    return render_response(request, 'page_user/user_sector_assistant_dashboard.html', {'responsibilities':responsibilities, 'roles':roles, 'primary_role':primary_role, 'primary_sector':primary_sector, 'primary_master_plans':primary_master_plans, 'responsible_programs':responsible_programs})

def _view_program_manager_homepage(request, roles, responsibilities):
    return redirect('view_program_overview', (responsibilities[0].programs.all()[0].id))

def _view_program_manager_assistant_homepage(request, roles, responsibilities):
    return redirect('view_program_overview', (responsibilities[0].programs.all()[0].id))

def _view_general_homepage(request, roles, responsibilities):
    return render_response(request, 'page_user/user_dashboard.html', {'responsibilities':responsibilities, 'roles':roles})

#
# INBOX
#

@login_required
def view_user_inbox(request):
    (object_comments, unread_count) = comment_functions.get_user_unread_comments(request.user.get_profile())
    return render_response(request, "page_user/user_inbox.html", {'object_comments':object_comments, 'unread_count':unread_count})

#
# SETTINGS
#

@login_required
def view_user_settings(request):
    if request.method == 'POST':
        if 'profile_button' in request.POST and request.POST.get('profile_button'):
            form_profile = ChangeUserProfileForm(request.POST)
            if form_profile.is_valid():
                firstname = form_profile.cleaned_data['firstname']
                lastname =form_profile.cleaned_data['lastname']
                
                user_account = request.user.get_profile()
                user_account.firstname = firstname
                user_account.lastname = lastname
                user_account.save()
                
                messages.success(request, 'แก้ไขข้อมูลผู้ใช้เรียบร้อย')
                return redirect('view_user_settings')
        else:
            form_profile = ChangeUserProfileForm(initial={'firstname':request.user.get_profile().firstname, 'lastname':request.user.get_profile().lastname})
        
        if 'password_button' in request.POST and request.POST.get('password_button'):
            form_password = ChangeUserPasswordForm(request.POST)
            if form_password.is_valid():
                password1 = form_password.cleaned_data['password1']
                password2 =form_password.cleaned_data['password2']
                
                user = request.user
                user.set_password(password1)
                user.save()
                
                messages.success(request, 'เปลี่ยนรหัสผ่านเรียบร้อย')
                return redirect('view_user_settings')
        else:
            form_password = ChangeUserPasswordForm()
    
    else:
        form_profile = ChangeUserProfileForm(initial={'firstname':request.user.get_profile().firstname, 'lastname':request.user.get_profile().lastname})
        form_password = ChangeUserPasswordForm()
    
    return render_response(request, "page_user/user_settings.html", {'form_profile':form_profile, 'form_password':form_password,})

@login_required
def view_user_responsibility(request):
    
    if not permission.has_roles(request.user, 'sector_manager_assistant,sector_specialist'):
        raise Http404
    
    responsibility = UserRoleResponsibility.objects.filter(user=request.user.get_profile())[0]
    
    primary_role = request.user.groups.all()[0]
    primary_sector = responsibility.sectors.all()[0]
    
    if request.method == 'POST':
        programs = request.POST.getlist('program')
        
        responsibility.programs.clear()
        for program_id in programs:
            program = Program.objects.get(pk=program_id)
            responsibility.programs.add(program)
        
        return redirect('view_user_homepage')
    
    else:
        master_plans = [sector_master_plan.master_plan for sector_master_plan in SectorMasterPlan.objects.filter(sector=primary_sector).order_by('master_plan__ref_no')]
        
        for master_plan in master_plans:
            plans = Plan.objects.filter(master_plan=master_plan)
            
            for plan in plans:
                programs = Program.objects.filter(plan=plan)
                for program in programs: program.responsible = _responsible_this_program(program, responsibility.programs.all())
                plan.programs = programs
            
            master_plan.plans = plans
        
        return render_response(request, "page_user/user_sector_assistant_responsibility.html", {'primary_role':primary_role, 'master_plans':master_plans})

def _responsible_this_program(program, my_programs):
    for my_program in my_programs:
        if my_program.id == program.id:
            return True
    return False
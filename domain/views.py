# -*- encoding: utf-8 -*-
import calendar
from datetime import datetime, date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect

from forms import *
from models import *

from accounts.models import *
from budget.models import *
from comment.models import *
from kpi.models import *
from report.models import *

from helper import utilities, permission
from helper.shortcuts import render_response, render_page_response, access_denied

#
# SECTOR #######################################################################
#

@login_required
def view_organization(request):
    master_plans = MasterPlan.objects.all().order_by('ref_no')
    sectors = Sector.objects.all().order_by('ref_no')
    return render_response(request, 'organization.html', {'sectors':sectors, 'master_plans':master_plans})

@login_required
def view_sector_overview(request, sector_ref_no):
    sector = get_object_or_404(Sector, ref_no=sector_ref_no)
    sector_master_plans = SectorMasterPlan.objects.filter(sector=sector).order_by('master_plan__ref_no')
    master_plans = [sector_master_plan.master_plan for sector_master_plan in sector_master_plans]
    
    return render_page_response(request, 'overview', 'page_sector/sector_overview.html', {'sector':sector, 'master_plans':master_plans})

#
# MASTER PLAN #######################################################################
#

@login_required
def view_master_plan_overview(request, master_plan_ref_no):
    master_plan = get_object_or_404(MasterPlan, ref_no=master_plan_ref_no)
    
    return render_page_response(request, 'overview', 'page_sector/master_plan_overview.html', {'master_plan': master_plan})

@login_required
def view_master_plan_programs(request, master_plan_ref_no):
    master_plan = get_object_or_404(MasterPlan, ref_no=master_plan_ref_no)
    
    # Plans
    plans = Plan.objects.filter(master_plan=master_plan).order_by('ref_no')
    for plan in plans:
        plan.programs = Program.objects.filter(plan=plan).order_by('ref_no')
    
    return render_page_response(request, 'programs', 'page_sector/master_plan_programs.html', {'master_plan': master_plan, 'plans':plans})

#
# MASTER PLAN MANAGEMENT #######################################################################
#

@login_required
def view_master_plan_manage_organization(request, master_plan_ref_no):
    master_plan = get_object_or_404(MasterPlan, ref_no=master_plan_ref_no)
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    current_date = date.today().replace(day=1)
    plans = Plan.objects.filter(master_plan=master_plan).order_by('ref_no')
    
    for plan in plans:
        plan.programs = Program.objects.filter(plan=plan).order_by('ref_no')
        for program in plan.programs:
            program.removable = Project.objects.filter(program=program).count() == 0
    
    return render_page_response(request, 'organization', 'page_sector/manage_master_plan/manage_organization.html', {'master_plan':master_plan, 'plans':plans})

@login_required
def view_master_plan_add_plan(request, master_plan_ref_no):
    master_plan = get_object_or_404(MasterPlan, ref_no=master_plan_ref_no)
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    if request.method == 'POST':
        form = PlanModifyForm(request.POST, master_plan=master_plan)
        if form.is_valid():
            plan = Plan.objects.create(ref_no=form.cleaned_data['ref_no'], name=form.cleaned_data['name'], master_plan=master_plan)
            
            messages.success(request, 'เพิ่มกลุ่มแผนงานเรียบร้อย')
            return redirect('view_master_plan_manage_organization', (master_plan.ref_no))
            
    else:
        form = PlanModifyForm(master_plan=master_plan)
    
    return render_page_response(request, 'organization', 'page_sector/manage_master_plan/manage_organization_modify_plan.html', {'master_plan':master_plan, 'form':form})

@login_required
def view_master_plan_edit_plan(request, plan_id):
    plan = get_object_or_404(Plan, pk=plan_id)
    master_plan = plan.master_plan
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    if request.method == 'POST':
        form = PlanModifyForm(request.POST, master_plan=master_plan)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            plan.ref_no = cleaned_data['ref_no']
            plan.name = cleaned_data['name']
            plan.save()
            
            messages.success(request, 'แก้ไขกลุ่มแผนงานเรียบร้อย')
            return redirect('view_master_plan_manage_organization', (master_plan.ref_no))
    else:
        form = PlanModifyForm(master_plan=master_plan, initial={'plan_id':plan.id, 'ref_no':plan.ref_no, 'name':plan.name})
    
    return render_page_response(request, 'organization', 'page_sector/manage_master_plan/manage_organization_modify_plan.html', {'master_plan':master_plan, 'plan':plan, 'form':form})

@login_required
def view_master_plan_delete_plan(request, plan_id):
    plan = get_object_or_404(Plan, pk=plan_id)
    master_plan = plan.master_plan
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    if not Program.objects.filter(plan=plan).count():
        plan.delete()
        messages.success(request, 'ลบกลุ่มแผนงานเรียบร้อย')
    else:
        messages.error(request, 'ไม่สามารถลบกลุ่มแผนงานได้ เนื่องจากมีแผนงานที่อยู่ภายใต้')
    
    return redirect('view_master_plan_manage_organization', (master_plan.ref_no))

@login_required
def view_master_plan_add_program(request, master_plan_ref_no):
    master_plan = get_object_or_404(MasterPlan, ref_no=master_plan_ref_no)
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    if Plan.objects.filter(master_plan=master_plan).count() == 0:
        messages.error(request, 'กรุณาสร้างกลุ่มแผนงานก่อนการสร้างแผนงาน')
        return redirect('view_master_plan_manage_organization', (master_plan.ref_no))
    
    if request.method == 'POST':
        form = MasterPlanProgramForm(request.POST, master_plan=master_plan)
        if form.is_valid():
            program = Program.objects.create(
                plan=form.cleaned_data['plan'],
                ref_no=form.cleaned_data['ref_no'],
                name=form.cleaned_data['name'],
                abbr_name=form.cleaned_data['abbr_name'],
                manager_name=form.cleaned_data['manager_name'],
                start_date=form.cleaned_data['start_date'],
                end_date=form.cleaned_data['end_date'],
                )
            
            messages.success(request, u'เพิ่มแผนงานเรียบร้อย')
            return redirect('view_master_plan_manage_organization', (master_plan.ref_no))
        
    else:
        form = MasterPlanProgramForm(master_plan=master_plan)
    
    return render_page_response(request, 'organization', 'page_sector/manage_master_plan/manage_organization_modify_program.html', {'master_plan':master_plan, 'form':form})

@login_required
def view_master_plan_edit_program(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    master_plan = program.plan.master_plan
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    if request.method == 'POST':
        form = MasterPlanProgramForm(request.POST, master_plan=master_plan)
        if form.is_valid():
            program.plan = form.cleaned_data['plan']
            program.ref_no = form.cleaned_data['ref_no']
            program.name = form.cleaned_data['name']
            program.abbr_name = form.cleaned_data['abbr_name']
            program.manager_name = form.cleaned_data['manager_name']
            program.start_date = form.cleaned_data['start_date']
            program.end_date = form.cleaned_data['end_date']
            program.save()
            
            messages.success(request, u'แก้ไขแผนงานเรียบร้อย')
            return redirect('view_master_plan_manage_organization', (master_plan.ref_no))
        
    else:
        form = MasterPlanProgramForm(master_plan=master_plan, initial={'program_id':program.id, 'plan':program.plan.id, 'ref_no':program.ref_no, 'name':program.name, 'abbr_name':program.abbr_name, 'description':program.description, 'start_date':program.start_date, 'end_date':program.end_date, 'manager_name':program.manager_name})
    
    return render_page_response(request, 'organization', 'page_sector/manage_master_plan/manage_organization_modify_program.html', {'master_plan':master_plan, 'program':program, 'form':form})

@login_required
def view_master_plan_delete_program(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    master_plan = program.plan.master_plan

    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    removable = True
    
    if Project.objects.filter(program=program).count():
        messages.error(request, u'ไม่สามารถลบแผนงานได้ เนื่องจากยังมีโครงการที่อยู่ภายใต้แผนงานนี้')
        removable = False
    
    if Report.objects.filter(program=program).count():
        messages.error(request, u'ไม่สามารถลบแผนงานได้ เนื่องจากยังมีรายงานที่แผนงานนี้สร้างขึ้น')
        removable = False
    
    if ReportSubmission.objects.filter(program=program).exclude(state=NO_ACTIVITY).count():
        messages.error(request, u'ไม่สามารถลบแผนงานได้ เนื่องจากยังมีรายงานที่แผนงานเขียนหรือส่งไปแล้ว')
        removable = False
    
    if removable:
        # REMOVE REPORT
        ReportAssignment.objects.filter(program=program).delete()
        
        # REMOVE BUDGET
        BudgetScheduleRevision.objects.filter(schedule__program=program).delete()
        schedules = BudgetSchedule.objects.filter(program=program)
        
        schedule_ids = [schedule.id for schedule in schedules]
        
        comments = Comment.objects.filter(object_name='budget', object_id__in=schedule_ids)
        comment_replies = CommentReply.objects.filter(comment__in=comments)
        
        UnreadComment.objects.filter(comment__in=comments).delete()
        UnreadCommentReply.objects.filter(reply__in=comment_replies).delete()
        
        comment_replies.delete()
        comments.delete()
        
        schedules.delete()
        
        # REMOVE KPI
        DomainKPICategory.objects.filter(program=program).delete()
        kpis = DomainKPI.objects.filter(program=program)
        DomainKPISchedule.objects.filter(kpi__in=kpis).delete()
        
        kpis.delete()
        
        # REMOVE PROGRAM
        program.delete()
        messages.success(request, u'ลบแผนงานเรียบร้อย')
    
    return redirect('view_master_plan_manage_organization', (master_plan.ref_no))

#
# PROGRAM #######################################################################
#

@login_required
def view_program_overview(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    
    return render_page_response(request, 'overview', 'page_program/program_overview.html', {'program':program, })

@login_required
def view_program_projects(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    projects = Project.objects.filter(program=program).order_by('ref_no')
    return render_page_response(request, 'projects', 'page_program/program_projects.html', {'program':program, 'projects':projects})

@login_required
def view_program_add_project(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    
    if request.method == 'POST':
        form = ProjectModifyForm(request.POST)
        if form.is_valid():
            project = Project.objects.create(
                program=program,
                ref_no=form.cleaned_data['ref_no'],
                contract_no=form.cleaned_data['contract_no'],
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                start_date=form.cleaned_data['start_date'],
                end_date=form.cleaned_data['end_date'],
                created_by=request.user.get_profile()
            )
            
            messages.success(request, u'เพิ่มโครงการเรียบร้อย')
            return redirect('view_program_projects', (program.id))
        
    else:
        form = ProjectModifyForm(initial={'program_id':program.id})
    
    return render_page_response(request, 'projects', 'page_program/program_projects_modify_project.html', {'program':program, 'form':form})

@login_required
def view_program_edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    program = project.program
    
    if request.method == 'POST':
        form = ProjectModifyForm(request.POST)
        if form.is_valid():
            project.ref_no = form.cleaned_data.get('ref_no')
            project.contract_no = form.cleaned_data.get('contract_no')
            project.name = form.cleaned_data.get('name')
            project.description = form.cleaned_data.get('description')
            project.start_date = form.cleaned_data.get('start_date')
            project.end_date = form.cleaned_data.get('end_date')
            project.save()
            
            messages.success(request, u'แก้ไขโครงการเรียบร้อย')
            return redirect('view_program_projects', (program.id))
        
    else:
        form = ProjectModifyForm(initial={'program_id':program.id, 'project_id':project.id, 'ref_no':project.ref_no, 'contract_no':project.contract_no, 'name':project.name, 'description':project.description, 'start_date':project.start_date, 'end_date':project.end_date})
    
    project.removable = Activity.objects.filter(project=project).count() == 0
    return render_page_response(request, 'projects', 'page_program/program_projects_modify_project.html', {'program':program, 'form':form, 'project':project})

#
# PROJECT #######################################################################
#

@login_required
def view_project_overview(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    current_date = date.today()
    
    current_activities = Activity.objects.filter(project=project, start_date__lte=current_date, end_date__gte=current_date)
    return render_page_response(request, 'overview', 'page_program/project_overview.html', {'project':project, 'current_activities':current_activities})

@login_required
def view_project_edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    program = project.program
    
    if request.method == 'POST':
        form = ProjectModifyForm(request.POST)
        if form.is_valid():
            project.ref_no = form.cleaned_data.get('ref_no')
            project.contract_no = form.cleaned_data.get('contract_no')
            project.name = form.cleaned_data.get('name')
            project.description = form.cleaned_data.get('description')
            project.start_date = form.cleaned_data.get('start_date')
            project.end_date = form.cleaned_data.get('end_date')
            project.save()
            
            messages.success(request, u'แก้ไขโครงการเรียบร้อย')
            return redirect('view_project_overview', (project.id))
        
    else:
        form = ProjectModifyForm(initial={'program_id':program.id, 'project_id':project.id, 'ref_no':project.ref_no, 'contract_no':project.contract_no, 'name':project.name, 'description':project.description, 'start_date':project.start_date, 'end_date':project.end_date})
    
    project.removable = Activity.objects.filter(project=project).count() == 0
    return render_page_response(request, '', 'page_program/project_edit_project.html', {'project':project, 'form':form})

@login_required
def view_project_delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    program = project.program
    
    if not Activity.objects.filter(project=project).count():
        project.delete()
        messages.success(request, u'ลบโครงการเรียบร้อย')
    else:
        messages.error(request, 'ไม่สามารถลบโครงการที่มีกิจกรรมอยู่ได้')
    
    return redirect('view_program_projects', (program.id))

@login_required
def view_project_activities(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    activities = Activity.objects.filter(project=project).order_by('-start_date')
    return render_page_response(request, 'activities', 'page_program/project_activities.html', {'project':project, 'activities':activities})

@login_required
def view_project_add_activity(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    
    if request.method == 'POST':
        form = ActivityModifyForm(request.POST)
        if form.is_valid():
            activity = Activity.objects.create(project=project,
                name=form.cleaned_data['name'],
                start_date=form.cleaned_data['start_date'],
                end_date=form.cleaned_data['end_date'],
                description=form.cleaned_data['description'],
                location=form.cleaned_data['location'],
                result_goal=form.cleaned_data['result_goal'],
                result_real=form.cleaned_data['result_real'],
                created_by=request.user.get_profile(),
                )
            
            messages.success(request, u'เพิ่มกิจกรรมเรียบร้อย')
            return redirect('view_project_activities', (project.id))

    else:
        form = ActivityModifyForm()
    
    return render_page_response(request, 'activities', 'page_program/project_activities_modify_activity.html', {'project':project, 'form':form})

@login_required
def view_project_edit_activity(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    project = activity.project
    
    if request.method == 'POST':
        form = ActivityModifyForm(request.POST)
        if form.is_valid():
            activity = Activity.objects.create(project=project,
                name=form.cleaned_data['name'],
                start_date=form.cleaned_data['start_date'],
                end_date=form.cleaned_data['end_date'],
                description=form.cleaned_data['description'],
                location=form.cleaned_data['location'],
                result_goal=form.cleaned_data['result_goal'],
                result_real=form.cleaned_data['result_real'],
                created_by=request.user.get_profile(),
                )
            
            messages.success(request, u'เพิ่มกิจกรรมเรียบร้อย')
            return redirect('view_project_activities', (project.id))

    else:
        form = ActivityModifyForm(initial=activity.__dict__)
    
    return render_page_response(request, 'activities', 'page_program/project_activities_modify_activity.html', {'project':project, 'form':form, 'activity':activity})

#
# ACTIVITY #######################################################################
#

@login_required
def view_activity_overview(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    return render_page_response(request, 'overview', 'page_program/activity_overview.html', {'activity':activity, })

@login_required
def view_activity_edit_activity(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    
    if request.method == 'POST':
        form = ActivityModifyForm(request.POST)
        if form.is_valid():
            activity = Activity.objects.create(project=project,
                name=form.cleaned_data['name'],
                start_date=form.cleaned_data['start_date'],
                end_date=form.cleaned_data['end_date'],
                description=form.cleaned_data['description'],
                location=form.cleaned_data['location'],
                result_goal=form.cleaned_data['result_goal'],
                result_real=form.cleaned_data['result_real'],
                created_by=request.user.get_profile(),
                )
            
            messages.success(request, u'เพิ่มกิจกรรมเรียบร้อย')
            return redirect('view_project_activities', (project.id))

    else:
        form = ActivityModifyForm(initial=activity.__dict__)
    
    return render_page_response(request, '', 'page_program/activity_edit_activity.html', {'activity':activity, 'form':form})

@login_required
def view_activity_delete_activity(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    project = activity.project
    
    activity.delete()
    messages.success(request, u'ลบโครงการเรียบร้อย')
    
    return redirect('view_project_activities', (project.id))
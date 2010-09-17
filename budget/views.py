# -*- encoding: utf-8 -*-

from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from budget import functions as budget_functions
from report import functions as report_functions
from models import *

from budget.models import BudgetSchedule
from domain.models import Sector, MasterPlan, SectorMasterPlan, Plan, Program
from report.models import ReportAssignment, ReportSubmission

from helper import utilities, permission
from helper.shortcuts import render_page_response, access_denied

#
# SECTOR #######################################################################
#

@login_required
def view_sector_budget(request, sector_ref_no):
    sector = get_object_or_404(Sector, ref_no=sector_ref_no)
    sector_master_plans = SectorMasterPlan.objects.filter(sector=sector)
    master_plans = []
    for sm in sector_master_plans:
        master_plans.append(sm.master_plan)
    quarter_year = utilities.master_plan_current_year_number()
    ctx = {'sector': sector, 'master_plans': master_plans, 'quarter_year': quarter_year}
    return render_page_response(request, 'budget', 'page_sector/sector_budget.html', ctx)

#
# MASTER PLAN #######################################################################
#

@login_required
def view_master_plan_budget(request, master_plan_ref_no):
    master_plan = get_object_or_404(MasterPlan, ref_no=master_plan_ref_no)
    plans = Plan.objects.filter(master_plan=master_plan).order_by('ref_no')
    
    current_year = date.today().year
    has_programs = False
    
    for plan in plans:
        programs = Program.objects.filter(plan=plan).order_by('ref_no')
        
        for program in programs:
            quarters = {1:{'grant':0,'claim':0}, 2:{'grant':0,'claim':0}, 3:{'grant':0,'claim':0}, 4:{'grant':0,'claim':0}}
            for schedule in BudgetSchedule.objects.filter(program=program, schedule_on__year=current_year):
                quarter_number = utilities.find_quarter_number(schedule.schedule_on)
                quarters[quarter_number]['grant'] = quarters[quarter_number]['grant'] + schedule.grant_budget
                quarters[quarter_number]['claim'] = quarters[quarter_number]['claim'] + schedule.claim_budget
            
            program.quarters = quarters
        
        if programs: has_programs = True
        plan.programs = programs
    
    return render_page_response(request, 'budget', 'page_sector/master_plan_budget.html', {'current_year':current_year, 'master_plan':master_plan, 'plans':plans, 'has_programs':has_programs})

#
# MASTER PLAN MANAGEMENT #######################################################################
#

@login_required
def view_master_plan_manage_program_budget(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    master_plan = program.plan.master_plan
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    budget_schedules = BudgetSchedule.objects.filter(program=program).order_by('-schedule_on')
    
    if request.method == 'POST':
        updating_schedules = list()
        for schedule in request.POST.getlist('schedule'):
            try:
                (schedule_id, grant_budget, schedule_on) = schedule.split(',')
                (schedule_on_year, schedule_on_month, schedule_on_day) = schedule_on.split('-')
                schedule_on = date(int(schedule_on_year), int(schedule_on_month), int(schedule_on_day))
                grant_budget = int(grant_budget)
            except:
                messages.error(request, 'ข้อมูลไม่อยู่ในรูปแบบที่ถูกต้อง กรุณากรอกใหม่อีกครั้ง')
                return redirect('view_master_plan_manage_program_budget', (program.id))
            else:
                create_revision = False
                
                if schedule_id and schedule_id != 'none':
                    schedule = BudgetSchedule.objects.get(pk=schedule_id)
                    
                    if schedule.grant_budget != grant_budget or schedule.schedule_on != schedule_on:
                        create_revision = True
                        
                        schedule.grant_budget = grant_budget
                        schedule.schedule_on = schedule_on
                        schedule.save()
                    
                else:
                    schedule = BudgetSchedule.objects.create(program=program, grant_budget=grant_budget, claim_budget=0, schedule_on=schedule_on)
                    create_revision = True
                
                if create_revision:
                    revision = BudgetScheduleRevision.objects.create(
                        schedule=schedule,
                        grant_budget=schedule.grant_budget,
                        claim_budget=schedule.claim_budget,
                        schedule_on=schedule.schedule_on,
                        revised_by=request.user.get_profile()
                    )
                
                updating_schedules.append(schedule)
            
        # Remove schedule
        for budget_schedule in budget_schedules:
            found = False
            for schedule in updating_schedules:
                if schedule == budget_schedule:
                    found = True
            
            if not found:
                BudgetScheduleRevision.objects.filter(schedule=budget_schedule).delete()
                budget_schedule.delete()
        
        return utilities.redirect_or_back('view_master_plan_manage_organization', (master_plan.ref_no), request)
    
    return render_page_response(request, 'organization', 'page_sector/manage_master_plan/manage_program_budget.html', {'master_plan':master_plan, 'program':program, 'schedules':budget_schedules})

#
# PROGRAM #######################################################################
#

@login_required
def view_program_budget(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    schedules = BudgetSchedule.objects.filter(program=program).order_by('-schedule_on')
    return render_page_response(request, 'budget', 'page_program/program_budget.html', {'program':program, 'schedules':schedules})

#
# BUDGET SCHEDULE #######################################################################
#

@login_required
def view_budget_overview(request, schedule_id):
    schedule = get_object_or_404(BudgetSchedule, pk=schedule_id)
    
    ref_projects = []
    ref_report_submissions = []
    
    for reference in BudgetScheduleReference.objects.filter(schedule=schedule):
        if reference.project:
            ref_projects.append(reference)
        elif reference.report_submission:
            ref_report_submissions.append(reference)
    
    revisions = BudgetScheduleRevision.objects.filter(schedule=schedule).order_by('-revised')
    return render_page_response(request, 'overview', 'page_kpi/budget_overview.html', {'schedule':schedule, 'references':references, 'revisions':revisions})

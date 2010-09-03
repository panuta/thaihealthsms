# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from domain.models import Sector, MasterPlan, Program

from helper.shortcuts import render_response, render_page_response, access_denied

#
# SECTOR #######################################################################
#

@login_required
def view_sector_kpi(request, sector_ref_no):
    sector = get_object_or_404(Sector, ref_no=sector_ref_no)
    return render_page_response(request, 'kpi', 'page_sector/sector_kpi.html', {'sector':sector, })

#
# MASTER PLAN #######################################################################
#

@login_required
def view_master_plan_kpi(request, master_plan_ref_no):
    master_plan = get_object_or_404(MasterPlan, ref_no=master_plan_ref_no)
    return render_page_response(request, 'kpi', 'page_sector/master_plan_kpi.html', {'master_plan':master_plan, })

#
# MASTER PLAN MANAGEMENT #######################################################################
#

@login_required
def view_master_plan_manage_program_kpi(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    master_plan = program.plan.master_plan
    return render_page_response(request, 'organization', 'page_sector/manage_master_plan/manage_program_kpi.html', {'master_plan':master_plan, 'program':program, })

@login_required
def view_master_plan_manage_kpi(request, master_plan_ref_no):
    master_plan = get_object_or_404(MasterPlan, ref_no=master_plan_ref_no)
    return render_page_response(request, 'kpi', 'page_sector/manage_master_plan/manage_kpi.html', {'master_plan':master_plan, })

#
# PROGRAM #######################################################################
#

@login_required
def view_program_kpi(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    
    return render_page_response(request, 'kpi', 'page_program/program_kpi.html', {'program':program, })

#
# KPI SCHEDULE #######################################################################
#

@login_required
def view_kpi_overview(request, schedule_id):
    schedule = get_object_or_404(DomainKPISchedule, pk=schedule_id)
    return render_page_response(request, 'overview', 'page_kpi/kpi_overview.html', {'schedule':schedule, })
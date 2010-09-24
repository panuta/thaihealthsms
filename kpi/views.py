# -*- encoding: utf-8 -*-
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from forms import *
from models import *

from report import functions as report_functions

from domain.models import Sector, MasterPlan, SectorMasterPlan, Program, Project
from report.models import ReportAssignment, ReportSubmission

from helper import utilities, permission
from helper.shortcuts import render_response, render_page_response, access_denied

#
# SECTOR #######################################################################
#

@login_required
def view_sector_kpi(request, sector_ref_no):
    sector = get_object_or_404(Sector, ref_no=sector_ref_no)
    sector_master_plans = SectorMasterPlan.objects.filter(sector=sector)
    master_plans = []
    for sm in sector_master_plans:
        master_plans.append(sm.master_plan)
    quarter_year = utilities.master_plan_current_year_number()
    ctx = {'sector': sector, 'master_plans': master_plans, 'quarter_year': quarter_year}
    return render_page_response(request, 'kpi', 'page_sector/sector_kpi.html', ctx)

#
# MASTER PLAN #######################################################################
#

@login_required
def view_master_plan_kpi(request, master_plan_ref_no):
    master_plan = get_object_or_404(MasterPlan, ref_no=master_plan_ref_no)
    quarter_year = utilities.master_plan_current_year_number()
    ctx = {'master_plan': master_plan, 'quarter_year': quarter_year}
    return render_page_response(request, 'kpi', 'page_sector/master_plan_kpi.html', ctx)

#
# MASTER PLAN MANAGEMENT #######################################################################
#

def view_master_plan_manage_program_kpi(request, program_id, quarter_year):
    program = get_object_or_404(Program, pk=program_id)
    master_plan = program.plan.master_plan
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    if not quarter_year:
        current_quarter_year = utilities.master_plan_current_year()
    else:
        current_quarter_year = int(quarter_year)
    
    kpi_category_choices = []
    for dict in DomainKPI.objects.filter(master_plan=master_plan, year=current_quarter_year).values('category'):
        if dict['category']:
            kpi_category = DomainKPICategory.objects.get(pk=dict['category'])
            kpis = DomainKPI.objects.filter(master_plan=master_plan, year=current_quarter_year, category=kpi_category)
            kpi_category_choices.append({'category':kpi_category, 'kpis':kpis})
    
    kpi_no_category_choices = DomainKPI.objects.filter(master_plan=master_plan, year=current_quarter_year, category=None)
    
    kpi_schedules = DomainKPISchedule.objects.filter(program=program, quarter_year=current_quarter_year)
    
    if request.method == 'POST':
        # 'schedule' - kpi_id , schedule_id , target , quarter - "123,None,100,1"
        schedules = request.POST.getlist('schedule')
        
        updating_schedules = list()
        for schedule in schedules:
            try:
                (kpi_id, schedule_id, target, quarter) = schedule.split(',')
                kpi_id = int(kpi_id)
                target = int(target)
                quarter = int(quarter)
            except:
                messages.error(request, 'ข้อมูลไม่อยู่ในรูปแบบที่ถูกต้อง กรุณากรอกใหม่อีกครั้ง')
                return redirect('view_master_plan_manage_program_kpi', (program.id))
            else:
                kpi = DomainKPI.objects.get(pk=kpi_id)
                
                if schedule_id and schedule_id != 'none':
                    schedule = DomainKPISchedule.objects.get(pk=schedule_id)
                    
                    if schedule.target != target or schedule.quarter_year != current_quarter_year or schedule.quarter != quarter:
                        schedule.target = target
                        schedule.quarter_year = current_quarter_year
                        schedule.quarter = quarter
                        schedule.save()
                    
                else:
                    schedule = DomainKPISchedule.objects.create(kpi=kpi, program=program, target=target, result=0, quarter_year=current_quarter_year, quarter=quarter)
                
            updating_schedules.append(schedule)
        
        # Remove schedule
        for program_schedule in kpi_schedules:
            found = False
            for schedule in updating_schedules:
                if schedule == program_schedule:
                    found = True
                    
            if not found:
                # TODO - Delete Comment
                program_schedule.delete()
        
        messages.success(request, 'แก้ไขแผนผลลัพธ์ของแผนงานเรียบร้อย')
        return utilities.redirect_or_back('view_master_plan_manage_organization', (master_plan.ref_no), request)
    
    # GET SCHEDULE
    
    column_schedules = [[], [], [], []]
    for schedule in kpi_schedules:
        column_schedules[schedule.quarter-1].append(schedule)
    
    max_height = 0
    for i in range(0, 4):
        if max_height < len(column_schedules[i]): max_height = len(column_schedules[i])
    
    row_schedules = []
    for i in range(0, max_height):
        row_schedule = {}
        
        for quarter in range(0, 4):
            try:
                row_schedule[str(quarter+1)] = column_schedules[quarter][i]
            except:
                row_schedule[str(quarter+1)] = ''
        
        row_schedules.append(row_schedule)
    
    return render_page_response(request, 'organization', 'page_sector/manage_master_plan/manage_program_kpi.html', {'master_plan':master_plan, 'program':program, 'row_schedules':row_schedules, 'kpi_no_category_choices':kpi_no_category_choices, 'kpi_category_choices':kpi_category_choices, 'current_quarter_year':current_quarter_year})

# MANAGE KPI

@login_required
def view_master_plan_manage_kpi(request, master_plan_ref_no, kpi_year):
    master_plan = get_object_or_404(MasterPlan, ref_no=master_plan_ref_no)
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    if kpi_year:
        year_number = int(kpi_year)
    else:
        year_number = utilities.master_plan_current_year_number()
    
    kpi_categories = []
    for dict in DomainKPI.objects.filter(master_plan=master_plan, year=year_number).values('category').distinct():
        try:
            kpi_category = DomainKPICategory.objects.get(pk=dict['category'])
        except DomainKPICategory.DoesNotExist:
            pass
        else:
            kpis = DomainKPI.objects.filter(master_plan=master_plan, year=year_number, category=kpi_category).order_by('ref_no')
            
            for kpi in kpis:
                kpi.removable = DomainKPISchedule.objects.filter(kpi=kpi).count() == 0
            
            kpi_category.kpis = kpis
            kpi_categories.append(kpi_category)
    
    print year_number
    no_category_kpis = DomainKPI.objects.filter(master_plan=master_plan, year=year_number, category=None)
    print no_category_kpis
    
    for kpi in no_category_kpis:
        kpi.removable = DomainKPISchedule.objects.filter(kpi=kpi).count() == 0
    
    return render_page_response(request, 'kpi', 'page_sector/manage_master_plan/manage_kpi.html', {'master_plan':master_plan, 'kpi_categories':kpi_categories, 'no_category_kpis':no_category_kpis, 'kpi_year':year_number})

@login_required
def view_master_plan_manage_kpi_add_kpi(request, master_plan_ref_no):
    master_plan = get_object_or_404(MasterPlan, ref_no=master_plan_ref_no)
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    if request.method == 'POST':
        form = DomainKPIModifyForm(request.POST, master_plan=master_plan)
        if form.is_valid():
            kpi = DomainKPI.objects.create(
                master_plan = master_plan,
                ref_no = form.cleaned_data['ref_no'],
                name = form.cleaned_data['name'],
                abbr_name = form.cleaned_data['abbr_name'],
                year = form.cleaned_data['year'] - 543,
                unit_name = form.cleaned_data['unit_name'],
                category = form.cleaned_data['category'],
            )
            
            messages.success(request, 'เพิ่มตัวชี้วัดเรียบร้อย')
            return utilities.redirect_or_back('view_master_plan_manage_kpi', (master_plan.ref_no), request)
            
    else:
        form = DomainKPIModifyForm(master_plan=master_plan)
    
    return render_page_response(request, 'organization', 'page_sector/manage_master_plan/manage_kpi_modify_kpi.html', {'master_plan':master_plan, 'form':form})

@login_required
def view_master_plan_manage_kpi_edit_kpi(request, kpi_id):
    kpi = get_object_or_404(DomainKPI, pk=kpi_id)
    master_plan = kpi.master_plan
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    if request.method == 'POST':
        form = DomainKPIModifyForm(request.POST, master_plan=master_plan)
        if form.is_valid():
            kpi.ref_no = form.cleaned_data['ref_no']
            kpi.name = form.cleaned_data['name']
            kpi.abbr_name = form.cleaned_data['abbr_name']
            kpi.year = form.cleaned_data['year']- 543
            kpi.unit_name = form.cleaned_data['unit_name']
            kpi.category = form.cleaned_data['category']
            kpi.save()
            
            messages.success(request, 'แก้ไขตัวชี้วัดเรียบร้อย')
            return redirect('view_master_plan_manage_kpi', (master_plan.ref_no))
            
    else:
        form = DomainKPIModifyForm(master_plan=master_plan, initial={'ref_no':kpi.ref_no, 'name':kpi.name, 'abbr_name':kpi.abbr_name, 'year':kpi.year+543, 'category':kpi.category, 'unit_name':kpi.unit_name})
    
    return render_page_response(request, 'organization', 'page_sector/manage_master_plan/manage_kpi_modify_kpi.html', {'master_plan':master_plan, 'form':form, 'kpi':kpi})

@login_required
def view_master_plan_manage_kpi_delete_kpi(request, kpi_id):
    kpi = get_object_or_404(DomainKPI, pk=kpi_id)
    master_plan = kpi.master_plan
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    if not DomainKPISchedule.objects.filter(kpi=kpi).count():
        kpi.delete()
        messages.success(request, 'ลบตัวชี้วัดเรียบร้อย')
    else:
        messages.error(request, 'ไม่สามารถลบตัวชี้วัด เนื่องจากยังมีแผนงานที่ผูกอยู่กับตัวชี้วัดนี้')
    
    return redirect('view_master_plan_manage_kpi', (master_plan.ref_no))

# MANAGE KPI CATEGORY

@login_required
def view_master_plan_manage_kpi_category(request, master_plan_ref_no):
    master_plan = get_object_or_404(MasterPlan, ref_no=master_plan_ref_no)
    categories = DomainKPICategory.objects.filter(master_plan=master_plan).order_by('name')
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    for category in categories:
        category.removable = DomainKPI.objects.filter(category=category).count() == 0
    
    return render_page_response(request, 'kpi_category', 'page_sector/manage_master_plan/manage_kpi_category.html', {'master_plan':master_plan, 'categories':categories})

@login_required
def view_master_plan_manage_kpi_add_category(request, master_plan_ref_no):
    master_plan = get_object_or_404(MasterPlan, pk=master_plan_ref_no)
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    if request.method == 'POST':
        form = DomainKPICategoryModifyForm(request.POST)
        if form.is_valid():
            category = DomainKPICategory.objects.create(master_plan=master_plan, name=form.cleaned_data['name'])
            
            messages.success(request, 'เพิ่มประเภทตัวชี้วัดเรียบร้อย')
            return redirect('view_master_plan_manage_kpi_category', (master_plan.ref_no))
            
    else:
        form = DomainKPICategoryModifyForm()
    
    return render_page_response(request, 'kpi_category', 'page_sector/manage_master_plan/manage_kpi_modify_category.html', {'master_plan':master_plan, 'form':form})

@login_required
def view_master_plan_manage_kpi_edit_category(request, kpi_category_id):
    kpi_category = get_object_or_404(DomainKPICategory, pk=kpi_category_id)
    master_plan = kpi_category.master_plan
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    if request.method == 'POST':
        form = DomainKPICategoryModifyForm(request.POST)
        if form.is_valid():
            kpi_category.name = form.cleaned_data['name']
            kpi_category.save()
            
            messages.success(request, 'แก้ไขประเภทตัวชี้วัดเรียบร้อย')
            return redirect('view_master_plan_manage_kpi_category', (master_plan.ref_no))
            
    else:
        form = DomainKPICategoryModifyForm(initial={'name':kpi_category.name})
    
    return render_page_response(request, 'kpi_category', 'page_sector/manage_master_plan/manage_kpi_modify_category.html', {'master_plan':master_plan, 'form':form, 'kpi_category':kpi_category})

@login_required
def view_master_plan_manage_kpi_delete_category(request, kpi_category_id):
    kpi_category = get_object_or_404(DomainKPICategory, pk=kpi_category_id)
    master_plan = kpi_category.master_plan
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    if not DomainKPI.objects.filter(category=kpi_category).count():
        kpi_category.delete()
        messages.success(request, 'ลบประเภทตัวชี้วัดเรียบร้อย')
    else:
        messages.error(request, 'ไม่สามารถลบประเภทตัวชี้วัด เนื่องจากยังมีตัวชี้วัดที่อยู่ในประเภทตัวชี้วัดนี้')
    
    return redirect('view_master_plan_manage_kpi_category', (master_plan.ref_no))

#
# PROGRAM #######################################################################
#

@login_required
def view_program_kpi(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    current_year = date.today().year
    
    years = [dict['kpi__year'] for dict in DomainKPISchedule.objects.filter(program=program).values('kpi__year').distinct()]
    
    categories = []
    category_ids = DomainKPISchedule.objects.filter(program=program).values('kpi__category').distinct()
    
    for category_id in category_ids:
        if category_id['kpi__category']:
            category = DomainKPICategory.objects.get(pk=category_id['kpi__category'])
            kpi_ids = DomainKPISchedule.objects.filter(program=program, kpi__category=category).order_by('kpi__ref_no').values('kpi').distinct()
        else:
            category = DomainKPICategory()
            kpi_ids = DomainKPISchedule.objects.filter(program=program, kpi__category=None).order_by('kpi__ref_no').values('kpi').distinct()
        
        kpis = []
        for kpi_id in kpi_ids:
            kpi = DomainKPI.objects.get(id=kpi_id['kpi'])
            
            schedules = {}
            for i in range(1, 5):
                try:
                    schedules[str(i)] = DomainKPISchedule.objects.get(kpi=kpi, program=program, quarter_year=current_year, quarter=i)
                except:
                    schedules[str(i)] = ''
            
            kpi.schedules = schedules
            kpis.append(kpi)
        
        category.kpis = kpis
        categories.append(category)
    
    return render_page_response(request, 'kpi', 'page_program/program_kpi.html', {'program':program, 'categories':categories, 'years':years, 'current_year':current_year})

#
# KPI SCHEDULE #######################################################################
#

@login_required
def view_kpi_overview(request, schedule_id):
    schedule = get_object_or_404(DomainKPISchedule, pk=schedule_id)
    
    if permission.access_obj(request.user, 'program kpi remark edit', schedule.program):
        if request.method == 'POST':
            form = ModifyKPIRemarkForm(request.POST)
            if form.is_valid():
                schedule.remark = form.cleaned_data['remark']
                schedule.save()
                
                messages.success(request, 'แก้ไขหมายเหตุเรียบร้อย')
                return redirect('view_kpi_overview', (schedule.id))
            
        else:
            form = ModifyKPIRemarkForm(initial={'remark':schedule.remark})
    else:
        form = None
    
    ref_projects = []
    ref_report_submissions = []
    
    for reference in DomainKPIScheduleReference.objects.filter(schedule=schedule):
        if reference.project:
            ref_projects.append(reference)
        elif reference.report_submission:
            ref_report_submissions.append(reference)
    
    return render_page_response(request, 'overview', 'page_kpi/kpi_overview.html', {'schedule':schedule, 'form':form, 'ref_projects':ref_projects, 'ref_report_submissions':ref_report_submissions})

@login_required
def view_kpi_overview_edit_reference(request, schedule_id):
    schedule = get_object_or_404(DomainKPISchedule, pk=schedule_id)
    
    if not permission.access_obj(request.user, 'program kpi reference edit', schedule.program):
        return access_denied(request)
    
    if request.method == 'POST':
        DomainKPIScheduleReference.objects.filter(schedule=schedule).delete()
        
        for form_project in request.POST.getlist('project'):
            try:
                project = Project.objects.get(pk=form_project)
            except Project.DoesNotExist:
                pass
            else:
                (reference, created) = DomainKPIScheduleReference.objects.get_or_create(schedule=schedule, project=project)
                reference.description = request.POST.get('desc_project_%d' % project.id)
                reference.save()
        
        for form_report in request.POST.getlist('report'):
            try:
                report_submission = ReportSubmission.objects.get(pk=form_report)
            except ReportSubmission.DoesNotExist:
                pass
            else:
                (reference, created) = DomainKPIScheduleReference.objects.get_or_create(schedule=schedule, report_submission=report_submission)
                reference.description = request.POST.get('desc_report_%d' % report_submission.id)
                reference.save()
        
        messages.success(request, 'แก้ไขข้อมูลประกอบเรียบร้อย')
        return redirect('view_kpi_overview', schedule.id)
    
    projects = Project.objects.filter(program=schedule.program).order_by('name')
    reports = report_functions.get_reports_for_edit_reference(schedule.program)
    
    for reference in DomainKPIScheduleReference.objects.filter(schedule=schedule):
        if reference.project:
            for project in projects:
                if project.id == reference.project.id:
                    project.has_reference = True
                    project.reference_description = reference.description
        
        elif reference.report_submission:
            for report in reports:
                for submission in report.submissions:
                    if submission.id == reference.report_submission.id:
                        submission.has_reference = True
                        submission.reference_description = reference.description
    
    return render_page_response(request, 'overview', 'page_kpi/kpi_overview_edit_reference.html', {'schedule':schedule, 'projects':projects, 'reports':reports})

# -*- encoding: utf-8 -*-

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from forms import *
from models import *

from domain.models import Sector, MasterPlan, Program

from helper import utilities, permission
from helper.shortcuts import render_response, render_page_response, access_denied

#
# SECTOR #######################################################################
#

@login_required
def view_sector_kpi(request, sector_ref_no):
    sector = get_object_or_404(Sector, ref_no=sector_ref_no)
    
    # TODO
    
    return render_page_response(request, 'kpi', 'page_sector/sector_kpi.html', {'sector':sector, })

#
# MASTER PLAN #######################################################################
#

@login_required
def view_master_plan_kpi(request, master_plan_ref_no):
    master_plan = get_object_or_404(MasterPlan, ref_no=master_plan_ref_no)
    
    # TODO
    
    return render_page_response(request, 'kpi', 'page_sector/master_plan_kpi.html', {'master_plan':master_plan, })

#
# MASTER PLAN MANAGEMENT #######################################################################
#

def view_master_plan_manage_program_kpi(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    master_plan = program.plan.master_plan
    
    if not permission.access_obj(request.user, 'master_plan manage', master_plan):
        return access_denied(request)
    
    kpi_choices = DomainKPI.objects.filter(of_master_plan=master_plan).order_by('ref_no')
    kpi_schedules = DomainKPISchedule.objects.filter(of_program=program).order_by('-quarter_year', '-quarter')
    
    if request.method == 'POST':
        # 'schedule' - kpi_id , schedule_id , target , target_on - "123,None,100,2010-01-01"
        schedules = request.POST.getlist('schedule')
        
        updating_schedules = list()
        for schedule in schedules:
            try:
                (kpi_id, schedule_id, target, quarter_year, quarter_month) = schedule.split(',')
                target = int(target)
            except:
                set_message(request, u"ข้อมูลไม่อยู่ในรูปแบบที่ถูกต้อง กรุณากรอกใหม่อีกครั้ง")
                return redirect('view_master_plan_manage_program_kpi', (program.id))
            else:
                kpi = DomainKPI.objects.get(pk=kpi_id)
                
                if schedule_id and schedule_id != 'none':
                    schedule = DomainKPISchedule.objects.get(pk=schedule_id)
                    
                    if schedule.target != target or schedule.quarter_year != quarter_year or schedule.quarter != quarter_month:
                        schedule.target = target
                        schedule.quarter_year = quarter_year
                        schedule.quarter = quarter_month
                        schedule.save()
                    
                else:
                    schedule = DomainKPISchedule.objects.create(kpi=kpi, of_program=program, target=target, result=0, quarter_year=quarter_year, quarter=quarter_month)
                
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
        
        messages.success(request, 'แก้ไขแผนผลลัพธ์เรียบร้อย')
        return redirect('view_master_plan_manage_organization', (program.plan.master_plan.ref_no))
    
    return render_page_response(request, 'organization', 'page_sector/manage_master_plan/manage_program_kpi.html', {'master_plan':master_plan, 'program':program, 'kpi_choices':kpi_choices, 'kpi_schedules':kpi_schedules})

# MANAGE KPI

@login_required
def view_master_plan_manage_kpi(request, master_plan_ref_no, kpi_year):
    master_plan = get_object_or_404(MasterPlan, ref_no=master_plan_ref_no)
    
    if kpi_year:
        year_number = int(kpi_year) - 543
    else:
        year_number = utilities.master_plan_current_year_number(master_plan)
    
    kpi_categories = []
    for dict in DomainKPI.objects.filter(of_master_plan=master_plan, year=year_number).values('category').distinct():
        try:
            kpi_category = DomainKPICategory.objects.get(pk=dict['category'])
        except DomainKPICategory.DoesNotExist:
            pass
        else:
            kpis = DomainKPI.objects.filter(of_master_plan=master_plan, year=year_number, category=kpi_category).order_by('ref_no')
            
            for kpi in kpis:
                kpi.removable = DomainKPISchedule.objects.filter(kpi=kpi).count() == 0
            
            kpi_category.kpis = kpis
            kpi_categories.append(kpi_category)
    
    no_category_kpis = DomainKPI.objects.filter(of_master_plan=master_plan, year=year_number, category=None)
    
    for kpi in no_category_kpis:
        kpi.removable = DomainKPISchedule.objects.filter(kpi=kpi).count() == 0
    
    year_choices = []
    for dict in DomainKPI.objects.filter(of_master_plan=master_plan).order_by('year').values('year').distinct():
        year_choices.append(int(dict['year']))
    
    return render_page_response(request, 'kpi', 'page_sector/manage_master_plan/manage_kpi.html', {'master_plan':master_plan, 'kpi_categories':kpi_categories, 'no_category_kpis':no_category_kpis, 'year_choices':year_choices, 'kpi_year':year_number})

@login_required
def view_master_plan_manage_kpi_add_kpi(request, master_plan_ref_no):
    master_plan = get_object_or_404(MasterPlan, ref_no=master_plan_ref_no)
    
    if request.method == 'POST':
        form = DomainKPIModifyForm(request.POST, master_plan=master_plan)
        if form.is_valid():
            kpi = DomainKPI.objects.create(
                of_master_plan = master_plan,
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
    master_plan = kpi.of_master_plan
    
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
    master_plan = kpi.of_master_plan
    
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
    categories = DomainKPICategory.objects.filter(of_master_plan=master_plan).order_by('name')
    
    for category in categories:
        category.removable = DomainKPI.objects.filter(category=category).count() == 0
    
    return render_page_response(request, 'kpi', 'page_sector/manage_master_plan/manage_kpi_category.html', {'master_plan':master_plan, 'categories':categories})

@login_required
def view_master_plan_manage_kpi_add_category(request, master_plan_ref_no):
    master_plan = get_object_or_404(MasterPlan, pk=master_plan_ref_no)
    
    if request.method == 'POST':
        form = DomainKPICategoryModifyForm(request.POST)
        if form.is_valid():
            category = DomainKPICategory.objects.create(of_master_plan=master_plan, name=form.cleaned_data['name'])
            
            messages.success(request, 'เพิ่มประเภทตัวชี้วัดเรียบร้อย')
            return redirect('view_master_plan_manage_kpi_category', (master_plan.ref_no))
            
    else:
        form = DomainKPICategoryModifyForm()
    
    return render_page_response(request, 'organization', 'page_sector/manage_master_plan/manage_kpi_modify_category.html', {'master_plan':master_plan, 'form':form})

@login_required
def view_master_plan_manage_kpi_edit_category(request, kpi_category_id):
    kpi_category = get_object_or_404(DomainKPICategory, pk=kpi_category_id)
    master_plan = kpi_category.of_master_plan
    
    if request.method == 'POST':
        form = DomainKPICategoryModifyForm(request.POST)
        if form.is_valid():
            kpi_category.name = form.cleaned_data['name']
            kpi_category.save()
            
            messages.success(request, 'แก้ไขประเภทตัวชี้วัดเรียบร้อย')
            return redirect('view_master_plan_manage_kpi_category', (master_plan.ref_no))
            
    else:
        form = DomainKPICategoryModifyForm(initial={'name':kpi_category.name})
    
    return render_page_response(request, 'organization', 'page_sector/manage_master_plan/manage_kpi_modify_category.html', {'master_plan':master_plan, 'form':form, 'kpi_category':kpi_category})

@login_required
def view_master_plan_manage_kpi_delete_category(request, kpi_category_id):
    kpi_category = get_object_or_404(DomainKPICategory, pk=kpi_category_id)
    master_plan = kpi_category.of_master_plan
    
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
    
    # TODO
    
    return render_page_response(request, 'kpi', 'page_program/program_kpi.html', {'program':program, })

#
# KPI SCHEDULE #######################################################################
#

@login_required
def view_kpi_overview(request, schedule_id):
    schedule = get_object_or_404(DomainKPISchedule, pk=schedule_id)
    
    # TODO
    
    return render_page_response(request, 'overview', 'page_kpi/kpi_overview.html', {'schedule':schedule, })
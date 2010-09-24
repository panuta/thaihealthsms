# -*- encoding: utf-8 -*-

from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string

from forms import *

from accounts.models import UserAccount, UserRoleResponsibility
from domain.models import *

from helper import utilities, permission
from helper.shortcuts import render_response, render_page_response, access_denied

@login_required
def view_administration(request):
    return redirect('/administration/organization/')

#
# ORGANIZATION #######################################################################
#

@login_required
def view_administration_organization(request):
    if not request.user.is_superuser: return access_denied(request)
    
    sectors = Sector.objects.all().order_by('ref_no')
    for sector in sectors:
        sector.removable = SectorMasterPlan.objects.filter(sector=sector).count() == 0
    
    master_plans = MasterPlan.objects.all().order_by('ref_no')
    for master_plan in master_plans:
        master_plan.removable = Plan.objects.filter(master_plan=master_plan).count() == 0
        
        managing_sectors = SectorMasterPlan.objects.filter(master_plan=master_plan)
        
        master_plan.sectors = []
        for sector in managing_sectors:
            master_plan.sectors.append(sector.sector.ref_no)
    
    return render_page_response(request, 'organization', 'page_administration/manage_organization.html', {'sectors':sectors, 'master_plans':master_plans})

@login_required
def view_administration_organization_add_sector(request):
    if not request.user.is_superuser: return access_denied(request)

    if request.method == 'POST':
        form = ModifySectorForm(request.POST)
        if form.is_valid():
            Sector.objects.create(ref_no=form.cleaned_data['ref_no'], name=form.cleaned_data['name'])
            
            messages.success(request, 'เพิ่มสำนักเรียบร้อย')
            return redirect('view_administration_organization')
    else:
        form = ModifySectorForm()

    return render_page_response(request, 'organization', 'page_administration/manage_organization_modify_sector.html', {'form':form})

@login_required
def view_administration_organization_edit_sector(request, sector_ref_no):
    if not request.user.is_superuser: return access_denied(request)
    sector = get_object_or_404(Sector, ref_no=sector_ref_no)

    if request.method == 'POST':
        form = ModifySectorForm(request.POST)
        if form.is_valid():
            sector.ref_no = form.cleaned_data['ref_no']
            sector.name = form.cleaned_data['name']
            sector.save()
            
            messages.success(request, 'แก้ไขสำนักเรียบร้อย')
            return redirect('view_administration_organization')

    else:
        form = ModifySectorForm(initial={'sector_id':sector.id, 'ref_no':sector.ref_no, 'name':sector.name})

    return render_page_response(request, 'organization', 'page_administration/manage_organization_modify_sector.html', {'sector':sector, 'form':form})

@login_required
def view_administration_organization_delete_sector(request, sector_ref_no):
    if not request.user.is_superuser: return access_denied(request)
    sector = get_object_or_404(Sector, ref_no=sector_ref_no)
    
    if not SectorMasterPlan.objects.filter(sector=sector).count():
        sector.delete()
        messages.success(request, 'ลบสำนักเรียบร้อย')
    else:
        messages.error(request, 'ไม่สามารถลบสำนักได้เนื่องจากยังมีข้อมูลแผนหลักอยู่ภายใต้')

    return redirect('view_administration_organization')

@login_required
def view_administration_organization_add_masterplan(request):
    if not request.user.is_superuser: return access_denied(request)
    
    if request.method == 'POST':
        form = ModifyMasterPlanForm(request.POST)
        if form.is_valid():
            ref_no = form.cleaned_data['ref_no']
            name = form.cleaned_data['name']
            sectors = form.cleaned_data['sectors']
            
            master_plan = MasterPlan.objects.create(ref_no=ref_no, name=name)
            
            for sector in sectors: SectorMasterPlan.objects.create(sector=sector, master_plan=master_plan)
            
            messages.success(request, 'เพิ่มแผนหลักเรียบร้อย')
            return redirect('view_administration_organization')

    else:
        form = ModifyMasterPlanForm()
    
    has_sectors = Sector.objects.all().count() > 0
    return render_page_response(request, 'organization', 'page_administration/manage_organization_modify_master_plan.html', {'form':form, 'has_sectors':has_sectors})

@login_required
def view_administration_organization_edit_masterplan(request, master_plan_ref_no):
    if not request.user.is_superuser: return access_denied(request)
    master_plan = get_object_or_404(MasterPlan, ref_no=master_plan_ref_no)

    if request.method == 'POST':
        form = ModifyMasterPlanForm(request.POST)
        if form.is_valid():
            ref_no = form.cleaned_data['ref_no']
            name = form.cleaned_data['name']
            sectors = form.cleaned_data['sectors']
            
            master_plan.ref_no = ref_no
            master_plan.name = name
            master_plan.save()
            
            SectorMasterPlan.objects.filter(master_plan=master_plan).delete()
            for sector in sectors: SectorMasterPlan.objects.create(sector=sector, master_plan=master_plan)
            
            messages.success(request, 'แก้ไขแผนหลักเรียบร้อย')
            return redirect('view_administration_organization')

    else:
        form = ModifyMasterPlanForm(initial={'sectors':[sector.sector.id for sector in SectorMasterPlan.objects.filter(master_plan=master_plan)], 'master_plan_id':master_plan.id, 'ref_no':master_plan.ref_no, 'name':master_plan.name})
    
    has_sectors = Sector.objects.all().count() > 0
    return render_page_response(request, 'organization', 'page_administration/manage_organization_modify_master_plan.html', {'master_plan':master_plan, 'form':form, 'has_sectors':has_sectors})

@login_required
def view_administration_organization_delete_masterplan(request, master_plan_ref_no):
    if not request.user.is_superuser: return access_denied(request)
    master_plan = get_object_or_404(MasterPlan, ref_no=master_plan_ref_no)

    if not Plan.objects.filter(master_plan=master_plan).count():
        master_plan.delete()
        SectorMasterPlan.objects.filter(master_plan=master_plan).delete()
        
        messages.success(request, 'ลบแผนหลักเรียบร้อย')
    else:
        messages.error(request, 'ไม่สามารถลบแผนหลักได้เนื่องจากยังมีข้อมูลกลุ่มแผนงานหรือแผนงานอยู่ภายใต้')

    return redirect('view_administration_organization')

#
# USERS #######################################################################
#

@login_required
def view_administration_users(request):
    if not request.user.is_superuser: return access_denied(request)
    user_accounts = UserAccount.objects.filter(user__is_superuser=False).extra(select={'lfirstname':'lower(firstname)', 'llastname':'lower(lastname)'}).order_by('lfirstname', 'llastname')
    
    paginator = Paginator(user_accounts, settings.ADMIN_MANAGE_USERS_PER_PAGE)
    
    try:
        page = int(request.GET.get('p', '1'))
    except ValueError:
        page = 1
    
    try:
        user_accounts = paginator.page(page)
    except (EmptyPage, InvalidPage):
        user_accounts = paginator.page(paginator.num_pages)
    
    return render_page_response(request, 'users', 'page_administration/manage_users.html', {'user_accounts': user_accounts})

@login_required
def view_administration_users_add(request):
    if not request.user.is_superuser: return access_denied(request)
    
    responsible_input_mode = 0 # Determine to show which type of responsibility input in template
    
    if request.method == 'POST':
        form = UserAccountForm(request.POST)
        is_valid = True
        
        try:
            role = request.POST.get('role')
            group = Group.objects.get(name=role)
            group_details = RoleDetails.objects.get(role=group)
            
            if group_details.level == RoleDetails.SECTOR_LEVEL:
                responsible_input_mode = 1
            elif group_details.level == RoleDetails.PROGRAM_LEVEL:
                responsible_input_mode = 2
        except:
            is_valid = False
            messages.error(request, 'ข้อมูลตำแหน่งที่ส่งมาไม่อยู่ในรูปแบบที่ถูกต้อง')
        
        if form.is_valid() and is_valid:
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']
            role = form.cleaned_data['role']
            
            password = utilities.make_random_user_password()
            
            if group_details.level == RoleDetails.SECTOR_LEVEL:
                sector_id = request.POST.get('responsible_sector')
                
                try:
                    responsible_sector = Sector.objects.get(pk=sector_id)
                except:
                    is_valid = False
                    messages.error(request, 'ไม่มีข้อมูลสำนักที่สังกัด กรุณากรอกข้อมูลให้ครบถ้วน')
            
            elif group_details.level == RoleDetails.PROGRAM_LEVEL:
                program_ids = request.POST.getlist('responsible_program')
                responsible_programs = []
                
                if program_ids:
                    for program_id in program_ids:
                        try:
                            responsible_programs.append(Program.objects.get(pk=program_id))
                        except:
                            pass
                    
                if not responsible_programs:
                    is_valid = False
                    messages.error(request, 'ไม่มีข้อมูลแผนงานที่สังกัด กรุณากรอกข้อมูลให้ครบถ้วน')
            
            else:
                is_valid = False
                messages.error(request, 'ข้อมูลตำแหน่งที่ส่งมาไม่อยู่ในรูปแบบที่ถูกต้อง')
            
            if is_valid:
                user = User.objects.create_user(username, email, password=password)
                
                user_account = UserAccount.objects.get(user=user)
                user_account.firstname = firstname
                user_account.lastname = lastname
                user_account.random_password = password
                user_account.save()
                
                user.groups.add(group)
                responsibility = UserRoleResponsibility.objects.create(user=user_account, role=group)
                
                if group_details.level == RoleDetails.SECTOR_LEVEL:
                    responsibility.sectors.add(responsible_sector)
                
                elif group_details.level == RoleDetails.PROGRAM_LEVEL:
                    for program in responsible_programs:
                        responsibility.programs.add(program)
                
                email_render_dict = {'username':username, 'password':password, 'settings':settings, 'site':Site.objects.get_current()}
                email_subject = render_to_string('email/create_user_subject.txt', email_render_dict)
                email_message = render_to_string('email/create_user_message.txt', email_render_dict)
                
                send_mail(email_subject, email_message, settings.SYSTEM_NOREPLY_EMAIL, [email])
                
                messages.success(request, 'เพิ่มผู้ใช้เรียบร้อย')
                return redirect('view_administration_users_password', user.id)
            
    else:
        form = UserAccountForm()
    
    sectors = Sector.objects.all().order_by('ref_no')
    master_plans = MasterPlan.objects.all().order_by('ref_no')
    
    # TODO: Check integrity of the following value
    
    responsible_sector = '' # Can be any string
    if 'responsible_sector' in request.POST:
        sector_id = request.POST.get('responsible_sector')
        responsible_sector = Sector.objects.get(pk=sector_id)
    
    responsible_programs = []
    if 'responsible_program' in request.POST:
        program_ids = request.POST.getlist('responsible_program')
        responsible_programs = [Program.objects.get(pk=program_id) for program_id in program_ids]
    
    return render_page_response(request, 'users', 'page_administration/manage_users_modify_user.html', {'form': form, 'sectors':sectors, 'master_plans':master_plans, 'responsible_sector':responsible_sector, 'responsible_programs':responsible_programs, 'responsible_input_mode':responsible_input_mode})

@login_required
def view_administration_users_edit(request, user_id):
    if not request.user.is_superuser: return access_denied(request)
    user = get_object_or_404(User, pk=user_id)
    
    responsible_input_mode = 0 # Determine to show which type of responsibility input in template
    
    if request.method == 'POST':
        form = UserAccountForm(request.POST)
        is_valid = True
        
        try:
            role = request.POST.get('role')
            group = Group.objects.get(name=role)
            group_details = RoleDetails.objects.get(role=group)
            
            if group_details.level == RoleDetails.SECTOR_LEVEL:
                responsible_input_mode = 1
            elif group_details.level == RoleDetails.PROGRAM_LEVEL:
                responsible_input_mode = 2
        except:
            is_valid = False
            messages.error(request, 'ข้อมูลตำแหน่งที่ส่งมาไม่อยู่ในรูปแบบที่ถูกต้อง')
        
        if form.is_valid() and is_valid:
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']
            role = form.cleaned_data['role']
            
            if group_details.level == RoleDetails.SECTOR_LEVEL:
                sector_id = request.POST.get('responsible_sector')
                
                try:
                    responsible_sector = Sector.objects.get(pk=sector_id)
                except:
                    is_valid = False
                    messages.error(request, 'ไม่มีข้อมูลสำนักที่สังกัด กรุณากรอกข้อมูลให้ครบถ้วน')
            
            elif group_details.level == RoleDetails.PROGRAM_LEVEL:
                program_ids = request.POST.getlist('responsible_program')
                responsible_programs = []
                
                if program_ids:
                    for program_id in program_ids:
                        try:
                            responsible_programs.append(Program.objects.get(pk=program_id))
                        except:
                            pass
                    
                if not responsible_programs:
                    is_valid = False
                    messages.error(request, 'ไม่มีข้อมูลแผนงานที่สังกัด กรุณากรอกข้อมูลให้ครบถ้วน')
            
            else:
                is_valid = False
                messages.error(request, 'ข้อมูลตำแหน่งที่ส่งมาไม่อยู่ในรูปแบบที่ถูกต้อง')
            
            if is_valid:
                user.username = username
                user.email = email
                user.save()
                
                user_account = UserAccount.objects.get(user=user)
                user_account.firstname = firstname
                user_account.lastname = lastname
                user_account.save()
                
                user.groups.clear()
                user.groups.add(group)
                
                UserRoleResponsibility.objects.filter(user=user_account).delete()
                responsibility = UserRoleResponsibility.objects.create(user=user_account, role=group)
                
                if group_details.level == RoleDetails.SECTOR_LEVEL:
                    responsibility.sectors.add(responsible_sector)
                
                elif group_details.level == RoleDetails.PROGRAM_LEVEL:
                    for program in responsible_programs:
                        responsibility.programs.add(program)
                
                messages.success(request, 'แก้ไขข้อมูลผู้ใช้เรียบร้อย')
                return redirect('view_administration_users')
        
        responsible_sector = ''
        if 'responsible_sector' in request.POST:
            sector_id = request.POST.get('responsible_sector')
            responsible_sector = Sector.objects.get(pk=sector_id)
        
        responsible_programs = []
        if 'responsible_program' in request.POST:
            program_ids = request.POST.getlist('responsible_program')
            responsible_programs = [Program.objects.get(pk=program_id) for program_id in program_ids]
        
    else:
        form = UserAccountForm(initial={
            'user_id':user.id,
            'username':user.username,
            'email':user.email,
            'firstname':user.get_profile().firstname,
            'lastname':user.get_profile().lastname,
            'role':user.groups.all()[0].name,
        });
        
        group_details = RoleDetails.objects.get(role=user.groups.all()[0])
        responsibility = UserRoleResponsibility.objects.filter(user=user.get_profile())[0]
        
        responsible_sector = ''
        responsible_programs = []
        
        if group_details.level == RoleDetails.SECTOR_LEVEL:
            responsible_input_mode = 1
            responsible_sector = responsibility.sectors.all()[0]
        elif group_details.level == RoleDetails.PROGRAM_LEVEL:
            responsible_input_mode = 2
            responsible_programs = responsibility.programs.all()
        
    sectors = Sector.objects.all().order_by('ref_no')
    master_plans = MasterPlan.objects.all().order_by('ref_no')
    
    return render_page_response(request, 'users', 'page_administration/manage_users_modify_user.html', {'form': form, 'editing_user':user, 'sectors':sectors, 'master_plans':master_plans, 'responsible_sector':responsible_sector, 'responsible_programs':responsible_programs, 'responsible_input_mode':responsible_input_mode})

@login_required
def view_administration_users_password(request, user_id):
    if not request.user.is_superuser: return access_denied(request)
    user = User.objects.get(pk=user_id)
    new_user_account = UserAccount.objects.get(user=user)
    return render_page_response(request, 'users', 'page_administration/manage_users_password.html', {'new_user_account': new_user_account})

@login_required
def view_administration_users_change_password(request, user_id):
    if not request.user.is_superuser: return access_denied(request)
    user = User.objects.get(pk=user_id)
    
    if request.method == 'POST':
        form = UserChangePasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            messages.success(request, 'ตั้งรหัสผ่านใหม่เรียบร้อย')
            return redirect('view_administration_users')
        
    else:
        form = UserChangePasswordForm()
    
    return render_page_response(request, 'users', 'page_administration/manage_users_change_password.html', {'editing_user': user, 'form':form})



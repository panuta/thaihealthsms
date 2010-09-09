from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from accounts.models import UserRoleResponsibility
from domain.models import SectorMasterPlan

from helper.shortcuts import render_response

def view_homepage(request):
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
    return render_response(request, 'page_user/user_sector_assistant_dashboard.html', {'responsibilities':responsibilities, 'roles':roles, 'primary_role':primary_role, 'primary_sector':primary_sector, 'primary_master_plans':primary_master_plans, 'responsible_programs':responsible_programs})

def _view_program_manager_homepage(request, roles, responsibilities):
    return redirect('view_program_overview', (responsibilities[0].programs.all()[0].id))

def _view_program_manager_assistant_homepage(request, roles, responsibilities):
    return redirect('view_program_overview', (responsibilities[0].programs.all()[0].id))

def _view_general_homepage(request, roles, responsibilities):
    return render_response(request, 'page_user/user_dashboard.html', {'responsibilities':responsibilities, 'roles':roles})
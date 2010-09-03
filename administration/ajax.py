from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import simplejson

from accounts.models import RoleDetails
from domain.models import MasterPlan, Program

@login_required
def ajax_get_group_level(request):
    role_name = request.GET.get('role_name')
    
    if role_name:
        try:
            group_details = RoleDetails.objects.get(role__name=role_name)
        except RoleDetails.DoesNotExist:
            pass
        else:
            return HttpResponse(group_details.level)
    
    return HttpResponse('')

def ajax_get_master_plan_programs(request):
    master_plan = get_object_or_404(MasterPlan, pk=request.GET.get('master_plan_id'))
    programs = Program.objects.filter(plan__master_plan=master_plan).order_by('ref_no')
    
    programs_json = []
    for program in programs:
        programs_json.append({'id':program.id, 'ref_no':program.ref_no, 'name':program.name})
    
    return HttpResponse(simplejson.dumps(programs_json))
    
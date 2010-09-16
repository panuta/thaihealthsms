# -*- encoding: utf-8 -*-

from datetime import date

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.utils import simplejson

from models import *

from helper import permission

@login_required
def ajax_update_kpi_schedule(request):
    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        new_target = request.POST.get('target', '')
        new_result = request.POST.get('result', '')
        
        try:
            kpi_schedule = DomainKPISchedule.objects.get(pk=schedule_id)
        except:
            raise Http404
        
        is_changed = False
        
        if new_target:
            if not permission.access_obj(request.user, 'program kpi target edit', kpi_schedule.program):
                return HttpResponse(simplejson.dumps({'error':'denied'}))
            
            try:
                new_target = int(new_target)
            except:
                return HttpResponse(simplejson.dumps({'error':'invalid'}))
            
            if new_target < 0:
                return HttpResponse(simplejson.dumps({'error':'invalid'}))
            
            target = new_target
            is_changed = True
        else:
            target = kpi_schedule.target
        
        if new_result:
            if not permission.access_obj(request.user, 'program kpi result edit', kpi_schedule.program):
                return HttpResponse(simplejson.dumps({'error':'denied'}))
            
            try:
                new_result = int(new_result)
            except:
                return HttpResponse(simplejson.dumps({'error':'invalid'}))
            
            if new_result < 0:
                return HttpResponse(simplejson.dumps({'error':'invalid'}))
            
            result = new_result
            is_changed = True
        else:
            result = kpi_schedule.result
        
        if is_changed:
            kpi_schedule.target = target
            kpi_schedule.result = result
            kpi_schedule.save()
        
        return HttpResponse("")
        
    else:
        raise Http404


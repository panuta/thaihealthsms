# -*- encoding: utf-8 -*-

from datetime import datetime, date

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.utils import simplejson

from models import *

from helper import permission

@login_required
def ajax_update_budget_schedule(request):
    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        new_grant = request.POST.get('grant', '')
        new_claim = request.POST.get('claim', '')
        
        try:
            budget_schedule = BudgetSchedule.objects.get(pk=schedule_id)
        except:
            raise Http404
        
        is_changed = False
        
        if new_grant:
            if not permission.access_obj(request.user, 'program budget grant edit', budget_schedule.program):
                return HttpResponse(simplejson.dumps({'error':'denied'}))
            
            try:
                new_grant = int(new_grant)
            except:
                return HttpResponse(simplejson.dumps({'error':'invalid'}))
            
            if new_grant < 0:
                return HttpResponse(simplejson.dumps({'error':'invalid'}))
            
            grant = new_grant
            is_changed = True
        else:
            grant = budget_schedule.grant_budget
        
        if new_claim:
            if not permission.access_obj(request.user, 'program budget claim edit', budget_schedule.program):
                return HttpResponse(simplejson.dumps({'error':'denied'}))
            
            try:
                new_claim = int(new_claim)
            except:
                return HttpResponse(simplejson.dumps({'error':'invalid'}))
            
            if new_claim < 0:
                return HttpResponse(simplejson.dumps({'error':'invalid'}))
            
            claim = new_claim
            is_changed = True
        else:
            claim = budget_schedule.claim_budget
        
        if is_changed:
            revision = BudgetScheduleRevision.objects.create(
                schedule = budget_schedule,
                grant_budget = grant,
                claim_budget = claim,
                schedule_on = budget_schedule.schedule_on,
                revised_by = request.user.get_profile()
            )
            
            budget_schedule.grant_budget = grant
            budget_schedule.claim_budget = claim
            
            if claim != 0 and not budget_schedule.claimed_on:
                budget_schedule.claimed_on = datetime.now()
            
            budget_schedule.save()
        
        return HttpResponse("")
    else:
        raise Http404
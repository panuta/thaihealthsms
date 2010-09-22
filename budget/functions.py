
from datetime import date

from models import *

def determine_schedule_status(schedule):
    # NORMAL, CLAIMED_EQUAL, CLAIMED_LOWER, CLAIMED_HIGHER, LATE
    current_date = date.today()
    
    if schedule.claimed_on:
        if schedule.grant_budget < schedule.claim_budget:
            return 'claimed_higher'
        elif schedule.grant_budget > schedule.claim_budget:
            return 'claimed_lower'
        else:
            return 'claimed_equal'
    else:
        if schedule.schedule_on < current_date:
            return 'late'
        elif schedule.schedule_on > current_date:
            return 'future'
        else:
            return 'today'

def get_late_budget_schedule_for_program(program):
    current_date = date.today()
    return BudgetSchedule.objects.filter(program=program, schedule_on__lt=current_date, claimed_on=None)
    

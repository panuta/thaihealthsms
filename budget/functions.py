
from datetime import date

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

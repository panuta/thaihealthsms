from datetime import date

from django.conf import settings

from models import *

from helper.utilities import find_quarter

def get_kpi_progress_for_master_plan_overview(master_plan, kpi_category, quarter, quarter_year):
    if kpi_category:
        schedules = DomainKPISchedule.objects.filter(kpi__master_plan=master_plan, kpi__category=kpi_category, quarter=quarter, quarter_year=quarter_year)
    else:
        schedules = DomainKPISchedule.objects.filter(kpi__master_plan=master_plan, kpi__category=None, quarter=quarter, quarter_year=quarter_year)
    
    if schedules:
        percent = 0
        for schedule in schedules:
            percent = percent + float(schedule.result) / schedule.target * 100
        
        return '%.2f' % (percent / len(schedules))
    else:
        return ''

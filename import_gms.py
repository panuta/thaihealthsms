CURRENT_PB_YEAR = '55'

SMS_PLAN_VIEW_URL = 'http://61.90.139.134/gms/api/?view=plan&format=json&page=0&pbyear=55'
SMS_CONTRACT_VIEW_URL = 'http://61.90.139.134/gms/api/?view=contract&format=json&page=0'

from django.core.management import setup_environ
import settings
setup_environ(settings)

import datetime
import urllib

from django.contrib.auth.models import User
from django.util import simplejson

from accounts.models import UserAccount
from domain.models import *

def convert_to_date(str):
    (year_str, month_str, date_str) = str.split(' ')[0].split('-')
    return datetime.date(int(year_str), int(month_str), int(date_str))

admin_user = UserAccount.objects.get(user=User.objects.get(username='admin'))

# File logs
startdate = datetime.datetime.today()
logfile = open('import_gms-%02d-%02d-%02d.log' % (startdate.year, startdate.month, startdate.date), 'w')
logfile.write('Import operation starting on %02d/%02d/%02d %02d:%02d\n', % (startdate.date, startdate.month, startdate.year, startdate.hour, startdate.minute))

# Retrieve plan list in JSON format from GMS
import_url = urllib.urlopen(SMS_PLAN_VIEW_URL)
raw_plan_list = simplejson.loads(import_url.read())

# Insert plans and projects to SMS
for raw_plan in raw_plan_list:
    try:
        master_plan = MasterPlan.objects.get(ref_no=int(raw_plan['PBMCode']))
        break;
    except:
        logfile.write('ERROR: Unknown MasterPlan code [PBMCode="%s"]\n' % raw_plan['PBMCode'])
    
    (plan, created) = Plan.objects.get_or_create(ref_no=raw_plan['BudgetPlan'])
    plan.master_plan = master_plan
    plan.name = raw_plan['BudgetPlanName']
    plan.save()

    import_url = urllib.urlopen(SMS_CONTRACT_VIEW_URL + '&projectcode=%s' % raw_plan['ProjectCode'])
    raw_project_list = simplejson.loads(import_url.read())

    if len(raw_project_list) == 0:
        logfile.write('ERROR: Project not found [ProjectCode="%s"]\n' % raw_plan['ProjectCode'])

    elif len(raw_project_list) > 1:
        logfile.write('ERROR: GMS returned a multiple Project record [ProjectCode="%s"]\n' % raw_plan['PBMCode'])

    else:
        try:
            project = Project.objects.get(ref_no=raw_plan['ProjectCode'])
        except Project.DoesNotExist:
            project = Project.objects.create(
                plan=plan,
                ref_no=raw_plan['ProjectCode'],
                contract_no=raw_project_list[0]['ContractNo'],
                name=raw_project_list[0]['ProjectThai'],
                start_date=convert_to_date(raw_project_list[0]['DateStart']),
                end_date=convert_to_date(raw_project_list[0]['DateFinish']),
                created_by=admin_user,
                )
        else:
            # Update existing record, in case there's a change
            project.name = raw_project_list[0]['ProjectThai']
            start_date=convert_to_date(raw_project_list[0]['DateStart'])
            end_date=convert_to_date(raw_project_list[0]['DateFinish'])

"""
All MasterPlan Code in GMS
15
90
03
07
09
05
08
01
02
04
06
10
99
NULL
14
16
12
17
11
13
"""
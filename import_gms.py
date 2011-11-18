CURRENT_PB_YEAR = '55'

HOST = 'http://61.90.139.134/gms/api/'
APIKEY = 'WY0sSJA693sZsHRxT7oTwdzVM83mK0XQcffTYPPes1YUklgH6X5oxQ0xjv8WneG'

SMS_PLAN_VIEW_URL = HOST + '?view=SMS_PLAN_VIEW&format=json&page=0&general=1&where=pbyear%3d%2755%27&apikey=' + APIKEY 
SMS_CONTRACT_VIEW_URL = HOST + '?view=SMS_CONTRACT_VIEW&format=json&page=0&general=1&apikey=' + APIKEY
SMS_CONTRACT_MONEY_URL = HOST + '?view=SMS_Contract_Money&format=json&page=0&general=1&apikey=' + APIKEY

# SMS_PLAN_VIEW_URL = 'http://61.90.139.134/gms/api/?view=plan&format=json&page=0&pbyear=55'
# SMS_CONTRACT_VIEW_URL = 'http://61.90.139.134/gms/api/?view=contract&format=json&page=0'
# SMS_CONTRACT_MONEY_URL = 'http://61.90.139.134/gms/api/?view=money&format=json&page=0'

from django.core.management import setup_environ
import settings
setup_environ(settings)

import datetime
import urllib

from django.contrib.auth.models import User
from django.utils import simplejson

from accounts.models import UserAccount
from domain.models import *
from budget.models import *

def convert_to_date(str):
    (year_str, month_str, date_str) = str.split(' ')[0].split('-')
    return datetime.date(int(year_str), int(month_str), int(date_str))

def find_project(raw_project_list, project_code):
    for raw_project in raw_project_list:
        if raw_project['ProjectCode'] == project_code:
            return raw_project
    return None

admin_user = UserAccount.objects.get(user=User.objects.get(username='admin'))

# File logs
startdate = datetime.datetime.today()
logfile = open('import_gms-%02d-%02d-%02d.log' % (startdate.year, startdate.month, startdate.day), 'w')
logfile.write('Import operation started on %02d/%02d/%02d %02d:%02d\n' % (startdate.day, startdate.month, startdate.year, startdate.hour, startdate.minute))

# Retrieve data JSON format from GMS
import_url = urllib.urlopen(SMS_PLAN_VIEW_URL)
raw_plan_list = simplejson.loads(import_url.read())

import_url = urllib.urlopen(SMS_CONTRACT_VIEW_URL)
raw_project_list = simplejson.loads(import_url.read())

import_url = urllib.urlopen(SMS_CONTRACT_MONEY_URL)
raw_money_list = simplejson.loads(import_url.read())

stat_plan_created = 0
stat_project_created = 0
stat_budget_created = 0

# Insert plans and projects to SMS
for raw_plan in raw_plan_list:

    try:
        master_plan = MasterPlan.objects.get(ref_no=int(raw_plan['PBMCode']))
    except:
        logfile.write('ERROR: Unknown MasterPlan code [PBMCode="%s"]\n' % raw_plan['PBMCode'])
        continue

    try:
        plan = Plan.objects.get(ref_no=raw_plan['BudgetPlan'])
    except Plan.DoesNotExist:
        plan = Plan.objects.create(master_plan=master_plan, ref_no=raw_plan['BudgetPlan'], name=raw_plan['BudgetPlanName'])
        stat_plan_created = stat_plan_created + 1

    raw_project = find_project(raw_project_list, raw_plan['ProjectCode'])

    if not raw_project:
        logfile.write('ERROR: Project not found in SMS_CONTRACT_VIEW [ProjectCode="%s"]\n' % raw_plan['ProjectCode'])
    else:
        try:
            project = Project.objects.get(ref_no=raw_plan['ProjectCode'])
        except Project.DoesNotExist:
            project = Project.objects.create(
                plan=plan,
                ref_no=raw_plan['ProjectCode'],
                contract_no=raw_project['ContractNo'],
                name=raw_project['ProjectThai'],
                start_date=convert_to_date(raw_project['DateStart']),
                end_date=convert_to_date(raw_project['DateFinish']),
                created_by=admin_user,
            )
            stat_project_created = stat_project_created + 1
        else:
            # Update project name and date, if imported data is different than in SMS database
            project.name = raw_project['ProjectThai']
            start_date=convert_to_date(raw_project['DateStart'])
            end_date=convert_to_date(raw_project['DateFinish'])

for raw_money in raw_money_list:
    try:
        project = Project.objects.get(ref_no=raw_money['ProjectCode'])
    except Project.DoesNotExist:
        logfile.write('ERROR: Project not found in SMS_CONTRACT_MONEY [ProjectCode="%s"]\n' % raw_plan['ProjectCode'])

    try:
        budget_schedule = BudgetSchedule.objects.get(project=project, schedule_on=convert_to_date(raw_money['DateDue']))
    except BudgetSchedule.DoesNotExist:
        budget_schedule = BudgetSchedule.objects.create(
            project=project,
            schedule_on=convert_to_date(raw_money['DateDue']),
            grant_budget=int(float(raw_money['MoneyOperate'])),
        )

        revision = BudgetScheduleRevision.objects.create(
            schedule=budget_schedule,
            grant_budget=budget_schedule.grant_budget,
            claim_budget=budget_schedule.claim_budget,
            schedule_on=budget_schedule.schedule_on,
            revised_by=admin_user
        )

        stat_budget_created = stat_budget_created + 1

enddate = datetime.datetime.today()
logfile.write('Summary: Created %d plans\n' % stat_plan_created)
logfile.write('Summary: Created %d projects\n' % stat_project_created)
logfile.write('Summary: Created %d budget schedules\n' % stat_budget_created)
logfile.write('Import operation ended on %02d/%02d/%02d %02d:%02d\n' % (startdate.day, startdate.month, startdate.year, startdate.hour, startdate.minute))

logfile.close()

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
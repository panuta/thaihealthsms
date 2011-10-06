from django.core.management import setup_environ
import settings
setup_environ(settings)

from django.contrib.auth.models import User

from accounts.models import UserAccount
from domain.models import *

import datetime
def convert_to_date(str):
    (year_str, month_str, date_str) = str.split(' ')[0].split('-')
    return datetime.date(int(year_str), int(month_str), int(date_str))

from django.utils import simplejson
import urllib

import_url = urllib.urlopen('http://localhost:8002/echo_projects/')
json_str = import_url.read()

projects_list = simplejson.loads(json_str)

project_columns = []
projects = []

for index, row in enumerate(projects_list):
    if index == 0:
        for index in range(len(row)):
            project_columns.append(row[index])
        print project_columns
    else:
        
        project = {}
        for index in range(len(row)):
            #print row[index]
            print row[index]
            project[project_columns[index]] = row[index]
        
        projects.append(project)

for project in projects:
    # TODO: Find program object

    admin_user = UserAccount.objects.get(user=User.objects.get(username='admin'))

    Project.objects.create(
        ref_no=project['ProjectCode'],
        contract_no=project['ContractNo'],
        name=project['ProjectThai'],
        start_date=convert_to_date(project['DateStart']),
        end_date=convert_to_date(project['DateFinish']),
        created_by=admin_user,
    )

from django.conf.urls.defaults import *

urlpatterns = patterns('report.views',
    url(r'^master_plan/(?P<master_plan_ref_no>\d+)/manage/report/$', 'view_master_plan_manage_report', name='view_master_plan_manage_report'),
    url(r'^program/(?P<program_id>\d+)/reports/$', 'view_program_reports', name='view_program_reports'),
    url(r'^report/(?P<submission_id>\d+)/$', 'view_report_overview', name='view_report_overview'),
    
)

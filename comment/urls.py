from django.conf.urls.defaults import *

urlpatterns = patterns('comment.views',
    
    url(r'^project/(?P<project_id>\d+)/comments/$', 'view_project_comments', name='view_project_comments'),
    url(r'^activity/(?P<activity_id>\d+)/comments/$', 'view_activity_comments', name='view_activity_comments'),
    
    url(r'^report/(?P<submission_id>\d+)/comments/$', 'view_report_comments_by_submission', name='view_report_comments_by_submission'),
    url(r'^program/(?P<program_id>\d+)/report/(?P<report_id>\d+)/(?P<schedule_dateid>\w+)/comments/$', 'view_report_comments', name='view_report_comments'),
    
    url(r'^kpi/(?P<schedule_id>\d+)/comments/$', 'view_kpi_comments', name='view_kpi_comments'),
    url(r'^budget/(?P<schedule_id>\d+)/comments/$', 'view_budget_comments', name='view_budget_comments'),
)
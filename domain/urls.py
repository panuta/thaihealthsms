from django.conf.urls.defaults import *

urlpatterns = patterns('domain.views',
    # Sector
    url(r'^organization/$', 'view_organization', name='view_organization'),
    url(r'^sector/(?P<sector_ref_no>\d+)/$', 'view_sector_overview', name='view_sector_overview'),
    
    # Master Plan
    url(r'^master_plan/(?P<master_plan_ref_no>\d+)/$', 'view_master_plan_overview', name='view_master_plan_overview'),
    url(r'^master_plan/(?P<master_plan_ref_no>\d+)/programs/$', 'view_master_plan_programs', name='view_master_plan_programs'),
    
    # Master Plan Management
    url(r'^master_plan/(?P<master_plan_ref_no>\d+)/manage/organization/$', 'view_master_plan_manage_organization', name='view_master_plan_manage_organization'),
    url(r'^master_plan/(?P<master_plan_ref_no>\d+)/manage/plan/add/$', 'view_master_plan_add_plan', name='view_master_plan_add_plan'),
    url(r'^master_plan/manage/plan/(?P<plan_id>\d+)/edit/$', 'view_master_plan_edit_plan', name='view_master_plan_edit_plan'),
    url(r'^master_plan/manage/plan/(?P<plan_id>\d+)/delete/$', 'view_master_plan_delete_plan', name='view_master_plan_delete_plan'),
    url(r'^master_plan/(?P<master_plan_ref_no>\d+)/manage/program/add/$', 'view_master_plan_add_program', name='view_master_plan_add_program'),
    url(r'^master_plan/manage/program/(?P<program_id>\d+)/edit/$', 'view_master_plan_edit_program', name='view_master_plan_edit_program'),
    url(r'^master_plan/manage/program/(?P<program_id>\d+)/delete/$', 'view_master_plan_delete_program', name='view_master_plan_delete_program'),
    
    # Program
    url(r'^program/(?P<program_id>\d+)/$', 'view_program_overview', name='view_program_overview'),
    url(r'^program/(?P<program_id>\d+)/projects/$', 'view_program_projects', name='view_program_projects'),
    url(r'^project/(?P<program_id>\d+)/projects/add/$', 'view_program_add_project', name='view_program_add_project'),
    
    # Project
    url(r'^project/(?P<project_id>\d+)/$', 'view_project_overview', name='view_project_overview'),
    url(r'^project/(?P<project_id>\d+)/activities/$', 'view_project_activities', name='view_project_activities'),
    
    
    #url(r'^project/(?P<project_id>\d+)/projects/$', 'view_project_projects', name='view_project_projects'),
    #url(r'^project/(?P<project_id>\d+)/projects/add/$', 'view_project_add', name='view_project_add'),
    #url(r'^project/(?P<project_id>\d+)/delete/$', 'view_project_delete', name='view_project_delete'),
    #url(r'^project/(?P<project_id>\d+)/edit/$', 'view_project_edit', name='view_project_edit'),
    
    #url(r'^project/(?P<project_id>\d+)/activities/add/$', 'view_activity_add', name='view_activity_add'),

    # Activity
    url(r'^activity/(?P<activity_id>\d+)/$', 'view_activity_overview', name="view_activity_overview"),
    #url(r'^activity/(?P<activity_id>\d+)/edit/$', 'view_activity_edit', name="view_activity_edit"),
    #url(r'^activity/(?P<activity_id>\d+)/delete/$', 'view_activity_delete', name="view_activity_delete"),
)

#urlpatterns += patterns('domain.ajax',
#    url(r'^ajax/list/master_plans/$', 'ajax_list_master_plans', name='ajax_list_master_plans'),
#    url(r'^ajax/list/projects/$', 'ajax_list_projects', name='ajax_list_projects'),
#    url(r'^ajax/list/project/activities/$', 'ajax_list_project_activities', name='ajax_list_project_activities'),
#)

from django.conf.urls.defaults import *

urlpatterns = patterns('budget.views',
    url(r'^sector/(?P<sector_ref_no>\d+)/budget/$', 'view_sector_budget', name='view_sector_budget'),
    
    url(r'^master_plan/manage/program/(?P<program_id>\d+)/budget/$', 'view_master_plan_manage_program_budget', name='view_master_plan_manage_program_budget'),
    url(r'^master_plan/(?P<master_plan_ref_no>\d+)/budget/$', 'view_master_plan_budget', name='view_master_plan_budget'),
    
    url(r'^program/(?P<program_id>\d+)/budget/$', 'view_program_budget', name='view_program_budget'),
    
    url(r'^budget/(?P<schedule_id>\d+)/$', 'view_budget_overview', name='view_budget_overview'),
    url(r'^budget/(?P<schedule_id>\d+)/reference/edit/$', 'view_budget_overview_edit_reference', name='view_budget_overview_edit_reference'),
)

urlpatterns += patterns('budget.ajax',
    url(r'^ajax/budget/schedule/update/$', 'ajax_update_budget_schedule', name="ajax_update_budget_schedule"),
)

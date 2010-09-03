from django.conf.urls.defaults import *

urlpatterns = patterns('kpi.views',
    url(r'^sector/(?P<sector_ref_no>\d+)/kpi/$', 'view_sector_kpi', name='view_sector_kpi'),
    url(r'^master_plan/(?P<master_plan_ref_no>\d+)/kpi/$', 'view_master_plan_kpi', name='view_master_plan_kpi'),
    url(r'^program/(?P<program_id>\d+)/kpi/$', 'view_program_kpi', name='view_program_kpi'),
    
    
    # Manage - Master Plan - KPI
    url(r'^master_plan/(?P<master_plan_ref_no>\d+)/manage/kpi/$', 'view_master_plan_manage_kpi', name='view_master_plan_manage_kpi'),
    
    # Manage - Master Plan - KPI - KPI Category
    #url(r'^master_plan/(?P<master_plan_id>\d+)/manage/kpi_category/add/$', 'view_master_plan_add_kpi_category', name='view_master_plan_add_kpi_category'),
    #url(r'^master_plan/manage/kpi_category/(?P<kpi_category_id>\d+)/edit/$', 'view_master_plan_edit_kpi_category', name='view_master_plan_edit_kpi_category'),
    #url(r'^master_plan/manage/kpi_category/(?P<kpi_category_id>\d+)/delete/$', 'view_master_plan_delete_kpi_category', name='view_master_plan_delete_kpi_category'),
    
    # Manage - Master Plan - KPI - KPI
    #url(r'^master_plan/(?P<master_plan_id>\d+)/manage/kpi/add/$', 'view_master_plan_add_kpi', name='view_master_plan_add_kpi'),
    #url(r'^master_plan/manage/kpi/(?P<kpi_id>\d+)/edit/$', 'view_master_plan_edit_kpi', name='view_master_plan_edit_kpi'),
    #url(r'^master_plan/manage/kpi/(?P<kpi_id>\d+)/delete/$', 'view_master_plan_delete_kpi', name='view_master_plan_delete_kpi'),
    
    url(r'^master_plan/manage/program/(?P<program_id>\d+)/kpi/$', 'view_master_plan_manage_program_kpi', name='view_master_plan_manage_program_kpi'),
    
    url(r'^kpi/(?P<schedule_id>\d+)/$', 'view_kpi_overview', name='view_kpi_overview'),
)

#urlpatterns += patterns('kpi.ajax',
#    url(r'^ajax/kpi/update/$', 'ajax_update_kpi_value', name="ajax_update_kpi_value"),
#    
#)
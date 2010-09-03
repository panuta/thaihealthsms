from django.conf.urls.defaults import *

urlpatterns = patterns('administration.views',
	url(r'^administration/$', 'view_administration', name='view_administration'),
	
	# Organization
	url(r'^administration/organization/$', 'view_administration_organization', name='view_administration_organization'),
	url(r'^administration/organization/sector/add/$', 'view_administration_organization_add_sector', name='view_administration_organization_add_sector'),
	url(r'^administration/organization/sector/(?P<sector_ref_no>\d+)/edit/$', 'view_administration_organization_edit_sector', name='view_administration_organization_edit_sector'),
	url(r'^administration/organization/sector/(?P<sector_ref_no>\d+)/delete/$', 'view_administration_organization_delete_sector', name='view_administration_organization_delete_sector'),
	url(r'^administration/organization/masterplan/add/$', 'view_administration_organization_add_masterplan', name='view_administration_organization_add_masterplan'),
	url(r'^administration/organization/masterplan/(?P<master_plan_ref_no>\d+)/edit/$', 'view_administration_organization_edit_masterplan', name='view_administration_organization_edit_masterplan'),
	url(r'^administration/organization/masterplan/(?P<master_plan_ref_no>\d+)/delete/$', 'view_administration_organization_delete_masterplan', name='view_administration_organization_delete_masterplan'),
	
	# Users
	url(r'^administration/users/$', 'view_administration_users', name='view_administration_users'),
	url(r'^administration/user/add/$', 'view_administration_users_add', name='view_administration_users_add'),
	url(r'^administration/user/(?P<user_id>\d+)/edit/$', 'view_administration_users_edit', name='view_administration_users_edit'),
	url(r'^administration/user/(?P<user_id>\d+)/password/$', 'view_administration_users_password', name='view_administration_users_password'),
	url(r'^administration/user/(?P<user_id>\d+)/change_password/$', 'view_administration_users_change_password', name='view_administration_users_change_password'),
)

urlpatterns += patterns('administration.ajax',
	url(r'^ajax/admin/get_group_level/$', 'ajax_get_group_level', name='ajax_get_group_level'),
	url(r'^ajax/admin/get_master_plan_programs/$', 'ajax_get_master_plan_programs', name='ajax_get_master_plan_programs'),
)
from django.conf.urls.defaults import *

urlpatterns = patterns('accounts.views',
    (r'^accounts/login/', 'hooked_login'),
    (r'^accounts/first_time/', 'view_first_time_login'),
    
    url(r'^settings/$', 'view_user_settings', name='view_user_settings'),
)

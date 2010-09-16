import os

from django.conf.urls.defaults import *
from django.conf import settings
from django.views.static import serve

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^', include('thaihealthsms.accounts.urls')),
    (r'^', include('thaihealthsms.administration.urls')),
    (r'^', include('thaihealthsms.comment.urls')),
    (r'^', include('thaihealthsms.domain.urls')),
    (r'^', include('thaihealthsms.budget.urls')),
    (r'^', include('thaihealthsms.kpi.urls')),
    (r'^', include('thaihealthsms.report.urls')),
    
    (r'^accounts/', include('registration.backends.default.urls')),
    
    (r'^admin/(.*)', admin.site.root),
    
    url(r'^$', 'accounts.views.view_user_homepage', name='view_user_homepage'),
)

if settings.DEBUG:
    urlpatterns += patterns('', 
        (r'^m/(?P<path>.*)$', serve, {
            'document_root' : os.path.join(os.path.dirname(__file__), "media")
        })
    )
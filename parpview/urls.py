from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Example:
    # (r'^parpview/', include('parpview.foo.urls')),
    (r'^$', 'parpview.viewer.views.pgd2_dummy'),
    (r'^ut/$', 'parpview.viewer.views.usetemplate'),
    (r'^style/(?P<stylefile>[^/]+)$', 'parpview.viewer.views.getstyle'),
    (r'^pgdiff/(?P<pg1>\d+)/(?P<pg2>\d+)/$', 'parpview.viewer.views.pgroupdiff'),
    (r'^pgd1/$', 'parpview.viewer.views.pgd1_dummy'),
    (r'^pgd1/(?P<order>\w+)/(?P<sortmode>\w+)/(?P<graphmode>\w+)/(?P<pg1>\d+)/(?P<pg2>\d+)/$',
     'parpview.viewer.views.pgd1'),
    (r'^pgd2/$', 'parpview.viewer.views.pgd2_dummy'),
    (r'^pgd2/(?P<sortmode>\w+)/$',
     'parpview.viewer.views.pgd2'),
    (r'^pgd3/(?P<sortmode>\w+)/$',
     'parpview.viewer.views.pgd3'),
    (r'^pgview/(?P<pg_id>\d+)/$', 'parpview.viewer.views.pgview'),
    (r'^pgdiff/(?P<params>.+)/$', 'parpview.viewer.views.pgdiff2'),
    # Workflow
    (r'^wf/?$', 'parpview.viewer.views.wf'),
    (r'^wfinfo/(?P<wf>\d+)', 'parpview.viewer.views.workflow_info'),
    (r'^wfcinfo/(?P<wf>\d+)/(?P<wfc>\d+)',
     'parpview.viewer.views.workflow_condinfo'),
    (r'^wfdiff/(?P<wf>\d+)/(?P<wfc1>\d+)/(?P<wfc2>\d+)',
     'parpview.viewer.views.wfdiff'),
    (r'^wft-tcw/(?P<trial_id>\d+)',
     'parpview.viewer.views.wf_timechart_img'),
    (r'^wft-tc/(?P<trial_id>\d+)',
     'parpview.viewer.views.get_wf_timechart'),
    (r'^wft-tc-c/(?P<trial_id>\d+)',
     'parpview.viewer.views.wf_timechart_canvas'),
    # Static
    (r'^img/(?P<imgpath>.+\.png)$', 'parpview.viewer.views.getpng'),
    (r'^script/(?P<path>.+\.js)$', 'parpview.viewer.views.getjs'),
    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    # Resources
    (r'^resources/(?P<path>.*)$',
     'django.views.static.serve',
     {'document_root': settings.MEDIA_ROOT}),
)

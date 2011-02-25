from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^parpview/', include('parpview.foo.urls')),
    (r'^$', 'parpview.viewer.views.helloworld'),
    (r'^ut/$', 'parpview.viewer.views.usetemplate'),
    (r'^pgdiff/(?P<pg1>\d+)/(?P<pg2>\d+)/$', 'parpview.viewer.views.pgroupdiff'),
    (r'^pgd1/$', 'parpview.viewer.views.pgd1_dummy'),
    (r'^pgd1/(?P<order>\w+)/(?P<sortmode>\w+)/(?P<graphmode>\w+)/(?P<pg1>\d+)/(?P<pg2>\d+)/$',
     'parpview.viewer.views.pgd1'),
    (r'^pgview/(?P<pg_id>\d+)/$', 'parpview.viewer.views.pgview'),
    (r'^pgdiff/(?P<params>.+)/$', 'parpview.viewer.views.pgdiff2'),
    (r'^img/(?P<imgpath>.+\.png)/$', 'parpview.viewer.views.getimage'),
    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

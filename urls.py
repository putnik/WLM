from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'vologda.views.home', name='home'),
    # url(r'^vologda/', include('vologda.foo.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_ROOT}),

    (r'^tinymce/', include('tinymce.urls')),

    url(r'^robots.txt$', 'django.views.static.serve', {'path':"/robots.txt",'document_root': settings.STATIC_ROOT, 'show_indexes': False }),
    url(r'^/?$', 'wlm.views.index_page'),
    url(r'^upload/?$', 'wlm.views.upload'),
    url(r'^add/?$', 'wlm.views.add'),
    url(r'^house/(?P<id>[0-9]+)/?$', 'wlm.views.house'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^ajax/markers/(?P<zoom>\d{1,2})/(?P<x_tile>\d+)/(?P<y_tile>\d+$)', 'wlm.ajax.get_tile_markers'),
)

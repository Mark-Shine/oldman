from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'redpoint.views.home', name='home'),
    url(r'^checkin$', 'redpoint.views.checkin_page', name='show_checkin'),
    url(r'^checkin/do$', 'redpoint.views.do_checkin', name='checkin'),
    # url(r'^checkin/do$', 'redpoint.views.do_checkin', name='checkin'),

    # url(r'^blog/', include('blog.urls')),
    # (r'^photologue/', include('photologue.urls')),
    url(r'^admin/', include(admin.site.urls)),

)

from django.conf import settings

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
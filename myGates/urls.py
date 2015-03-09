from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'myGates.views.home_view'),
    url(r'^login/$', 'myGates.views.loginview'),
    url(r'^auth/$', 'myGates.views.auth_and_login'),
    url(r'^signup/$', 'myGates.views.sign_up_in'),
    url(r'^logout/$', 'myGates.views.logout_view'),
    url(r'^gates_control/$', 'myGates.views.gates_control'),
    url(r'^open_gates/$', 'myGates.views.open_gates'),
    url(r'^close_gates/$', 'myGates.views.close_gates'),
    url(r'^camera_control/$', 'myGates.views.camera_control'),
    url(r'^camera/new/$', 'myGates.camsettings.views.camera_new'),
    url(r'^camera/delete/(\d{1,2})/$', 'myGates.camsettings.views.camera_delete'),
    url(r'^camera/(\d{1,2})/$', 'myGates.views.camera'),
    url(r'^camera_snap/(\d{1,2})/$', 'myGates.views.camera_snap'),
    url(r'^camera_thumb/(\d{1,2})/$', 'myGates.views.camera_thumb'),
    url(r'^camera_start/(\d{1,2})/$', 'myGates.views.camera_start'),
    url(r'^camera_stop/(\d{1,2})/$', 'myGates.views.camera_stop'),
    url(r'^video_stream/(\d{1,2})/$', 'myGates.views.video_stream'),
    url(r'^video_record/(\d{1,2})/$', 'myGates.views.video_record'),
    url(r'^camera_control/settings/(\d{1,2})$', 'myGates.camsettings.views.camera_settings'),
    url(r'^camera_control/settings/thanks/(\d{1,2})$', 'myGates.camsettings.views.camera_settings_thanks'),
    url(r'^zwave_control/$', 'myGates.views.zwave_control'),
    url(r'^zwave/new/$', 'myGates.zwave.views.zwave_controller_new'),
    url(r'^zwave/delete/(\d{1,2})/$', 'myGates.zwave.views.zwave_controller_delete'),
    url(r'^zwave/(\d{1,2})/$', 'myGates.views.zwavecontroller'),
    url(r'^zwave_switch_off/(?P<cntr>[^/]+)/(?P<dev>\d{1,2})/(?P<inst>\d{1,2})/$', 'myGates.views.zwave_switch_off'),
    url(r'^zwave_switch_on/(?P<cntr>[^/]+)/(?P<dev>\d{1,2})/(?P<inst>\d{1,2})/$', 'myGates.views.zwave_switch_on'),
    url(r'^zwave_clear_alarms/$', 'myGates.views.zwave_clear_alarms'),
    # url(r'^$', 'myGates.views.home', name='home'),
    # url(r'^myGates/', include('myGates.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

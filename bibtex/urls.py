from django.conf.urls import patterns, url

from bibtex import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^detail/(?P<epk>\d+)/$', views.detail, name='detail'),

	url(r'^add$', views.add, name='add'),
	url(r'^edit/(?P<epk>\d+)/$', views.edit, name='edit'),

	url(r'^view$', views.view, name='view'),
	url(r'^delete_confirm/(?P<epk>\d+)/$', views.delete_confirm, name='delete_confirm'),

	url(r'^search$', views.search, name='search'),
	url(r'^getsearch$', views.getsearch, name='getsearch'),

	url(r'^validate$', views.validate, name='validate'),
)

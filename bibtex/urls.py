from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from bibtex import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^detail/(?P<epk>\d+)/$', views.detail, name='detail'),
	url(r'^api/$', views.api, name='api'),

	url(r'^add$', views.add, name='add'),
	url(r'^edit/(?P<epk>\d+)/$', views.edit, name='edit'),
	url(r'^bulkupload$', views.bulkupload, name='bulkupload'),
	url(r'^bulkuploadadd$', views.bulkuploadadd, name='bulkuploadadd'),

	url(r'^view$', views.view, name='view'),
	url(r'^delete_confirm/(?P<epk>\d+)/$', views.delete_confirm, name='delete_confirm'),

	url(r'^add_file/(?P<epk>\d+)/$', views.add_file, name='add_file'),
	url(r'^delete_file/(?P<epk>\d+)/$', views.delete_file, name='delete_file'),

	url(r'^search$', views.search, name='search'),
	url(r'^getsearch$', views.getsearch, name='getsearch'),
	url(r'^searchkey$', views.searchkey, name='searchkey'),

	url(r'^addedit$', views.addedit, name='addedit'),
)

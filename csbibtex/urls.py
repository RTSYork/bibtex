from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
	url(r'^bibtex/', include('bibtex.urls', namespace="bibtex")),
	url(r'^admin/', include(admin.site.urls)),
)

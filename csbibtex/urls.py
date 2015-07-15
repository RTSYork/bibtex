from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
	url(r'^rts/bibtex/', include('bibtex.urls', namespace="bibtex")),
	url(r'^rts/admin/', include(admin.site.urls)),
)

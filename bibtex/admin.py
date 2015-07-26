import os
from django.contrib import admin
from bibtex.models import Entry, Docfile
from django.forms import TextInput, Textarea
from django.db import models
from django.conf import settings

class DocInline(admin.TabularInline):
	def link(self, instance):
		l = settings.MEDIA_URL + instance.filename
		return "<a href=\"" + l + "\">" + l + "</a>"
	link.allow_tags = True
	extra = 0
	model = Docfile
	readonly_fields = ('link',)


class FileNumFilter(admin.SimpleListFilter):
	title = 'num files'
	parameter_name = 'numfiles'

	def lookups(self, request, model_admin):
		return (
			('0', '0'),
			('1', '1'),
			('more', '> 1'),
		)

	def queryset(self, request, queryset):
		rv = set()
		for item in queryset:
			count = len(item.docfile_set.all())
			if self.value() == '0' and count == 0:
				rv.add(item.pk)
			elif self.value() == '1' and count == 1:
				rv.add(item.pk)
			elif self.value() == 'more' and count > 1:
				rv.add(item.pk)
		return queryset.filter(pk__in = rv)



class EntryAdmin(admin.ModelAdmin):
	list_display = (
		'key', 
		'owner', 
		'author', 
		'title',
		'year',
		'num_attached_files', 
		'has_abstract'
	)

	list_filter = ['entered', FileNumFilter, 'year']
	search_fields = ['key', 'owner', 'author', 'title', 'abstract']
	inlines = [DocInline]

	fieldsets = [
		(None, {'fields': [
			'key', 
			('owner', 'entered'),
			('author', 'year'),
			'title', 
			('abstract', 'bib'),
		]}),
		('Website optional', {
			'classes': ('collapse',),
			'fields': ['imgurl', 'html', 'downloadurl']
		}),
	]

	formfield_overrides = {
		models.TextField: {'widget': Textarea(attrs={'rows':10, 'cols': 60})},
		models.CharField: {'widget': TextInput(attrs={'size':100})}
	}


class DocfileAdmin(admin.ModelAdmin):
	pass

admin.site.register(Entry, EntryAdmin)
admin.site.register(Docfile, DocfileAdmin)



from django.contrib import admin
from bibtex.models import Entry, Docfile
from django.forms import TextInput, Textarea
from django.db import models

class DocInline(admin.StackedInline):
	extra = 0
	model = Docfile


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

	list_filter = ['year', 'entered']
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



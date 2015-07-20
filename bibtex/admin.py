from django.contrib import admin
from bibtex.models import Entry, Docfile

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

class DocfileAdmin(admin.ModelAdmin):
	pass

admin.site.register(Entry, EntryAdmin)
admin.site.register(Docfile, DocfileAdmin)



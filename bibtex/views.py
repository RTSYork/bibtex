from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django import forms

from bibtex.models import Entry, Docfile
import bibtex.library as library


def index(request):
	return render(request, 'bibtex/index.html', {
			'username': library.get_username(),
			'recent': Entry.objects.order_by('-entered')[:5],
		}
	)


def view(request):
	return render(request, 'bibtex/view.html', {
			'username': library.get_username(),
			'entries': Entry.objects.filter(owner=library.get_username()).order_by('-entered'),
		}
	)


def detail(request, epk):
	entry = get_object_or_404(Entry, pk=epk)
	return render(request, 'bibtex/detail.html', {
		'entry': entry, 
		'docfile_set': entry.docfile_set.all(),
		'abstract': library.get_entry_bibtex_data(entry.bib, 'abstract'),
		'owner': (entry.owner == library.get_username()),
	})


def add(request):
	return render(request, 'bibtex/add.html', {
		'username': library.get_username(),
		'entry': None
	})


def edit(request, epk):
	entry = None
	if epk != None: entry = get_object_or_404(Entry, pk=epk)
	return render(request, 'bibtex/add.html', {
		'username': library.get_username(),
		'entry': entry
	})


def delete_confirm(request, epk):
	entry = get_object_or_404(Entry, pk=epk)
	if entry.owner == library.get_username():
		entry.delete()
		return HttpResponse("OK")
	else:
		return HttpResponse("You do not own this entry.")


def search(request):
	return render(request, 'bibtex/search.html', {
		'fromyear': Entry.objects.order_by('year')[0].year,
		'toyear': Entry.objects.order_by('-year')[0].year,
	})


def getsearch(request):
	if not 'term' in request.POST: return HttpResponse("")
	query_string = request.POST['term'].strip()
	search_fields = []
	if 'search_title' in request.POST: search_fields.append('title')
	if 'search_author' in request.POST: search_fields.append('author')
	if 'search_all' in request.POST: search_fields.append('bib')
	entry_query = library.get_query(query_string, search_fields)
	if entry_query:
		found_entries = Entry.objects.filter(entry_query).order_by('-entered')
	else:
		found_entries = Entry.objects.order_by("-entered")

	if 'fromyear' in request.POST: found_entries = found_entries.filter(year__gte=int(request.POST['fromyear']))
	if 'toyear' in request.POST: found_entries = found_entries.filter(year__lte=int(request.POST['toyear']))

	return render(request, 'bibtex/searchresults.html', {'results': found_entries})


def validate(request):
	error = library.validate_bibtex(request.POST['bib'])
	db = None
	if not error:
		#If not editing, check the key is not already used (not strictly required but will assist with export)
		db = library.parse_bibstring(request.POST['bib'])
		if not 'edit' in request.POST:
			if len(Entry.objects.filter(key=db.entries[0]['id'])) > 0:
				error = "The key " + str(db.entries[0]['id']) + " is already present in the database."

	if not error:
		#All ok, add the details
		if 'edit' in request.POST:
			#Edit the existing entry
			entry = get_object_or_404(Entry, pk=request.POST['pk'])
			entry.entered = datetime.utcnow()
			entry.key = db.entries[0]['id']
			entry.title = db.entries[0]['title']
			entry.author = db.entries[0]['author']
			entry.year = db.entries[0]['year']
			entry.bib = request.POST['bib']
			entry.save()
		else:
			#Add a new entry
			Entry.objects.create(
				owner = library.get_username(),
				entered = datetime.utcnow(),
				key = db.entries[0]['id'],
				title = db.entries[0]['title'],
				author = db.entries[0]['author'],
				year = db.entries[0]['year'],
				bib = request.POST['bib'],
			)
		return HttpResponse("OK")
	else:
		return HttpResponse(error)



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

	print "@@"
	print entry.bib
	print library.get_entry_bibtex_data(entry.bib, 'abstract')
	print "@@"

	return render(request, 'bibtex/detail.html', {
		'entry': entry, 
		'docfile_set': entry.docfile_set.all(),
		'ftpbase': library.get_ftp_web_path(),
		'abstract': library.get_entry_bibtex_data(entry.bib, 'abstract'),
		'owner': (entry.owner == library.get_username()),
	})


def add(request):
	if library.get_username != "":
		return render(request, 'bibtex/add.html', {
			'username': library.get_username(),
			'entry': None
		})


def edit(request, epk):
	entry = None
	if epk != None: entry = get_object_or_404(Entry, pk=epk)
	return render(request, 'bibtex/add.html', {
		'username': library.get_username(),
		'docfile_set': entry.docfile_set.all(),
		'ftpbase': library.get_ftp_web_path(),
		'entry': entry
	})


def delete_confirm(request, epk):
	entry = get_object_or_404(Entry, pk=epk)
	if entry.owner == library.get_username():
		entry.delete()
		return HttpResponse("OK")
	else:
		return HttpResponse("You do not own this entry.")


def add_file(request, epk):
	entry = get_object_or_404(Entry, pk=epk)
	if entry.owner == library.get_username():
		if not 'file' in request.FILES:
			return HttpResponse("No file was submitted.")

		filename = library.write_file(request.FILES['file'], "somename")
		if filename != None:
			doc = Docfile.objects.create(entry = entry, filename = filename)
		else:
			return HttpResponse("Error whilst saving file. Please contact the database admin.")
		return HttpResponse("OK" + str(filename))
	else:
		return HttpResponse("You do not own the entry this file is attached to.")


def delete_file(request, epk):
	docfile = get_object_or_404(Docfile, pk=epk)
	entry = docfile.entry
	if entry.owner == library.get_username():
		docfile.delete()
		return HttpResponse("OK")
	else:
		return HttpResponse("You do not own the entry this file is attached to.")



def search(request):
	return render(request, 'bibtex/search.html', {
		'fromyear': Entry.objects.order_by('year')[0].year,
		'toyear': Entry.objects.order_by('-year')[0].year,
	})


def getsearch(request):
	vars = None
	if request.method == 'GET': vars = request.GET
	else: vars = request.POST

	if not 'term' in vars: query_string = ""
	else: query_string = vars['term'].strip()

	search_fields = []
	if 'search_title' in vars: search_fields.append('title')
	if 'search_author' in vars: search_fields.append('author')
	if 'search_all' in vars: search_fields.append('bib')
	entry_query = library.get_query(query_string, search_fields)
	if entry_query:
		found_entries = Entry.objects.filter(entry_query).order_by('-entered')
	else:
		found_entries = Entry.objects.order_by("-entered")

	if 'fromyear' in vars: found_entries = found_entries.filter(year__gte=int(vars['fromyear']))
	if 'toyear' in vars: found_entries = found_entries.filter(year__lte=int(vars['toyear']))

	if request.method == 'GET':
		return render(request, 'bibtex/searchresults_plain.html', {'results': found_entries})
	else:
		return render(request, 'bibtex/searchresults.html', {'results': found_entries})


def validate(request):
	if library.get_username != "":
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
				if entry.owner == library.get_username():		
					entry.entered = datetime.utcnow()
					entry.key = db.entries[0]['id']
					entry.title = library.strip_braces(db.entries[0]['title'])
					entry.author = db.entries[0]['author']
					entry.year = db.entries[0]['year']
					entry.bib = request.POST['bib']
					entry.save()
			else:
				#Add a new entry
				entry = Entry.objects.create(
					owner = library.get_username(),
					entered = datetime.utcnow(),
					key = db.entries[0]['id'],
					title = library.strip_braces(db.entries[0]['title']),
					author = db.entries[0]['author'],
					year = db.entries[0]['year'],
					bib = request.POST['bib'],
				)

			#Now, do we also have a file to upload?
			if 'file' in request.FILES:
				filename = library.write_file(request.FILES['file'], "somename")
				if filename != None:
					doc = Docfile.objects.create(entry = entry, filename = filename)
				else:
					return HttpResponse("BADFILE" + str(entry.pk))

			#All OK
			resp = HttpResponse("OK" + str(entry.pk))
			return resp
		else:
			resp = HttpResponse(error)
			return resp

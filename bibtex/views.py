from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpRequest, Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django import forms
from django.conf import settings

from bibtex.models import Entry, Docfile
import bibtex.library as library
import string


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
		'ftpbase': settings.MEDIA_URL,
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
		'ftpbase': settings.MEDIA_URL,
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

		origfilename = request.FILES['file']._name
		filename = library.write_file(request.FILES['file'], origfilename)

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


def searchkey(request):
	if 'key' in request.POST:
		if len(Entry.objects.filter(key__iexact=request.POST['key'])) > 0:
			return HttpResponse("YES")
		else:
			return HttpResponse("NO")


def addedit(request):
	if library.get_username() == "":
		return HttpResponse("Bad request.")
	if not ((request.POST.get('entryMode', None) == 'raw') or (request.POST.get('entryMode', None) == 'fields')):
		return HttpResponse("Bad request.")

	#If field input, then assemble the bibstring first
	if request.POST['entryMode'] == 'fields':
		assembledbib = library.assemble_bib(request)
	else:
		assembledbib = request.POST['bib']

	#Validate (and parse) the bibtex string
	error = library.validate_bibtex(assembledbib)
	db = None
	if not error:
		#If adding a new item, check the key is not already used
		db = library.parse_bibstring(assembledbib)
		if not 'edit' in request.POST:
			if len(Entry.objects.filter(key=db.entries[0]['id'])) > 0:
				error = "The key " + str(db.entries[0]['id']) + " is already present in the database."
	if error:
		return HttpResponse(error)

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
			entry.bib = assembledbib
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
			bib = assembledbib
		)

	#Now, do we also have a file to upload?
	if 'file' in request.FILES:
		origfilename = request.FILES['file']._name
		filename = library.write_file(request.FILES['file'], origfilename)
		if filename != None:
			doc = Docfile.objects.create(entry = entry, filename = filename)
		else:
			return HttpResponse("BADFILE" + str(entry.pk))

	#Maybe send an email
	if 'email' in request.POST:
		library.send_email(db, entry, request.build_absolute_uri(reverse('bibtex:detail', args=[entry.pk])))

	return HttpResponse("OK" + str(entry.pk))

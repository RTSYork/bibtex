from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpRequest, Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django import forms
from django.conf import settings
from django.core.files.base import ContentFile

from bibtex.models import Entry, Docfile
import bibtex.library as library
import string, json, os
import bibtexparser


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

		_, ext = os.path.splitext(request.FILES['file']._name) 
		origfilename = entry.key + ext
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

	if not 'term' in vars: 
		query_string = ""
	else: 
		query_string = vars['term'].strip()


	if 'search_bibkey' in vars:
		found_entries = Entry.objects.filter(key=query_string)
	elif 'search_dbkey' in vars:
		try:
			keyid = int(query_string)
			found_entries = Entry.objects.filter(pk=keyid)
		except:
			found_entries = []
	else:
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

	if not 'output' in vars:
		return render(request, 'bibtex/searchresults.html', {'results': found_entries})
	else:
		if vars['output'] == 'json':
			return HttpResponse(json.dumps(library.make_json_serialisable(found_entries)))
		else:
			return render(request, 'bibtex/searchresults_plain.html', {'results': found_entries, 'output': vars['output']})


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

	if not 'abstract' in db.entries[0]:
		db.entries[0]['abstract'] = ""

	#All ok, add the details
	if 'edit' in request.POST:
		#Edit the existing entry
		entry = get_object_or_404(Entry, pk=request.POST['pk'])
		if entry.owner == library.get_username():		
			entry.entered = datetime.utcnow()
			#entry.key = db.entries[0]['id'] #Editing should not change the key
			entry.title = library.sanitise(db.entries[0]['title'])
			entry.author = library.sanitise(db.entries[0]['author'])
			entry.abstract = db.entries[0]['abstract']
			entry.year = db.entries[0]['year']
			entry.bib = assembledbib
			entry.save()
	else:
		#Add a new entry
		entry = Entry.objects.create(
			owner = library.get_username(),
			entered = datetime.utcnow(),
			key = db.entries[0]['id'],
			title = library.sanitise(db.entries[0]['title']),
			author = library.sanitise(db.entries[0]['author']),
			abstract = db.entries[0]['abstract'],
			year = db.entries[0]['year'],
			bib = assembledbib
		)

	#Now, do we also have a file to upload?
	if 'file' in request.FILES:
		_, ext = os.path.splitext(request.FILES['file']._name) 
		origfilename = entry.key + ext
		filename = library.write_file(request.FILES['file'], origfilename)
		if filename != None:
			doc = Docfile.objects.create(entry = entry, filename = filename)
		else:
			return HttpResponse("BADFILE" + str(entry.pk))

	#Maybe send an email
	if 'email' in request.POST:
		library.send_email(db, entry, request.build_absolute_uri(reverse('bibtex:detail', args=[entry.pk])))

	return HttpResponse("OK" + str(entry.pk))


def bulkupload(request):
	if library.get_username != "":
		return render(request, 'bibtex/bulkupload.html', {'username': library.get_username()})

def bulkuploadadd(request):
	if library.get_username() == "":
		return HttpResponse("Bad request.")
	if not 'file' in request.FILES:
		return HttpResponse("No file was submitted.")

	bibtext = request.FILES['file'].read()

	print bibtext

	error = library.validate_bulk_bibtex(bibtext)
	if error:
		return HttpResponse(error)
	db = library.parse_bibstring(bibtext)
	if len(db.entries) < 1:
		return HttpResponse("No entries found in uploaded file.")

	for bibe in db.entries:
		if not 'abstract' in bibe:
			bibe['abstract'] == ""

		#Sort out the key
		#If it is in the old RTS format of R:Bloggs:2001a then we can use this information
		#if bibe['id'].startswith("R:"):
		#	t = bibe['id'][2:]
		#	if t.find(':') > 0:
		#		surname = t[:t.find(':')]
		#		year = t[t.find(':')+1:]
		#		newkey = library.get_new_bibkey(year, surname)
		#else:
		#Else, we can't
		newkey = library.get_new_bibkey(bibe['year'], bibe['author'])

		bibe['id'] = newkey

		#Dump the raw bibtex for this current entry
		newdb = bibtexparser.bibdatabase.BibDatabase()
		newdb.entries.append(bibe)
		rawbib = bibtexparser.dumps(newdb, bibtexparser.bwriter.BibTexWriter())

		entry = Entry.objects.create(
			owner = library.get_username(),
			entered = datetime.utcnow(),
			key = newkey,
			title = library.sanitise(bibe['title']),
			author = library.sanitise(bibe['author']),
			abstract = bibe['abstract'],
			year = bibe['year'],
			bib = rawbib
		)

	return HttpResponse("OK")

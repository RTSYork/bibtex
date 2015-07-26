from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpRequest, Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django import forms
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from bibtex.models import Entry, Docfile
import bibtex.library as library
import string, json, os
import bibtexparser
import bibsettings

def index(request):
	return render(request, 'bibtex/index.html', {
			'username': library.get_username(request),
			'recent': Entry.objects.order_by('-entered')[:5],
			'maintainer': bibsettings.maintainer
		}
	)


def view(request):
	return render(request, 'bibtex/view.html', {
			'username': library.get_username(request),
			'entries': Entry.objects.filter(owner=library.get_username(request)).order_by('-entered'),
		}
	)

def api(request):
	return render(request, 'bibtex/api.html', {'maintainer': bibsettings.maintainer})


def stats(request):
	fromyear = Entry.objects.order_by('year')[0].year
	toyear = Entry.objects.order_by('-year')[0].year

	data = "[\n"
	for i in range(fromyear, toyear+1):
		count = len(Entry.objects.filter(year=i))

		data += "\t{ label: " + str(i) + ", y: " + str(count) + " },\n"
	data += "];\n"

	return render(request, 'bibtex/stats.html', {'data': data})


def detail(request, epk):
	entry = get_object_or_404(Entry, pk=epk)
	return render(request, 'bibtex/detail.html', {
		'entry': entry, 
		'docfile_set': entry.docfile_set.all(),
		'ftpbase': settings.MEDIA_URL,
		'owner': (entry.owner == library.get_username(request)),
	})


def deldups(request):
	dup = set()
	for item in Entry.objects.all():
		count = len(item.docfile_set.all())
		if count > 1:
			for df in item.docfile_set.all():
				try:
					year = int(item.key[-4:])
					name = item.key[:-4]
					if not df.filename.startswith('R:' + name + ":" + str(year) + "."):
						repl = df.filename[1:].replace(':', '')
						repl = os.path.splitext(repl)[0]
						if len(Entry.objects.filter(key = repl)) > 0:
							dup.add("Remove " + str(df.filename) + " from " + str(item))
				except ValueError:
					pass
	return render(request, 'bibtex/dups.html', {'dups': dup})


def add(request):
	if library.get_username(request) != "":
		return render(request, 'bibtex/add.html', {
			'username': library.get_username(request),
			'entry': None
		})


def edit(request, epk):
	entry = None
	if epk != None: entry = get_object_or_404(Entry, pk=epk)
	return render(request, 'bibtex/add.html', {
		'username': library.get_username(request),
		'docfile_set': entry.docfile_set.all(),
		'ftpbase': settings.MEDIA_URL,
		'entry': entry
	})


def delete_confirm(request, epk):
	entry = get_object_or_404(Entry, pk=epk)
	if entry.owner == library.get_username(request):
		entry.delete()
		return HttpResponse("OK")
	else:
		return HttpResponse("You do not own this entry.")


def add_file(request, epk):
	entry = get_object_or_404(Entry, pk=epk)
	if entry.owner == library.get_username(request):
		if not 'file' in request.FILES:
			return HttpResponse("No file was submitted.")

		_, ext = os.path.splitext(request.FILES['file']._name) 
		origfilename = entry.key + ext
		ok, filename = library.write_file(request.FILES['file'], origfilename)
		if ok:
			doc = Docfile.objects.create(entry = entry, filename = filename)
		else:
			return HttpResponse("Error whilst saving file. Please contact the database admin. Error: " + filename)
		return HttpResponse("OK" + str(filename))
	else:
		return HttpResponse("You do not own the entry this file is attached to.")


def delete_file(request, epk):
	docfile = get_object_or_404(Docfile, pk=epk)
	entry = docfile.entry
	if entry.owner == library.get_username(request):
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
	if library.get_username(request) == "":
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
	if error:
		return HttpResponse(error)

	db = library.parse_bibstring(assembledbib)

	if not 'abstract' in db.entries[0]:
		db.entries[0]['abstract'] = ""

	#Update the key based on the author and year, and update the bibtex
	#If Editing, we can keep the same key. If not, we generate an unused one.
	if 'edit' in request.POST:
		db.entries[0]['id'] = library.get_new_bibkey(db.entries[0]['year'], db.entries[0]['author'], library.get_username(request), db.entries[0]['id'])
	else:
		db.entries[0]['id'] = library.get_new_bibkey(db.entries[0]['year'], db.entries[0]['author'], library.get_username(request))
	newdb = bibtexparser.bibdatabase.BibDatabase()
	newdb.entries.append(db.entries[0])

	wr = bibtexparser.bwriter.BibTexWriter()
	assembledbib = wr.write(newdb).encode('utf-8')

	#All ok, add the details
	if 'edit' in request.POST:
		#Edit the existing entry
		entry = get_object_or_404(Entry, pk=request.POST['pk'])
		if entry.owner == library.get_username(request):		
			entry.entered = datetime.utcnow()
			entry.key = db.entries[0]['id']
			entry.title = library.sanitise(db.entries[0]['title'])
			entry.author = library.sanitise(db.entries[0]['author'])
			entry.abstract = db.entries[0]['abstract']
			entry.year = db.entries[0]['year']
			entry.bib = assembledbib
			entry.save()
	else:
		#Add a new entry
		entry = Entry.objects.create(
			owner = library.get_username(request),
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
		ok, filename = library.write_file(request.FILES['file'], origfilename)
		if ok:
			doc = Docfile.objects.create(entry = entry, filename = filename)
		else:
			return HttpResponse("BADFILE" + str(entry.pk))

	#Maybe send an email
	if 'email' in request.POST:
		library.send_email(db, entry, request.build_absolute_uri(reverse('bibtex:detail', args=[entry.pk])), request)

	return HttpResponse("OK" + str(entry.pk))


def bulkupload(request):
	if library.get_username(request) != "":
		return render(request, 'bibtex/bulkupload.html', {
			'username': library.get_username(request),
			'maintainer': bibsettings.maintainer
		})

def bulkuploadadd(request):
	if library.get_username(request) == "":
		return HttpResponse("Bad request.")
	if not 'file' in request.FILES:
		return HttpResponse("No file was submitted.")

	bibtext = request.FILES['file'].read()
	error = library.validate_bulk_bibtex(bibtext)
	if error:
		return HttpResponse(error)
	db = library.parse_bibstring(bibtext)
	if len(db.entries) < 1:
		return HttpResponse("No entries found in uploaded file.")

	for bibe in db.entries:
		if not 'abstract' in bibe:
			bibe['abstract'] = ""
		origkey = bibe['id']
		bibe['id'] = library.get_new_bibkey(bibe['year'], bibe['author'], library.get_username(request))

		#Some fields are not supposed to appear in the raw bibtex
		datafields = ['image_url', 'abstract_html', 'download_url']
		dfs = {}
		for f in datafields:
			dfs[f] = bibe.get(f, "")
			if f in bibe: 
				del bibe[f]

		if dfs['download_url'] == "nil":
			dfs['download_url'] = ""

		newdb = bibtexparser.bibdatabase.BibDatabase()
		newdb.entries.append(bibe)

		wr = bibtexparser.bwriter.BibTexWriter()
		rawbib = wr.write(newdb).encode('utf-8')

		if 'uploaded_time' in bibe:
			try:
				etime = datetime.strptime(bibe['uploaded_time'], "%Y-%m-%d %H:%M:%S") 
			except:
				etime = datetime.utcnow()
		else:
			etime = datetime.utcnow()

		entry = Entry.objects.create(
			owner = library.get_username(request),
			entered = etime,
			key = bibe['id'],
			title = library.sanitise(bibe['title']),
			author = library.sanitise(bibe['author']),
			abstract = bibe['abstract'],
			year = bibe['year'],
			imgurl = dfs['image_url'],
			html = dfs['abstract_html'],
			downloadurl = dfs['download_url'],
			bib = rawbib
		)

		#Now is there a file already in the FTP directory for this? (Used by the migration from the original database)
		for f in os.listdir(settings.MEDIA_ROOT):
			path = os.path.join(settings.MEDIA_ROOT,f)
			if os.path.isfile(path) and f.startswith(origkey):
				Docfile.objects.create(entry = entry, filename = f)

	return HttpResponse("OK")

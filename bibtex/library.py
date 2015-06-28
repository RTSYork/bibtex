import bibtexparser
from bibtexparser.bparser import BibTexParser
import re, sys, logging, os, string

from bibtex.models import Entry, Docfile
import latextounicode

from django.db.models import Q
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.mail import send_mail

def parse_bibstring(bibstring):
	parser = BibTexParser()
	parser.ignore_nonstandard_types = False
	"""
	The \n is added to the bibstring because it appears that the final entry is not 
	correctly parsed if there is no trailing newline.
	"""
	return bibtexparser.loads(bibstring + "\n", parser)

def get_entry_bibtex_data(bibstring, data):
	db = parse_bibstring(bibstring)
	if len(db.entries) != 1:
		#Some parse error
		return None
	try:
		return db.entries[0][data]
	except KeyError:
		#Key does not exist
		return None


def check_bibtex_entry(entry, fix = False):
	"""
	Check whether an entry is suitable for the database. Returns None if all is ok, else
	returns a user-readable string describing the error.

	If fix is set to true then will 'fix' any problems by replacing errors with dummy values.
	This is only useful during testing and development.
	"""
	errors = []
	mandatory = ['id', 'title', 'author', 'year']
	for f in mandatory:
		if not f in entry:
			errors.append("The entry did not include the '" + f + "' field.")
			if fix:
				if f == "year":
					entry['year'] = "2000"
				else:
					entry[f] = "No" + f
	yearstr = entry['year']
	try:
		year = int(yearstr)
	except ValueError:
		errors.append("The year field should be a single integer year, i.e. '2001'.")
		if fix:
			entry['year'] = "2000"
	
	if len(errors) == 0:
		return None
	else:
		rv = ""
		for e in errors:
			rv += e + " "
		return rv


def fix_bulk_bibfile(infilename, outfilename):
	"""
	This is not used by the actual site, but is a utility function that can be called from 
	the django shell. (python manage.py shell)
	Will 'fix' common errors in a bulk bibtex file. This is no substitute for manually editing
	however, and is really only useful during testing and development.
	"""
	with open(infilename) as bibtex_file:
		bibtex_database = bibtexparser.load(bibtex_file)
		for e in bibtex_database.entries:
			error = check_bibtex_entry(e, True)
			if error != None:
				print "Error in entry " + str(e['id']) + ": " + str(error) + "  fixed."
	with open(outfilename, "w") as outfile:
		wr = bibtexparser.bwriter.BibTexWriter()
		outfile.write(wr.write(bibtex_database).encode('utf-8'))


def validate_bulk_bibtex(bibstring):
	db = parse_bibstring(bibstring)
	for entry in db.entries:
		rv = check_bibtex_entry(entry)
		if rv != None:
			return rv
	return None

def validate_bibtex_file(filename):
	with open(filename) as bibtex_file:
		bibtex_database = bibtexparser.load(bibtex_file)
		for e in bibtex_database.entries:
			error = check_bibtex_entry(e)
			if error != None:
				print "Error in entry " + str(e['id']) + ": " + str(error)


def validate_bibtex(bibstring):
	db = parse_bibstring(bibstring)
	if len(db.entries) != 1: 
		return "Your bibtex entry did not parse correctly."
	entry = db.entries[0]
	return check_bibtex_entry(entry)


def write_file(uploadedfile, origfilename):
	"""
	Write the file into MEDIA_ROOT
	Will check if there already is a file with that name, and if so, add _x onto the end of the name
	(but before the extension), where x is a positive integer.
	"""
	try:
		name, ext = os.path.splitext(origfilename)
		if default_storage.exists(name + ext):
			add = 1
			while default_storage.exists(name + "_" + str(add) + ext):
				add = add + 1
			outfname = name + "_" + str(add) + ext
		else:
			outfname = name + ext

		path = default_storage.save(outfname, ContentFile(uploadedfile.read()))
		print path
		return path
	except Exception as e:
		print str(e.message)
		#logger = logging.getLogger(__name__)
		#logger.error(str(e))
		return None


def get_username():
	return "iang"


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 



def strip_braces(text):
	'''
	Removes curly braces { and } from a string, unless those braces are escaped with
	a preceeding backslash: \{ \}
	The unholy regex uses negative lookbehind.
	'''
	return re.compile(r'(?<!\\)\{|(?<!\\)\}', flags=re.UNICODE).sub("", text)


def sanitise(text):
	"""
	Called when updating or adding to the database to create nice titles and auther 
	names etc.
	Strips out { } and converts latex accent commands into their Unicode equivalents
	"""
	converted = latextounicode.convert_string(text)
	stripped = strip_braces(converted)
	return stripped


def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    
    '''
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def send_email(db, entry, url):
	mailtemplate = """$user has added a new paper to the RTS Bibtex database. It can be viewed at:
$link

Paper details:
Title: $title
Author: $author
"""
	mailbody = string.Template(mailtemplate).substitute({
		'user': get_username(),
		'link': url,
		'title': entry.title,
		'author': entry.author
	})

	if entry.abstract != "":
		mailbody = mailbody + "Abstract: " + entry.abstract + "\n"
	mailbody = mailbody + "\n\nBibtex: " + entry.bib + "\n"

	try:
		pass
		#send_mail("New paper published", 
		#	mailbody, 
		#	'rtsbibtex-no-reply@cs.york.ac.uk', 
		#	['rts-group@york.ac.uk'],
		#	fail_silently=False)
	except:
		pass


def author_to_bibkey(s):
	try:
		allowed = [':', '-']
		names = bibtexparser.customization.getnames([i.strip() for i in s.replace('\n', ' ').split(" and ")])
		if len(names) < 1: 
			return None
		co = names[0].find(',')
		if co > 0:
			out = ""
			for c in names[0][:co]:
				if (c >= 'A' and c <= 'Z') or (c >= 'a' and c <= 'z') or (c >= '0' and c <= '9') or c in allowed:
					out = out + c
			if out == "":
				return None
			return out
		else:
			return None
	except:
		return None


def get_new_bibkey(year, author, existingkey=None):
	"""
	Return an unused bibtex key of the format SurnameYear
	Adds disambiguating letters from 'a' if multiple such keys exist
	If existingkey is not None, then we won't check for conflicts against existingkey
	"""
	bibauth = author_to_bibkey(author)
	if bibauth == None:
		bibauth = get_username()
	key = bibauth + str(year)
	
	if key != existingkey:
		if len(Entry.objects.filter(key=key)) > 0:
			disamb = 1
			key = key + chr(96 + disamb) #chr(97) == 'a'
			while len(Entry.objects.filter(key=key)) > 0: #while that key exists in the db
				if disamb == 26:
					#if this code ever triggers, someone has been very productive!
					disamb = 1
					key = key[:-1]
					key = key + 'aa'
				else:
					disamb = disamb + 1
					key = key[:-1]
					key = key + chr(96 + disamb)
	return key

def assemble_bib(request):
	p = request.POST
	bib = "@" + p['entrytype'] + "{" + get_new_bibkey(request.POST.get('manual_year', 'NoYear'), request.POST.get('manual_author', None)) + ",\n"
	for postitem, v in p.iteritems():
		val = str(v).strip()
		if postitem.startswith("manual_") and val != "":
			fieldname = postitem[7:]
			bib = bib + "\t" + fieldname + " = {" + val + "},\n" 
	bib = bib + "}\n"
	return bib


def make_json_serialisable(found_entries):
	out = {}
	for e in found_entries:
		item = {}
		item['owner'] = e.owner
		item['title'] = e.title
		item['year'] = e.year
		item['author'] = e.author 
		item['abstract'] = e.abstract
		item['bib'] = e.bib
		item['id'] = e.id
		item['lastedited'] = str(e.entered)

		if e.imgurl != "":
			item['imgurl'] = e.imgurl
		if e.html != "":
			item['html'] = e.html

		files = []
		for f in e.docfile_set.all():
			files.append(f.filename)

		item['files'] = files
		out[e.key] = item

	return out



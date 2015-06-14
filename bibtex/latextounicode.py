#!/usr/bin/env python
# -*- coding: latin-1 -*-

"""
Contains functions to convert a string containing Latex accent commands into
their Unicode equivalent. For example, to convert:
r'Michael Gonz\'{a}lez Harbour' into r'Michael González Harbour'

Not all commands are recognised because it is hard to get an exhaustive list 
of Latex accent commands. Also, only European languages are really attempted
due to the author's lack of knowledge.

Entry point is convert_string
"""

#Many Latex accent commands can be directly converted into Unicode combining characters
#This converts things like \^{a} into â
unicode_map = {
	'`': u'\u0300',
	"'": u'\u0301',
	'^': u'\u0302',
	'~': u'\u0303',
	'=': u'\u0304',
	'u': u'\u0306',
	'.': u'\u0307',
	'"': u'\u0308',
	'H': u'\u0308',
	'd': u'\u0323'
}

#For commands which do not correspond to a combining character.
#This converts things like \c{c} into ç
replace_map = {
	'c': {'c': 'ç'},
	'k': {'a': 'ą'},
	'l': {'': 'ł'},
	'o': {'': 'ø'},
	'r': {'a': 'å'},
	'a': {'a': 'å'},
	'v': {'s': 'š'},
}

#Latex has commands for 'undotted' i and j. This complication is automatically handled by Unicode
arg_map = {
	'\\i': 'i',
	'\\j': 'j'
}


def convert_string(s):
	"""
	Given a string, search for Latex accent commands and return a Unicode string that has
	the accent commands replaced with ther Unicode equivalents.

	Note that braces that are not part of an accent command (or which simply surround an accent 
	command) are left in. For example, r'{\^{a}}' becomes '{â}' whereas r'\^{a}' becomes 'â'.
	This is because it is easy to strip out braces just before display, but they may be required
	by other parse stages.
	"""

	#First, anything in arg_map can be trivially replaced
	for arg, rep in arg_map.iteritems():
		s = s.replace(arg, rep)

	converted = ""
	last = 0
	conv_points = get_conversion_points(s)
	for srt, end, cmd, arg in conv_points:
		conv = get_conversion(cmd, arg)
		if conv != None:
			converted += s[last:srt] + get_conversion(cmd, arg)
		else:
			converted += s[last:end]
		last = end + 1
	converted += s[last:]
	return converted


def get_conversion(cmd, arg):
	if cmd == "&":
		#HTML entity
		return '&' + arg.replace('\\', '')
	elif cmd in unicode_map:
		return arg + unicode_map[cmd]
	elif cmd in replace_map and arg in replace_map[cmd]:
		return replace_map[cmd][arg]
	else:
		#Cannot convert
		return None


def get_conversion_points(s):
	"""
	Returns a list of tuples of (startpoint, endpoint, cmd, arg)
	s[startpoint:endpoint] is the entire identified command.

	Uses a simple state machine to parse the string. This could also have
	been done with regexs, but this is faster and easy to make handle
	things like optional arguments.
	"""
	rv = []
	pos = 0
	while pos < len(s):
		if s[pos] == '\\': #All commands start with a \
			repstart = pos
			pos += 1
			cmd = s[pos] #All accent commands are single character names
			pos = pos + 1
			if s[pos] == '{': #{ } are optional for the argument
				pos += 1
				arg = ""
				while s[pos] != '}':
					arg += s[pos] #Build 'arg' as the contents of the { }
					pos += 1
			else:
				arg = s[pos] #If { } were not used, 'arg' is the next char
			repend = pos
			rv.append((repstart, repend, cmd, arg))
		pos = pos + 1
	return rv



if __name__ == "__main__":
	teststrings = [
		r"AB\'{a}CD",
		r"AB\'aCD",
		r"AB\'\iCD",
		r"AB\'{\i}CD",
		r"A. Burns and M. Gonz\'alez Harbour",
		r"J. \'{A}lvarez",
		r"G. Rodr\'{\i}guez-Navas",
		r"Michael Gonz\'{a}lez Harbour",
		r"Gu. Rodr{\'\i}guez-Navas",
		r"P. Ver\&\#237;ssimo",
		r"A. Llamos\'{\i}",
		r"M. Gonz\'{a}lez Harbour and Gu. Rodr{\'\i}guez-Navas and A. Llamos\'{\i}",
		r"\`{o}\'{o}\^{o}\"{o}\H{o}",
	]

	for s in teststrings:
		print convert_string(s)
		print

def test_file(filename):
	from bibtexparser.bparser import BibTexParser
	import bibtexparser
	f = open(filename).read()
	parser = BibTexParser()
	parsed = bibtexparser.loads(f + "\n", parser)
	for e in parsed.entries:
		if 'author' in e:
			if e['author'].find('\\') != -1:
				print e['author']
				convert_string(e['author'])

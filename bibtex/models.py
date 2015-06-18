import datetime

from django.db import models
from django.utils import timezone

class Entry(models.Model):
	#The username of the user who entered this entry
	owner = models.CharField(max_length=50)

	#When was this entry added to the database
	entered = models.DateTimeField('date entered')

	#Selected important fields from the bibtex
	key = models.CharField(max_length=50)
	title = models.CharField(max_length=200)
	author = models.CharField(max_length=200)
	year = models.IntegerField()
	abstract = models.TextField(default="")

	#The plain text version of the bibtex entry
	bib = models.TextField()

	#Additional information requested for the main website
	imgurl = models.CharField(max_length=100, default="")
	html = models.TextField(default="")

	def num_attached_files(self):
		return len(self.docfile_set.all())
	num_attached_files.short_description = "Files"

	def has_abstract(self):
		return self.abstract != ""
	has_abstract.short_description = "Abstract?"
	has_abstract.boolean = True

	def __str__(self):
		return self.owner + "_" + self.key


class Docfile(models.Model):
	entry = models.ForeignKey(Entry)
	filename = models.CharField(max_length=100)

from django.db import models
import rdflib

from id.settings import AUTHORITIES_URL
from id.authorities import skos

class Concept(models.Model):
    lccn = models.CharField(max_length=25, primary_key=True)
    pref_label = models.CharField(max_length=250, db_index=True)
    prefix = models.CharField(max_length=2)
    created = models.DateField(null=True)
    modified = models.DateTimeField(null=True)
    lcc = models.CharField(max_length=50, null=True)
    heading_tag = models.CharField(max_length=3)
    related = models.ManyToManyField('self')
    broader = models.ManyToManyField('self', symmetrical=False,
                                     related_name='narrower')

    @property
    def uri(self):
        return rdflib.URIRef(AUTHORITIES_URL + self.lccn + '#concept')

    @property
    def rdf(self):
        return skos.concept_graph(self)

    def extra_broader(self):
        """look up broader terms that are implied in the structure of 
        the heading, but which aren't linked to explicitly in the MARC data
        So for a pref_label of "Classification--Books--Education" it should
        return concept model instances for "Classification",
        "Classification--Books"
        """
        parts = self.pref_label.split('--')
        if len(parts) == 1:
            return []

        extras = []
        for i in range(1, len(parts)):
            shorter = '--'.join(parts[0:i])
            try:
                concept = Concept.objects.get(pref_label=shorter,
                                              prefix=self.prefix,
                                              heading_tag=self.heading_tag)
                extras.append(concept)
            except Concept.DoesNotExist:
                pass # sometimes the prefix may not exist

        return extras

    def __repr__(self):
        return "%s [%s] [%s]" % (self.pref_label, self.lccn, self.heading_tag)

    def __str__(self):
        return self.__repr__()
    
class AlternateLabel(models.Model):
    text = models.CharField(max_length=300, db_index=True)
    concept = models.ForeignKey(Concept, related_name='alternate_labels')

    def __repr__(self):
        return self.text

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.__repr__()

class EditorialNote(models.Model):
    text = models.TextField()
    concept = models.ForeignKey(Concept, related_name='editorial_notes')

class ScopeNote(models.Model):
    text = models.TextField()
    concept = models.ForeignKey(Concept, related_name='scope_notes')

class ChangeNote(models.Model):
    text = models.TextField()
    concept = models.ForeignKey(Concept, related_name='change_notes')

class HistoryNote(models.Model):
    text = models.TextField()
    concept = models.ForeignKey(Concept, related_name='history_notes')

class Definition(models.Model):
    text = models.TextField()
    concept = models.ForeignKey(Concept, related_name='definitions')

class Example(models.Model):
    text = models.TextField()
    concept = models.ForeignKey(Concept, related_name='examples')

class Source(models.Model):
    text = models.TextField()
    concept = models.ForeignKey(Concept, related_name='sources')

class SearchQuery(models.Model):
    query = models.TextField()
    hits = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True, db_index=True)

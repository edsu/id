from datetime import datetime, date

from django.test import TestCase
from pymarc import parse_xml_to_array
import rdflib

from id.settings import AUTHORITIES_URL
from id.authorities.marc import create_concept
from id.authorities.skos import concept_graph, SKOS, DCTERMS, OWL
from id.authorities.models import Concept
from id.authorities.management.commands import load_marcxml


class ConversionTests(TestCase):

    def test_marc_to_concept(self):
        r = parse_xml_to_array('test_data/record.xml')[0]
        c = create_concept(r)
        self.assertEqual(c.lccn, 'sh00000011')
        self.assertEqual(c.pref_label, 'ActionScript (Computer program language)')
        self.assertEqual(c.modified, datetime(2007, 10, 12, 7, 53, 10))
        self.assertEqual(c.created, date(2000, 9, 27))
        self.assertEqual(c.heading_tag, '150')

class RdfTests(TestCase):

    def setUp(self):
        c = load_marcxml.Command()
        c.handle('test_data/record.xml')

    def graph_asserts(self, g, t):
        if len(list(g.triples(t))) != 1:
            self.fail("(%s %s %s) not found in graph" % t)

    def test_concept_graph(self):
        c = Concept.objects.get(lccn='sh00000011')
        u = rdflib.URIRef(AUTHORITIES_URL + 'sh00000011#concept')

        g = c.rdf
        self.assertEqual(c.uri, u)
        self.graph_asserts(g, (u, SKOS['prefLabel'],
            rdflib.Literal('ActionScript (Computer program language)', 'en')))
        self.graph_asserts(g, (u, OWL['sameAs'],
            rdflib.URIRef('info:lc/authorities/sh00000011')))


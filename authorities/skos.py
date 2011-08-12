import rdflib

from id.settings import AUTHORITIES_URL

OWL = rdflib.Namespace('http://www.w3.org/2002/07/owl#')
SKOS = rdflib.Namespace('http://www.w3.org/2004/02/skos/core#')
DCTERMS = rdflib.Namespace('http://purl.org/dc/terms/')
AUTHORITIES = rdflib.Namespace(AUTHORITIES_URL)

def concept_graph(c):
    """pass in a Concept model instance, get back an RDF graph
    """
    g = rdflib.ConjunctiveGraph()
    g.bind('owl', OWL)
    g.bind('skos', SKOS)
    g.bind('dcterms', DCTERMS)
    g.add((c.uri, SKOS['prefLabel'], rdflib.Literal(c.pref_label, 'en')))
    g.add((c.uri, OWL['sameAs'], rdflib.URIRef('info:lc/authorities/%s' % c.lccn)))

    _add_multi(c.uri, c.alternate_labels.all(), SKOS['altLabel'], g)
    _add_multi(c.uri, c.examples.all(), SKOS['example'], g)
    _add_multi(c.uri, c.editorial_notes.all(), SKOS['editorialNote'], g)
    _add_multi(c.uri, c.scope_notes.all(), SKOS['scopeNote'], g)
    _add_multi(c.uri, c.change_notes.all(), SKOS['changeNote'], g)
    _add_multi(c.uri, c.history_notes.all(), SKOS['historyNote'], g)
    _add_multi(c.uri, c.definitions.all(), SKOS['definition'], g)
    _add_multi(c.uri, c.sources.all(), DCTERMS['source'], g)

    for b in c.broader.all():
        g.add((c.uri, SKOS['broader'], b.uri))
        g.add((b.uri, SKOS['prefLabel'], rdflib.Literal(b.pref_label, 'en')))
    for n in c.narrower.all():
        g.add((c.uri, SKOS['narrower'], n.uri))
        g.add((n.uri, SKOS['prefLabel'], rdflib.Literal(n.pref_label, 'en')))
    for r in c.related.all():
        g.add((c.uri, SKOS['related'], r.uri))
        g.add((r.uri, SKOS['prefLabel'], rdflib.Literal(r.pref_label, 'en')))


    return g

def _add_multi(uri, model_instances, property, graph):
    for m in model_instances:
        graph.add((uri, property, rdflib.Literal(m.text, 'en')))



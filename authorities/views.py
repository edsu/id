from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator

from webob.acceptparse import Accept

from id.authorities import models as m
from id.authorities.skos import concept_graph
from id.settings import AUTHORITIES_URL

def concept(request, lccn):
    concept = get_object_or_404(m.Concept, lccn=lccn)
    host = request.get_host()

    accept = Accept('Accept', request.META.get('HTTP_ACCEPT', 'text/html'))
    best_match = accept.best_match(['text/html', 'application/rdf+xml']) 
    if best_match == 'application/rdf+xml':
        r = concept_rdf(request, lccn)
    else:
        alt_labels = concept.alternate_labels.all().order_by('text')
        broader = concept.broader.all().order_by('pref_label')
        extra_broader = concept.extra_broader()
        narrower = concept.narrower.all().order_by('pref_label')
        related = concept.related.all().order_by('pref_label')
        r = render_to_response('concept.html', dictionary=locals(), 
                               context_instance=RequestContext(request))
    # let downstream caches know that the resonse can vary depending 
    # on the Accept header that the client sent 
    r['Vary'] = 'Accept' 
    return r

def concept_rdf(request, lccn):
    concept = get_object_or_404(m.Concept, lccn=lccn)
    return HttpResponse(concept.rdf.serialize(format='xml'),
                        mimetype='application/rdf+xml; charset=utf-8')

def concept_turtle(request, lccn):
    concept = get_object_or_404(m.Concept, lccn=lccn)
    return HttpResponse(concept.rdf.serialize(format='n3'),
                        mimetype='application/turtle')

def concept_json(request, lccn):
    concept = get_object_or_404(m.Concept, lccn=lccn)
    return render_to_response('concept.html', dictionary=locals(), 
                              context_instance=RequestContext(request))

def concept_graphgear(request, lccn):
    concept = get_object_or_404(m.Concept, lccn=lccn)
    return render_to_response('graphgear.xml', dictionary=locals(),
                              context_instance=RequestContext(request))

def label(request, label):
    concepts = m.Concept.objects.filter(pref_label__iexact=label).all()
    if len(concepts) == 1:
        return HttpResponseRedirect(AUTHORITIES_URL + concepts[0].lccn)

    concepts = m.Concept.objects.filter(alternate_labels__text__iexact=label).all()
    if len(concepts) >= 1:
        return HttpResponseRedirect(AUTHORITIES_URL + concepts[0].lccn)

    return HttpResponseNotFound("No concept found with prefLabel or altLabel of %s" % label)

        

def search(request):
    page_title = 'Search'
    q = request.GET.get('q', None)
    try:
        page_num = int(request.GET.get('page', "1"))
    except: 
        page_num = 1
   
    # no query submitted
    if not q:
        # maybe this will get expensive under load?
        count = m.Concept.objects.all().count()
        recent_queries = m.SearchQuery.objects.filter(hits__gt=2).order_by('-created')[:5]
        return render_to_response('search.html', dictionary=locals(),
                                  context_instance=RequestContext(request))

    # execute query
    page_title += ': %s' % q
    mysqlq = ' '.join(["+%s" % p for p in q.split(' ')])
    concepts = m.Concept.objects.filter(pref_label__search=mysqlq).all().order_by('pref_label')

    # figure out paging
    paginator = Paginator(concepts, 25)
    page = paginator.page(page_num)
    page_range = _page_range_short(paginator, page)

    # save query history unless the request was for a particular 
    # page in the search results, don't want a bunch of paging 
    # to turn up as a different search
    if not request.GET.get('page'):
        search = m.SearchQuery.objects.create(query=q, hits=paginator.count)

    # render response
    return render_to_response('search_results.html', dictionary=locals(),
                              context_instance=RequestContext(request))

def _page_range_short(paginator, page):
    middle = 10 
    for p in paginator.page_range:
        if p <= 3:
            yield p
        elif paginator.num_pages - p < 3:
            yield p
        elif abs(p - page.number) < middle:
            yield p
        elif abs(p - page.number) == middle:
            yield "..."

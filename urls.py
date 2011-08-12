from django.conf.urls.defaults import *

from id.settings import MEDIA_ROOT

urlpatterns = patterns('id.authorities.views',
    url(r'^authorities/(?P<lccn>(sh|sj|sp).+)\.rdf$', 'concept_rdf', 
        name='authorities_concept_rdf'),
    url(r'^authorities/(?P<lccn>(sh|sj|sp).+)\.json$', 'concept_json',
        name='authorities_concept_json'),
    url(r'^authorities/(?P<lccn>(sh|sj|sp).+)\.ttl$', 'concept_turtle',
        name='authorities_concept_turtle'),
    url(r'^authorities/(?P<lccn>(sh|sj|sp).+)\.gg$', 'concept_graphgear',
        name='authorities_concept_graphgear'),
    url(r'^authorities/(?P<lccn>(sh|sj|sp).+)$', 'concept', 
        name='authorities_concept'),
    url(r'^authorities/search$', 'search',
        name='authorities_search'),
    url(r'^authorities/label/(?P<label>.+)$', 'label',
        name='authorities_label'),
    url(r'^authorities/?$', 'search', name='authorities_home')
)

urlpatterns += patterns('',
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': MEDIA_ROOT}, name='id_static'),
)




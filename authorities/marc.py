import logging
from datetime import datetime, date
from unicodedata import normalize

from pymarc.marcxml import map_xml, record_to_xml
from django.db import reset_queries

from id.authorities import models as m

_log = logging.getLogger()


class ConversionException(Exception):
    def __init__(self, message):
        self.message = message
    def __unicode__(self):
        return unicode(self.message)

def lccn(r):
    if r['001']:
        return r['001'].data.replace(' ', '')
    return ConversionException('missing LCCN')

def format_field(f, separator=' ', include=[]):
    if f == None: return None
    parts = []
    has_include = len(include) > 0
    for subfield in f:
        if has_include and subfield[0] not in include:
            continue
        parts.append(subfield[1])
    return normalize('NFC', separator.join(parts))

def format_personal_field(f):
    return format_field(f, '--', ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 
                        'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 
                        'v', 'x', 'y', 'z'])

def format_corporate_field(f):
    return format_field(f, '--', ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 
                        'j', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'v', 'x', 
                        'y', 'z'])

def format_meeting_field(f):
    return format_field(f, '--', ['a', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 
                        'k', 'l', 'n', 'p', 'q', 's', 't', 'v', 'x', 'y', 'z'])

def format_title_field(f):
    return format_field(f, '--', ['a', 'd', 'f', 'g', 'h', 'i', 'k', 'l', 'm', 
                        'n', 'o', 'p', 'r', 's', 't', 'v', 'x', 'y', 'z'])

def format_chronological_field(f):
    return format_field(f, '--', ['a', 'i', 'v', 'x', 'y', 'z'])

def format_topical_field(f):
    return format_field(f, '--', ['a', 'b', 'v', 'x', 'y', 'z'])

def format_geographic_field(f):
    return format_field(f, '--', ['a', 'v', 'x', 'y', 'z'])

def format_genre_field(f):
    return format_field(f, '--', ['a', 'v', 'x', 'y', 'z'])

def format_general_subd_field(f):
    return format_field(f, '--', ['v', 'x', 'y', 'z'])

def format_geographic_subd_field(f):
    return format_field(f, '--', ['v', 'x', 'y', 'z'])

def format_chronological_subd_field(f):
    return format_field(f, '--', ['v', 'x', 'y', 'z'])

def format_genre_subd_field(f):
    return format_field(f, '--', ['v', 'x', 'y', 'z'])

def personal_heading(r):
    return format_personal_field(r['100'])

def corporate_heading(r):
    return format_corporate_field(r['110'])

def meeting_heading(r):
    return format_meeting_field(r['111'])

def title_heading(r):
    return format_title_field(r['130'])

def chronological_heading(r):
    return format_corporate_field(r['148'])

def topical_heading(r):
    return format_topical_field(r['150'])

def geographic_heading(r):
    return format_geographic_field(r['151'])

def genre_heading(r):
    return format_genre_field(r['155'])

def general_subd(r):
    return format_general_subd_field(r['180'])

def geographic_subd(r):
    return format_geographic_subd_field(r['181'])

def chronological_subd(r):
    return format_chronological_subd_field(r['182'])

def genre_subd(r):
    return format_genre_subd_field(r['185'])

def pref_label(r):
    label = personal_heading(r) or corporate_heading(r) \
        or meeting_heading(r) or title_heading(r) \
        or chronological_heading(r) or topical_heading(r) \
        or geographic_heading(r) or genre_heading(r) \
        or general_subd(r) or geographic_subd(r) \
        or chronological_subd(r) or genre_subd(r)
    if not label: 
        raise ConversionException("no preflabel found")
    return label

def alt_labels(r):
    return map(format_personal_field, r.get_fields('400')) + \
        map(format_corporate_field, r.get_fields('410')) + \
        map(format_meeting_field, r.get_fields('411')) + \
        map(format_title_field, r.get_fields('430')) + \
        map(format_chronological_field, r.get_fields('448')) + \
        map(format_topical_field, r.get_fields('450')) + \
        map(format_geographic_field, r.get_fields('451')) + \
        map(format_genre_field, r.get_fields('455')) + \
        map(format_general_subd_field, r.get_fields('480')) + \
        map(format_geographic_subd_field, r.get_fields('481')) + \
        map(format_chronological_subd_field, r.get_fields('482')) + \
        map(format_genre_subd_field, r.get_fields('485'))

def is_broader(f):
    if f['w'] and f['w'] == 'g':
        return True
    return False

def broader_terms(r):
    return \
        map(format_personal_field, filter(is_broader, r.get_fields('500'))) \
        + map(format_corporate_field, filter(is_broader, r.get_fields('510'))) \
        + map(format_meeting_field, filter(is_broader, r.get_fields('511'))) \
        + map(format_title_field, filter(is_broader, r.get_fields('530'))) \
        + map(format_chronological_field, filter(is_broader, r.get_fields('548'))) \
        + map(format_topical_field, filter(is_broader, r.get_fields('550'))) \
        + map(format_geographic_field, filter(is_broader, r.get_fields('551'))) \
        + map(format_genre_field, filter(is_broader, r.get_fields('555'))) \
        + map(format_general_subd_field, filter(is_broader, r.get_fields('580'))) \
        + map(format_geographic_subd_field, filter(is_broader, r.get_fields('581'))) \
        + map(format_chronological_subd_field, filter(is_broader, r.get_fields('582'))) \
        + map(format_genre_subd_field, filter(is_broader, r.get_fields('585')))

def is_related(f):
    return f['w'] == None or not (f['w'] == 'g' or f['w'] == 'h')

def related_terms(r):
    return \
        map(format_personal_field, filter(is_related, r.get_fields('500'))) \
        + map(format_corporate_field, filter(is_related, r.get_fields('510'))) \
        + map(format_meeting_field, filter(is_related, r.get_fields('511'))) \
        + map(format_title_field, filter(is_related, r.get_fields('530'))) \
        + map(format_chronological_field, filter(is_related, r.get_fields('548'))) \
        + map(format_topical_field, filter(is_related, r.get_fields('550'))) \
        + map(format_geographic_field, filter(is_related, r.get_fields('551'))) \
        + map(format_genre_field, filter(is_related, r.get_fields('555'))) \
        + map(format_general_subd_field, filter(is_related, r.get_fields('580'))) \
        + map(format_geographic_subd_field, filter(is_related, r.get_fields('581'))) \
        + map(format_chronological_subd_field, filter(is_related, r.get_fields('582'))) \
        + map(format_genre_subd_field, filter(is_related, r.get_fields('585')))

def source_data_found_notes(r):
    return [format_field(f, include=['a', 'b', 'u']) for f in r.get_fields('670')]

def source_data_not_found_notes(r):
    return [format_field(f, include=['a']) for f in r.get_fields('675')]

def historical_notes(r):
    return [format_field(f, include=['a', 'b', 'u']) for f in r.get_fields('678')]

def editorial_notes(r):
    return source_data_not_found_notes(r) 

def definitions(r):
    return historical_notes(r)

def scope_notes(r):
    return [format_field(f, include=['a', 'i']) for f in r.get_fields('680')]

def subject_example_tracing_note(r):
    return [format_field(f, include=['a', 'i']) for f in r.get_fields('681')]

def deleted_heading_notes(r):
    return [format_field(f, include=['a', 'i']) for f in r.get_fields('682')]

def application_history_notes(r):
    return [format_field(f, include=['a']) for f in r.get_fields('688')]

def example_notes(r):
    return subject_example_tracing_note(r)

def change_notes(r):
    return deleted_heading_notes(r)

def history_notes(r):
    return application_history_notes(r)

def source_notes(r):
    return source_data_found_notes(r)

def general_notes(r):
    return nonpublic_general_note(r)

def created(r):
        d = datetime.strptime(r['008'].data[0:6], '%y%m%d')
        return date(d.year, d.month, d.day)

def modified(r):
        s = r['005'].data[0:-2] # remove the second fraction
        return datetime.strptime(s, '%Y%m%d%H%M%S')

def lcc(r):
        return format_field(r['053'], include=['a'])

def concept_with_pref_label(label):
    concepts = list(m.Concept.objects.filter(name=label))
    if len(subjects) == 0:
        raise ConversionException("no concept with preflabel %s" % label)
    else:
        return concepts[0] 

def heading_tag(r):
    for field in r:
        if field.tag.startswith('1'):
            return field.tag

def prefix(r):
    return lccn(r)[0:2]

main_heading_tags = ['100', '110', '111', '130', '148', '150', '151', '155']

subdivision_tags = ['180', '181', '182', '185']

def create_concept(r):
    c = m.Concept()
    c.lccn = lccn(r)
    c.pref_label = pref_label(r)
    c.created = created(r)
    c.modified = modified(r)
    c.lcc = lcc(r)
    c.heading_tag = heading_tag(r)
    c.prefix = prefix(r)
    c.save()
    for label in alt_labels(r):
        a = m.AlternateLabel(text=label, concept=c)
        a.save()
    for note in editorial_notes(r):
        n = m.EditorialNote(text=note, concept=c)
        n.save()
    for note in scope_notes(r):
        n = m.ScopeNote(text=note, concept=c)
        n.save()
    for note in change_notes(r):
        n = m.ChangeNote(text=note, concept=c)
        n.save()
    for note in history_notes(r):
        n = m.HistoryNote(text=note, concept=c)
        n.save()
    for note in definitions(r):
        n = m.Definition(text=note, concept=c)
    for note in example_notes(r):
        n = m.Example(text=note, concept=c)
        n.save()
    for note in source_notes(r):
        n = m.Source(text=note, concept=c)
        n.save()
    c.save()
    reset_queries()
    _log.info("created concept %s (%s)" % (c.pref_label, c.lccn))
    
    return c

def link_concept(r):
    label = pref_label(r)
    tag = heading_tag(r)
    c1 = m.Concept.objects.get(lccn=lccn(r))
   
    for bt in broader_terms(r):
        _log.debug('linking %s broader %s' % (c1, bt))
        c2 = find_concept(bt, c1.heading_tag, c1.prefix)
        if c2 == None:
            _log.error("couldn't find concept for pref_label=%s tag=%s" % \
                    (bt, c1.heading_tag))
            continue
        c1.broader.add(c2)
        _log.info('linked %s broader %s' % (c1, c2))

    for rt in related_terms(r):
        _log.debug('linking %s related %s' % (c1, rt))
        c2 = find_concept(rt, c1.heading_tag, c1.prefix)
        if c2 == None:
            _log.error("couldn't find concept for pref_label=%s tag=%s" % \
                    (rt, c1.heading_tag))
            continue
        c1.related.add(c2)
        _log.info('linked %s related %s' % (c1, c2))

    c1.save()
    reset_queries()

def find_concept(pref_label, heading_tag, prefix):
    # first look for concept with pref_label and exact heading tag
    concepts = list(m.Concept.objects.filter(pref_label=pref_label,
                                           heading_tag=heading_tag,
                                           prefix=prefix))
    if len(concepts) == 1:
        return concepts[0]
    elif len(concepts) > 1:
        _log.error("too many matches for pref_label=%s tag=%s, prefix=%s" % \
            (pref_label, heading_tag, prefix))
        return None

    # a concept with the heading tag can't be found, so broaden 
    # out to look for any main or subdivision heading tags appropriately

    if heading_tag in main_heading_tags:
        possible_tags = main_heading_tags
    else:
        possible_tags = subdivision_tags

    concepts = list(m.Concept.objects.filter(pref_label=pref_label,
                                           heading_tag__in=possible_tags,
                                           prefix=prefix))
    if len(concepts) == 0:
        return None
    elif len(concepts) == 1:
        return concepts[0]
    else:
        _log.error("too many matches for %s tags=(%s) prefix=%s" % \
            (pref_label, ','.join(possible_tags), prefix))
        return None

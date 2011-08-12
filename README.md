id is a django project for serving up LCSH authority data as SKOS RDF, JSON
and HTML. Once upon a time it was the prototype code for the service running
at id.loc.gov, but it has since been superseded. It is here in GitHub mainly 
for historical reasons, and also to keep the MARC -> SKOS mapping, which could
be useful for some purposes in the future.

The paper [LCSH, SKOS and Linked Data](http://arxiv.org/abs/0805.2855) has some
background information, on why this project was done.

## Installation

1. install python
1. install mysql
1. python setup.py build # should install python dependencies
1. echo "CREATE DATABASE id CHARACTER SET utf8; GRANT ALL ON id.* to '{username}'@'localhost' identified by '{password}';" | mysql -u root -p
1. update DATABASE_USER and DATABASE_PASSWORD in settings.py
1. update MEDIA_ROOT in settings.py to be the full path to the static directory
1. change AUTHORITIES_URL as appropriate in settings.py 
1. python manage.py syncdb
1. echo "ALTER table authorities_concept ADD FULLTEXT INDEX concept_fulltext_index (pref_label);" | mysql -u {username} -p id
1. python manage.py load_marcxml marc.xml
1. python manage.py runserver
1. go to http://localhost:8000/authorities

## License

Public Domain <http://creativecommons.org/licenses/publicdomain/>

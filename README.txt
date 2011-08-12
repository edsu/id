01. install python
02. install mysql
03. python setup.py build # should install python dependencies
04. echo "CREATE DATABASE id CHARACTER SET utf8; GRANT ALL ON id.* to '{username}'@'localhost' identified by '{password}';" | mysql -u root -p

05. update DATABASE_USER and DATABASE_PASSWORD in settings.py
06. update MEDIA_ROOT in settings.py to be the full path to the static directory
07. change AUTHORITIES_URL as appropriate in settings.py 
08. python manage.py syncdb
09. echo "ALTER table authorities_concept ADD FULLTEXT INDEX concept_fulltext_index (pref_label);" | mysql -u {username} -p id
10. python manage.py load_marcxml marc.xml
11. python manage.py runserver
12. go to http://localhost:8000/authorities

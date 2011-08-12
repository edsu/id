import logging
import fileinput

from django.core.management.base import BaseCommand
import pymarc

from id.authorities.marc import create_concept, link_concept

class Command(BaseCommand):
    help = 'load a marcxml file'
    args = '<marcxml filename>+'

    def handle(self, *files, **options):
        logging.basicConfig()
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('load_marcxml.log')
        formatter = logging.Formatter('[%(asctime)s %(levelname)s %(name)s] %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        for f in files:
            logger.info('creating concepts in %s' % f)
            for r in pymarc.MARCReader(file(f)):
                create_concept(r)

        for f in files:
            logger.info('linking concepts in: ' + ', '.join(files))
            for r in pymarc.MARCReader(file(f)):
                link_concept(r) 

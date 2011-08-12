import logging

from django.core.management.base import BaseCommand
from pymarc.marcxml import map_xml

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

        logger.info('creating concepts in: ' + ', '.join(files))
        map_xml(create_concept, *files)

        logger.info('linking concepts in: ' + ', '.join(files))
        map_xml(link_concept, *files)

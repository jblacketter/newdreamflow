from django.core.management.base import BaseCommand
from django.conf import settings
from apps.dreams.models import Dream
from algoliasearch_django import get_adapter
from algoliasearch_django.models import AlgoliaIndexError
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Initialize or rebuild Algolia search index for community dreams'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear the index before reindexing',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of records to index at once',
        )
    
    def handle(self, *args, **options):
        if not settings.ALGOLIA.get('APPLICATION_ID'):
            self.stdout.write(
                self.style.WARNING('Algolia not configured. Skipping index initialization.')
            )
            return
        
        try:
            # Get the model adapter
            adapter = get_adapter(Dream)
            
            if options['clear']:
                self.stdout.write('Clearing existing index...')
                adapter.clear_index()
                self.stdout.write(self.style.SUCCESS('Index cleared.'))
            
            # Get community dreams count
            community_dreams = Dream.objects.filter(privacy_level='community')
            count = community_dreams.count()
            
            if count == 0:
                self.stdout.write(
                    self.style.WARNING('No community dreams found to index.')
                )
                return
            
            self.stdout.write(f'Indexing {count} community dreams...')
            
            # Reindex all community dreams
            indexed = 0
            batch_size = options['batch_size']
            
            for start in range(0, count, batch_size):
                end = min(start + batch_size, count)
                batch = community_dreams[start:end]
                
                for dream in batch:
                    try:
                        adapter.save_record(dream)
                        indexed += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Failed to index dream {dream.id}: {e}')
                        )
                
                self.stdout.write(f'Indexed {indexed}/{count} dreams...')
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully indexed {indexed} dreams to Algolia!')
            )
            
        except Exception as e:
            logger.error(f"Error initializing Algolia index: {e}")
            self.stdout.write(
                self.style.ERROR(f'Error: {e}')
            )
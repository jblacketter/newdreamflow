import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError, ProgrammingError
from algoliasearch_django import get_adapter

from apps.things.models import Thing

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Initialize or rebuild Algolia search index for community things'
    
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
            # Get the model adapter for Thing
            adapter = get_adapter(Thing)
            
            if options['clear']:
                self.stdout.write('Clearing existing index...')
                adapter.clear_index()
                self.stdout.write(self.style.SUCCESS('Index cleared.'))
            
            # Get community things count
            community_things = Thing.objects.filter(privacy_level='community')
            count = community_things.count()
            
            if count == 0:
                self.stdout.write(
                    self.style.WARNING('No community things found to index.')
                )
                return
            
            self.stdout.write(f'Indexing {count} community things...')
            
            # Reindex all community things
            indexed = 0
            batch_size = options['batch_size']
            
            for start in range(0, count, batch_size):
                end = min(start + batch_size, count)
                batch = community_things[start:end]
                
                for thing in batch:
                    try:
                        adapter.save_record(thing)
                        indexed += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Failed to index thing {thing.id}: {e}')
                        )
                
                self.stdout.write(f'Indexed {indexed}/{count} things...')
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully indexed {indexed} things to Algolia!')
            )
            
        except (OperationalError, ProgrammingError) as exc:
            logger.error("Algolia index init aborted; database not ready: %s", exc)
            self.stdout.write(
                self.style.ERROR(
                    'Database is missing the `things` table. Run `python manage.py migrate` before indexing.'
                )
            )
        except Exception as e:
            logger.error(f"Error initializing Algolia index: {e}")
            self.stdout.write(
                self.style.ERROR(f'Error: {e}')
            )

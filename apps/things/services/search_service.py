from django.conf import settings
from algoliasearch.search.client import SearchClientSync
from algoliasearch_django import get_adapter
import logging

logger = logging.getLogger(__name__)


class AlgoliaSearchService:
    """Service for handling Algolia search operations."""
    
    def __init__(self):
        self.app_id = settings.ALGOLIA.get('APPLICATION_ID')
        self.api_key = settings.ALGOLIA.get('API_KEY')
        self.search_key = settings.ALGOLIA.get('SEARCH_API_KEY')
        self.index_prefix = settings.ALGOLIA.get('INDEX_PREFIX', 'thingjournal')
        
        if self.app_id and self.api_key:
            self.client = SearchClientSync(self.app_id, self.api_key)
            self.search_client = SearchClientSync(self.app_id, self.search_key)
            self.enabled = True
        else:
            logger.warning("Algolia credentials not found. Search functionality disabled.")
            self.enabled = False
    
    def get_index_name(self, model_name='things'):
        """Get the full index name with prefix."""
        return f"{self.index_prefix}_{model_name}"
    
    def search_things(self, query, filters=None, facets=None, page=0, per_page=20):
        """Search for things in Algolia."""
        if not self.enabled:
            return {'hits': [], 'nbHits': 0, 'page': 0, 'nbPages': 0}
        
        try:
            index = self.search_client.init_index(self.get_index_name())
            
            search_params = {
                'query': query,
                'hitsPerPage': per_page,
                'page': page,
            }
            
            if filters:
                search_params['filters'] = filters
            
            if facets:
                search_params['facets'] = facets
            
            return index.search(**search_params)
            
        except Exception as e:
            logger.error(f"Algolia search error: {e}")
            return {'hits': [], 'nbHits': 0, 'page': 0, 'nbPages': 0}
    
    def update_thing_index(self, thing):
        """Update a single thing in the index."""
        if not self.enabled or not thing.is_public_thing():
            return
        
        try:
            from apps.things.index import ThingIndex
            adapter = get_adapter(thing.__class__)
            adapter.save_record(thing)
        except Exception as e:
            logger.error(f"Error updating thing {thing.id} in Algolia: {e}")
    
    def remove_thing_from_index(self, thing):
        """Remove a thing from the index."""
        if not self.enabled:
            return
        
        try:
            from apps.things.index import ThingIndex
            adapter = get_adapter(thing.__class__)
            adapter.delete_record(thing)
        except Exception as e:
            logger.error(f"Error removing thing {thing.id} from Algolia: {e}")
    
    def get_search_settings(self):
        """Get search configuration for frontend."""
        if not self.enabled:
            return None
        
        return {
            'appId': self.app_id,
            'apiKey': self.search_key,
            'indexName': self.get_index_name(),
            'enabled': True,
        }


# Singleton instance
algolia_search = AlgoliaSearchService()
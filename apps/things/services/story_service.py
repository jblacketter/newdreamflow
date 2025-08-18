import re
from typing import List, Dict, Tuple
from django.utils import timezone


class StoryService:
    """Service for converting Things to Stories and managing story chunks."""
    
    # Average reading speed in words per second
    WORDS_PER_SECOND = 3  # About 180 words per minute
    
    def estimate_reading_time(self, text: str) -> float:
        """
        Estimate reading time in seconds for a given text.
        
        Args:
            text: The text to estimate reading time for
            
        Returns:
            Estimated reading time in seconds
        """
        if not text:
            return 0.0
            
        # Count words (split by whitespace and punctuation)
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        
        # Calculate time based on average reading speed
        reading_time = word_count / self.WORDS_PER_SECOND
        
        # Ensure minimum time of 1 second
        return max(reading_time, 1.0)
    
    def split_text_into_chunks(self, text: str, target_duration: float = 5.0) -> List[Dict]:
        """
        Split text into chunks that can be read in approximately the target duration.
        
        Args:
            text: The text to split
            target_duration: Target duration per chunk in seconds
            
        Returns:
            List of text chunks with metadata
        """
        if not text:
            return []
        
        # Calculate target words per chunk
        target_words = int(self.WORDS_PER_SECOND * target_duration)
        
        # Split text into sentences first (to avoid breaking mid-sentence)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for sentence in sentences:
            sentence_words = len(re.findall(r'\b\w+\b', sentence))
            
            # If adding this sentence would exceed target, save current chunk
            if current_word_count + sentence_words > target_words and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'text': chunk_text,
                    'duration': self.estimate_reading_time(chunk_text),
                    'word_count': current_word_count
                })
                current_chunk = [sentence]
                current_word_count = sentence_words
            else:
                current_chunk.append(sentence)
                current_word_count += sentence_words
        
        # Add the last chunk if there's content
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'duration': self.estimate_reading_time(chunk_text),
                'word_count': current_word_count
            })
        
        return chunks
    
    def create_story_from_thing(self, thing, story_title: str = None) -> Tuple['Story', List['Thing']]:
        """
        Create a Story from a long Thing by splitting it into chunks.
        
        Args:
            thing: The Thing model instance to convert
            story_title: Optional title for the story
            
        Returns:
            Tuple of (Story instance, List of Thing instances)
        """
        from apps.things.models import Thing, Story, StoryThing
        
        # Check if thing is long enough to warrant conversion
        reading_time = self.estimate_reading_time(thing.description)
        if reading_time <= 5:
            # Too short to split
            return None, []
        
        # Split the text into chunks
        chunks = self.split_text_into_chunks(thing.description)
        
        if len(chunks) <= 1:
            # No point in creating a story with just one chunk
            return None, []
        
        # Create the story
        story = Story.objects.create(
            user=thing.user,
            title=story_title or f"{thing.title or 'Untitled'} - Story",
            description=f"Story created from: {thing.title or 'Untitled Thing'}",
            privacy_level=thing.privacy_level
        )
        
        # Create Thing instances for each chunk
        created_things = []
        for idx, chunk in enumerate(chunks):
            chunk_thing = Thing.objects.create(
                user=thing.user,
                title=f"{thing.title or 'Part'} - Part {idx + 1}",
                description=chunk['text'],
                thing_date=thing.thing_date,
                privacy_level=thing.privacy_level,
                mood=thing.mood,
                # Copy semantic analysis from parent
                themes=thing.themes,
                symbols=thing.symbols,
                entities=thing.entities
            )
            created_things.append(chunk_thing)
            
            # Add to story with calculated duration
            StoryThing.objects.create(
                story=story,
                thing=chunk_thing,
                order=idx,
                duration=max(5, int(chunk['duration']))  # Minimum 5 seconds
            )
        
        # Copy images from original thing to the first chunk
        if created_things and thing.images.exists():
            first_chunk = created_things[0]
            for image in thing.images.all():
                from apps.things.models import ThingImage
                ThingImage.objects.create(
                    thing=first_chunk,
                    image=image.image,
                    image_url=image.image_url,
                    caption=image.caption,
                    order=image.order
                )
        
        return story, created_things
    
    def is_thing_long_enough(self, thing) -> bool:
        """
        Check if a Thing is long enough to warrant conversion to a Story.
        
        Args:
            thing: The Thing model instance
            
        Returns:
            True if thing should show "Convert to Story" option
        """
        if not thing.description:
            return False
            
        reading_time = self.estimate_reading_time(thing.description)
        return reading_time > 5  # More than 5 seconds of reading


# Singleton instance
story_service = StoryService()
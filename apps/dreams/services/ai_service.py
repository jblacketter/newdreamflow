import os
import json
from typing import Dict, List, Optional
import openai
from django.conf import settings


class AIService:
    """Service for AI-powered dream analysis and transcription."""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
    
    def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """Transcribe audio file to text using OpenAI Whisper."""
        if not self.api_key:
            return None
            
        try:
            with open(audio_file_path, 'rb') as audio_file:
                transcript = openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            return transcript
        except Exception as e:
            print(f"Transcription error: {e}")
            return None
    
    def analyze_dream(self, dream_text: str) -> Dict:
        """Analyze dream text to extract themes, symbols, and entities."""
        if not self.api_key:
            return {
                'themes': [],
                'symbols': [],
                'entities': []
            }
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a dream analysis assistant. Analyze the dream and extract:
                        1. Themes: Major recurring ideas or concepts
                        2. Symbols: Significant objects or symbols with potential meaning
                        3. Entities: People, places, or things mentioned
                        
                        Return as JSON with keys: themes, symbols, entities (each as arrays of strings).
                        Be objective and avoid interpretation - just identify elements."""
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this dream: {dream_text}"
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
            
        except Exception as e:
            print(f"Dream analysis error: {e}")
            return {
                'themes': [],
                'symbols': [],
                'entities': []
            }
    
    def find_patterns(self, dreams: List[Dict]) -> List[Dict]:
        """Analyze multiple dreams to find patterns."""
        if not self.api_key or len(dreams) < 3:
            return []
        
        try:
            dreams_text = "\n\n".join([
                f"Dream {i+1} ({d.get('date', 'Unknown date')}): {d.get('text', '')}"
                for i, d in enumerate(dreams)
            ])
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a dream pattern analyst. Identify recurring patterns across multiple dreams.
                        Look for:
                        1. Recurring themes or situations
                        2. Repeated symbols or objects
                        3. Common emotions or moods
                        4. Sequential patterns (one element following another)
                        
                        Return as JSON array with objects containing:
                        - name: Pattern name
                        - type: theme/symbol/emotion/sequence
                        - description: Brief description
                        - confidence: 0-1 score
                        - occurrences: which dream numbers it appears in"""
                    },
                    {
                        "role": "user",
                        "content": f"Find patterns in these dreams:\n\n{dreams_text}"
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
            
        except Exception as e:
            print(f"Pattern analysis error: {e}")
            return []


# Singleton instance
ai_service = AIService()
import os
import json
from typing import Dict, List, Optional
import openai
from django.conf import settings


class AIService:
    """Service for AI-powered thing analysis and transcription."""
    
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
    
    def analyze_thing(self, thing_text: str) -> Dict:
        """Analyze thing text to extract themes, symbols, and entities."""
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
                        "content": """You are a text analysis assistant. Analyze the text and extract:
                        1. Themes: Major recurring ideas or concepts
                        2. Symbols: Significant objects or symbols with potential meaning
                        3. Entities: People, places, or things mentioned
                        
                        Return as JSON with keys: themes, symbols, entities (each as arrays of strings).
                        Be objective and avoid interpretation - just identify elements."""
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this text: {thing_text}"
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
            
        except Exception as e:
            print(f"Thing analysis error: {e}")
            return {
                'themes': [],
                'symbols': [],
                'entities': []
            }
    
    def find_patterns(self, things: List[Dict]) -> List[Dict]:
        """Analyze multiple things to find patterns."""
        if not self.api_key or len(things) < 3:
            return []
        
        try:
            things_text = "\n\n".join([
                f"Thing {i+1} ({d.get('date', 'Unknown date')}): {d.get('text', '')}"
                for i, d in enumerate(things)
            ])
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a text pattern analyst. Identify recurring patterns across multiple texts.
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
                        - occurrences: which text numbers it appears in"""
                    },
                    {
                        "role": "user",
                        "content": f"Find patterns in these texts:\n\n{things_text}"
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
import spacy
from typing import Dict, List, Tuple
from django.utils.html import format_html, mark_safe


class SemanticService:
    """Service for semantic bit theory analysis of text."""
    
    def __init__(self):
        try:
            # Load the English language model
            self.nlp = spacy.load("en_core_web_sm")
            self.model_loaded = True
        except Exception as e:
            print(f"Warning: spaCy model not loaded. Error: {e}")
            print("Run: python -m spacy download en_core_web_sm")
            self.nlp = None
            self.model_loaded = False
    
    def extract_semantic_bits(self, text: str) -> Dict:
        """
        Extract semantic bits (verbs and nouns) from text.
        
        Returns:
            Dict with 'verbs', 'nouns', and 'tokens' lists
        """
        if not self.nlp or not text:
            return {
                'verbs': [],
                'nouns': [],
                'adjectives': [],
                'tokens': []
            }
        
        doc = self.nlp(text)
        
        verbs = []
        nouns = []
        adjectives = []
        tokens = []
        
        for token in doc:
            token_info = {
                'text': token.text,
                'pos': token.pos_,
                'tag': token.tag_,
                'lemma': token.lemma_,
                'is_stop': token.is_stop,
                'is_punct': token.is_punct
            }
            tokens.append(token_info)
            
            if token.pos_ == "VERB":
                verbs.append({
                    'text': token.text,
                    'lemma': token.lemma_,
                    'tag': token.tag_
                })
            elif token.pos_ == "NOUN":
                nouns.append({
                    'text': token.text,
                    'lemma': token.lemma_,
                    'tag': token.tag_
                })
            elif token.pos_ == "ADJ":
                adjectives.append({
                    'text': token.text,
                    'lemma': token.lemma_,
                    'tag': token.tag_
                })
        
        return {
            'verbs': verbs,
            'nouns': nouns,
            'adjectives': adjectives,
            'tokens': tokens,
            'stats': {
                'total_tokens': len(tokens),
                'verb_count': len(verbs),
                'noun_count': len(nouns),
                'adjective_count': len(adjectives)
            }
        }
    
    def is_available(self) -> bool:
        """Check if the semantic service is available."""
        return self.model_loaded and self.nlp is not None
    
    def create_highlighted_html(self, text: str) -> str:
        """
        Create HTML with color-coded semantic bits.
        
        Verbs: Blue (#3B82F6)
        Nouns: Green (#10B981)
        Adjectives: Purple (#8B5CF6)
        Others: Default color
        """
        if not self.nlp or not text:
            # Return a message if spaCy is not available
            if not self.nlp:
                return format_html(
                    '<div class="p-3 bg-yellow-50 border border-yellow-200 rounded">'
                    '<p class="text-yellow-800">Semantic analysis not available. '
                    'Please install spaCy: <code>python -m spacy download en_core_web_sm</code></p>'
                    '</div>'
                )
            return text
        
        doc = self.nlp(text)
        html_parts = []
        
        for token in doc:
            # Skip whitespace tokens
            if token.text.isspace():
                html_parts.append(token.text)
                continue
            
            # Determine color based on part of speech
            if token.pos_ == "VERB":
                # Verbs in blue - using !important for cross-browser compatibility
                html_parts.append(format_html(
                    '<span class="semantic-verb" style="color: #3B82F6 !important; font-weight: 500 !important; display: inline !important;" '
                    'data-pos="VERB" data-lemma="{}" title="Verb: {}">{}</span>',
                    token.lemma_, token.lemma_, token.text
                ))
            elif token.pos_ == "NOUN":
                # Nouns in green - using !important for cross-browser compatibility
                html_parts.append(format_html(
                    '<span class="semantic-noun" style="color: #10B981 !important; font-weight: 500 !important; display: inline !important;" '
                    'data-pos="NOUN" data-lemma="{}" title="Noun: {}">{}</span>',
                    token.lemma_, token.lemma_, token.text
                ))
            elif token.pos_ == "ADJ":
                # Adjectives in purple - using !important for cross-browser compatibility
                html_parts.append(format_html(
                    '<span class="semantic-adj" style="color: #8B5CF6 !important; font-weight: 500 !important; display: inline !important;" '
                    'data-pos="ADJ" data-lemma="{}" title="Adjective: {}">{}</span>',
                    token.lemma_, token.lemma_, token.text
                ))
            else:
                # Other words in default color
                html_parts.append(format_html(
                    '<span class="semantic-other" style="display: inline !important;" data-pos="{}" title="{}">{}</span>',
                    token.pos_, token.pos_, token.text
                ))
            
            # Add space after token if needed
            if token.whitespace_:
                html_parts.append(token.whitespace_)
        
        return mark_safe(''.join(html_parts))
    
    def get_semantic_relationships(self, text: str) -> List[Tuple]:
        """
        Extract subject-verb-object relationships from text.
        """
        if not self.nlp or not text:
            return []
        
        doc = self.nlp(text)
        relationships = []
        
        for token in doc:
            if token.pos_ == "VERB":
                # Find subject
                subject = None
                obj = None
                
                for child in token.children:
                    if child.dep_ in ["nsubj", "nsubjpass"]:
                        subject = child.text
                    elif child.dep_ in ["dobj", "pobj"]:
                        obj = child.text
                
                if subject or obj:
                    relationships.append({
                        'verb': token.text,
                        'subject': subject,
                        'object': obj
                    })
        
        return relationships
    
    def calculate_semantic_density(self, text: str) -> Dict:
        """
        Calculate the semantic density of text.
        Returns ratio of content words (verbs, nouns, adjectives) to total words.
        """
        if not self.nlp or not text:
            return {'density': 0, 'content_words': 0, 'total_words': 0}
        
        doc = self.nlp(text)
        content_words = 0
        total_words = 0
        
        for token in doc:
            if not token.is_punct and not token.is_space:
                total_words += 1
                if token.pos_ in ["VERB", "NOUN", "ADJ"]:
                    content_words += 1
        
        density = content_words / total_words if total_words > 0 else 0
        
        return {
            'density': round(density, 2),
            'content_words': content_words,
            'total_words': total_words
        }


# Singleton instance
semantic_service = SemanticService()
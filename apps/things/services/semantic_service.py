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
        Extract semantic bits (verb phrases and noun phrases) from text.
        Semantically bifurcates sentences into noun-like and verb-like components.
        
        Returns:
            Dict with 'verb_phrases', 'noun_phrases', and 'tokens' lists
        """
        if not self.nlp or not text:
            return {
                'verb_phrases': [],
                'noun_phrases': [],
                'tokens': []
            }
        
        doc = self.nlp(text)
        
        verb_phrases = []
        noun_phrases = []
        tokens = []
        
        # Extract noun chunks (includes adjectives and determiners)
        for chunk in doc.noun_chunks:
            noun_phrases.append({
                'text': chunk.text,
                'root': chunk.root.text,
                'root_lemma': chunk.root.lemma_,
                'start': chunk.start,
                'end': chunk.end
            })
        
        # Extract verb phrases with their modifiers
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
                # Collect verb with its modifiers (adverbs, auxiliaries, particles)
                phrase_tokens = [token]
                
                # Get adverbs modifying this verb
                for child in token.children:
                    if child.pos_ == "ADV" or child.dep_ in ["aux", "auxpass", "neg", "prt"]:
                        phrase_tokens.append(child)
                
                # Sort tokens by position in sentence
                phrase_tokens.sort(key=lambda t: t.i)
                phrase_text = ' '.join([t.text for t in phrase_tokens])
                
                verb_phrases.append({
                    'text': phrase_text,
                    'root': token.text,
                    'root_lemma': token.lemma_,
                    'tag': token.tag_
                })
        
        return {
            'verb_phrases': verb_phrases,
            'noun_phrases': noun_phrases,
            'tokens': tokens,
            'stats': {
                'total_tokens': len(tokens),
                'verb_phrase_count': len(verb_phrases),
                'noun_phrase_count': len(noun_phrases)
            }
        }
    
    def is_available(self) -> bool:
        """Check if the semantic service is available."""
        return self.model_loaded and self.nlp is not None
    
    def create_highlighted_html(self, text: str) -> str:
        """
        Create HTML with color-coded semantic phrases while preserving paragraph structure.
        
        Verb Phrases: Blue (#3B82F6) - includes verbs with their modifiers
        Noun Phrases: Green (#10B981) - includes nouns with their modifiers
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
        
        # Split text into paragraphs to preserve structure
        paragraphs = text.split('\n\n')
        html_paragraphs = []
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            # Process each paragraph
            doc = self.nlp(paragraph)
            
            # Mark noun chunks
            noun_chunk_tokens = set()
            for chunk in doc.noun_chunks:
                for i in range(chunk.start, chunk.end):
                    noun_chunk_tokens.add(i)
            
            # Mark verb phrases (verb + modifiers)
            verb_phrase_tokens = set()
            for token in doc:
                if token.pos_ == "VERB":
                    verb_phrase_tokens.add(token.i)
                    # Add modifiers
                    for child in token.children:
                        if child.pos_ == "ADV" or child.dep_ in ["aux", "auxpass", "neg", "prt"]:
                            verb_phrase_tokens.add(child.i)
            
            html_parts = []
            
            for token in doc:
                # Handle newlines within paragraphs (single line breaks)
                if '\n' in token.text:
                    html_parts.append('<br>')
                    continue
                    
                # Skip pure whitespace tokens
                if token.text.isspace():
                    html_parts.append(token.text)
                    continue
                
                # Determine color based on phrase membership
                if token.i in verb_phrase_tokens:
                    # Part of verb phrase - blue
                    html_parts.append(format_html(
                        '<span class="semantic-verb-phrase" style="color: #3B82F6 !important; font-weight: 500 !important; display: inline !important;" '
                        'data-phrase="verb" data-lemma="{}" title="Verb phrase component">{}</span>',
                        token.lemma_, token.text
                    ))
                elif token.i in noun_chunk_tokens:
                    # Part of noun phrase - green
                    html_parts.append(format_html(
                        '<span class="semantic-noun-phrase" style="color: #10B981 !important; font-weight: 500 !important; display: inline !important;" '
                        'data-phrase="noun" data-lemma="{}" title="Noun phrase component">{}</span>',
                        token.lemma_, token.text
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
            
            # Wrap each paragraph in a <p> tag
            html_paragraphs.append('<p>' + ''.join(html_parts) + '</p>')
        
        return mark_safe(''.join(html_paragraphs))
    
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
        Returns ratio of semantic content (verbs and nouns) to total words.
        """
        if not self.nlp or not text:
            return {'density': 0, 'content_words': 0, 'total_words': 0}
        
        doc = self.nlp(text)
        content_words = 0
        total_words = 0
        
        for token in doc:
            if not token.is_punct and not token.is_space:
                total_words += 1
                if token.pos_ in ["VERB", "NOUN"]:
                    content_words += 1
        
        density = content_words / total_words if total_words > 0 else 0
        
        return {
            'density': round(density, 2),
            'content_words': content_words,
            'total_words': total_words
        }


# Singleton instance
semantic_service = SemanticService()
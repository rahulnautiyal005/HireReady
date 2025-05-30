import json
import os
import re
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

# Load weak phrases dictionary from JSON file
def load_weak_phrases():
    try:
        with open('data/weak_phrases.json', 'r') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Error loading weak phrases dictionary: {str(e)}")
        # Fallback to basic dictionary if file can't be loaded

# Rabin-Karp algorithm implementation
def rabin_karp_search(text, pattern, d=256, q=101):
    """
    Rabin-Karp string matching algorithm.
    
    Args:
        text (str): Text to search in
        pattern (str): Pattern to search for
        d (int): Number of characters in the alphabet
        q (int): A prime number for hash calculation
        
    Returns:
        list: List of starting positions where pattern is found
    """
    result = []
    M = len(pattern)
    N = len(text)
    
    if M > N or M == 0:
        return result
    
    # Calculate hash value for pattern and first window of text
    pattern_hash = 0
    text_hash = 0
    h = 1
    
    # Calculate h = d^(M-1) % q
    for i in range(M-1):
        h = (h * d) % q
    
    # Calculate hash value for pattern and first window of text
    for i in range(M):
        pattern_hash = (d * pattern_hash + ord(pattern[i])) % q
        text_hash = (d * text_hash + ord(text[i])) % q
    
    # Slide pattern over text one by one
    for i in range(N - M + 1):
        # Check if hash values match
        if pattern_hash == text_hash:
            # Check for characters one by one
            match = True
            for j in range(M):
                if text[i + j] != pattern[j]:
                    match = False
                    break
            if match:
                result.append(i)
        
        # Calculate hash value for next window
        if i < N - M:
            text_hash = (d * (text_hash - ord(text[i]) * h) + ord(text[i + M])) % q
            # Make sure hash is positive
            if text_hash < 0:
                text_hash += q
    
    return result

def analyze_resume_text(text):
    """
    Analyze resume text to find weak phrases and suggest improvements.
    
    Args:
        text (str): The resume text to analyze
        
    Returns:
        dict: Dictionary containing improved text and list of improvements
    """
    weak_phrases = load_weak_phrases()
    improvements = []
    improved_text = text
    
    # Use case-insensitive search
    text_lower = text.lower()
    
    # Track positions to replace (to handle overlapping phrases)
    replacements = defaultdict(list)
    
    # Find all weak phrases using Rabin-Karp
    for weak_phrase, strong_phrase in weak_phrases.items():
        positions = rabin_karp_search(text_lower, weak_phrase.lower())
        
        for pos in positions:
            # Check that we're not matching in the middle of a word
            is_valid_match = True
            
            # Check character before match (if not at beginning)
            if pos > 0 and text_lower[pos-1].isalnum():
                is_valid_match = False
                
            # Check character after match (if not at end)
            end_pos = pos + len(weak_phrase)
            if end_pos < len(text_lower) and text_lower[end_pos].isalnum():
                is_valid_match = False
                
            if is_valid_match:
                # Get the actual case-preserved phrase from original text
                original_phrase = text[pos:pos+len(weak_phrase)]
                
                # Determine replacement phrase maintaining capitalization
                if original_phrase[0].isupper():
                    replacement = strong_phrase[0].upper() + strong_phrase[1:]
                else:
                    replacement = strong_phrase
                
                # Store the replacement information
                replacements[pos].append({
                    'end': pos + len(weak_phrase),
                    'original': original_phrase,
                    'replacement': replacement
                })
    
    # Sort positions in reverse order (to avoid affecting earlier positions when replacing)
    positions = sorted(replacements.keys(), reverse=True)
    
    # Make replacements in the text
    for pos in positions:
        # Use the first replacement at this position (if there are multiple)
        repl = replacements[pos][0]
        
        # Add to improvements list
        improvements.append({
            'original': repl['original'],
            'suggestion': repl['replacement']
        })
        
        # Make the replacement in the text
        improved_text = improved_text[:pos] + repl['replacement'] + improved_text[repl['end']:]
    
    return {
        'improved_text': improved_text,
        'improvements': improvements
    }
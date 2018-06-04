"""
Module for future refactorization of tokenizers.
TODO: Move `topicexplorer.lib.chinese` to this module.
TODO: Document how to create own tokenizer
TODO: Move boilerpalte from `vsm.extensions.corpusbuilders.util`
TODO: Create function for str -> tokenizer mappings. Shared among
      both init and serve stages.
"""
from builtins import str
from past.builtins import basestring

# Example character removal, used in simple_tokenizer
# In practice, we use string.punctuation for REMOVE.
REMOVE = '\'",.;:!?' + '0123456789'
REMOVE_TABLE = {ord(c): None for c in REMOVE}

def simple_tokenizer(text):
    """ 
    Example for returning a list of terms from text.
    1. Normalizes text by casting to lowercase.
    2. Removes punctuation from tokens.
    3. Returns tokens as indicated by whitespace.
    """
    text = text.lower()
    
    # Remove punctuation from file
    if isinstance(text, str):
        # Python 2+3 unicode strings
        text = text.translate(REMOVE_TABLE)
    elif isinstance(text, basestring):
        # Python 2 old-style strings
        text = text.translate(None, REMOVE.encode('utf-8'))

    # Split the tokens
    return text.split()

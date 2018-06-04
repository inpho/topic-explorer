"""
Module for future refactorization of tokenizers.
TODO: Move `topicexplorer.lib.chinese` to this module.
TODO: Document how to create own tokenizer
TODO: Move boilerpalte from `vsm.extensions.corpusbuilders.util`
TODO: Create function for str -> tokenizer mappings. Shared among
      both init and serve stages.
"""

def simple_tokenizer(text):
    """ 
    Example for returning a list of terms from text. 
    Simply removes spaces.
    """
    return text.split()

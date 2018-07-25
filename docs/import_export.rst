Import and Export
===================

``tez`` Files
---------------
``tez`` files are just ``zip`` files with a different extension. They contain:

 -  the ``ini`` configuration file
 -  the ``npz`` corpus file
 -  any ``npz`` topic model files
 -  a ``metadata.json`` for the corpus
 -  the raw corpus (only with the |export include-corpus|_ flag)

.. |export include-corpus| replace:: ``export --include-corpus``
.. _export include-corpus: #include-corpus


``topicexplorer export``
--------------------------

Command Line Arguments
''''''''''''''''''''''''

Output Path (``-o``)
"""""""""""""""""""""""
Specifies the output path for the `tez` file.

**Default:** Current direcotry

``--include-corpus``
""""""""""""""""""""""
Include the raw corpus for fulltext view. Corpus inclusion is disabled by default to protect copyrighted source data.


``topicexplorer import``
--------------------------

Command Line Arguments
''''''''''''''''''''''''

Output Path (``--o``)
"""""""""""""""""""""""
**Default:** Current directory

Examples
-------------------
This example shows how to use export and import.

::

    topicexplorer export workset.ini -o workset.tez
    topicexplorer import workset.tez



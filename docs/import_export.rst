Import and Export
===================

`tez` files
-------------
`tez` files are just `zip` files with a different extension. They contain:

 -  the `ini` configuration file
 -  the `npz` corpus file
 -  any `npz` topic model files
 -  a `metadata.json` for the corpus
 -  the raw corpus (only with the |export include-corpus|_ flag)

.. |export include-corpus| replace: ``export --include-corpus``
.. _export include-corpus: #include-corpus


``topicexplorer export``
--------------------------

Command Line Arguments
''''''''''''''''''''''''

Output Path (``--o``)
"""""""""""""""""""""""
**Default:** Current direcotry

``--include-corpus``
""""""""""""""""""""""


``topicexplorer import``
--------------------------

Command Line Arguments
''''''''''''''''''''''''

Output Path (``--o``)
"""""""""""""""""""""""
**Default:** Current direcotry


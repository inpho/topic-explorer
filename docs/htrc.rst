HathiTrust Integrations
=========================
The `HathiTrust`_ is a digital library with over 16 million volumes digitized by
a partnership of over 120 research institutions and libraries.

The digitized holdings include both in-copyright and public domain works.
Full-text access is given to the public domain works and works still in
copyright can be searched through the catalog.

The `HathiTrust Research Center`_ (HTRC) gives access to both public domain and
in-copyright text for computational analysis by members of partner institutions.
Research conducted with in-copyright HathiTrust resources must adhere to the
principles of *non-consumptive research*, as defined by the 2010 *Authors Guild
v. Google* ammended settlement agreement:

    "Non-Consumptive Research" means research in which computational analysis is
    performed on one or more Books, but not research in which a researcher reads or
    displays substantial portions of a Book to understand the intellectual content
    presented within the Book.”

Non-consumptive research includes image analysis and text extraction, textual
analysis and information extraction, linguistic analysis, automated translation, 
and indexing and search. 

The HTRC facilitates non-consumptive research in three ways supported by the InPhO
Topic Explorer:

1.  `HTRC Data Capsules`_ provide a secure virtual machine for resarchers
    wanting to derive their own datasets.
2.  `HTRC Algorithms`_ provide a push-button way to run the Topic Explorer on a
    remote machine and export model files for further analysis on a personal
    computer.
3.  `HTRC Extracted Features`_ allow for training of topic models on a personal
    computer through word counts.

Finally, each of these methods relies on `collection management`_ for keeping
track of HathiTrust IDs. The InPhO Topic Explorer also provides `metadata
management`_ to display titles in the browser and links to the fulltext views at
HathiTrust.

.. _HathiTrust:
    https://www.hathitrust.org/
.. _HathiTrust Research Center:
    https://analytics.hathitrust.org/
.. _HTRC Data Capsules: #working-with-htrc-data-capsules
.. _HTRC Extracted Features: #working-with-htrc0extracted-features
.. _HTRC Algorithms: #working-with-htrc-algorithms
.. _collection management: #working-with-collections
.. _metadata management: #adding-hathitrust-metadata


Working with Collections
--------------------------
Members of HathiTrust partner institutions can login and create curated
collections of HathiTrust materials using the Collection Builder. Non-members
have access to public collections through the interface, which can be modeled
using the `HTRC Extracted Features`_ and the InPhO Topic Explorer.

In general, the best way to export a collection from the Collection Builder is
to use the `HTRC Workset Toolkit`_. This will produce a ``txt`` file that can then
be used with the `HTRC Extracted Features`_.

1.  Install the HTRC Workset Toolkit: ``pip install htrc``
2.  Select a HathiTrust `collection`_.
3.  Copy the collection URL.
4.  Run the following command to get a volume list, remembering to put the URL
    in quotes:

    htrc export "https://babel.hathitrust.org/cgi/mb?a=listis;c=2027705310" > volumes.txt

5.  Follow the directions for `Working with HTRC Extracted Features`_.

.. _collection: https://babel.hathitrust.org/cgi/mb?colltype=featured
.. _HTRC Workset Toolkit:
    https://htrc.github.io/HTRC-WorksetToolkit/


Working with HTRC Data Capsules
---------------------------------
The InPhO Topic Explorer

.. _HTRC Data Capsule Tutorial:
    https://wiki.htrc.illinois.edu/display/COM/HTRC+Data+Capsule+Tutorial


Working with HTRC Extracted Features 
--------------------------------------
``topicexplorer init --htrc``


Working with HTRC Algorithms
------------------------------


Adding HathiTrust Metadata
----------------------------
``topicexplorer metadata --htrc``


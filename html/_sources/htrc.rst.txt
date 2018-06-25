HathiTrust Integrations
=========================
The `HathiTrust`_ is a digital library with over 16 million volumes digitized by
a partnership of over 120 research institutions and libraries.

The digitized holdings include both in-copyright and public domain works.
Full-text access is given to the public domain works and works still in
copyright can be searched through the catalog.


The `HathiTrust Research Center`_ (HTRC) gives access to both public domain and
in-copyright text for computational analysis by members of partner institutions.
Research carried out with these resources must follow principles of
`non-consumptive use`_, essentially ensuring the original text of each volume
cannot be reconstructed.

The HTRC and InPhO Topic Explorer facilitate non-consumptive use through three
integrations:

1.  `HTRC Algorithms`_ provide a push-button way to run the Topic Explorer on a
    remote machine and export model files for further analysis on a personal
    computer.
2.  `HTRC Data Capsules`_ provide a secure virtual machine for resarchers
    wanting to derive their own datasets.
3.  `HTRC Extracted Features`_ allow for training of topic models on a personal
    computer through word counts.

Each of these methods relies on `collection management`_ for keeping track of
HathiTrust IDs. The InPhO Topic Explorer also provides `metadata management`_ to
display titles in the browser and links to the fulltext views at HathiTrust.

.. _HathiTrust:
    https://www.hathitrust.org/
.. _HathiTrust Research Center:
    https://analytics.hathitrust.org/
.. _HTRC Data Capsules: #working-with-htrc-data-capsules
.. _HTRC Extracted Features: #working-with-htrc0extracted-features
.. _HTRC Algorithms: #working-with-htrc-algorithms
.. _non-consumptive research: 
.. _non-consumptive use:
    #non-consumptive-research
.. _collection management: #working-with-collections
.. _metadata management: #adding-hathitrust-metadata

Non-consumptive Research
--------------------------
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



Working with Collections
--------------------------
Any work with the HathiTrust requires management of HathiTrust IDs. The simplest
form of collection management involves a simple text file consisting of
identifiers::

    mdp.49015002517150
    mdp.39015045637462

With this list of identifiers, volumes can be downloaded for use in the `HTRC
Data Capsules`_ or via the `HTRC Extracted Features`_ capacity.


HahtiTrust Collection Builder
'''''''''''''''''''''''''''''''
Members of HathiTrust partner institutions can login and create curated
collections of HathiTrust materials using the `Collection Builder`_. Non-members
have access to public collections through the interface. These collections can
then be modeled using the InPhO Topic Explorer.

Collections can be exported via the `HTRC Workset Toolkit`_ to produce a ``txt``
file that can then be used with the `HTRC Extracted Features`_ or within the
`HTRC Data Capsules`_.

1.  Install the HTRC Workset Toolkit: ``pip install htrc``
2.  Select a HathiTrust `collection`_.
3.  Copy the collection URL.
4.  Run the following command to get a volume list, remembering to put the URL
    in quotes::

        htrc export "https://babel.hathitrust.org/cgi/mb?a=listis;c=2027705310" > volumes.txt

.. _Collection Builder:
    https://www.hathitrust.org/help_digital_library#CBBuild
.. _collection: https://babel.hathitrust.org/cgi/mb?colltype=featured
.. _HTRC Workset Toolkit:
    https://htrc.github.io/HTRC-WorksetToolkit/


Working with HTRC Algorithms
------------------------------
The InPhO Topic Explorer can be used without locally installing any software
through the HTRC Algorithms portal. This page will run the Explorer over a
HathiTrust Collection on a remote machine with a preset ``prep`` phase that
guarantees `non-consumptive use`_.

1.  `Sign in to HTRC Analytics.`_
2.  `Import a collection as a HTRC Workset.`_
3.  `Go to HTRC Algorithms`_ using the top navigation.
4.  Select the "InPhO Topic Explorer" algorithm.
5.  Select the newly imported collection.
6.  Run the algorithm, optionally customizing parameters.

At the end of execution, an interactive summary visualization will be shown that
groups similar topics together. Hovering over each circle in the visualization
will display the top 10 words in the topic.

Output
''''''''

Unlike with the `HTRC Data Capsules`_, output files do not have to undergo
non-consumptive review and are immediately available. 
Three files are available for download:

``workset.tez``
    This file can be used with the |topicexplorer import workset.tez|_ to launch
    the full visualization via |topicexplorer launch|_ or to analyze the models
    further using |topicexplorer notebook|_
``topics.json``
    This file contains the topics for each model trained, the top 10 terms in
    each topic, and their probabilities.
``cluster.csv``
    This file contains information that drives

.. _Sign in to HTRC Analytics.:
    https://analytics.hathitrust.org/signin
.. _Import a collection as a HTRC Workset.:
    https://analytics.hathitrust.org/staticworksets
.. _Go to HTRC Algorithms:
    https://analytics.hathitrust.org/statisticalalgorithms

.. |topicexplorer import workset.tez| replace:: 
    ``topicexplorer import workset.tez``
.. _topicexplorer import workset.tez: import_export.html
.. |topicexplorer launch| replace:: ``topicexplorer launch``
.. _topicexplorer launch: launch.html
.. |topicexplorer notebook| replace:: ``topicexplorer notebook``
.. _topicexplorer notebook: notebook.html

Working with HTRC Data Capsules
---------------------------------
The HTRC Data Capsules are virtual machines with secure access to the fulltext
data files via the Data API. The InPhO Topic Explorer is pre-installed on each
data capsule, and can be run with any parameter settings, unlike the HTRC
Algorithms mode.

Within the Data Capsule, the following command can be used to automate download
of a workset and guidance through the ``init``-``prep``-``train`` workflow::
    
    htrc run topicexplorer "https://babel.hathitrust.org/cgi/mb?a=listis;c=2027705310"

Analyses performed in HTRC Data Capsules must be reviewed for compliance with
`non-consumptive use`_ before result files can be exported.

.. seealso::
    `HTRC Data Capsule Tutorial`_
        A tutorial on basic usage of the HTRC Data Capsule.
        

.. _HTRC Data Capsule Tutorial:
    https://wiki.htrc.illinois.edu/display/COM/HTRC+Data+Capsule+Tutorial


Working with HTRC Extracted Features 
--------------------------------------
The `HTRC Extracted Features dataset`_ contains word counts for 15.7 million
volumes of public domain and in-copyright works. These word counts are already a
`non-consumptive use`_, so the extracted features can be downloaded to any
computer.

To use the InPhO Topic Explorer with extracted features: 

1.  Create a text file with volume IDs, possibly using the |htrc export
    command|_ on a HathiTrust collection URL.
2.  Use the ``--htrc`` flag on the Topic Explorer to download volumes from the
    extracted features dataset and construct a corpus object::

        topicexplorer init --htrc volumes.txt

    where volumes.txt is the name of the file containing volume IDs.

.. _HTRC Extracted Features dataset:
    https://wiki.htrc.illinois.edu/display/COM/Extracted+Features+Dataset
.. |htrc export command| replace:: ``htrc export`` command
.. _htrc export command: #hathitrust-collection-builder


Adding HathiTrust Metadata
----------------------------
The ``topicexplorer metadata --htrc`` command will add volume titles and 
links to the HathiTrust Page Turner fulltext view to the InPhO Topic Explorer
document view.

The metadata command may be run on datasets computed via HTRC Algorithms, in
Data Capsules, and using Extracted Features.

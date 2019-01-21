=============================
Topic Explorer Introduction
=============================

The InPhO Topic Explorer provides an integrated system for text modeling making
it simple to go from a set of documents to an interactive visualization of LDA
topic models. More advanced analysis is made possible by a built-in pipeline to
`Jupyter notebooks`_.

Live demos trained on the Stanford Encyclopedia of Philosophy, a selection of
books from the HathiTrust Digital Library, a collection of Chinese-language
texts and the original LDA training set of Associated Press articles are
available at `<https://www.hypershelf.org>`_.

.. |InPhO vsm module| replace:: InPhO ``vsm`` module
.. _InPhO vsm module: https://github.com/inpho/vsm
.. _Jupyter notebooks: http://jupyter.org/

.. TODO: Insert screenshots of hypershelf and cluster interfaces.

Installation
--------------
1.  Install `Anaconda for Python 3.6`_. During "Advanced Options" choose "Add
    Anaconda to my PATH environment variable".
2.  Open a Terminal (Mac and Linux) or PowerShell (Windows).
3.  Run ``pip install --pre topicexplorer``.
    
    **Note:** ``--pre`` has *two* `-` characters.

4.  Test installation by typing ``topicexplorer -h`` to print usage 
    instructions.

.. _Anaconda for Python 3.6: https://www.anaconda.com/download/


Example Workflow
------------------
The Topic Explorer is a 4-step process. Each step creates or modifies a
``.ini`` file that defines the links to corpus and model files, along with
other configuration options.

The Topic Explorer is run from the Terminal (macOS or Linux) or PowerShell
(Windows).

.. TODO: Insert workflow graphic

.. TODO: Insert tutorial asciinema
.. TODO: Insert tutorial corpus download

1.  Initialize the Topic Explorer on a file, folder of text files, or folder of
    folders::
        
        topicexplorer init example

    ``example`` will be replaced with the folder you select. A configuration
    file called ``example.ini`` will be generated.

2.  Prepare the corpus for modeling by removing common words to improve topic
    quality and removing uncommon words to improve modeling speed::

        topicexplorer prep example

    If you are unsure of what to select, we encourage experimentation but
    recommend the following settings::

        topicexplorer prep example --high-percent 50 --low-percent 10 --min-word-len 3 -q

3.  Train LDA models using the on-screen instructions::
        
        topicexplorer train example

4.  Launch the Topic Explorer::

        topicexplorer launch example

5.  Press Ctrl+C to quit the server instance.


.. seealso::
    |topicexplorer init|_
        More details on the data import step.
    |topicexplorer prep|_
        More details on the data preparation step.
    |topicexplorer train|_
        More details on topic modeling.
    |topicexplorer launch|_
        More details on the visualization interfaces.
    |topicexplorer notebook|_
        More details on the notebook interface.

.. |topicexplorer init| replace:: ``topicexplorer init``
.. _topicexplorer init: init.html
.. |topicexplorer prep| replace:: ``topicexplorer prep``
.. _topicexplorer prep: prep.html
.. |topicexplorer train| replace:: ``topicexplorer train``
.. _topicexplorer train: train.html
.. |topicexplorer launch| replace:: ``topicexplorer launch``
.. _topicexplorer launch: launch.html
.. |topicexplorer notebook| replace:: ``topicexplorer notebook``
.. _topicexplorer notebook: notebook.html


Licensing and Attribution
---------------------------
The project is released under an `MIT License`_.

Visualizations generated with the Topic Explorer are licensed under a `Creative
Commons Attribution 4.0 International (CC BY 4.0) License
<https://creativecommons.org/licenses/by/4.0/>`_.

The project may be cited as:
    
    Jaimie Murdock and Colin Allen. (2015) Visualization Techniques for
    Topic Model Checking in Proceedings of the 29th AAAI Conference on
    Artificial Intelligence (AAAI-15). Austin, Texas, USA, January 25-29,
    2015. https://hypershelf.org/

.. _MIT License: https://opensource.org/licenses/MIT

Collaboration and Maintenance
-------------------------------
The InPhO Topic Explorer is maintained by `Jaimie Murdock`_:

-  E-mail: `<jammurdo@indiana.edu>`_
-  Twitter: `@JaimieMurdock <https://twitter.com/JaimieMurdock>`_
-  GitHub: `@JaimieMurdock <https://github.com/JaimieMurdock>`_
-  Homepage `<http://jamram.net>`_

.. _Jaimie Murdock: http:/jamram.net/

Please report issues on the `issue tracker`_ or contact Jaimie directly.

.. _issue tracker: https://github.com/inpho/topic-explorer/issues

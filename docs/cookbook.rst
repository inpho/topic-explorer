Cookbook
==========

HathiTrust Collection to Topic Explorer
-----------------------------------------
The following script downloads `a collection of Vonnegut's works and associated
criticism <https://babel.hathitrust.org/cgi/mb?a=listis;c=1100976828>`_. It can
easily be adapted to other collections. 

::

    #!/bin/bash
    
    # install the tools
    pip install topicexplorer[htrc] htrc
    
    # make a folder
    mkdir -p /tmp/vonnegut
    cd /tmp/vonnegut
    
    # download the list of identifiers from IDAH's collection
    htrc export "https://babel.hathitrust.org/cgi/mb?a=listis;c=1100976828" > vonnegut.txt
    
    # train the models
    topicexplorer init vonnegut.txt -q --htrc --name "Vonnegut's works (and criticism thereof)"
    topicexplorer prep vonnegut.txt -q --high-percent 70 --low-percent 5 --lang en
    topicexplorer train vonnegut.txt -q -k 25 50 100 --iter 200 -p 4
    topicexplorer metadata vonnegut.txt --htrc

    # launch the explorer
    topicexplorer launch vonnegut.txt

Import and export
-------------------
This example shows how to use export and import.

::

    topicexplorer export workset.ini -o workset.tez
    topicexplorer import workset.tez

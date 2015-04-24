# InPhO Topic Explorer
[![Build Status](https://travis-ci.org/inpho/topic-explorer.svg?branch=master)](https://travis-ci.org/inpho/topic-explorer)
[![GitHub license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/inpho/topic-explorer/blob/master/LICENSE.txt)
[![PyPI](https://img.shields.io/pypi/v/topicexplorer.svg)](https://pypi.python.org/pypi/topicexplorer)

This interactive visualization displays information from the LDA topic models generated using the [InPhO VSM module](http://github.com/inpho/vsm/). Live demos trained on the Stanford Encyclopedia of Philosophy, a selection of books from the HathiTrust Digital Library, and the original LDA training set of Associated Press articles are available at [http://inphodata.cogs.indiana.edu](http://inphodata.cogs.indiana.edu/).

The color bands within each article's row show the topic distribution within that article, and the relative sizes of each band indicates the weight of that topic in the article. The total width of each row indicates similarity to the focal topic or document, measured by the quantity sim(doc) = 1 – JSD(doc, focus entity), where JSD is the Jensen-Shannon distance between the word probability distributions of each item. Each topic's label and color is arbitrarily assigned, but is consistent across articles in the browser.

Display options include topic normalization, alphabetical sort and topic sort. By normalizing topics, the combined width of each bar expands so that topic weights per document can be compared. By clicking a topic, the documents will reorder acoording to that topic's weight and topic bars will reorder according to the topic weights in the highest weighted document. When a topic is selected, clicking "Top Documents for [Topic]" will take you to a new page showing the most similar documents to that topic's word distribution. The original sort order can be restored with the "Reset Topic Sort" button.

## Installation
**Quick Install**

1.  Install the [Anaconda Python 2.7 Distribution](http://continuum.io/downloads). 
2.  Open a terminal and run `pip install topicexplorer==1.0b6`.

## Usage
![Workflow](http://inphodata.cogs.indiana.edu/img/workflow.png)

1.  Initialize the Topic Explorer on a file, folder of text files, or folder of folders:

    ```
    vsm init PATH [CONFIG]
    ```

    This will generate a configuration file called *CONFIG*.

2.  Train LDA models using the on-screen instructions:

    ```
    vsm train CONFIG
    ```

3.  Launch the topic explorer:

    ```
    vsm launch CONFIG
    ```

4.  Press Ctrl+C to quit all servers.

See the sample configuration files in the `config` directory for examples of how to extend the topic explorer.

## Development and Testing
1.  Clone the [repository](http://github.com/inpho/topic-explorer) and install dependencies:
    
    ```
    pip install -e git+https://github.com/inpho/topic-explorer#egg=topicexplorer
    ```

2.  Setup the Associated Press sample corpus released with [Blei (2003)](www.cs.princeton.edu/~blei/lda-c/) and train the corpus:

    ```
    ./demo.sh
    ```

3.  Launch the demo:

    ```
    vsm launch ap.ini
    ```


## Licensing and Attribution
The project is released under an [Open-Source Initiative-approved MIT License](http://opensource.org/licenses/MIT).

The InPhO Topic Explorer may be cited as:
 -  Jaimie Murdock and Colin Allen. (2015) *Visualization Techniques for Topic Model Checking* in Proceedings of the 29th AAAI Conference on Artificial Intelligence (AAAI-15). Austin, Texas, USA, January 25-29, 2015. [http://inphodata.cogs.indiana.edu/](http://inphodata.cogs.indiana.edu/)

A [BibTeX file](https://github.com/inpho/topic-explorer/blob/master/citation.bib) is included in the repository for easier attribution.

## Collaboration and Maintenance
The InPhO Topic Explorer is maintained by [Jaimie Murdock](http://jamram.net/):
 -  E-mail: jammurdo@indiana.edu
 -  Twitter: [@JaimieMurdock](http://twitter.com/JaimieMurdock)
 -  GitHub: [@JaimieMurdock](http://github.com/JaimieMurdock)
 -  Homepage: [http://jamram.net/](http://jamram.net/)

Please report issues on the [issue tracker](http://github.com/inpho/topic-explorer/issues) or contact Jaimie directly.

We are open to collaboration! If there's a feature you'd like to see implemented, please contact us and we can lend advice and technical assistance.


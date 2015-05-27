# InPhO Topic Explorer
[![Travis](https://img.shields.io/travis/inpho/topic-explorer.svg)](https://travis-ci.org/inpho/topic-explorer)
[![GitHub license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/inpho/topic-explorer/blob/master/LICENSE.txt)
[![PyPI](https://img.shields.io/pypi/v/topicexplorer.svg)](https://pypi.python.org/pypi/topicexplorer)

This interactive visualization displays information from the LDA topic models generated using the [InPhO VSM module](http://github.com/inpho/vsm/). Live demos trained on the Stanford Encyclopedia of Philosophy, a selection of books from the HathiTrust Digital Library, and the original LDA training set of Associated Press articles are available at [http://inphodata.cogs.indiana.edu](http://inphodata.cogs.indiana.edu/).

The color bands within each article's row show the topic distribution within that article, and the relative sizes of each band indicates the weight of that topic in the article. The total width of each row indicates similarity to the focal topic or document, measured by the quantity sim(doc) = 1 – JSD(doc, focus entity), where JSD is the Jensen-Shannon distance between the word probability distributions of each item. Each topic's label and color is arbitrarily assigned, but is consistent across articles in the browser.

Display options include topic normalization, alphabetical sort and topic sort. By normalizing topics, the combined width of each bar expands so that topic weights per document can be compared. By clicking a topic, the documents will reorder acoording to that topic's weight and topic bars will reorder according to the topic weights in the highest weighted document. When a topic is selected, clicking "Top Documents for [Topic]" will take you to a new page showing the most similar documents to that topic's word distribution. The original sort order can be restored with the "Reset Topic Sort" button.

## Installation

1.  Install the [Anaconda Python 2.7 Distribution](http://continuum.io/downloads). 
2.  Open a terminal and run `pip install --pre topicexplorer`.
3.  Test installation by typing `vsm -h` to print usage instructions.

See below for notes on developer installation.

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


## Developer Install

We **highly recommend** installing the [Anaconda Python 2.7 Distribution](http://continuum.io/downloads) first. Straightforward instructions are provided for Anaconda. If you want to roll your own install, some notes on dependencies are included below.

1. [Set up Git](https://help.github.com/articles/set-up-git/)

2.  Install Anaconda packages:
  
    ```
    conda install numpy scipy nltk matplotplib ipython
    ```

3.  Clone the repo and install in developer mode (`-e` flag):

    ```
    pip install -e git+https://github.com/inpho/topic-explorer#egg=topicexplorer
    ```

### Dependencies

 - **Debian/Ubuntu** (non-Anaconda) 
   1.  `sudo apt-get-install build-essential python-dev python-pip python-numpy python-matplotlib python-scipy python-ipython` 
   
   2.  [IPython Notebooks](http://ipython.org/install.html)

 - **Windows** 
   1.  Install [Microsoft Visual C++ Compiler for Python 2.7](http://www.microsoft.com/en-us/download/details.aspx?id=44266)

   2.  Install the Python packages below:
       *   [Numpy](http://sourceforge.net/projects/numpy/files/NumPy/)
       *   [Scipy](http://sourceforge.net/projects/scipy/files/scipy/)
       *   [matplotlib](http://matplotlib.org/downloads.html)
       *   [IPython Notebooks](http://ipython.org/install.html)

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


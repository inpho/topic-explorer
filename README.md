# InPhO Topic Explorer
[![Build Status](https://travis-ci.org/inpho/topic-explorer.svg?branch=master)](https://travis-ci.org/inpho/topic-explorer)
[![GitHub license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/inpho/topic-explorer/blob/master/LICENSE.txt)

This interactive visualization displays information from the LDA topic models generated using the [InPhO VSM module](http://github.com/inpho/vsm/). Live demos trained on the Stanford
Encyclopedia of Philosophy, a selection of books from the HathiTrust Digital Library, and the original LDA training set of Associated Press articles are available at [http://inphodata.cogs.indiana.edu].

The color bands within each article's row show the topic distribution within that article, and the relative sizes of each band indicates the weight of that topic in the article. The total width of each row indicates similarity to the focal topic or document, measured by the quantity sim(doc) = 1 – JSD(doc, focus entity), where JSD is the Jensen-Shannon distance between the word probability distributions of each item. Each topic's label and color is arbitrarily assigned, but is consistent across articles in the browser.

Display options include topic normalization, alphabetical sort and topic sort. By normalizing topics, the combined width of each bar expands so that topic weights per document can be compared. By clicking a topic, the documents will reorder acoording to that topic's weight and topic bars will reorder according to the topic weights in the highest weighted document. When a topic is selected, clicking "Top Documents for [Topic]" will take you to a new page showing the most similar documents to that topic's word distribution. The original sort order can be restored with the "Reset Topic Sort" button.

## Licensing and Attribution
The project is released under an Open-Source Initiative-approved MIT License.

The Topic Explorer may be cited as:
 -  Jaimie Murdock and Colin Allen. (2015) *Visualization Techniques for Topic Model Checking* in Proceedings of the 29th AAAI Conference (AAAI-15). Austin, Texas, USA, January 25-29, 2015.

A BibTeX file is included in the repository.

## Installation
The quickest way is to install the [Anaconda Python 2.7 Distribution](http://contiuum.io/downloads). Then open a terminal and run `pip install topicexplorer`.

## Usage
1.  Initialize the Topic Explorer on a file, folder of text files, or folder of folders of text files:

    ```
    vsm init PATH
    ```

    This will generate a configuration file.

2.  Train LDA models using the on-screen instructions and then
    ```
    vsm train CONFIG_FILE
    ```

3.  Launch the topic explorer:

    ```
    vsm launch CONFIG_FILE
    ```

4.  Press Ctrl+C to quit all servers.

See the sample configuration files in the `config` directory for examples of how to extend the topic explorer.

## Development and Testing
1.  Clone the repository:
    
    ```
    git clone git@github.com:inpho/topic-explorer.git
    ```
2.  Setup the topic-explorer package and install dependencies.

    ```
    cd topic-explorer
    python setup.py develop --user
    ```
3.  Setup the Associated Press sample corpus released with [Blei (2003)](www.cs.princeton.edu/~blei/lda-c/) and train the corpus:

    ```
    ./demo.sh
    ```

4.  Access at [http://localhost:16020](http://localhost:16020).


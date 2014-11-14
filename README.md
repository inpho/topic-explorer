# InPhO Topic Explorer
This interactive visualization displays information from the LDA topic models generated using the [InPhO VSM module](http://github.com/inpho/vsm/). Live demos trained on the Stanford
Encyclopedia of Philosophy, a selection of books from the HathiTrust Digital Library, and the original LDA training set of Associated Press articles are available at [http://inphodata.cogs.indiana.edu].

The color bands within each article's row show the topic distribution within that article, and the relative sizes of each band indicates the weight of that topic in the article. The total width of each row indicates similarity to the focal topic or document, measured by the quantity sim(doc) = 1 – JSD(doc, focus entity), where JSD is the Jensen-Shannon distance between the word probability distributions of each item. Each topic's label and color is arbitrarily assigned, but is consistent across articles in the browser.

Display options include topic normalization, alphabetical sort and topic sort. By normalizing topics, the combined width of each bar expands so that topic weights per document can be compared. By clicking a topic, the documents will reorder acoording to that topic's weight and topic bars will reorder according to the topic weights in the highest weighted document. When a topic is selected, clicking "Top Documents for [Topic]" will take you to a new page showing the most similar documents to that topic's word distribution. The original sort order can be restored with the "Reset Topic Sort" button.

## Installation
1.  Clone the repository:
    
    ```
    git clone git@github.com:inpho/topic-explorer.git
    ```
2.  Setup dependencies.

    ```
    python setup.py develop --user
    ```
3.  Setup the Associated Press sample corpus released with [Blei (2003)](www.cs.princeton.edu/~blei/lda-c/):

    ```
    cd demo-data
    sh get-data.sh
    ```

4.  Start the Topic Explorer for the given number of topics:

    ```
    cd ..
    python server.py -k 20 config/ap.ini
    ```
5.  Access at [http://localhost:18020](http://localhost:18020).


## Publications
 -  Jaimie Murdock and Colin Allen. (in review) Visualization Techniques for Topic Model Checking. [demo track] in Proceedings of the 29th AAAI Conference (AAAI-15). Austin, Texas, USA, January 25-29, 2015.

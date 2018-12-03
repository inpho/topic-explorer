"""
Prepares a corpus for modeling with stoplist management tools.


Stoplisting
=============

What is stoplisting?
----------------------
Extremely common words can be of little value in discriminating between
documents and can create uninterpretable topics. Terms like ``the``, ``of``,
``is``, ``and``, ``but``, and ``or`` are thus excluded from modeling. These
terms are called *stop words*. The process of removing stop words is
stoplisting.


How ``topicexplorer prep`` generates stoplists
------------------------------------------------
``topicexplorer prep`` generates stoplists from the frequencies of words in the
collection being modeled, rather than using the same list of words across
different collections. Arbitrary lists can still be excluded with the 
|stopword-file argument|_.

.. |stopword-file argument| replace:: ``--stopword-file`` argument
.. _stopword-file argument: #custom-stopwords-stopword-file

While most natural language processing (NLP) tools exclude common words,
``topicexplorer prep`` also provides functionality to remove low-frequency
words. 

The contribution of low-freuqency words to the probability distribution
is negligible -- if a word only occurs once in a 1 million word corpus (which
can easily be hit with only 25-50 volumes), then it has a .000001 probability of
occurring. The runtime improvements gained from excluding these low frequency
words from the word-topic matrix far outweigh the marginal improvements to model
fit.

Another benefit of removing low-frequency words is the removal of spurious
tokens introduced by optical character recognition (OCR) in scanned documents.

Finally, very small words can be excluded with the |min-word-len argument|_.
These small words often appear when mathematical formulas are in a text (e.g.,
``y = mx + b`` would introduce ``y``, ``mx``, and ``b``). Usually, they will be
caught by the low-frequency filters, but this ensures they are left out.

.. |min-word-len argument| replace:: ``--min-word-len`` argument
.. _min-word-len argument: #small-words-min-word-len


.. seealso::
    `Introduction to Information Retrieval -- stop words`_
        Stanford textbook on stop words.

.. _Stop words:
.. _Introduction to Information Retrieval -- stop words:
    https://nlp.stanford.edu/IR-book/html/htmledition/dropping-common-terms-stop-words-1.html



Recommended Settings
======================
Each argument has a suggested value. A quick start, assuming your corpus is in
a folder called "workset" is::

    topicexplorer prep workset --high-percent 50 --low-percent 10 --min-word-len 3 -q

These parameters work well for English-language text. For languages without
articles (e.g., "a", "the"), we recommend reducing the ``--high-percent``
argument to ``--high-percent 25``.


Command Line Arguments
========================

High-probability words (``--high-percent``)
---------------------------------------------
Remove common words from the corpus, accounting for up to ``HIGH_PERCENT`` of
the total occurrences in the corpus.

**Recommended, but not default:** ``--high-percent 50``


Low-probability words (``--low-percent``)
-------------------------------------------
Remove uncommon words from the corpus, accounting for up to ``LOW_PERCENT`` of
the total occurrences in the corpus.

**Recommended, but not default:** ``--low-percent 10``


Small words (``--min-word-len``)
----------------------------------
Remove words with few characters from the corpus. Often includes mathematical
notation and OCR errors. 

**Recommended, but not default:** ``--min-word-len 3``


Custom stopwords (``-stopword-file``)
---------------------------------------
Remove custom words from the corpus.


Quiet mode (``-q``)
---------------------
Suppresses all user input requests. Uses default values unless otherwise
specified by other argument flags. Very useful for scripting automated
pipelines.

"""

from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import input
from builtins import zip
from builtins import str
from past.utils import old_div

from configparser import RawConfigParser as ConfigParser
import json
import os.path
import re
import sys

from codecs import open
from unidecode import unidecode

import topicexplorer.config
from topicexplorer.lib.util import isint, is_valid_configfile, bool_prompt

from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget, Label, PopUpDialog, PopupMenu, CheckBox, FileBrowser, KeyboardEvent
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
from copy import deepcopy

# NLTK Langauges
langs = dict(da='danish', nl='dutch', en='english', fi='finnish', fr='french',
             de='german', hu='hungarian', it='italian', no='norwegian',
             pt='portuguese', ru='russian', es='spanish', sv='swedish',
             tr='turkish')

langs_rev = dict((v, k) for k, v in langs.items())


def get_item_counts(x):
    from scipy.stats import itemfreq
    import numpy as np
    try:
        # for speed increase with numpy >= 1.9.0
        items, counts = np.unique(x, return_counts=True)
    except:
        # for compatability
        ifreq = itemfreq(x)
        items = ifreq[:, 0]
        counts = ifreq[:, 1]
    return items, counts

def get_corpus_counts(c):
    import numpy as np
    #print(len(c), len(c.words), len(c.context_data[0]))
    items = np.arange(len(c.words)) 
    counts = np.zeros(c.words.shape, dtype=np.int32)
    for context in c.view_contexts(c.context_types[0], as_slices=True):
        i, N = np.unique(c.corpus[context], return_counts=True)
        counts[i] += N

    return items, counts


def stop_language(c, language):
    import nltk.corpus

    try:
        words = nltk.corpus.stopwords.words(language)
    except LookupError:
        import sys
        print("\nERROR: stopwords not available, download by running:")
        print("    python -m nltk.downloader stopwords")
        print("\nExiting...")
        sys.exit(74)
    except IOError:
        print("{} unsupported by default, use a custom stopwords file.".format(language))
        return c.words

    if c.words.dtype.char == 'S':
        words = [word.strip() for word in words if word in c.words]
    else:
        words = [word for word in words if word in c.words]
    return words


def detect_langs(corpus):
    global langs
    import langdetect

    for doc in corpus.view_contexts(corpus.context_types[-1], as_strings=True):
        lang = langdetect.detect(' '.join(doc))
        return [lang]


def lang_prompt(languages):
    global langs
    out_langs = set()
    print("Stoplist the following languages?", end=' ')
    for lang in languages:
        if lang in langs:
            if bool_prompt("{}?".format(langs[lang].capitalize()), default=True):
                out_langs.add(lang)
    return out_langs


def get_candidate_words(c, n_filter, sort=True, words=None,
                        items=None, counts=None):
    """ Takes a corpus and a filter and reutrns the candidate words.
    If n_filter > 0, filter words occuring at least n_filter times.
    If n_filter < 0, filter words occuring less than n_filter times.
    """
    if n_filter == 0:
        return []
    else:
        if items is None or counts is None:
            items, counts = get_corpus_counts(c)

        if n_filter > 0:
            filter = items[counts >= n_filter]
            if sort:
                filter = filter[counts[counts >= n_filter].argsort()[::-1]]
    
        elif n_filter < 0:
            filter = items[counts <= -n_filter]
            if sort:
                filter = filter[counts[counts <= -n_filter].argsort()[::-1]]

        mask = get_mask(c, words, filter=filter)
        return c.words[mask]


def get_mask(c, words=None, filter=None):
    import numpy as np
    if filter is None:
        mask = np.ones(len(c.words), dtype=bool)  # all elements included/True.
    else:
        mask = np.zeros(len(c.words), dtype=bool)  # all elements excluded/False.
        mask[filter] = True

    if words is not None:
        ix = np.in1d(c.words, list(words))
        ix = np.where(ix)
        mask[ix] = False              # Set unwanted elements to False

    return mask[:]


def get_small_words(c, min_len):
    return [word for word in c.words if len(word) < min_len]


def get_closest_bin(c, thresh, reverse=False, counts=None):
    """
    Takes a corpus `c` and a `thresh`, returning the frequency that 
    is the lowest match for that threshold. Default is to count up, 
    selecting a lower bound threshold. If `reverse=True`, sums are
    reversed, selecting a filter for the higher bound.


    """
    import numpy as np
    
    # get counts
    if counts is None:
        _, counts = get_corpus_counts(c)

    if thresh == 0 and reverse:
        return max(counts) + 1
    elif thresh == 0 and not reverse:
        return 1
    else:
        # sort counts
        counts = counts[counts.argsort()]
        if reverse:
            counts = counts[::-1]

        # find insertion point
        cumsum = old_div(np.cumsum(counts), float(c.original_length))
        return counts[min(np.searchsorted(cumsum, thresh), len(counts)-1)]


def get_high_filter_chart(c, words=None, items=None, counts=None, num=None):
    import numpy as np

    # Get frequency bins
    if items is None or counts is None:
        items, counts = get_corpus_counts(c)
    bins = np.arange(1.0, -0.01, -0.025)
    bins = [get_closest_bin(c, thresh, counts=counts) for thresh in bins]
    bins = sorted(set(bins))
    bins.append(max(counts))

    chart = ""

    bin_counts, bins = np.histogram(counts, bins=bins)
    chart += "{0:>8s} {1:>8s} {2:<36s} {3:>14s} {4:>8s}".format("Rate", 'Top', '% of corpus', "# words", "Rate") + "\n"
    last_row = 0
    for bin, count in zip(bins[-2::-1], np.cumsum(bin_counts[::-1])):
        filtered_counts = counts[get_mask(c, words)]
        if (filtered_counts >= bin).sum() > last_row:
            percentage = 1. - (old_div(counts[counts < bin].sum(), float(c.original_length)))
            chart += "{0:>5.0f}x".format(bin).rjust(8)
            chart += '{0:2.1f}% '.format(percentage * 100).rjust(10)
            chart += (u'\u2588' * int(percentage * 36)).ljust(36)
            chart += "{0:0.0f} words".format((filtered_counts >= bin).sum()).rjust(15)
            chart += " >={0:>5.0f}x".format(bin).ljust(8) + "\n"

        last_row = (filtered_counts >= bin).sum()

    chart += (' ' * 18) + "{} total occurrences".format(counts.sum()).ljust(34)
    chart += '{} words total'.format(get_mask(c, words).sum()).rjust(20)
    return chart

def get_high_filter_stops(c, words=None, items=None, counts=None, num=None):
    import numpy as np
    input_filter = num
    valid = True
    try:
        candidates = get_candidate_words(c, input_filter, words=words, items=items, counts=counts)
        places = np.in1d(c.words, candidates)
        places = dict(zip(candidates, np.where(places)[0]))
        candidates = sorted(candidates, key=lambda x: counts[places[x]], reverse=True)
        filtered_counts = counts[get_mask(c, words)]

        filtered = ""
        filtered += "Filter will remove " + str(filtered_counts[filtered_counts >= input_filter].sum())
        filtered += " occurrences " + "of these " + str(len(filtered_counts[filtered_counts >= input_filter])) + " words: "
        filtered += u' '.join(candidates)

        if len(candidates) == len(c.words):
            valid = False
            # filtered += "\n\nChoice of" + str(input_filter) + "will remove ALL words from the corpus."
            # filtered += "Please choose a different filter."

    except ValueError:
        input_filter = 0
    return (candidates, filtered, valid)


def get_low_filter_chart(c, words=None, items=None, counts=None, num=None):
    import numpy as np

    # Get frequency bins
    if items is None or counts is None:
        items, counts = get_corpus_counts(c)
    bins = np.arange(1.0, -0.01, -0.025)
    bins = [get_closest_bin(c, thresh, reverse=True, counts=counts) for thresh in bins]
    bins = sorted(set(bins))
    bins.append(max(counts))

    chart = ""

    bin_counts, bins = np.histogram(counts[counts.argsort()[::-1]], bins=bins)
    chart += "{0:>8s} {1:>8s} {2:<36s} {3:>14s} {4:>8s}".format("Rate", 'Bottom', '% of corpus', "# words", "Rate") + "\n"
    last_row = 0
    for bin, count in zip(bins, np.cumsum(bin_counts)):
        filtered_counts = counts[get_mask(c, words)]
        if last_row < (filtered_counts < bin).sum() <= len(filtered_counts):
            percentage = (old_div(counts[counts <= bin].sum(), float(c.original_length)))
            chart += "{0:>5.0f}x".format(bin).rjust(8)
            chart += '{0:2.1f}%'.format(percentage * 100).rjust(9)
            chart += " " + (u'\u2588' * int(percentage * 36)).ljust(36)
            chart += "{0:0.0f} words".format((filtered_counts <= bin).sum()).rjust(15)
            chart += " <={0:>5.0f}x".format(bin).ljust(8) + "\n"
            if (filtered_counts < bin).sum() == len(filtered_counts):
                break
        last_row = (filtered_counts >= bin).sum()

    chart += (' ' * 18) + "{} total occurrences".format(counts.sum()).ljust(34)
    chart += '{} words total'.format(get_mask(c, words).sum()).rjust(20)
    return chart

def get_low_filter_stops(c, words=None, items=None, counts=None, num=None):
    import numpy as np
    input_filter = num
    valid = True
    try:
        candidates = get_candidate_words(c, -input_filter, words=words, items=items, counts=counts)
        places = np.in1d(c.words, candidates)
        places = dict(zip(candidates, np.where(places)[0]))
        candidates = sorted(candidates, key=lambda x: counts[places[x]])
        filtered_counts = counts[get_mask(c, words)]

        filtered = ""
        filtered += "Filter will remove " + str(filtered_counts[filtered_counts <= input_filter].sum()) + " tokens"
        filtered += "of these " + str(len(filtered_counts[filtered_counts <= input_filter])) + " words: "
        filtered += u' '.join(candidates)


        if len(candidates) == len(c.words):
            valid = False
            # filtered += "\n\nChoice of" + str(input_filter) + "will remove ALL words from the corpus."
            # filtered += "Please choose a different filter."

    except ValueError:
        input_filter = 0

    return (candidates, filtered, valid)

# Stores all of the variables for the labels
class PrepData(Frame):
    def __init__(self):
        self.stoplist = set()
        self.label = Label("change this")
        self.summaryHigh = Text(label="  Words:", name="summaryHighFreq", max_length=5)
        self.summaryHighPercent = Text("Percent:", "summaryHighPercent", max_length=5)
        self.high = Text("  Words:", "highFreq", max_length=5)
        self.highPercent = Text("Percent:", "highPercent", max_length=5)
        self.highChart = Label("high label", align="^")
        self.highStop = Label("high stop", align="^")
        self.highStop.text = "hello"
        self.highCandidates = []
        self.summaryLow = Text("  Words:", "summaryLowFreq", max_length=5)
        self.summaryLowPercent = Text("Percent:", "summaryLowPercent", max_length=5)
        self.low = Text("  Words:", "lowFreq", max_length=5)
        self.lowPercent = Text("Percent:", "lowPercent", max_length=5)
        self.lowChart = Label("low label", align="^")
        self.lowStop = Label("low stop", align="^")
        self.lowCandidates = []
        self.minWord = Text("Minimum word length:", "length", max_length=5)
        self.counter = 0
        self.error = Label("Error message")
        self.switch = 0
        self.stopCandidates = []
        self.english = CheckBox("Yes", label="Apply English stopwords")
        self.englishCandidates = []
        self.prepSize = Label("need to update length", align="^")
        self.fileName = "<None>"
        self.stopwordFile = Label("Current stopworded file: <None>", align="^")
        self.fileCandidates = []

# Initial landing scene
class Summary(Frame):
    # Makes the layout of the scene
    def __init__(self, screen):
        super(Summary, self).__init__(screen, screen.height, screen.width, hover_focus=True,
                                        title="Summary", reduce_cpu=True)

        global data

        # super().set_theme("green")

        highTitle = Layout([100])
        self.add_layout(highTitle)
        highTitle.add_widget(Divider(height=1, line_char=" "))
        highTitle.add_widget(Label("High Frequency Word Filter\n--------------------------", align="^", height=2))

        highOptions = Layout([7, 2, 6])
        self.add_layout(highOptions)
        highOptions.add_widget(data.summaryHigh, 1)
        highOptions.add_widget(data.summaryHighPercent, 1)

        highButton = Layout([1])
        self.add_layout(highButton)
        highButton.add_widget(Divider(height=1, line_char=" "), 0)
        highButton.add_widget(Button("High frequency wizard", self._high), 0)
        highButton.add_widget(Divider(height=2, line_char="-"), 0)
        highButton.add_widget(Divider(height=1, line_char=" "), 0)
        
        lowTitle = Layout([100])
        self.add_layout(lowTitle)
        lowTitle.add_widget(Label("Low Frequency Word Filter\n-------------------------", align="^", height=2))

        lowOptions = Layout([7, 2, 6])
        self.add_layout(lowOptions)
        lowOptions.add_widget(data.summaryLow, 1)
        lowOptions.add_widget(data.summaryLowPercent, 1)

        lowButton = Layout([1])
        self.add_layout(lowButton)
        lowButton.add_widget(Divider(height=1, line_char=" "), 0)
        lowButton.add_widget(Button("Low frequency wizard", self._low), 0)
        lowButton.add_widget(Divider(height=2, line_char="-"), 0)
        lowButton.add_widget(Divider(height=1, line_char=" "), 0)

        stopwordHeader = Layout([1])
        self.add_layout(stopwordHeader)
        stopwordHeader.add_widget(Label("Stopwords\n---------", align="^", height=2), 0)

        stopwords = Layout([8, 6, 4])
        self.add_layout(stopwords)
        stopwords.add_widget(data.english, 1)
        
        stopMinWords = Layout([8, 5, 5])
        self.add_layout(stopMinWords)
        stopMinWords.add_widget(data.minWord, 1)

        stopwordFileLayout = Layout([1])
        self.add_layout(stopwordFileLayout)
        stopwordFileLayout.add_widget(data.stopwordFile, 0)
        stopwordFileLayout.add_widget(Divider(height=1, line_char=" "), 0)
        stopwordFileLayout.add_widget(Button("Select new file", self._chooseFile), 0)
        stopwordFileLayout.add_widget(Divider(height=2, line_char="-"), 0)
        stopwordFileLayout.add_widget(Divider(height=1, line_char=" "), 0)

        corpusLenLayout = Layout([1])
        self.add_layout(corpusLenLayout)
        corpusLenLayout.add_widget(Label("Corpus Length\n-------------", align="^", height=2), 0)
        corpusLenLayout.add_widget(Label("Original corpus length: " + str(data.c.original_length), align="^"))
        corpusLenLayout.add_widget(data.prepSize)
        corpusLenLayout.add_widget(Divider(height=1, line_char=" "), 0)

        layout2 = Layout([1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("prep", self._prep), 0)
        layout2.add_widget(Button("exit", self._exit), 1)
        self.fix()
    
    # Preps the corpus
    def _prep(self):
        self.save()
        global data
        minNum = 3
        # Ensure that there is a valid value for one of the high fields
        try:
            high = validate(data.summaryHigh, data.summaryHighPercent, data.high, data.highPercent, "high", False)
        except Exception as e:
            self._scene.add_effect(PopUpDialog(self._screen, e.args[0], e.args[1], on_close=self._prepHigh))
            return
        # Ensure that there is a valid value for one of the low fields
        try:
            low = validate(data.summaryLow, data.summaryLowPercent, data.low, data.lowPercent, "low", True)
        except Exception as e:
            self._scene.add_effect(PopUpDialog(self._screen, e.args[0], e.args[1], on_close=self._prepLow))
            return
        # Ensure there is a valid calue for the min word field
        if data.minWord.value != "":
            try:
                minNum = int(data.minWord.value)
            except Exception as e:
                self._scene.add_effect(PopUpDialog(self._screen, "Please enter a valid value for Minimum Word Length", ["OK"]))
                return
        # Apply English stopwords if the checkbox is selected
        if data.english.value:
            data.englishCandidates = stop_language(data.c, "english")
        else:
            data.englishCandidates = []
        # Get the stopwords from a file
        if data.fileName != "<None>":
            with open(data.fileName, encoding='utf8') as swf:
                    data.fileCandidates = [word.strip() for word in swf]

                    if len(data.fileCandidates):
                        print("Applying custom stopword file to remove {} word{}.".format(
                            len(data.fileCandidates), 's' if len(data.fileCandidates) > 1 else ''))
        else:
            data.fileCandidates = []
        data.highCandidates, filtered, valid = get_high_filter_stops(data.c, words=data.stoplist, items=data.items, counts=data.counts,
                                                                num=high)
        # Checks to see if the value entered with filter the whole corpus out
        if not valid:
            self._scene.add_effect(PopUpDialog(self._screen, "Current filter for high will remove all values, please choose a different filter", ["OK"]))
            return
        data.lowCandidates, filtered, valid = get_low_filter_stops(data.c, words=data.stoplist, items=data.items, counts=data.counts,
                                                                num=low)
        # Checks to see if the value entered with filter the whole corpus out
        if not valid:
            self._scene.add_effect(PopUpDialog(self._screen, "Current filter for low will remove all values, please choose a different filter", ["OK"]))
            return
        data.stopCandidates = get_small_words(data.c, minNum)
        raise StopApplication("Quitting")

    # Reset highlighting of fields
    @staticmethod
    def _fix(selection):
        global data
        data.summaryHighPercent.blur()
        data.summaryHigh.blur()

    # Handle button clicks for high value popup
    @staticmethod
    def _prepHigh(selection):
        global data
        if str(selection) == "0":
            data.summaryHighPercent._value = "30.0"
        elif str(selection) == "1":
            data.summaryHighPercent._value = "0.0"
        else:
            data.summaryHighPercent.focus()
            data.summaryHigh.focus()
            confirm()

    # Handle button clicks for low value popup
    @staticmethod
    def _prepLow(selection):
        global data
        if str(selection) == "0":
            data.summaryLowPercent._value = "20.0"
        elif str(selection) == "1":
            data.summaryLowPercent._value = "0.0"
        else:
            data.summaryLowPercent.focus()
            data.summaryLow.focus()
            confirm()

    # Handle button click of the <high> button on the Summary scene
    def _high(self):
        self.save()
        global data
        
        # Determine if one of the high values are valid
        try:
            high = validate(data.summaryHigh, data.summaryHighPercent, data.high, data.highPercent, "high", False)
        except Exception as e:
            if e.args[2]:
                self._scene.add_effect(PopUpDialog(self._screen, e.args[0], e.args[1], on_close=self._popupHigh))
            else:
                self._scene.add_effect(PopUpDialog(self._screen, e.args[0], e.args[1]))
            return
        
        data.highCandidates, filtered, valid = get_high_filter_stops(data.c, words=data.stoplist, items=data.items, counts=data.counts,
                                                                num=high)
        # Checks to see if the value entered with filter the whole corpus out
        if not valid:
            self._scene.add_effect(PopUpDialog(self._screen, "Current filter for high will remove all values, please choose a different filter", ["OK"]))
            return
        
        temp = deepcopy(data.stoplist)
        temp.update(data.highCandidates)
        chart = get_high_filter_chart(data.c, words=temp, items=data.items, counts=data.counts,
                                                                num=high)
        (columns, line) = os.get_terminal_size()
        data.highChart.text = chart
        data.highChart._required_height = chart.count('\n') + 1
        data.highStop.text = filtered
        data.highStop._required_height = line - data.highChart._required_height - 5
        data.highFreqScene.fix()
        raise NextScene("High Freq")

    # Handle button clicks for high popup
    @staticmethod
    def _popupHigh(selection):
        global data
        if str(selection) == "0":
            data.summaryHighPercent._value = "30.0"
        elif str(selection) == "1":
            data.summaryHighPercent._value = "0.0"
        else:
            data.summaryHighPercent.focus()
            data.summaryHigh.focus()
            confirm()
            return
        high = validate(data.summaryHigh, data.summaryHighPercent, data.high, data.highPercent, "high", False)
        data.highCandidates, filtered, valid = get_high_filter_stops(data.c, words=data.stoplist, items=data.items, counts=data.counts,
                                                                num=high)
        temp = deepcopy(data.stoplist)
        temp.update(data.highCandidates)
        chart = get_high_filter_chart(data.c, words=temp, items=data.items, counts=data.counts,
                                                                num=high)
        (columns, line) = os.get_terminal_size()
        data.highChart.text = chart
        data.highChart._required_height = chart.count('\n') + 1
        data.highStop.text = filtered
        data.highStop._required_height = line - data.highChart._required_height - 5
        data.highFreqScene.fix()
        raise NextScene("High Freq")
    
    # Handle button click of the <low> button on the Summary scene
    def _low(self):
        self.save()
        global data
        
        # Determine if one of the low values are valid
        try:
            low = validate(data.summaryLow, data.summaryLowPercent, data.low, data.lowPercent, "low", True)
        except Exception as e:
            if e.args[2]:
                self._scene.add_effect(PopUpDialog(self._screen, e.args[0], e.args[1], on_close=self._popupLow))
            else:
                self._scene.add_effect(PopUpDialog(self._screen, e.args[0], e.args[1]))
            return
            
        data.lowCandidates, filtered, valid = get_low_filter_stops(data.c, words=data.stoplist, items=data.items, counts=data.counts,
                                                                num=low)
        # Checks to see if the value entered with filter the whole corpus out
        if not valid:
            self._scene.add_effect(PopUpDialog(self._screen, "Current filter for low will remove all values, please choose a different filter", ["OK"]))
            return
        (columns, line) = os.get_terminal_size()
        temp = deepcopy(data.stoplist)
        temp.update(data.lowCandidates)
        chart = get_low_filter_chart(data.c, words=temp, items=data.items, counts=data.counts,
                                                            num=low)
        data.lowChart.text = chart
        data.lowChart._required_height = chart.count('\n') + 1
        data.lowStop.text = filtered
        data.lowStop._required_height = line - data.lowChart._required_height - 5
        data.lowFreqScene.fix()
        raise NextScene("Low Freq")
    
    # Handle button clicks for low popup
    @staticmethod
    def _popupLow(selection):
        global data
        if str(selection) == "0":
            data.summaryLowPercent._value = "20.0"
        elif str(selection) == "1":
            data.summaryLowPercent._value = "0.0"
        else:
            data.summaryLowPercent.focus()
            data.summaryLow.focus()
            confirm()
            return
        low = validate(data.summaryLow, data.summaryLowPercent, data.low, data.lowPercent, "low", True)
        data.lowCandidates, filtered, valid = get_low_filter_stops(data.c, words=data.stoplist, items=data.items, counts=data.counts,
                                                                num=low)
        temp = deepcopy(data.stoplist)
        temp.update(data.lowCandidates)
        chart = get_low_filter_chart(data.c, words=temp, items=data.items, counts=data.counts,
                                                                num=low)
        (columns, line) = os.get_terminal_size()
        data.lowChart.text = chart
        data.lowChart._required_height = chart.count('\n') + 1
        data.lowStop.text = filtered
        data.lowStop._required_height = line - data.lowChart._required_height - 5
        data.lowFreqScene.fix()
        raise NextScene("Low Freq")

    def _chooseFile(self):
        raise NextScene("File Browser")

    # Exits without prepping
    @staticmethod
    def _exit():
        sys.exit(0)
        raise StopApplication("Quitting")

# High frequency scene
class HighFreq(Frame):
    # Loads in the scene layout
    def __init__(self, screen):
        super(HighFreq, self).__init__(screen, screen.height, screen.width, hover_focus=True,
                                        title="High Frequency Word Filter", reduce_cpu=True)

        global data
        data.highFreqScene = self
        
        chartLayout = Layout([1])
        self.add_layout(chartLayout)
        chartLayout.add_widget(data.highChart, 0)
        fieldsLayout = Layout([7, 2, 6])
        self.add_layout(fieldsLayout)
        fieldsLayout.add_widget(data.high, 1)
        fieldsLayout.add_widget(data.highPercent, 1)
        stopLayout = Layout([1])
        self.add_layout(stopLayout)
        stopLayout.add_widget(data.highStop)
        layout2 = Layout([1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("Ok", self._ok), 0)
        layout2.add_widget(Button("Update", self._change), 1)
        self.fix()

    # Handle button click of Ok
    def _ok(self):
        self.save()
        global data

        # Determines if one of the high values are valid
        try:
            high = validate(data.high, data.highPercent, data.summaryHigh, data.summaryHighPercent, "high", False)
        except Exception as e:
            if e.args[2]:
                self._scene.add_effect(PopUpDialog(self._screen, e.args[0], e.args[1], on_close=self._popup))
            else:
                self._scene.add_effect(PopUpDialog(self._screen, e.args[0], e.args[1]))
            return

        data.highCandidates, filtered, valid = get_high_filter_stops(data.c, words=data.stoplist, items=data.items, counts=data.counts,
                                                                num=high)
        # Checks to see if the value entered with filter the whole corpus out
        if not valid:
            self._scene.add_effect(PopUpDialog(self._screen, "Current filter for high will remove all values, please choose a different filter", ["OK"]))
            return
        (columns, line) = os.get_terminal_size()
        temp = deepcopy(data.stoplist)
        temp.update(data.highCandidates)
        chart = get_high_filter_chart(data.c, words=temp, items=data.items, counts=data.counts,
                                                                num=high)
        data.highChart.text = chart
        data.highChart._required_height = chart.count('\n') + 1
        data.highStop.text = filtered
        data.highStop._required_height = line - data.highChart._required_height - 5
        data.highFreqScene.fix()
        updatePreppedLength()
        raise NextScene("Summary")

    # Handle button clicks for high popup
    @staticmethod
    def _popup(selection):
        # Handle the selections
        if str(selection) == "0":
            data.highPercent._value = "30.0"
        elif str(selection) == "1":
            data.highPercent._value = "0.0"
        else:
            data.highPercent.focus()
            data.high.focus()
            confirm()
            return
        high = validate(data.high, data.highPercent, data.summaryHigh, data.summaryHighPercent, "high", False)
        data.highCandidates, filtered, valid = get_high_filter_stops(data.c, words=data.stoplist, items=data.items, counts=data.counts,
                                                                num=high)
        (columns, line) = os.get_terminal_size()
        temp = deepcopy(data.stoplist)
        temp.update(data.highCandidates)
        chart = get_high_filter_chart(data.c, words=temp, items=data.items, counts=data.counts,
                                                                num=high)
        data.highChart.text = chart
        data.highChart._required_height = chart.count('\n') + 1
        data.highStop.text = filtered
        data.highStop._required_height = line - data.highChart._required_height - 5
        data.highFreqScene.fix()
        raise NextScene("Summary")
    
    # Handle button click for Update
    def _change(self):
        self.save()
        global data

        # Determine if one of the high values are valid
        try:
            high = validate(data.high, data.highPercent, data.summaryHigh, data.summaryHighPercent, "high", False)
        except Exception as e:
            if e.args[2]:
                self._scene.add_effect(PopUpDialog(self._screen, e.args[0], e.args[1], on_close=self._popupChange))
            else:
                self._scene.add_effect(PopUpDialog(self._screen, e.args[0], e.args[1]))
            return

        data.highCandidates, filtered, valid = get_high_filter_stops(data.c, words=data.stoplist, items=data.items, counts=data.counts,
                                                                num=high)
        # Checks to see if the value entered with filter the whole corpus out
        if not valid:
            self._scene.add_effect(PopUpDialog(self._screen, "Current filter for high will remove all values, please choose a different filter", ["OK"]))
            return
        
        (columns, line) = os.get_terminal_size()
        temp = deepcopy(data.stoplist)
        temp.update(data.highCandidates)
        chart = get_high_filter_chart(data.c, words=temp, items=data.items, counts=data.counts,
                                                                num=high)
        data.highChart.text = chart
        data.highChart._required_height = chart.count('\n') + 1
        data.highStop.text = filtered
        data.highStop._required_height = line - data.highChart._required_height - 5
        data.highFreqScene.fix()
    
    # Handle button click for popup after clicking change
    @staticmethod
    def _popupChange(selection):
        # Handle the selections
        if str(selection) == "0":
            data.highPercent._value = "30.0"
        elif str(selection) == "1":
            data.highPercent._value = "0.0"
        else:
            data.highPercent.focus()
            data.high.focus()
            confirm()
            return
        high = validate(data.high, data.highPercent, data.summaryHigh, data.summaryHighPercent, "high", False)
        data.highCandidates, filtered, valid = get_high_filter_stops(data.c, words=data.stoplist, items=data.items, counts=data.counts,
                                                                num=high)
        (columns, line) = os.get_terminal_size()
        temp = deepcopy(data.stoplist)
        temp.update(data.highCandidates)
        chart = get_high_filter_chart(data.c, words=temp, items=data.items, counts=data.counts,
                                                                num=high)
        data.highChart.text = chart
        data.highChart._required_height = chart.count('\n') + 1
        data.highStop.text = filtered
        data.highStop._required_height = line - data.highChart._required_height - 5
        data.highFreqScene.fix()

# Low frequency scene
class LowFreq(Frame):
    # Loads in the scene layout
    def __init__(self, screen):
        super(LowFreq, self).__init__(screen, screen.height, screen.width, hover_focus=True,
                                        title="Low Frequency Word Filter", reduce_cpu=True)

        global data
        data.lowFreqScene = self
        
        chartLayout = Layout([1])
        self.add_layout(chartLayout)
        chartLayout.add_widget(data.lowChart, 0)
        fieldsLayout = Layout([7, 2, 6])
        self.add_layout(fieldsLayout)
        fieldsLayout.add_widget(data.low, 1)
        fieldsLayout.add_widget(data.lowPercent, 1)
        stopLayout = Layout([1])
        self.add_layout(stopLayout)
        stopLayout.add_widget(data.lowStop)
        layout2 = Layout([1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("Ok", self._ok), 0)
        layout2.add_widget(Button("Update", self._change), 1)
        self.fix()

    # Handle button click of Ok
    def _ok(self):
        self.save()
        global data
        
        # Determines if one of the low values are valid
        try:
            low = validate(data.low, data.lowPercent, data.summaryLow, data.summaryLowPercent, "low", True)
        except Exception as e:
            if e.args[2]:
                self._scene.add_effect(PopUpDialog(self._screen, e.args[0], e.args[1], on_close=self._popup))
            else:
                self._scene.add_effect(PopUpDialog(self._screen, e.args[0], e.args[1]))
            return
            
        data.lowCandidates, filtered, valid = get_low_filter_stops(data.c, words=data.stoplist, items=data.items, counts=data.counts,
                                                                num=low)
        # Checks to see if the value entered with filter the whole corpus out
        if not valid:
            self._scene.add_effect(PopUpDialog(self._screen, "Current filter for low will remove all values, please choose a different filter", ["OK"]))
            return
        (columns, line) = os.get_terminal_size()
        temp = deepcopy(data.stoplist)
        temp.update(data.lowCandidates)
        chart = get_low_filter_chart(data.c, words=temp, items=data.items, counts=data.counts,
                                                            num=low)
        data.lowChart.text = chart
        data.lowChart._required_height = chart.count('\n') + 1
        data.lowStop.text = filtered
        data.lowStop._required_height = line - data.lowChart._required_height - 5
        data.lowFreqScene.fix()
        updatePreppedLength()
        raise NextScene("Summary")
    
    # Handle button clicks for low popup
    @staticmethod
    def _popup(selection):
        # Handle the selections
        if str(selection) == "0":
            data.lowPercent._value = "20.0"
        elif str(selection) == "1":
            data.lowPercent._value = "0.0"
        else:
            data.lowPercent.focus()
            data.low.focus()
            confirm()
            return
        low = validate(data.low, data.lowPercent, data.summaryLow, data.summaryLowPercent, "low", True)

        data.lowCandidates, filtered, valid = get_low_filter_stops(data.c, words=data.stoplist, items=data.items, counts=data.counts,
                                                                num=low)
        (columns, line) = os.get_terminal_size()
        temp = deepcopy(data.stoplist)
        temp.update(data.lowCandidates)
        (chart, text) = get_low_filter_chart(data.c, words=temp, items=data.items, counts=data.counts,
                                                            num=low)
        data.lowChart.text = chart
        data.lowChart._required_height = chart.count('\n') + 1
        data.lowStop.text = filtered
        data.lowStop._required_height = line - data.lowChart._required_height - 5
        data.lowFreqScene.fix()
        raise NextScene("Summary")
    
    # Handle button click for Update
    def _change(self):
        self.save()
        global data
        
        # Determine if one of the low values are valid
        try:
            low = validate(data.low, data.lowPercent, data.summaryLow, data.summaryLowPercent, "low", True)
        except Exception as e:
            if e.args[2]:
                self._scene.add_effect(PopUpDialog(self._screen, e.args[0], e.args[1], on_close=self._popupChange))
            else:
                self._scene.add_effect(PopUpDialog(self._screen, e.args[0], e.args[1]))
            return
            
        data.lowCandidates, filtered, valid = get_low_filter_stops(data.c, words=data.stoplist, items=data.items, counts=data.counts,
                                                                num=low)
        # Checks to see if the value entered with filter the whole corpus out
        if not valid:
            self._scene.add_effect(PopUpDialog(self._screen, "Current filter for low will remove all values, please choose a different filter", ["OK"]))
            return
        (columns, line) = os.get_terminal_size()
        temp = deepcopy(data.stoplist)
        temp.update(data.lowCandidates)
        chart = get_low_filter_chart(data.c, words=temp, items=data.items, counts=data.counts,
                                                            num=low)
        data.lowChart.text = chart
        data.lowChart._required_height = chart.count('\n') + 1
        data.lowStop.text = filtered
        data.lowStop._required_height = line - data.lowChart._required_height - 5
        data.lowFreqScene.fix()
    
    # Handle button click for popup after clicking change
    @staticmethod
    def _popupChange(selection):
        # Handle the selections
        if str(selection) == "0":
            data.lowPercent._value = "20.0"
        elif str(selection) == "1":
            data.lowPercent._value = "0.0"
        else:
            data.lowPercent.focus()
            data.low.focus()
            confirm()
            return
        low = validate(data.low, data.lowPercent, data.summaryLow, data.summaryLowPercent, "low", True)
        data.lowCandidates, filtered, valid = get_low_filter_stops(data.c, words=data.stoplist, items=data.items, counts=data.counts,
                                                                num=low)
        (columns, line) = os.get_terminal_size()
        temp = deepcopy(data.stoplist)
        temp.update(data.lowCandidates)
        chart = get_low_filter_chart(data.c, words=temp, items=data.items, counts=data.counts,
                                                                num=low)
        data.lowChart.text = chart
        data.lowChart._required_height = chart.count('\n') + 1
        data.lowStop.text = filtered
        data.lowStop._required_height = line - data.lowChart._required_height - 5
        data.lowFreqScene.fix()

# Taken from: https://github.com/peterbrittain/asciimatics/blob/master/samples/treeview.py
class Files(Frame):
    def __init__(self, screen):
        super(Files, self).__init__(
            screen, screen.height, screen.width, has_border=False)

        # Create the (very simple) form layout...
        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)

        # Now populate it with the widgets we want to use.
        self._details = Text()
        self._details.disabled = True
        self._details.custom_colour = "field"
        regex = "^([\w+\- ]*)(.txt)$"
        self._list = FileBrowser(Widget.FILL_FRAME,
                                 os.path.abspath("."),
                                 name="mc_list",
                                 on_select=self.popup,
                                 on_change=self.details,
                                 file_filter=regex)
        layout.add_widget(Label("Local disk browser sample"))
        layout.add_widget(Divider())
        layout.add_widget(self._list)
        layout.add_widget(Divider())
        layout.add_widget(self._details)
        layout.add_widget(Label("Press Enter to select, 'q' to quit without making changes, or 'c' to clear file selection."))

        # Prepare the Frame for use.
        self.fix()

    def popup(self):
        # Just confirm whenever the user actually selects something.
        if not self._list.value.endswith(".txt") and "." in self._list.value:
            self._scene.add_effect(PopUpDialog(self._screen, "Please pick a valid file (a .txt file or a file with no extension)", ["OK"]))
        else:
            global data
            f = open(self._list.value, "r")
            text = f.read()
            data.tempFileName = self._list.value
            self._scene.add_effect(PopUpDialog(self._screen, "Use the selected file with the following text?\n" + text, ["Yes", "No"], on_close=self.handlePopup))

    @staticmethod
    def handlePopup(selection):
        if str(selection) == "0":
            global data
            data.stopwordFile.text = "Current stopworded file: " + data.tempFileName
            data.fileName = data.tempFileName
            updatePreppedLength()
            raise NextScene("Summary")

    def details(self):
        # If python magic is installed, provide a little more detail of the current file.
        if self._list.value:
            if os.path.isdir(self._list.value):
                self._details.value = "Directory"
            elif os.path.isfile(self._list.value):
                try:
                    self._details.value = magic.from_file(self._list.value)
                except NameError:
                    self._details.value = "File (run 'pip install python-magic' for more details)"
        else:
            self._details.value = "--"

    def process_event(self, event):
        # Do the key handling for this Frame.
        global data
        if isinstance(event, KeyboardEvent):
            if event.key_code in [ord('q'), ord('Q'), Screen.ctrl("c")]:
                updatePreppedLength()
                raise NextScene("Summary")
            elif event.key_code in [ord('c'), ord('C')]:
                data.stopwordFile.text = "Current stopword file: <None>"
                data.fileName = "<None>"
                updatePreppedLength()
                raise NextScene("Summary")

        # Now pass on to lower levels for normal handling of the event.
        return super(Files, self).process_event(event)

# Determine if the values for the num and percent fields are valid
def validate(num, percent, numPair, percentPair, iden, rev):
    defaults = {"high": "30%", "low": "20%"}
    if num.value == "" and percent.value == "":
        raise Exception("Apply default of " + str(defaults[iden]) + " for the " + iden + " frequency, don't stop list, or edit value?", ["Yes", "Don't stop list", "Edit value"], True)
    if num.value != "" and percent.value != "":
        raise Exception("Pleae enter a value for only one " + iden + " field", ["Ok"], False)
    try:
        msg = "error"
        if num.value != "":
            msg = "Please enter a valid " + iden + " value (int)"
            ret = int(num.value)
            numPair._value = num.value
            percentPair._value = ""
        if percent.value != "":
            msg = "Please enter a valid " + iden + " percent value (float or int)"
            ret = float(percent.value)
            percentPair._value = percent.value
            numPair._value = ""
            ret = get_closest_bin(data.c, 1 - (ret / 100.), reverse=rev, counts=data.counts)
    except:
        raise Exception(msg, ["Ok"], False)
    return ret

# Update the prepped length by storing c and stoplist in temp varibles,
# then updaing the originals, and then restoring the originals
def updatePreppedLength():
    global data
    temp = deepcopy(data.stoplist)
    tempC = deepcopy(data.c)
    if data.english.value:
        data.englishCandidates = stop_language(tempC, "english")
        temp.update(data.englishCandidates)
    if data.fileName != "<None>":
        with open(data.fileName, encoding='utf8') as swf:
                data.fileCandidates = [word.strip() for word in swf]
                if len(data.fileCandidates):
                    print("Applying custom stopword file to remove {} word{}.".format(
                        len(data.fileCandidates), 's' if len(data.fileCandidates) > 1 else ''))
                    temp.update(data.fileCandidates)
    minNum = 3
    if data.minWord.value != "":
        try:
            minNum = int(data.minWord.value)
        except Exception:
            minNum = 3
    data.stopCandidates = get_small_words(tempC, minNum)
    temp.update(data.stopCandidates)
    temp.update(data.lowCandidates)
    temp.update(data.highCandidates)
    tempC.in_place_stoplist(temp)
    data.prepSize.text = str("Prepared corpus length: " + str(len(tempC)))

# Highlight the necessary fields
def confirm():
    global data
    tempScreen = data.wholeScreen.current_scene._effects[0]._screen
    tempScene = data.wholeScreen.current_scene
    tempScene.add_effect(PopUpDialog(tempScreen, "Please input a value in one of the highlighted fields", ["OK"], on_close=reset))

# Reset all highlighted fields
def reset(selection):
    global data
    data.summaryHigh.blur()
    data.summaryHighPercent.blur()
    data.summaryLow.blur()
    data.summaryLowPercent.blur()
    data.high.blur()
    data.highPercent.blur()
    data.low.blur()
    data.lowPercent.blur()

def main(args):
    global data
    data = PrepData()

    config = topicexplorer.config.read(args.config_file)

    if config.getboolean("main", "sentences"):
        from vsm.extensions.ldasentences import CorpusSent as Corpus
    else:
        from vsm.corpus import Corpus

    if args.lang is None:
        args.lang = []

    args.corpus_path = config.get("main", "corpus_file")
    data.c = Corpus.load(args.corpus_path)

    if data.c.original_length != len(data.c.corpus):
        print("Corpus has already been prepared. Proceed to training or")
        print("re-init the corpus to apply a different set of stopwords.")
        print("\nTIP: Train the LDA models with:")
        print("         topicexplorer train", args.config_file)
        sys.exit(1)

    # auto-guess a language
    """
    new_langs = [lang for lang in detect_langs(c) if lang in langs and lang not in args.lang]
    if new_langs:
        args.lang.extend(new_langs)
    """

    # # Language information, not sure if I should remove it

    # # add default locale if no other languages are specified
    # # do not add if in quiet mode -- make everything explicit
    # if not args.lang and not args.quiet:
    #     import locale
    #     locale = locale.getdefaultlocale()[0].split('_')[0].lower()
    #     if locale in langs.keys():
    #         args.lang.append(locale)

    # # check for any new candidates
    # args.lang = [lang for lang in args.lang if stop_language(data.c, langs[lang])]
    # if args.lang and not args.quiet:
    #     args.lang = lang_prompt(args.lang)

    # data.stoplist = set()
    # # Apply stop words
    # print(" ")
    # for lang in args.lang:
    #     print("Applying", langs[lang], "stopwords")
    #     candidates = stop_language(data.c, langs[lang])
    #     if len(candidates):
    #         data.stoplist.update(candidates)
    
    # Apply custom stopwords file
    if args.stopword_file:
        data.fileName = args.stopword_file
        data.stopwordFile.text = "Current stopworded file: " + args.stopword_file
        # with open(args.stopword_file, encoding='utf8') as swf:
        #     candidates = [unidecode(word.strip()) for word in swf]
        #     data.fileCandidates = [word.strip() for word in swf]

        #     if len(data.fileCandidates):
        #         print("Applying custom stopword file to remove {} word{}.".format(
        #             len(data.fileCandidates), 's' if len(data.fileCandidates) > 1 else ''))
        #         data.stoplist.update(candidates)

    if args.min_word_len:
        candidates = get_small_words(data.c, args.min_word_len)
        if len(candidates):
            data.lowCandidates = candidates
            data.minWord._value = args.min_word_len
            # print("Filtering {} small word{} with less than {} characters.".format(
            #     len(candidates), 's' if len(candidates) > 1 else '', args.min_word_len))
            # data.stoplist.update(candidates)

    # cache item counts
    data.items, data.counts = get_corpus_counts(data.c)
    if args.high_filter is None and args.high_percent is None and args.quiet:
        pass
    elif args.high_filter:
        candidates = get_candidate_words(data.c, args.high_filter, sort=False, items=data.items, counts=data.counts)
        if len(candidates):
            data.highCandidates = candidates
            data.summaryHigh._value = args.high_filter
    elif args.high_percent:
        args.high_filter = get_closest_bin(data.c, 1 - (args.high_percent / 100.), counts=data.counts)
        print(args.high_filter)
        candidates = get_candidate_words(data.c, args.high_filter, sort=False, items=data.items, counts=data.counts)
        if len(candidates):
            data.highCandidates = candidates
            data.summaryHighPercent._value = args.high_percent
    

    if args.low_filter is None and args.low_percent is None and args.quiet:
        pass
    elif args.low_filter:
        candidates = get_candidate_words(data.c, -1 * args.low_filter, sort=False, items=data.items, counts=data.counts)
        if len(candidates):
            data.lowCandidates = candidates
            data.summaryLow._value = args.low_filter
    elif args.low_percent:
        args.low_filter = get_closest_bin(data.c, 1 - (args.low_percent / 100.), reverse=True, counts=data.counts)
        print(args.low_filter)
        candidates = get_candidate_words(data.c, -1 * args.low_filter, sort=False, items=data.items, counts=data.counts)
        if len(candidates):
            data.lowCandidates = candidates
            data.summaryLowPercent._value = args.low_percent

    def gui(screen, scene):
        scenes = [
            Scene([Summary(screen)], -1, name="Summary"),
            Scene([HighFreq(screen)], -1, name="High Freq"),
            Scene([LowFreq(screen)], -1, name="Low Freq"),
            Scene([Files(screen)], -1, name="File Browser")
        ]
        global data
        data.wholeScreen = screen
        screen.play(scenes, stop_on_resize=True, start_scene=scene)

    data.prepSize.text = str("Prepared corpus length: " + str(len(data.c)))

    updatePreppedLength()

    last_scene = None
    while True:
        try:
            Screen.wrapper(gui, catch_interrupt=True, arguments=[last_scene])
            break
            # sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene

    data.stoplist.update(data.highCandidates)
    data.stoplist.update(data.lowCandidates)
    data.stoplist.update(data.stopCandidates)
    data.stoplist.update(data.englishCandidates)
    data.stoplist.update(data.fileCandidates)

    if not data.stoplist:
        print("No stopwords applied.\n\n")

        sys.exit(0)
    else:
        print("\n\nApplying {} stopword{}".format(len(data.stoplist),
                                                  's' if len(data.stoplist) > 1 else ''))
        data.c.in_place_stoplist(data.stoplist)
        print(len(data.c))
        print("\n")

    def name_corpus(dirname, languages, lowfreq=None, highfreq=None):
        corpus_name = [dirname]

        if args.lang:
            corpus_name.append('nltk')
            corpus_name.append(''.join(args.lang))

        if lowfreq is not None and lowfreq > 0:
            corpus_name.append('freq%s' % lowfreq)
        if highfreq is not None and highfreq > 0:
            corpus_name.append('N%s' % highfreq)

        corpus_name = '-'.join(corpus_name)
        corpus_name += '.npz'
        return corpus_name

    dirname = os.path.basename(args.corpus_path).split('-nltk-')[0].replace('.npz', '')
    corpus_name = name_corpus(dirname, ['en'], args.low_filter, args.high_filter)

    model_path = os.path.dirname(args.corpus_path)
    args.corpus_path = os.path.join(model_path, corpus_name)
    data.c.save(args.corpus_path)

    config.set("main", "corpus_file", args.corpus_path)
    config.remove_option("main", "model_pattern")
    with open(args.config_file, 'w') as configfh:
        config.write(configfh)


def populate_parser(parser):
    import argparse
    parser.add_argument("config_file", help="Path to Config",
                        type=lambda x: is_valid_configfile(parser, x))

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--high", type=int, dest="high_filter",
                        help=argparse.SUPPRESS, default=None)
    group.add_argument("--high-percent", type=float, dest="high_percent",
                        help="High frequency word filter", default=None)
    
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--low", type=int, dest="low_filter",
                        default=None, help=argparse.SUPPRESS)
    group.add_argument("--low-percent", type=float, dest="low_percent",
                        default=None, help="Low frequency word filter")

    parser.add_argument("--min-word-len", type=int, dest="min_word_len",
                        default=0, help="Filter short words [Default: 0]")

    parser.add_argument("--stopword-file", dest="stopword_file",
                        help="File with custom stopwords")

    parser.add_argument("-q", "--quiet", help="Do not prompt for input",
                        action="store_true")

    parser.add_argument("--lang", nargs='+', choices=langs.keys(),
                        help=argparse.SUPPRESS, metavar='xx')
    """
    parser.epilog = ('Available language stoplists (use 2-letter code): \n\t' +
                     '\n\t'.join(['{k}    {v}'.format(k=k, v=v.capitalize())
                                  for k, v in sorted(langs.items(),
                                                     key=lambda x: x[1])]))
    """

if __name__ == '__main__':
    import argparse
    from argparse import ArgumentParser
    parser = ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    populate_parser(parser)
    args = parser.parse_args()

    main(args)

data = ""
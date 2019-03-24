from codecs import open
import numpy as np

from vsm.corpus import align_corpora
from vsm.model.ldacgsseq import LdaCgsQuerySampler
from vsm.viewer.ldacgsviewer import LdaCgsViewer
from vsm.extensions.corpusbuilders import toy_corpus, corpus_from_strings

def build_sample(filename: str, v: LdaCgsViewer, n_iterations: int=200):
    with open(filename, encoding='utf8') as textfile:
        text = [textfile.read()]

    origin = corpus_from_strings(text, nltk_stop=False, stop_freq=0)
    #origin = toy_corpus('origin1st.txt', is_filename=True, stop_freq=0, nltk_stop=True)
    origin.context_types = [v.model.context_type]
    
    c = align_corpora(v.corpus, origin)
    q = LdaCgsQuerySampler(v.model, old_corpus=v.corpus, new_corpus=c,
                           context_type=v.model.context_type, align_corpora=False)
    q.train(n_iterations=n_iterations)
    return q

def get_topics(query_sample):
    return np.squeeze(query_sample.top_doc / sum(query_sample.top_doc))

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('configfile')
    parser.add_argument('textfile')
    parser.add_argument('-N', help='number of samples to generate', type=int, default=1)
    parser.add_argument('-k', help='number of topics', type=int)
    args = parser.parse_args()

    import topicexplorer
    te = topicexplorer.from_config(args.config_file)

    for i in range(args.N):
        sample = build_sample(args.textfile, te[args.k])
        topics = get_topics(sample)
        print(*topics)


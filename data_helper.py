#coding=utf8
#coding=utf8
from __future__ import print_function
from __future__ import division
from gensim import corpora, models, similarities
import os


class Vocab(object):
    def __init__(self, vocab_file, min_frequence = 10000):
        self._word_to_id = {}
        self._id_to_word = {}
        self._count = 0
        with open(vocab_file, 'r') as vocab_f:
            next(vocab_f)
            for line in vocab_f:
                pieces = line.split(',')
                if len(pieces) != 2:
                    print('Warning: incorrectly formatted line in vocabulary file: %s\n'%line)
                    continue
                w = pieces[0]
                count = pieces[1]
                if w in self._word_to_id:
                    raise Exception('Duplicated word in vocabulary file: %s' % w)
                self._word_to_id[w] = int(count)
                self._id_to_word[int(count)] = w
    def word2id(self, word):
        return self._word_to_id[word]

    def id2word(self, word_id):
        if word_id not in self._id_to_word:
            raise ValueError('Id not found in vocab: %d' % word_id)
        else:
            return self._id_to_word[word_id]

def make_dictionary(dictionary_file, seg_corpus = None):
    '''
    :param seg_corpus: 分好词的文本数据
    :return: 建立的词典
    '''
    if os.path.exists(dictionary_file) or seg_corpus == None:
        dictionary = corpora.Dictionary.load(dictionary_file)
    else:

        dictionary = corpora.Dictionary(seg_corpus)
        corpora.Dictionary.save(dictionary, dictionary_file)
    return dictionary


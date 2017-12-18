#coding=utf8
from __future__ import print_function
from __future__ import division
from data_helper import *
import jieba
import csv
import sys
BasePath = sys.path[0]
def map_word(tuple_file):
    map_dict = dict()
    number_list = list()
    csv_reader = csv.reader(open(tuple_file))
    next(csv_reader)
    for row in csv_reader:
        number = map(int, row[0:3]) + map(float, row[3:])
        number_list.append(number)
    return number_list

class CoSearch(object):
    def __init__(self, csv_tuple_path, csv_dict_path):
        print(1)
        self.vocab = Vocab(csv_dict_path)
        self.number_list = map_word(csv_tuple_path)
        # self.result_list = []
    def search(self, id, number_list):
        result_list = list()
        for i in number_list:
            if i[0] == id:
                result_list.append((i[1], i[2], i[3]))
            if i[1] == id:
                result_list.append((i[0], i[2], i[3]))
        # print(result_list)
        sorted_result_list = sorted(result_list, key=lambda key: key[2], reverse=True)
        return sorted_result_list

    def search_word(self, word, topn = 5):
        ret_dict = {'key':[],
                    'value': []}
        search_key = self.vocab.word2id(word)
        sorted_result_list = self.search(search_key, self.number_list)
        if (len(sorted_result_list) > topn):
            for i in sorted_result_list[0:topn]:
                # print(i)
                ret_dict['key'].append(self.vocab.id2word(i[0]))
                ret_dict['value'].append(i[2])
        else:
            for i in sorted_result_list:
                ret_dict['key'].append(self.vocab.id2word(i[0]))
                ret_dict['value'].append(i[2])
        return ret_dict

    def get_keywords(self, sentence):
        print(1)
        seg_sentence = list(jieba.cut(sentence))
        return_word_list = list()
        return_relation_list = dict()
        for word in set(seg_sentence):
            try:
                # print(word)
                # word_tuple_list = w2v_model_min_count5.most_similar(word.decode('utf8'), topn=5)
                relation_dict = self.search_word(word.encode('utf8'))
                word_dict_list = [{'word': key,
                                   'cluster': word.encode('utf8')} for key in relation_dict['key']]

                return_word_list += word_dict_list
                tmp_list = list()
                relation_word_dict = dict(zip(relation_dict['key'], relation_dict['value']))
                for key, value in relation_word_dict.items():
                    print(key)
                    print(value)

                for tuple in zip(relation_dict['key'], relation_dict['value']):
                    tmp_list.append({'key': tuple[0], 'value': tuple[1]})
                return_relation_list[word] = tmp_list
            # return_relation_list.append({word:relation_dict})
            # return_relation_list.append({relation_dict})

            except:
                continue

        return return_word_list, return_relation_list
if __name__ == "__main__":
    csv_tuple_path = BasePath + '/csv/csv_tuple_pos_select.csv'
    csv_dict_path = BasePath + '/csv/csv_dict_pos_select.csv'
    Cosearch = CoSearch(csv_tuple_path, csv_dict_path)
    x = "诈骗"
    print(Cosearch.search_word(x))
    sentence = "诈骗"
    print(Cosearch.get_keywords(sentence))
#coding=utf8
from __future__ import print_function
from __future__ import division
from gensim import corpora, models, similarities
import os
from data_helper import *
import datetime
import numpy as np
from itertools import combinations
import math
import json
from My_BasePath import *
import csv


def doc2bag_corpus(dictionary, seg_corpus):

    bag_of_words_corpus = [dictionary.doc2bow(pdoc) for pdoc in seg_corpus]
    return bag_of_words_corpus

def save_json(save_path, data):
    with open(save_path, 'w+') as f:
        json.dump(data, f, ensure_ascii = False)

def load_json(save_path):
    with open(save_path, 'r') as f:
        return json.load(f)

def save_bag_corpus(dictionary, corpus, save_path):
    bag_corpus = doc2bag_corpus(dictionary, corpus)
    bag_sen_dict = dict()
    for i in range(0, len(bag_corpus)):
        tmp_sen = bag_corpus[i]
        bag_sen = [word_tuple[0] for word_tuple in tmp_sen]
        bag_sen_dict[i+1] = bag_sen
    save_json(save_path, bag_sen_dict)
    return bag_sen_dict

def save_count_in_sen(bag_sen_dict, save_count_word_in_sen_path):
    count_word_in_sen_dict = dict()
    for i in range(1, len(bag_sen_dict) + 1):
        tmp_word_id_list = bag_sen_dict[str(i)]
        for word_id in tmp_word_id_list:
            if word_id not in count_word_in_sen_dict:
                count_word_in_sen_dict[word_id] = [i]
            else:
                count_word_in_sen_dict[word_id].append(i)

    save_json(save_count_word_in_sen_path, count_word_in_sen_dict)
    return count_word_in_sen_dict

def save_candidate_pair(bag_sen_dict, save_candidate_path):
    candidate_dict = dict()
    for i in range(1, len(bag_sen_dict) + 1):
        comb = list(combinations(bag_sen_dict[str(i)], 2))
        for com_tuple in comb:
            if str(com_tuple) not in candidate_dict:
                candidate_dict[str(com_tuple)] = 1
            elif(str(com_tuple) in candidate_dict):
                candidate_dict[str(com_tuple)] += 1
    save_json(save_candidate_path, candidate_dict)
    return candidate_dict

def save_high_frequence_data(candidate_dict, save_candidate_file):
    i = 1
    for key, value in candidate_dict.items():
        i += 1
        if (value >= 2):
            i = i + 1
        if value < 10:
            del candidate_dict[key]
    #保存高频词对
    save_json(save_candidate_file, candidate_dict)
    return candidate_dict


def nmi_get(cij, ci, cj, count_sen):
    nmi_list = []
    cij.append(count_sen - cij[0] - cij[1] - cij[2])
    pij = np.array(cij) / count_sen
    pi = ci / count_sen
    pj = cj / count_sen
    for i in range(0, 4):
        if (pij[i] == 0):
            nmi_list.append(0)
            continue
        if i == 0:
            nmi_list.append(pij[i] * np.log2(pij[i] / (pi*pj)))
        elif i == 1:
            nmi_list.append(pij[i] * np.log2(pij[i] / (pi * (1 - pj))))
        elif i == 2:
            nmi_list.append(pij[i] * np.log2(pij[i] / ((1 - pi) * pj)))
        elif i == 3:
            nmi_list.append(pij[i] * np.log2(pij[i] / ((1 - pi) * (1 - pj))))

    return np.sum(np.array(nmi_list))

def save_count_word_pair_data(bag_sen_dict, word_in_sen_dict,
                              candidate_high_frequence_dict, save_count_word_pair_path):
    sen_size = len(bag_sen_dict)
    time_str = datetime.datetime.now().isoformat()

    i = 1
    for key, value in candidate_high_frequence_dict.items():
        if(i%1000 == 0):
            time_str = datetime.datetime.now().isoformat()

        i += 1
        id_list = key[1:-1].split(', ')
        w_1_1 = len(set(word_in_sen_dict[str(id_list[0])]))#统计每个高频词组[词1，词2]，词1出现在文档中的次数综合,一共在多少文档中出现过
        w_2_1 = len(set(word_in_sen_dict[str(id_list[1])]))

        l_10 = len(set(word_in_sen_dict[str(id_list[0])]) - set(word_in_sen_dict[str(id_list[1])]))#在词1里面不在词2里面的文档编号数量(出现词1的文档，但不出现词2的文档)
        l_01 = len(set(word_in_sen_dict[str(id_list[1])]) - set(word_in_sen_dict[str(id_list[0])]))#在词2里面不在词1里面的文档编号数量(出现词2的文档，但不出现词1的文档)

        nmi = nmi_get([value, l_10, l_01], w_1_1, w_2_1, sen_size)
        if (math.isnan(nmi)):
            del candidate_high_frequence_dict[key]
            continue

        candidate_high_frequence_dict[key] = [value, nmi]
    save_json(save_count_word_pair_path, candidate_high_frequence_dict)
    return candidate_high_frequence_dict
def save_data_to_csv(dictionary, count_word_pair_dict, csv_tuple_path, csv_dict_path):
    csvfile1 = open(csv_tuple_path, 'wb')
    writer1 = csv.writer(csvfile1)
    writer1.writerow(['w1', 'w2', 'count', 'pmi'])
    csvfile2 = open(csv_dict_path, 'wb')
    writer2 = csv.writer(csvfile2)
    writer2.writerow(['token', 'id'])

    data = list()
    id_all_list = list()
    for key, value in count_word_pair_dict.items():
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        # print(key)
        # print(value)
        id_list = key[1:-1].split(', ')
        id_all_list += id_list
        #data.append((int(id_list[0]), int(id_list[1]), int(value[0]), float(value[1])))
        data.append((id_list[0],  id_list[1],  value[0], value[1]))
    writer1.writerows(data)
    csvfile1.close()

    save_dict = list()
    for i in set(id_all_list):
        save_dict.append((dictionary[int(i)], i))
        # save_dict.append((dictionary[int(i)], i))

    writer2.writerows(save_dict)
    csvfile2.close()








def construct_correlation(filepath,csv_tuple_path, csv_dict_path):
    with open(filepath, 'rb') as fp:
        data = json.load(fp)
    corpus = data['content_wordlist']
    dictionary_path = BasePath + "/correlation_data/dict.pickle"
    dictionary = make_dictionary(dictionary_path, corpus)

    # # 将语料保存为词袋模型-
    save_path = BasePath + "/data/bag_sen_dict.txt"
    bag_sen_dict = save_bag_corpus(dictionary, corpus, save_path)  # 存储每个文档的向量表示，向量中每一个元素为词在字典中的位置

    # 统计每个单词出现的句子或段落#每个词出现在文档中的集合词id: 文档1,文档2，文档10，文档22
    save_path = BasePath + "/data/bag_sen_dict.txt"
    bag_sen_dict = load_json(save_path)
    save_count_word_in_sen_path = BasePath + "/data/count_word_in_sen_list.txt"
    count_word_in_sen_dict = save_count_in_sen(bag_sen_dict, save_count_word_in_sen_path)
    count_word_in_sen_dict = load_json(save_count_word_in_sen_path)


    # 统计候选词对#(词1，词2):频率，(词1，词2)已经出现在某一个文档中，频率为所有文档中出现的次数
    save_path = BasePath + "/data/bag_sen_dict.txt"
    bag_sen_dict = load_json(save_path)
    save_candidate_file_path = BasePath + "/data/candidate_word_pair.txt"
    candidate_dict = save_candidate_pair(bag_sen_dict, save_candidate_file_path)

    # 挑选高频词对,小于10的抛弃, 保存高频词对
    save_candidate_file_path = BasePath + "/data/candidate_word_pair.txt"
    candidate_dict = load_json(save_candidate_file_path)
    save_high_frequence_path = BasePath + "/data/high_frequence_word_pair.txt"
    candidate_high_frequence_dict = save_high_frequence_data(candidate_dict, save_high_frequence_path)

    # 对高频词对统计11 10 01
    # 加载高频词对 (id1, id2) = count(11)
    candidate_high_frequence_dict_path = BasePath + "/data/high_frequence_word_pair.txt"
    candidate_high_frequence_dict = load_json(candidate_high_frequence_dict_path)

    # 加载词---句子集合 w_id = [s1, s2, s3, s4 ...]
    count_word_in_sen_path = BasePath + "/data/count_word_in_sen_list.txt"
    word_in_sen_dict = load_json(count_word_in_sen_path)

    # 统计高频词相关统计量, 并转换为(w1, w2) = [count(11), count(10), count(01)], 保存高频词相关统计量
    bag_sen_dict_path = BasePath + "/data/bag_sen_dict.txt"
    bag_sen_dict = load_json(bag_sen_dict_path)

    candidate_high_frequence_dict_path = BasePath + "/data/high_frequence_word_pair.txt"
    candidate_high_frequence_dict = load_json(candidate_high_frequence_dict_path)

    save_count_word_pair_path = BasePath + "/data/high_frequence_count_word_pair.txt"
    count_word_pair_dict = save_count_word_pair_data(bag_sen_dict, word_in_sen_dict,
                                                     candidate_high_frequence_dict,  save_count_word_pair_path)
    # 将数据保存到csv,便于图数据库的存储
    print("将数据保存到csv")
    save_count_word_pair_path = BasePath + "/data/high_frequence_count_word_pair.txt"
    count_word_pair_dict = load_json(save_count_word_pair_path)
    print("the len of candidate count high frequence_dict is : {}".format(len(count_word_pair_dict)))

    dictionary_path = BasePath + "/correlation_data/dict.pickle"
    dictionary = make_dictionary(dictionary_path)

#    csv_tuple_path = BasePath + '/csv/csv_tuple_pos_select.csv'
  #  csv_dict_path = BasePath + '/csv/csv_dict_pos_select.csv'
    save_data_to_csv(dictionary, count_word_pair_dict, csv_tuple_path, csv_dict_path)


if __name__ == "__main__":
    print(1)
    filepath = BasePath + "/seg_corpus/data_corpus.json"
    csv_tuple_path = BasePath + "/csv/csv_tuple_pos_select.csv"
    csv_dict_path = BasePath + "/csv/csv_dict_pos_select.csv"
    construct_correlation(filepath, csv_tuple_path, csv_dict_path)
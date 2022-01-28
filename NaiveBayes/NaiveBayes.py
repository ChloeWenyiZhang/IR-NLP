import os
import re
from decimal import *
import time
import numpy as np
import re
from nltk.corpus import stopwords
from nltk import word_tokenize,pos_tag
from nltk.stem import WordNetLemmatizer

import nltk
nltk.download('stopwords')

# 去除停用词
sr = stopwords.words('english')
def delete_stopwords(token_words):
    cleaned_words = [word for word in token_words if word not in sr]
    return cleaned_words


def getVocabulary(V):
# Python 代码首先尝试将数据集的词汇表构建为一个集合。
    vocabulary = set()
    cardinality_of_examples = 0
    for v in V:
        textfile_names = os.listdir("./train" + "/" + v)
        cardinality_of_examples += len(textfile_names)
        for textfile in textfile_names:
            try:
                with open("./train" + "/" + v + "/" + textfile) as f:
                    for line in f:
                        # 使用正则表达式获取每个字母单词来实现的。
                        # 暴力只保留英文单词，除此之外全部去掉
                        raw_word_list=re.findall(r"[A-Za-z]+", line)
                        for word in raw_word_list:
                            if word not in sr:
                                vocabulary.add(word)
                            
            except UnicodeDecodeError:
                with open("./train" + "/" + v + "/" + textfile, encoding="iso-8859-15") as f:# 区别两种encoding的方式
                    for line in f:
                        raw_word_list=re.findall(r"[A-Za-z]+", line)
                        for word in raw_word_list:# 使用正则表达式获取每个字母单词来实现的。
                            if word not in sr:
                                vocabulary.add(word)           
    return [vocabulary, cardinality_of_examples]        

# 然后我们通过找到 p (w | v)和 p (v)来学习数据集。
def initialise_pw_given_v(vocabulary, V):
    pw_given_v = {}
    for v in V:
        pw_given_v[v] = {}
        for word in vocabulary:
            pw_given_v[v][word] = 0
    return pw_given_v

# 对于每个 v，我们在字典中记录单词和它们的频率。
def initialise_count(vocabulary, V): # count[v][wordj] = number of word in v
    count = {}
    for v in V:
        count[v] = {}
        for word in vocabulary:
            count[v][word] = 0
    return count

# 然后，我们使用相应单词的计数、词汇集的长度和计算每个文档中单词位置的数量来分配 p (w | v)的每个成员。
# 我们不需要组合所有的文档，我们只需迭代遍历它们并记录单词位置的计数器即可
     
def learn_naive_bayes_text(cardinality_of_examples, vocabulary, V):
    pw_given_v = initialise_pw_given_v(vocabulary, V)
    Pv = {}
    count = initialise_count(vocabulary, V)   
    for v in V:
        textfile_names = os.listdir("./train" + "/" + v)
        cardinality_of_docs = len(textfile_names)
        Pv[v] = Decimal(cardinality_of_docs / cardinality_of_examples)
        number_of_distinct_word_positions = 0
        for textfile in textfile_names:
            try:
                with open("./train" + "/" + v + "/" + textfile) as f:       
                    for line in f:
                        regex = re.findall(r"[A-Za-z]+", line)
                        # regex_=delete_stopwords(regex)
                        number_of_distinct_word_positions += len(regex)
                        for word in regex:
                            if word not in vocabulary:
                                continue
                            else:
                                # print("Counting word " + word + " in 20news-bydate-train" + "/" + v + "/" + textfile + "...")    
                                count[v][word] += 1
            except UnicodeDecodeError:
                with open("./train" + "/" + v + "/" + textfile, encoding="iso-8859-15") as f:   
                    for line in f:
                        regex = re.findall(r"[A-Za-z]+", line)
                        # regex_=delete_stopwords(regex)
                        number_of_distinct_word_positions += len(regex)
                        for word in regex:
                            if word not in vocabulary:
                                continue
                            else:
                                # print("Counting word " + word + "in 20news-bydate-train" + "/" + v + "/" + textfile + "using encoding iso-8859-15...") 
                                count[v][word] += 1          
        for vocab_word in vocabulary: #vocab_word == wk
            pw_given_v[v][vocab_word] = Decimal((count[v][vocab_word] + 1) / (number_of_distinct_word_positions + len(vocabulary)))
            # print("Storing pw_given_v[{}][{}] as {}...".format(v, vocab_word, pw_given_v[v][vocab_word]))
    return Pv, pw_given_v, count
# 单个文档的分类是通过查找当前词典中存在的文档中的所有单词来完成的。
# 然后我们得到每个 v 的所有 p (w | v)和 p (v)的乘积，并将它们存储在一个字典中，其中概率乘积作为键存储，而 v 作为值存储。
# 然后，我们对所述结果字典的键使用函数 max () ，并使用该函数值给出分类器对给定文档进行分类的内容。

def classify_naives_bayes_text(path_to_document, pw_given_v, vocabulary, V, Pv):
    # print("Classifying textfile at " + path_to_document + "...")
    positions = []
    try:
        with open(path_to_document) as f:
            for line in f:
                for word in re.findall(r"[A-Za-z]+", line):
                    if word in vocabulary:
                        positions.append(word)
    except UnicodeDecodeError:
        with open(path_to_document, encoding="iso-8859-15") as f:
            for line in f:
                for word in re.findall(r"[A-Za-z]+", line):
                    if word in vocabulary:
                        positions.append(word)
    results = {}
    given_p_for_v = 0
    for v in V:
        given_p_for_v = Pv[v]
        for word in positions:
            given_p_for_v *= pw_given_v[v][word]
        results[given_p_for_v] = v
    arg_max = max(results.keys())
    return results[arg_max]


def main():
    V = os.listdir("./train")
    print(V)
    print("Python 代码首先尝试将数据集的词汇表构建为一个集合。\n")
    vocabulary, cardinality_of_examples = getVocabulary(V)
    print("学习训练集\n")
    Pv, pw_given_v, count = learn_naive_bayes_text(cardinality_of_examples, vocabulary, V)
    number_of_documents_in_test = 0 # 测试集中的文本数量
    documents_classified_correctly = 0 # 测试集中正确分类的文本数量
    number_of_documents_classified_as_v = {}# 测试集中的文本数量,以class进行分类
    number_of_documents_classified_as_v_classified_correctly = {}# 测试集中的正确分类文本数量,以class进行分类
    for v in V:
        number_of_documents_classified_as_v_classified_correctly[v] = 0
        number_of_documents_classified_as_v[v] = 0
    for v in V:
        #_ = os.listdir("20news-bydate-test/" + v)
        _ = os.listdir("./train/" + v)
        number_of_documents_in_test += len(_)
        number_of_documents_classified_as_v[v] += len(_)

    #v_given_by_classifer = ""
    #print("选取测试集进行测试\n")
    #for v in V:
    #    textfile_names = os.listdir("./train/" + v)
    #    # textfile_names = os.listdir("20news-bydate-train/" + v)
    #    for textfile in textfile_names:
    #        v_given_by_classifer = classify_naives_bayes_text("./train/" + v + "/" + textfile, pw_given_v, vocabulary, V, Pv)
    #        # v_given_by_classifer = classify_naives_bayes_text("20news-bydate-train/" + v + "/" + textfile, pw_given_v, vocabulary, V, Pv)

    #        if(v == v_given_by_classifer):
    #            # print("Document {} classified as {} and is correct\n".format(textfile, v_given_by_classifer))
    #            documents_classified_correctly += 1
    #            number_of_documents_classified_as_v_classified_correctly[v] += 1
    #for v in V:
    #    sum_of_v_documents = 0
    #    count_of_words_given_v = count[v]
    #    for word in vocabulary:
    #        sum_of_v_documents += count_of_words_given_v[word]
    #print("There are {} documents in the training set.\n".format(cardinality_of_examples))
    #print("There are {} documents in the testing set.\n".format(number_of_documents_in_test))
    #print("{} documents were classified correctly using the naive bayes text classifer.\n".format(documents_classified_correctly))
    #print("The accuracy rate is {}%.".format((documents_classified_correctly/number_of_documents_in_test) * 100))
    
    v_givenby_classifer = ""
    print("对test.txt进行分类\n")
    testfile_names = os.listdir("./test-all-in-one")
    for testfile in testfile_names:
        v_givenby_classifer = classify_naives_bayes_text("./test-all-in-one/" + testfile, pw_given_v, vocabulary, V, Pv)
        print(v_givenby_classifer)
        with open('./answer_10195501425.txt', 'a') as f:
            f.write("%s" % testfile)
            f.write(";")
            f.write("%s\n" % v_givenby_classifer)
            
    f.close()

if __name__ == "__main__":
    time1=time.time()
    main()
    time2=time.time()
    print(time2-time1)

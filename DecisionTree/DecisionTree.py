import jieba

from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

from sklearn import tree
from sklearn.metrics import precision_recall_curve  
from sklearn.metrics import classification_report  
from sklearn.cross_validation import train_test_split

import numpy as np
import scipy as sp

class stopword(object):
    def __init__(self, file):
        fd = open(file, encoding='utf-8')
        self.data = []
        for word in fd:
            self.data.append(word.strip())


class Data(object):
    def __init__(self, train_file, stop_file=None):
        # 去停用词
        def remove_stopwords(stop_list, data_list):
            result = []
            # 这里面的leave_word不能作为最终的特征，因为leave_word当中每个词只出现一次
            # 当多个非停用词出现在一句话中的时候，信息就会损失
            leave_word = set(data_list) - set(stop_list)
            for word in data_list:
                if word in leave_word:
                    result.append(word)
            return result

        self.data = []
        self.label = []

        file = open(train_file, "r", encoding='utf-8')
        if stop_file is not None:
            self.stopwords = set(stopword(stop_file).data)
        else:
            self.stopwords = set()

        i=0
        for line in file:
            split_line = line.split('\t')

            if len(split_line) != 2:
                print(line)
                continue

            label, content = split_line
            content = remove_stopwords(self.stopwords, list(jieba.cut(content)))
            content = ' '.join(content)
            self.data.append(content)
            self.label.append(int(label))
            print("Loading data %d:%s" % (i,label),end="\r" )
            i+=1
        print("Finish: Data Loading.")

def DecisionTreeClassifyTfidf(data_file, stop=None, extract_features=False):
    data = Data(data_file, stop)

    # 统计每个词的TF-IDF
    vectorizer = TfidfVectorizer(max_df=0.5,
                                 max_features=3000,
                                 min_df=2,
                                 use_idf=True,
                                 lowercase=False,
                                 decode_error='ignore',
                                 analyzer=str.split).fit(data.data)
    train_x, test_x, train_y, test_y = train_test_split(data.data, data.label, test_size=0.2)
    train_x = vectorizer.transform(train_x)
    test_x = vectorizer.transform(test_x)
    print("Finising: TF-TDF")

    
    DecisionTree = DecisionTreeClassifier(criterion="entropy",
                                          splitter="best",
                                          max_depth=None,
                                          min_samples_split=2,
                                          min_samples_leaf=2)
    print("Finishing: DecisionTree")

    # 训练加上测评
    # DecisionTree.fit(train_x, train_y)
    # print("使用词袋模型做为文本特征，并使用决策树算法的分类准确率为：", end=' ')
    # print(DecisionTree.score(test_x, test_y))
    # 训练加上测评
    print("Waiting for Training.........................")
    DecisionTree.fit(train_x, train_y)
    #with open("1.tree.dot", 'w') as f:
    #    f = tree.export_graphviz(DecisionTree, out_file=f)
    #print("\n使用TF-IDF模型做为文本特征，并使用决策树算法的分类F1值为：", end=' ')
    precision, recall, thresholds = precision_recall_curve(test_y, DecisionTree.predict(test_x))
    F1 = recall * precision * 2 / (recall + precision)
    print("\n")
    print("               normal\t\tspam\t\tavg/total")
    print("Recall     : ",recall)
    print("Precision  : ",precision)
    print("F1         : ",F1)

    if extract_features is True:
        # 特征提取，提取词汇
        words = vectorizer.get_feature_names()
        feature_importance = DecisionTree.feature_importances_
        word_importances_dict = dict(zip(words, feature_importance))

        number = 0
        for word, importance in sorted(word_importances_dict.items(), key=lambda val: val[1], reverse=True):
            print(word, importance)
            number += 1
            if number == 200:
                break




if __name__ == '__main__':
    DecisionTreeClassifyTfidf('../train/train.txt', '../stopword.txt', extract_features=False)
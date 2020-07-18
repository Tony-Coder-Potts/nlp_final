# from gensim.models import Word2Vec
#
# word2vec_model = Word2Vec.load('trainingmodel2.model')


# pairs = [
#     ('不能', '可以')
# ]
# for w1, w2 in pairs:
#     print('%r\t%r\t%.2f' % (w1, w2, word2vec_model.similarity(w1, w2)))
print('开始加载')

with open('word2vec/word2vecs', 'rt', encoding='utf-8') as f:
    for line in f:
        word2vec = eval(line)
stop_words = []
with open('word2vec/stop_words.txt', 'rt', encoding='utf-8') as f:
    for line in f:
        line = line[:len(line) - 1]
        stop_words.append(line)
stop_words = set(stop_words)

import jieba
import numpy as np
from numpy import dot
from numpy.linalg import norm

jieba.load_userdict('word2vec/user_dict.txt')
cosine = lambda a, b: dot(a, b) / (norm(a) * norm(b))

print('加载完成')

# while True:
#     s, t = input(), input()
def compare(s, t):
    s_words, t_words = jieba.lcut(s), jieba.lcut(t)
    s_words = [word for word in s_words if word not in stop_words]
    t_words = [word for word in t_words if word not in stop_words]
    print(s_words, t_words)
    s_vec, t_vec = np.zeros(280), np.zeros(280)
    for word in s_words:
        if word in word2vec:
            s_vec += np.array(word2vec[word])
    for word in t_words:
        if word in word2vec:
            t_vec += np.array(word2vec[word])
    # print(cosine(s_vec, t_vec))
    return cosine(s_vec, t_vec)


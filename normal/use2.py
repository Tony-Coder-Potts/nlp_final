# import time
# start =time.clock() # debug

import jieba
import jieba.analyse
import pinyin


# jieba.enable_paddle()
jieba.load_userdict('normal/dict_modified.txt')


from .variables import variables

# 标点符号等常量
PUNCTUATION_LIST = variables().PUNCTUATION_LIST
phrase_freq = variables().phrase_freq
cn_words_dict = variables().cn_words_dict


# 统计个单词的词频
# def construct_dict(file_path):
#     word_freq = {}
#     with open(file_path, "r", encoding='utf-8') as f:
#         for line in f:
#             info = line.split()
#             word = info[0]
#             frequency = info[1]
#             word_freq[word] = frequency
#     return word_freq
#
#
# FILE_PATH = "variables/token_freq_pos%40350k_jieba.txt"
# phrase_freq = construct_dict(FILE_PATH)
#
# with open('variables/freq_pos_jieba.txt', 'w') as f:
#     f.write(str(phrase_freq))
#     f.close()


# 载入编辑距离的单词列表
# cn_words_dict 用于编辑距离的，从里面选择字来菜如或者替换目标词
# def load_cn_words_dict(file_path):
#     cn_words_dict = ""
#     with open(file_path, "r", encoding='utf-8') as f:
#         for word in f:
#             cn_words_dict += word.strip()  # 去除首尾空格
#     return cn_words_dict
#
#
# cn_words_dict = load_cn_words_dict("cn_dict.txt")  # 导入单字
# with open('cn_words_dict.txt', 'w', encoding='utf-8') as f:
#     f.write(str(cn_words_dict))
#     f.close()

# 函数计算与中文短语的距离
# cn_words_dict 用于编辑距离的，从里面选择字来菜如或者替换目标词
def edits1(phrase, cn_words_dict):
    """`所有的编辑都是一个编辑远离'短语."""
    # phrase = phrase.decode("utf-8")
    splits = [(phrase[:i], phrase[i:]) for i in range(len(phrase) + 1)]  # 将单词前后分开
    deletes = [L + R[1:] for L, R in splits if R]  # 删除
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]  # 转换
    replaces = [L + c + R[1:] for L, R in splits if R for c in cn_words_dict]  # 替换
    inserts = [L + c + R for L, R in splits for c in cn_words_dict]  # 插入
    return set([phrase] + deletes + transposes + replaces + inserts)


# 编辑距离生成的词是否在我们前面得到的{词：词频}列表里，是就返回
def known(phrases):
    return set(phrase for phrase in phrases if phrase in phrase_freq)


# 得到错误短语的候选短语
# 我们根据候选词的拼音对其重要性进行排序
# 如果候选词的拼音与错误词完全匹配，则将候选词进行一级数组
# 如果候选词的第一个词的拼音与错误词的第一个词匹配，我们将其按二级数组
# 否则我们把候选短语放入第三个数组
def get_candidates(error_phrase):
    candidates_1st_order = []
    candidates_2nd_order = []
    candidates_3nd_order = []
    # pinyin.get，get使用一个简单的get()函数，则可以返回拼音的符号，format="strip"去掉音调， delimiter="/"拼音之间的分隔符
    error_pinyin = pinyin.get(error_phrase, format="strip", delimiter="/")  # 错误拼音
    error_pinyin = str(error_pinyin)  # 转换成字符串格式，为后面选择拼音打下基础
    # cn_words_dict = load_cn_words_dict("cn_dict.txt")  # 导入单字


    candidate_phrases = edits1(error_phrase, cn_words_dict) # 编辑距离生成的候选词组


    for candidate_phrase in candidate_phrases:  # 遍历编辑距离生成的候选词组
        candidate_pinyin = pinyin.get(candidate_phrase, format="strip", delimiter="/")  # 候选词拼音
        candidate_pinyin = str(candidate_pinyin)

        if candidate_pinyin == error_pinyin:  # 如果错误词拼音等于候选词拼音,则加入第一选择
            candidates_1st_order.append(candidate_phrase)
        elif candidate_pinyin.split("/")[0] == error_pinyin.split("/")[0]:
            candidates_2nd_order.append(candidate_phrase)
        else:
            candidates_3nd_order.append(candidate_phrase)  # 否则加入第三个
    return candidates_1st_order, candidates_2nd_order, candidates_3nd_order,error_phrase


# 自动更正单词
def auto_correct(error_phrase):
    c1_order, c2_order, c3_order,error_phrase = get_candidates(error_phrase)  # 得到的候选正确词
    # print(c1_order, c2_order, c3_order)
    value1, value2, value3 = [], [], []
    if c1_order:
        for i1 in c1_order:
            if i1 in phrase_freq:
                value1.append(i1)
        return max(value1, key=phrase_freq.get, default=error_phrase)
        # 一级候选存在，如果候选词拼音与错误单词完全正确，则返回候选词词频最大的单词
    elif c2_order:
        for i2 in c2_order:
            if i2 in phrase_freq:
                value2.append(i2)
        return max(value2, key=phrase_freq.get)
        # 一级候选不存在，二级候选存在，返回二级候选词频最大的词
    else:
        for i3 in c3_order:
            if i3 in phrase_freq:
                value3.append(i3)
        return max(value3, key=phrase_freq.get)
        # 否则，返回三级候选词频最大的


# 对于任何一个给定的句子，用结巴做分词，
# 割完成后，检查word_freq dict中是否存在剩余的短语，如果不存在，则它是拼写错误的短语
# 使用auto_correct函数纠正拼写错误的短语
# 输出正确的句子

def auto_correct_sentence(error_sentence):
    jieba_cut = jieba.cut(error_sentence, cut_all=False)
    seg_list = "\t".join(jieba_cut).split("\t")  # 分词
    correct_sentence = ""
    for phrase in seg_list:
        correct_phrase = phrase  # 当前词语
        if phrase not in PUNCTUATION_LIST:  # 去除标点符号
            if phrase not in phrase_freq.keys():
                correct_phrase = auto_correct(phrase)  # 对当前学习进行修正
                if True:
                    print(phrase, correct_phrase)
                    pass
        correct_sentence += correct_phrase
    return correct_sentence


def import_synonyms():
    """
    用于格式化同义词库内容至单独文件，导入原始文件仅需一次，若不发生变动则仅需再次导入处理后的数据即可
    :return: None
    如果文件不存在会报FileNotFoundError
    """
    synonyms_tmp = {}
    try:
        with open('variables/同义词库.txt', 'rt', encoding='utf-8') as input_file:
            count = 0
            for line in input_file:
                # 读取到的换行是\n，split如果不提供参数默认sep=' '，所以split(' ')和split(sep=' ')这样的写法都是不必要的
                words = line.replace('\n', '').split()
                # 切片后第一项为标记代码，直接忽略
                for i in range(1, len(words)):
                    # 存储的方式是，保存每一个词所在的行数，这样访问的速度最快
                    # 缺点是，如果一个词所在的行数很多那么遍历的时候速度会比较慢且空间占用比较大
                    # 但是这个应当是目前最好的解决方案了
                    if not words[i] in synonyms_tmp:
                        synonyms_tmp[words[i]] = [count]
                    else:
                        synonyms_tmp[words[i]].append(count)
                count += 1
    except:
        raise FileNotFoundError
    else:
        variables.synonyms = synonyms_tmp
    # 这个是我写的保存至文件版本的，和后面的读取文件版配套
    # 之所以这么做是因为，如果每次都去刷同义词库文件的话，对于内存的开销会很大，而且Python的遍历速度让人无语凝噎......
    with open('synonyms.txt', 'w', encoding='utf-8') as f:
        f.write(str(synonyms_tmp))
        f.close()


def load_synonyms():
    """
    加载格式化后的同义词库，即一全局变量
    :return: 格式化后的同义词库字典
    """
    # 这个是我原来写的保存至文件版的，现在改用其他文件的变量了
    # with open('synonyms.txt', 'r', encoding='utf-8') as f:
    #     synonyms = eval(f.read())
    # return synonyms
    return variables().synonyms


def cut(s):
    synonyms = load_synonyms()
    for i in range(len(s), 1, -1):
        for j in range(0, len(s) - i + 1):
            if s[j : j + i] in synonyms:
                return s[j : j + i]
    return None


def _compare(s_words, t_words, is_one_pair=False, num=0):
    """
    这是实现比较功能的函数，将两个句子切片后的列表分别传入
    :param s_words: 先被切片的列表
    :param t_words: 被s_words比较的列表
    :param is_one_pair: 判定是对一对词组进行比较还是对关键词进行交叉对比
    :param num: 该词组在句子切片中的位置
   :return: Bool值，True为相同
    """

    print(s_words, t_words)

    synonyms = load_synonyms()
    if is_one_pair == False:
        result = True
        for s_word in s_words:
            # 引入is_matched，若比对到相同词汇则相同，若无相同词汇则进入同义词库进行比对，比对成功则相同
            is_matched = False
            for t_word in t_words:
                if s_word == t_word:
                    is_matched = True
                    t_words.remove(t_word)
                    break
                elif s_word.find(t_word) != -1 or t_word.find(s_word) != -1:
                    is_matched = True
                    t_words.remove(t_word)
                    break
                elif s_word in synonyms and t_word in synonyms:
                    for x in synonyms[s_word]:
                        if x in synonyms[t_word]:
                            is_matched = True
                            t_words.remove(t_word)
                            break
                # 若同义词库内不存在该词汇，则输出并报错，便于扩展词库内容
                elif s_word not in synonyms or t_word not in synonyms:
                    print(
                        "Warning: One or two of these words below may not be in the Thesaurus: \n",
                        s_word,
                        '\n',
                        t_word
                    )
                    # raise Exception("Not Found in the Thesaurus.")
                    s_cut, t_cut = cut(s_word), cut(t_word)
                    if s_cut != None and t_cut != None:
                        for x in synonyms[s_cut]:
                            if x in synonyms[t_cut]:
                                is_matched = True
                                t_words.remove(t_word)
                                break
            if not is_matched:
                result = False
        return result
    else:
        # 取出两个不同的词组
        s_word = s_words[num]
        t_word = t_words[num]
        # 若均存在，则进行比较
        if s_word.find(t_word) != -1 or t_word.find(s_word) != -1:
            return True
        elif s_word in synonyms and t_word in synonyms:
            for x in synonyms[s_word]:
                if x in synonyms[t_word]:
                    return True
                else:
                    return False
        else:
            # 不存在的话报错
            print(
                "Warning: One or two of these words below may not be in the Thesaurus: \n",
                s_word,
                '\n',
                t_word
            )
            # raise Exception("Not Found in the Thesaurus.")
            s_cut, t_cut = cut(s_word), cut(t_word)
            if s_cut != None and t_cut != None:
                for x in synonyms[s_cut]:
                    if x in synonyms[t_cut]:
                        is_matched = True
                        t_words.remove(t_word)
                        break


# def main():
def compare(x_error, y_error):
    # x_error = '我已经关闭另一个号的花呗了怎么在这个号开通'
    # y_error = '蚂蚁花呗关闭了。怎么开通另一个'

    # while True:
        # x_error, y_error = input(), input()
    print('分词结果：')
    print(jieba.lcut(x_error))
    print(jieba.lcut(y_error))
    s, t = auto_correct_sentence(x_error), auto_correct_sentence(y_error)
    # s, t = x_error, y_error
    print('纠错结果：\n' + s)
    print(t)
    s_words = jieba.lcut(s)
    t_words = jieba.lcut(t)
    # 判定两个句子差异性，0为相近，1为不相近
    # 相近的条件为，两句话仅有一处不相同
    is_similar_sentence = 1
    not_the_same_part = -1
    if len(s_words) == len(t_words):
        temp = 0
        for i in range(len(s_words)):
            if s_words[i] != t_words[i]:
                temp += 1
                not_the_same_part = i
        if temp <= 1:
            is_similar_sentence = 0
    if is_similar_sentence == 0:
        # print(compare(s_words, t_words, True, not_the_same_part))
        return _compare(s_words, t_words, True, not_the_same_part)
    else:
        s_words, t_words = jieba.analyse.extract_tags(s), jieba.analyse.extract_tags(t)
        # print(compare(s_words, t_words))
        return _compare(s_words, t_words)


    # break # debug


# if __name__ == "__main__":
    # main()


# end = time.clock() # debug
# print('Running time: %s Seconds'%(end-start))
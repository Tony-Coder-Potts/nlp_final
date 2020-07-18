from keras.models import Model, load_model
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import pickle
import jieba

MAX_SEQUENCE_LENGTH = 25

jieba.load_userdict('lstm_method/user_dict.txt')

stop_words = []
with open('lstm_method/stopwords.txt', 'rt', encoding='utf-8') as f:
    for line in f:
        line = line[:len(line) - 1]
        stop_words.append(line)
stop_words = set(stop_words)
stop_words.update(' ')

tokenizer_path = 'lstm_method/tokenizer.pkl'
    # tokenizer = pickle.load(tokenizer_path)
with open(tokenizer_path, 'rb') as f:  
    tokenizer = pickle.loads(f.read())

model_path = 'lstm_method/demo_model.h5'
model = load_model(model_path)

def compare(test_data_1, test_data_2):
    # test_sequences_1 = tokenizer.texts_to_sequences(sentences1_test)
    # test_sequences_2 = tokenizer.texts_to_sequences(sentences2_test)
    # test_data_1 = pad_sequences(test_sequences_1, maxlen=MAX_SEQUENCE_LENGTH)
    # test_data_2 = pad_sequences(test_sequences_2, maxlen=MAX_SEQUENCE_LENGTH)

    test_data_1 = [[word for word in jieba.lcut(test_data_1) if word not in stop_words]]
    test_data_2 = [[word for word in jieba.lcut(test_data_2) if word not in stop_words]]
    
    test_data_1 = tokenizer.texts_to_sequences(test_data_1)
    test_data_2 = tokenizer.texts_to_sequences(test_data_2)
    test_data_1 = pad_sequences(test_data_1, maxlen=MAX_SEQUENCE_LENGTH)
    test_data_2 = pad_sequences(test_data_2, maxlen=MAX_SEQUENCE_LENGTH)
    
    predicts = model.predict([test_data_1, test_data_2], batch_size=10, verbose=1)
    return float(predicts)

# while True:
#     print(test_model(input(), input()))
import librosa
import pandas as pd
import numpy as np

from utils import save_url, label, url, start_time, end_time, extract_mfcc, test_url
from pydub import AudioSegment
from datetime import datetime
from hmmlearn import hmm


def split_wave(url_name, start, end):
    split_url = url_name.split('.')
    try:
        start_dt = datetime.strptime(start, '%H:%M:%S.%f')
    except:
        start_dt = datetime.strptime(start, '%H:%M:%S')

    try:
        end_dt = datetime.strptime(end, '%H:%M:%S.%f')
    except:
        end_dt = datetime.strptime(end, '%H:%M:%S')
    audio = AudioSegment.from_wav(split_url[0] + '.wav')
    extract = audio[convert_to_mili(start_dt):convert_to_mili(end_dt)]
    extract.export("test.wav", format="wav")


def convert_to_mili(time: datetime):
    return (time.hour * 3600 + time.minute * 60 + time.second + time.microsecond * 10 ** -6) * 1000


class Model:
    def __init__(self):
        self.data = pd.read_csv(save_url)
        msk = np.random.rand(len(self.data)) < 0.8
        self.train = self.data[msk]
        self.test = self.data[~msk]
        self.train_data = {}
        self.test_data = {}
        self.hmm_models = {}
        self.states_num = 5
        self.mix_num = 3
        tmp_p = 1.0 / (self.states_num - 2)
        self.tran_max = np.array([[tmp_p, tmp_p, tmp_p, 0, 0], [0, tmp_p, tmp_p, tmp_p, 0], [0, 0, tmp_p, tmp_p, tmp_p],
                                  [0, 0, 0, 0.5, 0.5], [0, 0, 0, 0, 1]], dtype=float)
        self.start_probPrior = np.array([0.5, 0.5, 0, 0, 0], dtype=float)
        self.score_cnt = 0
        self.err = 0
        self.score_list = {}

    def create_train_data(self):
        for index, record in self.train.iterrows():
            label_name = record[label]
            start_time_extract = record[start_time]
            end_time_extract = record[end_time]
            url_extract = record[url]
            split_wave(url_extract, start_time_extract, end_time_extract)
            feature = extract_mfcc(test_url)
            if feature is None:
                continue
            if label_name not in self.train_data.keys():
                print(label_name + f'train {index}')
                self.train_data[label_name] = []
                self.train_data[label_name].append(feature)
            else:
                print(label_name + f'train {index}')
                exist_feature = self.train_data[label_name]
                exist_feature.append(feature)
                self.train_data[label_name] = exist_feature

    def create_test_data(self):
        for index, record in self.test.iterrows():
            label_name = record[label]
            start_time_extract = record[start_time]
            end_time_extract = record[end_time]
            url_extract = record[url]
            split_wave(url_extract, start_time_extract, end_time_extract)
            feature = extract_mfcc(test_url)
            if feature is None:
                continue
            if label_name not in self.test_data.keys():
                print(label_name + f'test {index}')
                self.test_data[label_name] = []
                self.test_data[label_name].append(feature)
            else:
                print(label_name + f'test {index}')
                exist_feature = self.test_data[label_name]
                exist_feature.append(feature)
                self.test_data[label_name] = exist_feature

    def train_model(self):
        print('-----------------------------------------------Train------------------------------------------------')
        for label in self.train_data.keys():
            trainData = self.train_data[label]
            # trainData = np.vstack(trainData)
            # param = set(trainData.ravel())
            model = hmm.GMMHMM(n_components=self.states_num)
            # length = np.zeros([len(trainData), ], dtype=int)
            # for m in range(len(trainData)):
            #     length[m] = trainData[m].shape[0]
            model.fit(trainData)
            self.hmm_models[label] = model

    def score(self):
        print('-----------------------------------------------Predict------------------------------------------------')
        for label in self.test_data.keys():
            feature = self.test_data[label]
            # for feat in feature:
            #     # feat = np.vstack(feat)
            for model_label in self.hmm_models.keys():
                model = self.hmm_models[model_label]
                if len(feature) > 4:
                    score = model.score(feature[0:4])
                else:
                    score = model.score(feature[0:-1])
                self.score_list[model_label] = score
            predict = max(self.score_list, key=self.score_list.get)
            print("Test on true label ", label, ": predict result label is ", predict)
            if predict == label:
                self.score_cnt += 1
            else:
                self.err += 1


if __name__ == "__main__":
    model = Model()
    model.create_train_data()
    model.create_test_data()
    model.train_model()
    model.score()
    print(f'{model.score_cnt} vs {model.err}')

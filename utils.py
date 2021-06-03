import os
import librosa

main_url = "data"
save_url = "data/preprocessor/data.csv"
label = "labels"
url = "url"
start_time = "start_time"
end_time = "end_time"
test_url = "test.wav"
max_features = 142


def get_list_dir():
    list_dir = []
    for dirname, dirnames, filenames in os.walk(main_url):
        for dir_file in dirnames:
            list_dir.append(os.path.join(dirname, dir_file))
    return list_dir


def extract_mfcc(url_name):
    wave, sr = librosa.load(url_name)
    mfcc = librosa.feature.mfcc(wave, n_mfcc=1)
    if len(mfcc[0]) < 142:
        return None
    return mfcc[0][0:max_features - 1]

import csv

import pysrt
import os
from utils import save_url, get_list_dir


class Preprocessor:
    def __init__(self, list_url: str):
        self.list_labels = []
        self.list_url = list_url
        self.tail_str = ".srt"
        self.tail_wav = ".wav"
        self.data = [['url', 'start_time', 'end_time', 'labels']]

    def get_labels(self, dir_name: str):
        dir_name_split = dir_name.split("_")
        if len(dir_name_split) == 2:
            self.list_labels.append(dir_name_split[1])
            return dir_name_split[1]

    def check_is_srt_file(self, name_file: str):
        return name_file.__contains__(self.tail_str)

    def check_is_wav_file(self, name_file: str):
        return name_file.__contains__(self.tail_wav)

    def get_list_detail_url(self, parent_url):
        children_url = []
        for dirname, _, filenames in os.walk(parent_url):
            for file in filenames:
                if self.check_is_srt_file(file):
                    children_url.append(os.path.join(dirname, file))
        return children_url

    def preprocessor(self):
        for url in self.list_url:
            label = self.get_labels(url)
            children_list_url = self.get_list_detail_url(url)
            for children_url in children_list_url:
                subs = pysrt.open(children_url)
                i = 0
                while True:
                    times = [children_url]
                    start_time = subs[i].start.to_time()
                    times.append(start_time)
                    if i + 10 >= len(subs):
                        end_time = subs[-1].end.to_time()
                        times.append(end_time)
                    else:
                        end_time = subs[i + 10].end.to_time()
                        times.append(end_time)
                    times.append(label)
                    self.data.append(times)
                    i = i + 10
                    if i >= len(subs):
                        break
        self.save_to_csv(save_url)

    def save_to_csv(self, url):
        file = open(url, 'w+', newline='')
        with file:
            write = csv.writer(file)
            write.writerows(self.data)


if __name__ == '__main__':
    list_dir = get_list_dir()
    preprocessor = Preprocessor(list_dir)
    preprocessor.preprocessor()

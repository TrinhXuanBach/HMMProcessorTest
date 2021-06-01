import os

main_url = "data"
save_url = "data/preprocessor/data.csv"


def get_list_dir():
    list_dir = []
    for dirname, dirnames, filenames in os.walk(main_url):
        for dir_file in dirnames:
            list_dir.append(os.path.join(dirname, dir_file))
    return list_dir

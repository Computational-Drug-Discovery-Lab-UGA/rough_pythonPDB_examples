#!/usr/bin/python
import urllib.request
import re
import time
import os

class IDS:
    def __init__(self, directory_path):
        self.base_url = "https://files.rcsb.org/pub/pdb/data/structures/all/pdb/"
        self.id = []
        self.num_ids = 0
        self.matcher = re.compile(r"(b)(\')(\<)(a)(\s)(href)(\=)").match
        self.url = "https://files.rcsb.org/view/"
        self.directory_path = directory_path
        self.file = open(self.directory_path + "LIST_OF_ALL_IDS.txt", "w")
        self.page = ""

    def set_length(self):
        start_time = time.time()
        for subdir in urllib.request.urlopen(self.base_url):
            if str(subdir)[11:13] == "pd":
                self.num_ids += 1
        print("--- %s seconds ---" % (time.time() - start_time))

    def set_ids(self):
        start_time = time.time()
        self.id = [None] * self.num_ids
        i = 0
        for subdir in urllib.request.urlopen(self.base_url):
            if str(subdir)[11:13] == "pd":
                self.id[i] = str(subdir)[11:18]
                i += 1
        print("--- %s seconds ---" % (time.time() - start_time))

    def write_file(self):
        start_time = time.time()
        for e in self.id:
            self.page += (e + "\n")
        self.file.write(self.page)
        self.file.close()
        print("--- %s seconds ---" % (time.time() - start_time))


def give_me_list():
    while True:
        directory_path = input("Where do you want the LIST_OF_ALL_IDS.txt to go? \n(enter absolute directory path): ")
        if not os.path.exists(directory_path):
            print("\n------------------------------------------\n"
                  "ERROR: directory path does not exist...try again\n"
                  "\n------------------------------------------\n")
            continue
        break
    full_list = IDS(directory_path)
    full_list.set_length()
    full_list.set_ids()
    full_list.write_file()
    return directory_path + "LIST_OF_ALL_IDS.txt"


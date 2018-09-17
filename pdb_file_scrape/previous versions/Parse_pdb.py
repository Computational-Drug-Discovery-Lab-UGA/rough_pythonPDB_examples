#!/usr/bin/python

""""for database work python interpreter must be 3.4.4
https://www.python.org/downloads/release/python-344/
http://www.mysqltutorial.org/getting-started-mysql-python-connector/ DB
from PyPI (pip install mysql-connector) or from source code (python setup.py install)
https://github.com/sanpingz/mysql-connector"""

#IF PARTICLE NUMBER SKIPS A BEAT THEN A TER IS LOCATED THERE#

import re
import os
import os.path
import sys
import shutil
import urllib.request
import time
from create_db import create_database
import mysql.connector
#only needed if you have to use another server other than MySQLcddl
from create_db import protein_db
from create_db import need_to_specify_server

"""regualar expressions for parsing, and fixing exceptions
may not need this any longer
regex_one = re.compile(r"(1|0)(\.)\d{5}(\.)\d{2}")
regex_neg = re.compile(r"(\.)(\d{3})((\-)|(\d))(\d{2,3})(\.)(\d{2,3})")
regex_col34 = re.compile(r"((\w){4,6})((\s)+)((\d)+)((\s)+)(((\S){5,8})|((\S){2})(\S|\'))((\S){5})")
regex_col34_better = re.compile(r"(((\w){4,6})((\s)+)((\d)+)((\s)+)(((\S)+)|((\S){2})(\S|\'))((\S){5}))")
regex_col34_better3 = re.compile(r"(((\w){4,6})((\s)+)((\d)+)((\s)+)(\S){4,})")
regex_chain = re.compile(r"((\w){4,6})((\s)+)((\d)+)((\s)+)((\S)+)((\s)+)((\S)+)((\s)+)(\w)((\d){4,8})")
regex_chain_num = re.compile(r"((\w){4,6})((\s)+)((\d)+)((\s)+)((\S)+)((\s)+)((\S)+)((\s)+)((\S)+)((\d){4,5})((\s)+)")
"""
"""def clean_line(line):
    fix_line = str(line)
    add_index_HET = 0
    if "HETATM" in fix_line:
        add_index_HET = 1
    if (re.search(regex_col34, fix_line) != None)or \
            (re.search(regex_col34_better, fix_line) != None) or\
                        (re.search(regex_col34_better3, fix_line) != None):
        fix_line = fix_line[:16+add_index_HET] + " " + fix_line[16+add_index_HET:]
        add_index_HET = 2
    if (re.search(regex_chain, fix_line) != None) or \
            (re.search(regex_chain_num, fix_line) != None):
        fix_line = fix_line[:22 + add_index_HET] + " " + fix_line[22 + add_index_HET:]
    if (re.search(regex_neg, fix_line) != None):
        fix_string = re.search(regex_neg, fix_line).group(0)
        index_needed = fix_line.index(fix_string)
        fix_line = fix_line[:(index_needed + 4)] + " " + fix_line[(index_needed + 4):]
    if (re.search(regex_one, fix_line) != None):
        fix_string = re.search(regex_one, fix_line).group(0)
        index_needed = fix_line.index(fix_string)
        fix_line = fix_line[:(index_needed + 4)] + " " + fix_line[(index_needed + 4):]
    return fix_line"""

regex_ext = re.compile(r"\S{4}(\.)(pdb)")

def add_all(num, dir, id_file):
    # this is the command used in
    # write_to_web where you
    # input the pdb_id,
    # ******WARNING******
    #   WILL DOWNLOAD ALL
    #   150,000 pdb files
    # to use, you need list of all pdbs
    # "D:/Lab work/LIST_OF_ALL_IDS.txt"
    try:
        with open(str(id_file)) as txt:
            i = 0
            for line in txt:
                if i == num:
                    not_in_dir = False
                    file_name = str(line[3:7])
                    if not ((file_name + ".pdb").lower() in dir) or ((file_name + ".pdb").upper() in dir):
                        not_in_dir = True
                    if not_in_dir:
                        return file_name, i + 1
                    else:
                        return "", i + 1
                i += 1
    except(FileNotFoundError):
        print("\n----------------\n"
              "ERROR: THIS FILE DOES NOT EXIST\n"
              "\n--------SYSTEM EXITING--------\n")
        sys.exit(2)
def protein_info(file):
    multiple_models = False
    num_atoms = 0
    num_model = 0
    list_length = 0
    i = 0
    func_length = 0
    with open(file) as f:
        for l in f:
            list_length += 1
    p_list = [None] * list_length
    with open(file) as f:
        for l in f:
            if "ATOM" == l[:4] or "HETATM" == l[:6]:
                p_list[i] = [" "] * 15
                p_list[i][0] = l[0:6].strip()
                p_list[i][1] = l[6:11].strip()
                #index 11 not included
                p_list[i][2] = l[12:16].strip()
                p_list[i][3] = l[16]
                p_list[i][4] = l[17:21].strip()
                p_list[i][5] = l[21].strip()
                p_list[i][6] = l[22:26].strip()
                p_list[i][7] = l[26]
                p_list[i][8] = l[30:38].strip()
                p_list[i][9] = l[38:46].strip()
                p_list[i][10] = l[46:54].strip()
                p_list[i][11] = l[54:60].strip()
                p_list[i][12] = l[60:66].strip()
                p_list[i][13] = l[76:78].strip()
                p_list[i][14] = l[78:80]
                i += 1
                func_length += 1
                num_atoms += 1
            if "MODEL" == l[:5]:
                num_model += 1
                p_list[i] = [" "]*2
                p_list[i][0] = "MODEL"
                p_list[i][1] = str(num_model)
                multiple_models = True
                i += 1
                func_length += 1
    return p_list, func_length, multiple_models, num_model, (num_atoms + 1)

def create_functional_list(list, l, multiple_models):
    x = 0
    if multiple_models:
        functional_list = [None] * l
    else:
        functional_list = [None] * (l + 1)
        functional_list[0] = ['MODEL', 1.0]
        x = 1

    for e in list:
        if (e != None) and (len(e) != 0):
            e_temp = [None] * len(e)
            o = 0
            for ee in e:
                try:
                    e_temp[o] = float(ee)
                except ValueError:
                    e_temp[o] = ee
                o += 1
            functional_list[x] = e_temp
            x += 1
    return functional_list

def breakup_models(list, num_model):
    index_models = [None] * num_model
    num_atoms = 0
    models = [None] * num_model
    i = 0
    ii = 0
    for e in list:
        if e[0] == "MODEL":
            index_models[i] = ii
            i += 1
        ii += 1
    i = 0
    for e in models:
        if i < (num_model - 1):
            models[i] = list[index_models[i]:index_models[i + 1]]
        else:
            models[i] = list[index_models[i]:]
        i += 1

    return models

def directory_list(dir):
    num = 0
    for dirs, subdirs, file_list in os.walk(dir):
        for file in file_list:
            if re.search(regex_ext, file):
                num += 1
        dir_list = [None] * num
    return dir_list
def create_pdb_bank():
    while True:
        parent_dir = input("Please input the ABSOLUTE parent directory path "
                           "where the new directory will be located\n\n")
        ext = input("Enter new folder name: \n")
        new_dir = parent_dir + "/" + ext
        if os.path.exists(new_dir):
            print("ERROR: directory path already exists...try again.\n")
            continue
        break
    os.mkdir(new_dir)
    return new_dir
def extract_pdb():
    dir_to = create_pdb_bank()
    dir_from = input("\nPlease input the ABSOLUTE path where you would like to search: \n")
    if not os.path.exists(dir_from) or not os.path.exists(dir_to):
        print("ERROR: directory path does not exist...system exiting")
        sys.exit(12)

    for dirs, subdirs, filelist in os.walk(dir_from):
        for file in filelist:
            if ".pdb" in file:
                file_path = str(dirs) + "/" + str(file)
                try:
                    shutil.copy2(file_path, dir_to)
                except shutil.SameFileError:
                    continue
    return dir_to

def write_from_web():

    page = ""
    base_url = "https://files.rcsb.org/view/"
    add_from_web = input("\n--------------------------------------\n"
                         "Would you like to download .pdb files from the web? (y) or (n)\n"
                         "________________________________________\n")
    if add_from_web == "y":
        while True:
            directory_path = input("\n--------------------------------\n"
                                   "Where do you want these files saved?\n"
                                   "Enter the directory path (or create to make a new directory):\n"
                                   "__________________________________\n")
            if directory_path == "create":
                directory_path = extract_pdb()
            if not os.path.exists(directory_path):
                print("\n------------------------------------------\n"
                      "ERROR: directory path does not exist...try again\n"
                      "\n------------------------------------------\n")
                continue
            break
    else:
        return
    num_input = 0
    all = False
    num_all = 0
    id_file = ""
    while True:
        if add_from_web == "y":
            while True:
                if not all:
                    pdb_id = input("\n------------------------\n"
                                   "Enter pdb id (or exit, or all): ")
                all = [True if pdb_id == "all" else False]
                if all:
                    if num_all == 0:
                        id_file = os.path.realpath(__file__)[:-13] + "/" + "LIST_OF_ALL_IDS.txt"
                        num_all += 1
                    pdb_id, num_input = add_all(num_input, os.listdir(directory_path), id_file)

                    if pdb_id == "":
                        continue
                print("________________________\n")
                if pdb_id == "exit":
                    return
                file_name = str(pdb_id) + ".pdb"
                try:
                    urllib.request.urlopen(base_url + file_name)
                except(urllib.error.HTTPError or TimeoutError or urllib.error.URLError): #added 1/4/17
                    print("\n-----------------------\n"
                          "That pdb id does not exist, \n "
                          "or that protein does not have a pdb file\n"
                          "...try again or exit\n"
                          "\n-----------------------\n")
                    if(all):
                        num_input = 0
                    continue
                except (TypeError):#this is to account for the end of list
                    return
                if (file_name.lower() in os.listdir(directory_path)) or (
                            file_name.upper() in os.listdir(directory_path)):
                    print("\n" + "-----------------\n" +
                          file_name + " is already in " + directory_path +
                          "\n...try again\n"
                          "-----------------\n")
                    continue
                break
            target_url = base_url + file_name
            page = ""
            try:
                with urllib.request.urlopen(target_url) as f:
                    for l in f:
                        l = str(l)
                        l = l[2:]
                        l = l[:-3]
                        page += l + "\n"
                file = open(directory_path + "/" + file_name, "w")
                file.write(page)
                file.close()
                print(file_name + " downloaded>>>>")
            except(urllib.error.HTTPError or TimeoutError or urllib.error.URLError):
                num_input = 0
            except (TypeError): #this is to account for the end of list
                return

class Protein_Structure:  # added
    def __init__(self, fil, name):
        self.file_name = name
        self.dir_path = fil
        self.list_length = 0
        self.particle_list = []
        self.num_atoms = 0

    def get_file(self):
        return self.file_name

    #might add more functionality

def main():
    write_from_web()
    database_password = ""
    database_action_verification = input("\n----------------------------\n"
                                         "Are you going to deposit pdbs in a database? (y) or (n)\n"
                                         "_______________________________\n")
    if database_action_verification == "y":
        database_password =  input("\n----------------------------\n"
                                         "What is the root database server password that is at localHost?\n"
                                         "_______________________________\n")
        db = mysql.connector.connect(user="root", password=database_password, host="localhost", database="proteins")
    while True:
        directory_path = input("\n----------------------------\n"
                               "Please enter the ABSOLUTE directory path where the .pdb files "
                               "are located\n"
                               "OR enter create to search computer for files\n"
                               "IF FILES ARE SCATTERED or EXACT LOCATION IS NOT KNOWN"
                               "-> use create command:\n"
                               "_______________________________\n")
        if directory_path == "create":
            directory_path = extract_pdb()
        if not os.path.exists(directory_path):
            print("\n---------------------------------\n"
                  "ERROR: directory path does not exist...try again\n"
                  "\n---------------------------------\n")
            continue
        break
    f = 0
    reset_directory = True
    start_time = time.time()
    while reset_directory:
        for file in os.listdir(directory_path):
            start_file_time = time.time()
            if re.search(regex_ext, file) == None:
                directory_path = input(
                    "\n----------------------------------\n"
                    "This directory path contains no pdb files.\n"
                    "Enter the ABSOLUTE location of the pdb files:\n"
                    "-----------------------------------\n")
                reset_directory = True
                break
            if re.search(regex_ext, file) != None:
                reset_directory = False
                current_file_name = file
                current_abs_path = directory_path + "/" + str(file)
                current_protein = Protein_Structure(current_abs_path, current_file_name)

                temp_list, current_protein.list_length, multiple_models, num_model, current_protein.num_atoms  = protein_info(current_abs_path)
                current_protein.particle_list = create_functional_list(temp_list,
                                                                       current_protein.list_length, multiple_models)

                if multiple_models:
                    current_protein.particle_list = breakup_models(current_protein.particle_list, num_model)
                    current_protein.num_atoms = len(current_protein.particle_list[0]) - 1
                if database_action_verification == "y":
                    create_database(db, current_protein, multiple_models)
                print("---file " + str(f+1) + " of " + str(len(os.listdir(directory_path))) + "---\n")
                print(current_protein.file_name + " was added to the database in %s seconds " % (time.time() - start_file_time))
                print("_________________________\n")
                f += 1
        db.close()
    print("--- %s seconds ---" % (time.time() - start_time))


main()




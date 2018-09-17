#!/usr/bin/python
""""
This program needs a mysql database server running on the machine.
This program creates an organized database called "proteins" on the
server that is on the development engine that has the coordinate
files for all pdbs the user specifies. A small protion of this 
program is oop, but the over use of oop in this type of program 
will only slow it down. 

TER IS SKIPPED THIS WILL MAKE IT LOOK LIKE AN ATOM IS MISSING AS THEY
HAVE NUMBERS
"""
import re
import os
import os.path
import sys
import shutil
import urllib.request
import time
from Create_db import create_database
import pymysql
from warnings import filterwarnings
"""These are all of the necessary packages for this program to work."""

#this is just a regex that confirms a file is .pdb
regex_ext = re.compile(r"\S{4}(\.)(pdb)")

"""This method is used to extract the raw information from the coordinate file
section in a pdb file. This is a list of strings. 
"""
def protein_info(file):
    multiple_models = False
    num_atoms = 0
    num_model = 0
    list_length = 0
    i = 0
    func_length = 0#this is the length not including TER and ANYSOU
    with open(file) as f:
        for l in f:
            list_length += 1
    p_list = [None] * list_length
    with open(file) as f:
        for l in f:#this separates the lines of the coordinate files
            if "ATOM" == l[:4] or "HETATM" == l[:6]:
                p_list[i] = [" "] * 15
                p_list[i][0] = l[0:6].strip()
                p_list[i][1] = l[6:11].strip()
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
            if "MODEL" == l[:5]:#ex: ["MODEL" , 1]
                num_model += 1
                p_list[i] = [" "] * 2
                p_list[i][0] = "MODEL"
                p_list[i][1] = str(num_model)
                multiple_models = True
                i += 1
                func_length += 1
    return p_list, func_length, multiple_models, num_model, (num_atoms + 1)


"""This method is used to change the list of strings into 
a list of floats and strings for preparation of input into the 
database. Might be able to make this into protein info. 
"""
def create_functional_list(string_list, l, multiple_models):
    x = 0
    if multiple_models:
        functional_list = [None] * l
    else:
        functional_list = [None] * (l + 1)
        functional_list[0] = ['MODEL', 1.0]
        x = 1

    for e in string_list:#changes members of list to respective data types
        if (e != None) and (len(e) != 0):
            e_temp = [None] * len(e)
            if len(e) == 2:
                e_temp[0] = str(e[0])
                e_temp[1] = float(e[1])
            else:
                e_temp[0] = str(e[0])
                e_temp[1] = float(e[1])
                e_temp[2] = str(e[2])
                e_temp[3] = str(e[3])
                e_temp[4] = str(e[4])
                e_temp[5] = str(e[5])
                e_temp[6] = float(e[6])
                e_temp[7] = str(e[7])
                e_temp[8] = float(e[8])
                e_temp[9] = float(e[9])
                e_temp[10] = float(e[10])
                e_temp[11] = float(e[11])
                e_temp[12] = float(e[12])
                e_temp[13] = str(e[13])
                e_temp[14] = str(e[14])
            functional_list[x] = e_temp
            x += 1
    return functional_list


"""This is used to break up the models when there is more than one model.
"""
def breakup_models(input_list, num_model):
    index_models = [None] * num_model
    num_atoms = 0
    models = [None] * num_model
    i = 0
    ii = 0
    for e in input_list:
        if e[0] == "MODEL":
            index_models[i] = ii
            i += 1
        ii += 1
    i = 0
    for e in models:
        if i < (num_model - 1):
            models[i] = input_list[index_models[i]:index_models[i + 1]]
        else:
            models[i] = input_list[index_models[i]:]
        i += 1

    return models


"""This is used to download pdb's from the web."""
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
    network_err = False
    while True:
        if add_from_web == "y":
            while True:
                if not all:
                    pdb_id = input("\n------------------------\n"
                                   "Enter pdb id (or exit, or all): ")
                if pdb_id.strip().lower() == "all":
                    all = True
                else:
                    all = False
                if all:
                    network_err = add_all(base_url, directory_path)
                    return network_err
                print("________________________\n")
                if pdb_id == "exit":
                    return
                file_name = str(pdb_id) + ".pdb"
                try:
                    urllib.request.urlopen(base_url + file_name)
                except(urllib.error.HTTPError or TimeoutError or urllib.error.URLError):  # added 1/4/17
                    print("\n-----------------------\n"
                          "That pdb id does not exist, \n "
                          "or that protein does not have a pdb file\n"
                          "...try again or exit\n"
                          "\n-----------------------\n")
                    if (all):
                        num_input = 0
                    continue
                except (TypeError):  # this is to account for the end of list
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
                pdb_file = directory_path + "/" + file_name
                urllib.request.urlretrieve(target_url, pdb_file)
                print(file_name + " downloaded>>>>")
            except(urllib.error.HTTPError or TimeoutError or urllib.error.URLError):
                print("ERROR: Network connection problem when "
                      "trying to download " + file_name + ". \nReturning to program...")
                return True


"""This is used inside of write_from_web in case the user wants
to download every single pdb file."""
def add_all(base_url, pdb_files_dir):
    # this is the command used in
    # write_to_web
    # ******WARNING******
    #   WILL DOWNLOAD ALL
    #   125,000+ pdb files
    #~100 GB are needed

    url = "ftp://ftp.wwpdb.org/pub/pdb/derived_data/index/source.idx"
    id_file = os.path.dirname(__file__) + "/" + "LIST_OF_ALL_IDS.txt"
    urllib.request.urlretrieve(url, id_file)
    try:
        with open(str(id_file)) as txt:
            i = 0
            for line in txt:
                if i >= 4:
                    not_in_dir = True
                    file_name = str(line[:5]).strip().lower() + ".pdb"
                    if (file_name in os.listdir(pdb_files_dir)) or ((file_name[0:4].upper() + ".pdb") in os.listdir(pdb_files_dir)):
                        not_in_dir = False
                    if not_in_dir:
                        try:
                            target_url = base_url + "/" + file_name
                            pdb_file = str(pdb_files_dir) + "/" + str(file_name)
                            urllib.request.urlretrieve(target_url, pdb_file)
                            print("________________________\n")
                            print(file_name + " downloaded>>>>")
                        except(urllib.error.HTTPError or TimeoutError or urllib.error.URLError):
                            print("________________________\n")
                            print(file_name + " DOES NOT EXIST ON RCSB.ORG")
                            continue
                        except TypeError:  # this is to account for the end of list
                            return False
                    else:
                        print("________________________\n\n" +
                              file_name + " is already in " + pdb_files_dir)
                        continue
                i += 1
    except(FileNotFoundError):
        print("\n----------------\n"
              "ERROR: ID FILE DOES NOT EXIST\n"
              "\n--------SYSTEM EXITING--------\n")
        sys.exit(0)


"""Creates a directory with all found pdbs"""
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


"""Finds all pdbs and creates a directory with create_pdb_bank."""
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


"""This is the object that will have the proteins coordinate file
information and the name of the file."""
class ProteinStructure:
    def __init__(self, fil, name):
        self.file_name = name
        self.dir_path = fil
        self.list_length = 0
        self.particle_list = []
        self.num_atoms = 0

    def get_file(self):
        return self.file_name


"""This is simply the main method where the main flow of the 
program is."""
def main():
    while True:
        network_problem = False
        network_problem = write_from_web()
        if not network_problem:
            break
    database_password = ""
    database_action_verification = input("\n----------------------------\n"
                                         "Are you going to deposit pdbs in a database? (y) or (n)\n"
                                         "_______________________________\n")
    while True:
        try:
            if database_action_verification == "y":
                database_password = input("\n----------------------------\n"
                                          "What is the root database server password that is at localHost?\n"
                                          "_______________________________\n")
                db = pymysql.connect(user="root", password=database_password, host="localhost")
                cursor = db.cursor()
                filterwarnings('ignore', category= pymysql.Warning)#surpresses warning of proteins already exits
                cursor.execute("CREATE DATABASE IF NOT EXISTS proteins")
            else:
                print("THEN WHAT ARE YOU DOING HERE????\n"
                      "BYEEEEEEEEE.....")
                sys.exit(0)
            break
        except(pymysql.ProgrammingError):
            print("Access Denied...try again.")
            continue
        except(pymysql.InterfaceError):
            print("The MySQL server @localhost is not running...\nSystem exiting...")
            sys.exit(0)
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
                current_protein = ProteinStructure(current_abs_path, current_file_name)

                temp_list, current_protein.list_length, multiple_models, num_model, current_protein.num_atoms = protein_info(
                    current_abs_path)
                current_protein.particle_list = create_functional_list(temp_list,
                                                                       current_protein.list_length, multiple_models)

                if multiple_models:
                    current_protein.particle_list = breakup_models(current_protein.particle_list, num_model)
                    current_protein.num_atoms = len(current_protein.particle_list[0]) - 1
                error_happened = False
                already_added = False
                if database_action_verification == "y":
                    error_happened, already_added = create_database(db, current_protein, multiple_models)
                if not error_happened:
                    if not already_added:
                        print("---file " + str(f + 1) + " of " + str(len(os.listdir(directory_path))) + "---\n")
                        print(current_protein.file_name + " was added to the database in %s seconds " % (
                            time.time() - start_file_time))
                        print("_________________________\n")
                    else:
                        print("---file " + str(f + 1) + " of " + str(len(os.listdir(directory_path))) + "---\n")
                        print(current_protein.file_name + " has already been added.")
                        print("_________________________\n")
                f += 1
        db.close()
    print("--- %s seconds ---" % (time.time() - start_time))

#This calls the main method, initiating the entire program
main()

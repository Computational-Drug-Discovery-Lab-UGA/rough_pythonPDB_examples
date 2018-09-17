#!/usr/bin/python

import re
import os
import os.path
import sys
import shutil
import urllib.request
import time
from warnings import filterwarnings

regex_ext = re.compile(r"\S{4}(\.)(pdb)")

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
    a= 0
    with open(file) as f:
        for l in f:#this separates the lines of the coordinate files
            if(a==0):
                p_list[i] = [" "]*2
                p_list[i][0] = "MODEL"
                p_list[i][1] = 1
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
    return p_list, func_length

"""This is simply the main method where the main flow of the 
program is."""
def main():
    c = "AMP ADP ATP CDP CTP GMP GDP GTP TMP TTP UMP UDP UTP"
    d = "DA DC DG DT DI"
    r = "A C G U I"
    pp = "ALA CYS ASP GLU PHE GLY HIS ILE LYS LEU MET ASN PRO GLN ARG SER THR VAL TRP TYR"
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
    largestProtein = 0
    while reset_directory:
        if not os.path.exists(directory_path + "/" + "DNA"):
            os.mkdir(directory_path + "/" + "DNA")
        if not os.path.exists(directory_path + "/" + "RNA"):
            os.mkdir(directory_path + "/" + "RNA")
        for file in os.listdir(directory_path):
            hasDNA = False
            hasRNA = False
            # hasCofactor = False
            # hasIon = False
            # hasCarb = False
            if(os.path.isdir(file)):
                continue
            start_file_time = time.time()
            if re.search(regex_ext, file) != None:
                reset_directory = False
                current_abs_path = directory_path + "/" + str(file)
                temp_list, list_length = protein_info(current_abs_path)

                f += 1
            atom = 0
            actualAtom = 0
            while atom < list_length:
                if (temp_list[atom][0] == "MODEL" and temp_list[atom][1] == 1 or temp_list[atom][0] == "ATOM" or temp_list[atom][0] == "HETATM"):
                    while temp_list[atom][0] == "ATOM" or temp_list[atom][0] == "HETATM":
                        actualAtom += 1
                        atom += 1
                    break
                    """
                                        if (temp_list[atom][4] in pp):
                        s=0
                    next needs to be elif if above is uncommented
                    if(temp_list[atom][4] in d and not hasDNA):
                        shutil.copy2(current_abs_path, directory_path + "/" + "DNA")
                        hasDNA = True
                    elif (temp_list[atom][4] in r and not hasRNA):
                        shutil.copy2(current_abs_path, directory_path + "/" + "RNA")
                        hasRNA = True
                    elif (temp_list[atom][4] in c):
                        s=0
                    elif (temp_list[atom][4] is temp_list[atom][2]):
                        s=0
                    else:
                        is a ligand
                    if(hasDNA and hasRNA):
                        break
                    
                    """

                atom += 1
            if (actualAtom > largestProtein):
                largestProtein = actualAtom
            print("%s ->>> %d (actual = %d)" % (file, actualAtom, largestProtein))


    print("\nLARGEST ATOM = % \n\n" % largestProtein)
    print("--- %s seconds ---" % (time.time() - start_time))

#This calls the main method, initiating the entire program
main()

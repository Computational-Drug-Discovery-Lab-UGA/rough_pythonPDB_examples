# *****NEED python 3.4 interpreter*****
#!/usr/bin/python
import mysql.connector
import os
import traceback
import shutil
import sqlite3

def no_models(object, particles, cursor, pdb_id, db):
    model_num = 1
    i = 0
    hel = []
    try:
        for e in particles:
            hel = e
            alt = " "
            iC = " "
            ch = " "
            if i != 0:
                if e[3] == " ":
                    alt = None
                else:
                    alt = e[3]
                if e[7] == " ":
                    iC = None
                else:
                    iC = e[7]
                if e[14] == "  ":
                    ch = None
                else:
                    ch = e[14]
                cursor.execute(
                    "INSERT INTO " + pdb_id + """
                        (model, ATOM_OR_HETATM, Serial_num, name, altLoc, resName, Chain_id, resSeq, iCode, x, y, z, occupancy, tempFactor, element, charge)
                        VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                    (model_num, e[0], e[1], e[2], alt, e[4], e[5], e[6], iC, e[8], e[9], e[10], e[11], e[12], e[13], ch))
                db.commit()
            i += 1
    except(mysql.connector.errors.ProgrammingError) as err:
        move_to_error(object.dir_path, pdb_id, "PROGRAMMING_ERROR")
        traceback.print_tb(err.__traceback__)
        print(str(err))
        print("\n-----\n" + pdb_id + "\n-----\n")
        print(hel)
        cursor.execute("DROP TABLE IF EXISTS`%s`" % pdb_id)
        db.commit()
    except(IndexError) as err:
        move_to_error(object.dir_path, pdb_id, "INDEX_ERROR")
        traceback.print_tb(err.__traceback__)
        print("\n" + str(err) + "\n")
        print("\n-----\n" + pdb_id + "\n-----\n")
        print(hel)
        cursor.execute("DROP TABLE IF EXISTS`%s`" % pdb_id)
        db.commit()

def yes_models(object, particles, cursor, pdb_id, db):
    hel = []
    try:
        for e in particles:
            i = 0
            while i < len(e):
                hel = e[i]
                if e[i][0] == "MODEL":
                    model_num = int(e[i][1])
                    i += 1
                if i != 0:
                    if e[i][3] == " ":
                        alt = None
                    else:
                        alt = e[i][3]
                    if e[i][7] == " ":
                        iC = None
                    else:
                        iC = e[i][7]
                    if e[i][14] == "  ":
                        ch = None
                    else:
                        ch = e[i][14]
                    cursor.execute(
                    "INSERT INTO " + pdb_id + """
                                (model, ATOM_OR_HETATM, Serial_num, name, altLoc, resName, Chain_id, resSeq, iCode, x, y, z, occupancy, tempFactor, element, charge)
                                VALUES
                                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                 """,
                                (model_num, e[i][0], e[i][1], e[i][2], alt, e[i][4], e[i][5], e[i][6], iC,
                                e[i][8], e[i][9], e[i][10], e[i][11], e[i][12], e[i][13], ch))
                    db.commit()
                i += 1
    except(mysql.connector.errors.ProgrammingError) as err:
        move_to_error(object.dir_path, pdb_id, "PROGRAMMING_ERROR")
        traceback.print_tb(err.__traceback__)
        print(str(err))
        print("\n-----\n" + pdb_id + "\n-----\n")
        print(hel)
        cursor.execute("DROP TABLE IF EXISTS`%s`" % pdb_id)
        db.commit()
    except(IndexError) as err:
        move_to_error(object.dir_path, pdb_id, "INDEX_ERROR")
        traceback.print_tb(err.__traceback__)
        print("\n" + str(err) + "\n")
        print("\n-----\n" + pdb_id + "\n-----\n")
        print(hel)
        cursor.execute("DROP TABLE IF EXISTS`%s`" % pdb_id)
        db.commit()

def move_to_error(directory_path, pdb_id, type):
    error_dir = directory_path[:-19] + "/" + "error" + "/" + type
    if not os.path.exists(error_dir):
        os.mkdir(error_dir)
    current_file_path = directory_path[:-9] + "/" + pdb_id + ".pdb"
    new_file_path = error_dir + "/" + pdb_id + ".pdb"
    if os.path.exists(new_file_path):
        return
    shutil.copy2(current_file_path,new_file_path[:-8])

def need_to_specify_server():
    yes = input("\n------------"
                "Do you need to connect to a different Database server"
                " other than MySQLjax? (y) or (n) (if using sqlite.db (sqlite))"
                "------------\n")
    if yes == "y" or yes =="yes" :
        user = input("User: ")
        password = input("Password: ")
        host = input("HOST NAME: ")
        database = input("database: ")
        return user, password, host, database
    elif yes == "sqlite":
        return "sqlite", "sqlite", "sqlite", "sqlite"
    else:
        return "root", "Proteins11", "localhost", "proteins"

def protein_db(user, password, host, database):
    #if user == "sqlite":
    #    return
    db = mysql.connector.connect(user=user, password=password, host=host, database=database)
    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS proteins")
    db.commit()

def create_database(db, object, multiple_models):
    pdb_id = object.file_name[0:4]
    particles = object.particle_list
    """only needed if you need to specify another database
    user, password, host, database = need_to_specify_server()
    if user == "sqlite":
        db_path = input("\n------\nPlease enter the absolute path to the sqlite database\n------\n")
        db = sqlite3.connect(db_path)#need to account for errors here or it will crash if wrong
        cursor = db.cursor()
    else:"""
    cursor = db.cursor()
    cursor1 = db.cursor(buffered=True)
    # use database
    cursor1.execute("USE proteins")
    db.commit()
    #create id table
    try:
        cursor1.execute("SELECT COUNT(*) FROM `%s`" % pdb_id)
        db.commit()
        (count,) = cursor1.fetchone()
        db.commit()
        if multiple_models:
            mod_dir = object.dir_path[:-19] + "/" + "HAS_MODELS_pdb_files"
            if not os.path.exists(mod_dir):
                os.mkdir(mod_dir)
            if os.path.exists(mod_dir + "/" + pdb_id + ".pdb"):
                shutil.copy2(object.dir_path, mod_dir)
            elif((multiple_models==False) and((count > (100 + object.list_length)) or (count < (object.list_length - 100)))):
                cursor.execute("DROP TABLE IF EXISTS`%s`" % pdb_id)
                move_to_error(object.dir_path, pdb_id, "NUM_ROWS_OFF")
    except(mysql.connector.errors.ProgrammingError):
        cursor.execute("""CREATE TABLE IF NOT EXISTS `%s`(
                                  model DECIMAL(8,3),
                                  ATOM_OR_HETATM VARCHAR(8),
                                  Serial_num DECIMAL(8,3),
                                  name VARCHAR(6),
                                  altLoc VARCHAR(4),
                                  resName VARCHAR(6),
                                  Chain_id VARCHAR(4),
                                  resSeq DECIMAL(8,3),
                                  iCode VARCHAR(4),
                                  x DECIMAL(8,3),
                                  y DECIMAL(8,3),
                                  z DECIMAL(8,3),
                                  occupancy DECIMAL(6,3),
                                  tempFactor DECIMAL(6,3),
                                  element VARCHAR(4),
                                  charge VARCHAR(4))""" % pdb_id)
        db.commit()
        model_num = 0
        if not multiple_models:
            no_models(object, particles,cursor, pdb_id, db)
        else:
            yes_models(object, particles, cursor, pdb_id, db)

        '''for e in particles:
                hel = e
                alt = " "
                iC = " "
                ch = " "
                index_indicator = 0
                if not multiple_models:
                    model_num = 1
                    if index_indicator != 0:
                        if e[3] == " ":
                            alt = None
                        else:
                            alt = e[3]
                        if e[7] == " ":
                            iC = None
                        else:
                            iC = e[7]
                        if e[14] == "  ":
                            ch = None
                        else:
                            ch = e[14]
                        cursor.execute(
                "INSERT INTO " + pdb_id + """
                (model, ATOM_OR_HETATM, Serial_num, name, altLoc, resName, Chain_id, resSeq, iCode, x, y, z, occupancy, tempFactor, element, charge)
                VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (model_num, e[0], e[1], e[2], alt, e[4], e[5], e[6], iC, e[8], e[9], e[10], e[11], e[12], e[13], ch))
                        db.commit()
                        index_indicator += 1
                        continue

                else:
                    i = 0
                    while i < len(e):
                        if e[i][0] == "MODEL":
                            model_num = int(e[i][1])
                            i += 1
                        if i != 0:
                            if e[i][3] == " ":
                                alt = None
                            else:
                                alt = e[i][3]
                            if e[i][7] == " ":
                                iC = None
                            else:
                                iC = e[i][7]
                            if e[i][14] == "  ":
                                ch = None
                            else:
                                ch = e[i][14]
                            cursor.execute(
                                "INSERT INTO " + pdb_id + """
                                                        (model, ATOM_OR_HETATM, Serial_num, name, altLoc, resName, Chain_id, resSeq, iCode, x, y, z, occupancy, tempFactor, element, charge)
                                                        VALUES
                                                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                                            """,
                                (model_num, e[i][0], e[i][1], e[i][2], alt, e[i][4], e[i][5], e[i][6], iC,
                                 e[i][8], e[i][9], e[i][10], e[i][11], e[i][12], e[i][13], ch))
                            db.commit()
                            i += 1'''
        return db


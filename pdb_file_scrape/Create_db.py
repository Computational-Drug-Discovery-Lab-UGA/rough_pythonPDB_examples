# !/usr/bin/python
import pymysql
import os
import traceback
import shutil

"""This is the method that will fill the database proteins in.
This means that the database server that you are using must have 
a database called proteins.
ALSO This database server must be mysql."""
def create_database(db, object, multiple_models):
    pdb_id = object.file_name[0:4]
    particles = object.particle_list
    cursor = db.cursor()
    cursor.execute("USE proteins")
    db.commit()
    try:#this try checks to see if the table exists by counting rows
        cursor.execute("SELECT COUNT(*) FROM `%s`" % pdb_id)
        db.commit()
        (count,) = cursor.fetchone()
        db.commit()
        if multiple_models:
            mod_dir = object.dir_path[:-19] + "/" + "HAS_MODELS_pdb_files"
            if not os.path.exists(mod_dir):
                os.mkdir(mod_dir)
            if os.path.exists(mod_dir + "/" + pdb_id + ".pdb"):
                shutil.copy2(object.dir_path, mod_dir)
            elif ((multiple_models == False) and (
                        (count > (100 + object.list_length)) or (count < (object.list_length - 100)))):
                cursor.execute("DROP TABLE IF EXISTS`%s`" % pdb_id)
                move_to_error(object.dir_path, pdb_id, "NUM_ROWS_OFF")
        return False, True
    except(pymysql.ProgrammingError):#this programing error just specifies the existence of the table
        cursor.execute("""CREATE TABLE IF NOT EXISTS `%s`(
                                  model DECIMAL(8,3),
                                  ATOM_OR_HETATM VARCHAR(8),
                                  Serial_num DECIMAL(8,3),
                                  name VARCHAR(6),
                                  altLoc VARCHAR(4),
                                  resName VARCHAR(8),
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
        error_happened = False
        if not multiple_models:
            error_happened = no_models(object, particles, cursor, pdb_id, db)
        else:
            error_happened = yes_models(object, particles, cursor, pdb_id, db)
        return error_happened, False


"""Inserts data into tables that represent
proteins that only have one model."""
def no_models(object, particles, cursor, pdb_id, db):
    pdbid = '`' + pdb_id + '`'
    insert_statement = (
        "INSERT INTO " + pdbid + """(model, ATOM_OR_HETATM, Serial_num, name, altLoc, resName, Chain_id, resSeq, iCode, x, y, z, occupancy, tempFactor, element, charge) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""")
    model_num = 1
    import_array = [None] * (len(particles) - 1)
    row = -1
    for e in particles:
        if row != -1:
            import_array[row] = [None] * 16
        col = 1
        for ee in e:
            if e[0] != "MODEL":
                import_array[row][0] = model_num
                if type(ee) != float and ee == " " or ee == "  ":
                    import_array[row][col] = None
                else:
                    import_array[row][col] = ee
            col += 1
        row += 1
    try:
        i = 0
        num_import = 1
        while i < len(import_array):
            if (num_import) * 500 > len(import_array):
                if num_import > 1:
                    segment_import = [None] * (len(import_array) - ((num_import - 1) * 500))
                else:
                    segment_import = [None] * len(import_array)
            else:
                segment_import = [None] * 500
            ii = 0
            while ii < len(segment_import):
                segment_import[ii] = [None] * 16
                iii = 0
                for e in import_array[i]:
                    segment_import[ii][iii] = e
                    iii += 1
                ii += 1
                i += 1
            cursor.executemany(insert_statement, segment_import)
            db.commit()
            num_import += 1
        return False
    except(pymysql.ProgrammingError) as err:#this will move pdb file to an error file if error occurs
        move_to_error(object.dir_path, pdb_id, "PROGRAMMING_ERROR")
        traceback.print_tb(err.__traceback__)
        print(str(err))
        print("\n-----\n" + pdb_id + "\n-----\n")
        cursor.execute("DROP TABLE IF EXISTS`%s`" % pdb_id)
        db.commit()
        return True
    except(IndexError) as err:#this will move pdb file to an error file if error occurs
        move_to_error(object.dir_path, pdb_id, "INDEX_ERROR")
        traceback.print_tb(err.__traceback__)
        print("\n" + str(err) + "\n")
        cursor.execute("DROP TABLE IF EXISTS`%s`" % pdb_id)
        db.commit()
        return True


"""Inserts data into tables that represent 
proteins that have more than one model."""

def yes_models(object, particles, cursor, pdb_id, db):
    pdbid = '`' + pdb_id + '`'
    insert_statement = (
        "INSERT INTO " + pdbid + """(model, ATOM_OR_HETATM, Serial_num, name, altLoc, resName, Chain_id, resSeq, iCode, x, y, z, occupancy, tempFactor, element, charge) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""")
    iter_helper = ""
    i = 0
    for e in particles:
        for ee in e:
            if ee[0] != "MODEL":
                i += 1
    import_array = [None] * i
    model_num = 1
    row = 0
    for e in particles:
        for ee in e:
            import_array[row] = [None] * 16
            col = 1
            import_array[row][0] = model_num
            iter_helper = ee[0]
            for eee in ee:
                if ee[0] != "MODEL":
                    if type(eee) != float and eee == " " or eee == "  ":
                        import_array[row][col] = None
                    else:
                        import_array[row][col] = eee
                    col += 1
            if iter_helper != "MODEL":
                row += 1
        model_num += 1
    try:
        i = 0
        num_import = 1
        while i < len(import_array):
            if (num_import) * 500 > len(import_array):
                if num_import > 1:
                    segment_import = [None] * (len(import_array) - ((num_import - 1) * 500))
                else:
                    segment_import = [None] * len(import_array)
            else:
                segment_import = [None] * 500
            ii = 0
            while ii < len(segment_import):
                segment_import[ii] = [None] * 16
                iii = 0
                for e in import_array[i]:
                    segment_import[ii][iii] = e
                    iii += 1
                ii += 1
                i += 1
            cursor.executemany(insert_statement, segment_import)
            db.commit()
            num_import += 1
        return False
    except(pymysql.ProgrammingError) as err:#this will move pdb file to an error file if error occurs
        move_to_error(object.dir_path, pdb_id, "PROGRAMMING_ERROR")
        traceback.print_tb(err.__traceback__)
        print(str(err))
        print("\n-----\n" + pdb_id + "\n-----\n")
        cursor.execute("DROP TABLE IF EXISTS`%s`" % pdb_id)
        db.commit()
        return True
    except(IndexError) as err:#this will move pdb file to an error file if error occurs
        move_to_error(object.dir_path, pdb_id, "INDEX_ERROR")
        traceback.print_tb(err.__traceback__)
        print("\n" + str(err) + "\n")
        cursor.execute("DROP TABLE IF EXISTS`%s`" % pdb_id)
        db.commit()
        return True


"""This will move the pdb to an error file in the case 
that this deposit program ran into a problem."""
def move_to_error(directory_path, pdb_id, type):
    error_dir = directory_path[:-19] + "/" + "error" + "/" + type
    print(directory_path[-26:])
    if directory_path[-26:] == "PROGRAMMING_ERROR/" + pdb_id + ".pdb":
        if type != "PROGRAMMING_ERROR":
            error_dir = directory_path[-26:] + "/" + type
        else:
            return
    if not os.path.exists(error_dir):
        os.mkdir(error_dir)
    new_file_path = error_dir + "/" + pdb_id + ".pdb"
    if os.path.exists(new_file_path):
        return
    shutil.copy2(directory_path, new_file_path[:-8])

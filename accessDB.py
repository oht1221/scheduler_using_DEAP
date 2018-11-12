#-*-coding:utf-8-*-

import pyodbc



def AccessDB(database, username, password):
    dsn = 'hansundatasource'
    database = 'han_eng_back'
    '''database = 'hansun'
    username = 'Han_Eng_Back'
    password = 'HseAdmin1991' '''
    con_string = "DSN=%s;UID=%s;PWD=%s;DATBASE=%s"%(dsn, username, password, database)
    cnxn = pyodbc.connect(con_string)
    cursor = cnxn.cursor()

    return cursor

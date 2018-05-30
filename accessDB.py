import pyodbc

def AccessDB():
    server = '221.161.62.124,2433'
    database = 'hansun'
    username = 'Han_Eng_Back'
    password = 'HseAdmin1991'
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER='+server
                      +';데이터베이스='+database+';UID='+username+';PWD='+password)
    cursor = cnxn.cursor()

    return cursor
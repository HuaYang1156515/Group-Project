import mysql.connector
from mysql.connector import FieldType
from datetime import datetime
from config import connect

dbconn = None
connection = None
current_date = datetime.now().strftime("%Y%m%dHH:mm:ss")
def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn


#--------------------------------------------------------
# Query functions
# Sql, Parameters
#--------------------------------------------------------
def query_all(sql):
    connection = getCursor()
    connection.execute(sql)
    rows = connection.fetchall()
    
    columns = [column[0] for column in connection.description]  # get column name
    result = []
    for row in rows:
        result.append(dict(zip(columns, row)))  
    return result

def query_one(sql):
    connection = getCursor()
    connection.execute(sql)
    row = connection.fetchone()
    
    if row:
        columns = [column[0] for column in connection.description]  # get column name
        return dict(zip(columns, row))  
    else:
        return None

def db_execute(sql):
    connection = getCursor()
    connection.execute(sql)
    

def call_proc(proc_name,args):
    connection = getCursor()
    connection.callproc(proc_name,args)
    



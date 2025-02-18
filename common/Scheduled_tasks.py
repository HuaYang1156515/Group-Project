import mysql.connector
from mysql.connector import FieldType
from datetime import datetime

dbuser = "peixuanhan888" # Your MySQL username - likely 'root'
dbpass = "BsmpDB1234" # ---- PUT YOUR PASSWORD HERE ----
dbhost = "peixuanhan888.mysql.pythonanywhere-services.com" 
dbport = "3306"
dbname = "peixuanhan888$BsmpDB"


dbconn = None
connection = None
current_date = datetime.now().strftime("%Y%m%dHH:mm:ss")
def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=dbuser, \
    password=dbpass, host=dbhost, \
    database=dbname, autocommit=True)
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
    




def update_balance():
    

    # get current month year
    now = datetime.now()
    current_year_month = now.strftime("%m-%Y")
    sql = "SELECT month_year FROM monthly_tasks ORDER BY id DESC LIMIT 1"
    # check if it ran
    result = query_one(sql)
    

    if result:
        last_year_month = result["month_year"]
        if last_year_month == current_year_month:
           
            return
        elif last_year_month != current_year_month:
            # update all corporate business credit 
            db_execute("UPDATE u_business_customers SET credit_used = 0")
            

            # update schedule task
            db_execute(
                f"""INSERT INTO monthly_tasks (month_year) VALUES ('{current_year_month}')""")
            
            
    else:
        # first run
        db_execute("UPDATE u_business_customers SET credit_used = 0")
       

        db_execute(
                f"""INSERT INTO monthly_tasks (month_year) VALUES ('{current_year_month}')""")


if __name__ == "__main__":
    update_balance()

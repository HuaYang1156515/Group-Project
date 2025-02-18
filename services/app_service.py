from common  import hashing
from services import dbText
from models import user_model


# 分页函数
def paginate(page, per_page, total_items):
    num_pages = (total_items + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < num_pages
    return {
        'page': page,
        'per_page': per_page,
        'total_items': total_items,
        'num_pages': num_pages,
        'has_prev': has_prev,
        'has_next': has_next,
    }



# check username if existing
def check_username_existing(username):
   
    sql = f"""SELECT * FROM users WHERE username = '{username}'"""
    
    result = dbText.query_one(sql)
    return result


def user_check(username):
    # check user info 
    # Parameters: username
    results = dbText.query_one(f"""
        SELECT user_id, username, password,role,status FROM users where username = '{username}'""")
    if results:
        
        return user_model.User(results['user_id'], results['username'], results['password'], results['role'], results['status'])
    


def userid_check(user_id):
    # check user info 
    # Parameters: username
    results = dbText.query_one(f"""
        SELECT user_id, username, password,role,status FROM users where user_id = '{user_id}'""")
    if results:
        user_id, username, password,role,status = results
        return user_model.User(results['user_id'], results['username'], results['password'], results['role'], results['status'])




# create user
def create_user(username, password,role,status):
    
  
    hashed_password = hashing.hash_value(password)
    sql = f"""INSERT INTO users (username, password,role,status) VALUES ('{username}', '{hashed_password}','{role}','{status}')"""
    dbText.db_execute(sql)
    return True

# insert general customer
def insert_customer(user_id, first_name, last_name,  email):
    sql = f"""
    INSERT INTO u_customers (user_id, first_name, last_name, email)
    VALUES ('{user_id}', '{first_name}', '{last_name}', '{email}')
    """
    dbText.db_execute(sql)
    return True


# insert customer
def insert_b_customer(user_id, comp_name, cont_name, email):
    sql = f"""
    INSERT INTO u_business_customers (user_id, company_name, contact_name, email)
    VALUES ('{user_id}', '{comp_name}', '{cont_name}', '{email}')
    """
    dbText.db_execute(sql)
    return True



#------------------------#
#   base   #
#------------------------#

#categories

#get all category

def get_categories():

    sql = """select 0 as cate_id, 'All Categories' as name
            union
            SELECT cate_id,name
            FROM category where category_level = 1;"""
    result = dbText.query_all(sql)
    return result


# get cart list
def get_cart_list(user_id):
    
    sql = f"""SELECT o.*, p.product_name,pic.pic_url from order_cart o join product_info p on o.product_id = p.product_id join product_pic_info pic on p.product_id = pic.product_id where pic.is_master = 0 and o.user_id = {user_id} and o.if_paid = 1;"""
       
    result = dbText.query_all(sql)
    return result


#--------------------
# chat
#-----------------

def get_session_id(user_id):
    check_id = f"""select session_id from chat_sessions where customer_id = '{user_id}' order by session_id desc limit 1"""
    result = dbText.query_one(check_id)
    return result
def insert_session(user_id):
  
    result = get_session_id(user_id)
    if result:
        sql = f"""UPDATE chat_sessions SET status = 'waiting' WHERE session_id = '{result['session_id']}';"""
        dbText.db_execute(sql)
        return result['session_id']
    else:
        sql = f"""INSERT INTO chat_sessions(customer_id) value ('{user_id}')"""
        dbText.db_execute(sql)
        result = get_session_id(user_id)
        return result['session_id']


def insert_chat(session_id,sender_id,message):
    sql = f"""INSERT INTO chat (session_id, sender_id, chat) VALUES ('{session_id}', '{sender_id}', '{message}')"""
    dbText.db_execute(sql)
    return True

def chat_history(session_id):
    sql = f"""select c.*,u.username from chat c JOIN users u ON c.sender_id = u.user_id  where c.session_id = '{session_id}' order by chat_id asc;"""
    result = dbText.query_all(sql)
    return result



def close_chat(session_id):
    sql = f"""UPDATE chat_sessions SET status = 'close' WHERE session_id = '{session_id}';"""
    dbText.db_execute(sql)
    return True




def get_message_count(user_id):
    sql = f"""select count(*) as count from messagebox where recipient_user_id = '{user_id}' and status = 0"""
    result = dbText.query_one(sql)
    return result['count']
def get_cart_count(user_id):
    sql = f"""select count(*) as count from order_cart where user_id = '{user_id}' and selected = 0 and if_paid = 1;"""
    result = dbText.query_one(sql)
    return result['count']
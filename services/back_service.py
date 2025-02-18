from services import dbText
from decimal import Decimal

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

# 查询函数
def query_total_items(sql):
    
    # 查询总记录数
   
    total_items = dbText.query_one(sql)['count(*)']
    return total_items

def query_t_total_items(sql):
    
    # 查询总记录数
   
    total_items = dbText.query_one(sql)
    return total_items

def query_items(page,per_page,item_sql):
    
    # 计算起始位置
    
    offset = (page - 1) * per_page
    # 执行分页查询
    #connection.execute("SELECT * FROM items LIMIT %s, %s", (offset, per_page))
    item_sql = item_sql + f" limit {offset},{per_page}"
    items = dbText.query_all(item_sql )

    return items

#----------------------
#backend users related#
#-----------------------

# insert staff includes employee, manager
def insert_employee(user_id, first_name, last_name, email,type,pro_img):
    if type == 1:
        sql = f"""
    INSERT INTO u_staff (user_id, first_name, last_name, email,pro_img)
    VALUES ('{user_id}', '{first_name}', '{last_name}', '{email}','{pro_img}')
    """
    elif type == 2:
         sql = f"""
    INSERT INTO u_managers (user_id, first_name, last_name, email,pro_img)
    VALUES ('{user_id}', '{first_name}', '{last_name}', '{email}','{pro_img}')
    """
    dbText.db_execute(sql)
    return True

# get account info
def get_account(id):
    sql = f"""
SELECT u.*,usr.role
FROM users AS usr
JOIN u_managers AS u ON usr.user_id = u.user_id
WHERE usr.user_id = {id} AND usr.role = 2

UNION ALL


SELECT u.*,usr.role
FROM users AS usr
JOIN u_staff AS u ON usr.user_id = u.user_id
WHERE usr.user_id = {id} AND usr.role = 1
union

SELECT u.*,usr.role
FROM users AS usr
JOIN u_admins AS u ON usr.user_id = u.user_id
WHERE usr.user_id = {id} AND usr.role = 0

;"""
    result = dbText.query_one(sql)
    return result

# get customer or business customer info
def get_customer(id, type):
    if type == 3:
        sql = f""" SELECT u.*,usr.role
FROM users AS usr
JOIN u_customers AS u ON usr.user_id = u.user_id
WHERE usr.user_id = {id} AND usr.role = 3"""

    elif type == 4:
        sql = f"""SELECT u.*,usr.role
FROM users AS usr
JOIN u_business_customers AS u ON usr.user_id = u.user_id
WHERE usr.user_id = {id} AND usr.role = 4 """
    result = dbText.query_one(sql)
    return result


# get point or balance changed log

def get_point_log(user_id):
    sql = f""" select u.username,log.* from customer_point_log log join users u on log.user_id = u.user_id where log.user_id = '{user_id}' order by log.create_time;"""
    result = dbText.query_all(sql)
    return result

def update_account(user_id,fname,lname,gender,phone,email,image_name,type):
    if type == 1:
        sql = f"""update u_staff set first_name = '{fname}', last_name = '{lname}',gender = '{gender}',phone_number = '{phone}',email= '{email}', pro_img = '{image_name}' where user_id = '{user_id}'"""
    elif type == 2:
        sql = f"""update u_managers set first_name = '{fname}', last_name = '{lname}',gender = '{gender}',phone_number = '{phone}',email= '{email}', pro_img = '{image_name}' where user_id = '{user_id}'"""
    elif type == 0:
        sql = f"""update u_admins set first_name = '{fname}', last_name = '{lname}',gender = '{gender}',phone_number = '{phone}',email= '{email}', pro_img = '{image_name}' where user_id = '{user_id}'"""
    dbText.db_execute(sql)
    return True

def update_b_account(user_id,cname,con_name,phone,email,credit_limited):
    sql = f"""update u_business_customers set company_name = '{cname}', contact_name = '{con_name}',phone_number = '{phone}',email= '{email}' ,credit_limited = '{credit_limited}' where user_id = '{user_id}'"""

    dbText.db_execute(sql)
    return True
# update general account
def update_g_account(user_id,fname,lname,gender,phone,email,credit_points):
   
    sql = f"""update u_customers set first_name = '{fname}', last_name = '{lname}',gender = '{gender}',phone_number = '{phone}',email= '{email}', credit_points= '{credit_points}' where user_id = '{user_id}'"""

    dbText.db_execute(sql)
    return True


# get order amount tranfer points
def get_order_rate():
    sql = """SELECT COALESCE((SELECT value FROM promotion WHERE promotion_type = 6 ),0.01) AS value;"""
    result = dbText.query_one(sql)
    return result["value"] 

# update general account credit
def update_g_account_credit(user_id,credit_points,type):
    check = get_customer(user_id, 3)['credit_points']
    if type == 0:
        check += int(credit_points)
    elif type == 1:
        check-= int(credit_points)
    sql = f"""update u_customers set credit_points= '{check}' where user_id = '{user_id}'"""
    dbText.db_execute(sql)
    return True
# block account
def delete_account(user_id):

    sql = f"""update users set status = 1 where user_id = '{user_id}';"""
    dbText.db_execute(sql)
    return True


# activate account
def activate_account(user_id):
    sql = f"""update users set status = 0 where user_id = '{user_id}';"""
    dbText.db_execute(sql)
    return True

# incert credit or balance change
def insert_customer_log(user_id,source,refer_number,change_point,reason):
    # check_sql = f"""SELECT *
    # FROM u_business_customers
    # WHERE user_id = '{user_id}';"""
    # existing_credit = dbText.query_one(check_sql)['credit_limited']
    sql = f"""insert into customer_point_log (user_id,source,refer_number,change_point,reason) VALUES('{user_id}','{source}','{refer_number}','{change_point}','{reason}');"""
    dbText.db_execute(sql)
    return True

def check_log(user_id, order_no):
    sql = f"""select COALESCE((change_point),0) as points from customer_point_log where user_id='{user_id}' and refer_number = '{order_no}' and reason LIKE CONCAT('%', 'Order Completed', '%') """
    result = dbText.query_one(sql)
    return result["points"] 

# edit password

def update_pwd(new_pwd,user_id):
    sql = (f"""update users set password = '{new_pwd}' where user_id = '{user_id}'""")
    return  dbText.db_execute(sql)



#----------------------
# corporate 
#-----------------------



#get cooperate client application
def get_application():
    # 构建 SQL 查询语句
    sql = "SELECT u.company_name,u.contact_name ,app.*  FROM application app join u_business_customers u on app.user_id = u.user_id ;"
    
    # 执行 SQL 查询
    result = dbText.query_all(sql)
    return result

def get_application_by_id(application_id):
    sql = f"SELECT u.company_name,u.contact_name ,app.*  FROM application app join u_business_customers u on app.user_id = u.user_id WHERE app.app_id = '{application_id}'"
    result = dbText.query_one(sql)
    return result
 

def update_application_status(app_id, new_status):
    
    sql = f"UPDATE application SET status = '{new_status}' WHERE app_id = '{app_id}'"
    
    dbText.db_execute(sql)
    return True
    
def update_application_comment(app_id, comment):
    sql = f"UPDATE application SET reason = '{comment}' WHERE app_id = '{app_id}'"
    dbText.db_execute(sql)
    return True

def update_corporate_credit(user_id,credit):
    sql = f"""update u_business_customers set credit_limited = '{credit}' where user_id = '{user_id}'"""
    dbText.db_execute(sql)
    return True


#----------------------
#product related#
#-----------------------

#--------------categories----------------------#

# get categories info
def get_categories_parent():
    sql = f"""
    
    SELECT 0 AS parentid, 'root' AS name
    UNION
    SELECT parentid, name
    FROM category
    WHERE parentid = '0'
    
    """
    result = dbText.query_all(sql)
    return result

# insert_category
def insert_category(cate_id, parentid, category_level, name,description , sortorder):
    sql = f"""
    INSERT INTO category (cate_id, parentid, category_level, name,description ,  sortorder)
    VALUES ({cate_id}, '{parentid}', {category_level}, '{name.replace("'", "''")}', '{description.replace("'", "''") }', '{sortorder}')
    """
    dbText.db_execute(sql)
    return True

def delete_category(cate_id):
    sql = f"""delete from category where cate_id = '{cate_id}'"""
    dbText.db_execute(sql)
    return True

#get all category

def get_categories():

    sql = """SELECT cate_id,
       parentid,
       category_level,
       name,
       status,
       description,
       sortorder,
       createtime,
       updatetime,
       (SELECT name FROM category AS parent WHERE parent.cate_id = category.parentid) AS parent_name
FROM category;"""
    result = dbText.query_all(sql)
    return result

#get one level category
def get_one_cate():

    sql = """SELECT cate_id,
       parentid,
       category_level,
       name,
       status,
       description,
       sortorder,
       createtime
    FROM category where category_level = 1; """
    result = dbText.query_all(sql)
    return result

#get two level category
def get_two_cate():

    sql = """SELECT cate_id,
       parentid,
       category_level,
       name,
       status,
       description,
       sortorder,
       createtime
FROM category where category_level = 2; """
    result = dbText.query_all(sql)
    return result


#get all brand

def get_brand():

    sql = """ SELECT b.*, COUNT(p.product_id) AS product_count
FROM brand_info b
left JOIN product_info p ON b.brand_id = p.brand_id
GROUP BY b.brand_id;"""
    result = dbText.query_all(sql)
    return result

def get_brand_info(brand_id):

    sql = f""" SELECT * FROM brand_info where brand_id = '{brand_id}'"""
    result = dbText.query_one(sql)
    return result

# insert brand

def insert_band(brand_name, brand_logo, description):
    sql = f"""
    INSERT INTO brand_info (brand_name, brand_logo, brand_desc)
    VALUES ('{brand_name}', '{brand_logo}', '{description}')
    """
    dbText.db_execute(sql)
    return True


# update brand

def update_band(brand_id,brand_name, brand_logo, description):
    sql = f"""
    update brand_info set brand_name = '{brand_name}', brand_logo = '{brand_logo}', brand_desc = '{description}' where brand_id ='{brand_id}'
    """
    dbText.db_execute(sql)
    return True

# get product code existing

# Insert product
def insert_product(product_code,product_name, brand_id, one_category_id, two_category_id, price,if_promotion, cost, feature, weight,  descript):
    sql = f"""SELECT COUNT(*) FROM product_info WHERE product_code = '{product_code}' """
    existing_count = dbText.query_one(sql)['COUNT(*)']
    if existing_count > 0:
       return False
    sql = f"""
        INSERT INTO product_info (product_code,product_name, brand_id, one_category_id, two_category_id, price,if_promotion, cost, feature, weight,  descript)
        VALUES ('{product_code}','{product_name}',  '{brand_id}', '{one_category_id}', '{two_category_id}', '{price}','{if_promotion}', '{cost}', '{feature}', '{weight}','{descript}' )
    """
    
    dbText.db_execute(sql)
    return True


# Update product
def update_product(product_id,code,name, brand_id, one_category, two_category, price, if_pm, cost, feature, weight, desc):
    sql = f"""SELECT COUNT(*) FROM product_info WHERE product_code = '{code}' AND product_id != {product_id}"""
    existing_count = dbText.query_one(sql)['COUNT(*)']
    if existing_count > 0:
       return False
    sql = f"""
        UPDATE product_info
        SET product_name = '{name}', price = {price}, product_code = '{code}', cost = {cost}, descript = '{desc}',  if_promotion = {if_pm},
            brand_id = {brand_id}, one_category_id = {one_category}, two_category_id = {two_category}, weight = {weight}, feature = '{feature}'
        WHERE product_id = {product_id}
    """
    print(sql)
    dbText.db_execute(sql)
    return True


# get product id after insert 
def get_product_id(code):
    sql = f"""SELECT product_id from product_info where product_code = '{code}' order by product_id desc limit 1"""
   
    result = dbText.query_one(sql)
   
    return result['product_id']

# insert product pic
def insert_product_pic(product_id, pic_url, is_master, pic_order):
   
    sql = f"""
    INSERT INTO product_pic_info (product_id, pic_url, is_master, pic_order)
    VALUES ('{product_id}', '{pic_url}', {is_master}, {pic_order})
    """
   
    dbText.db_execute(sql)
    return True


# update product pic
def update_product_pic(product_id, pic_url):
    sql = f"""SELECT COUNT(*) FROM product_pic_info WHERE product_id = {product_id} and is_master = 0"""
    existing_count = dbText.query_one(sql)['COUNT(*)']
    if existing_count == 0:
        sql = f"""
    INSERT INTO product_pic_info (product_id, pic_url, is_master, pic_order)
    VALUES ({product_id}, '{pic_url}', 0, 0)
    """
   
        dbText.db_execute(sql)



    else:
        sql = f"""
        UPDATE product_pic_info SET pic_url = '{pic_url}' WHERE product_id = {product_id} and is_master = 0
        """
        dbText.db_execute(sql)
    return True

# get specified product
def get_product_info(product_id):
    sql = f"""select p.*, c.pic_url from product_info p left join product_pic_info c on p.product_id = c.product_id and c.is_master = 0 where p.product_id = {product_id} """
    return dbText.query_one(sql)

# off shelf 
def off_product(product_id):
    sql = f"""UPDATE product_info set publish_status = 0 where product_id = {product_id} """
    return dbText.db_execute(sql)

# off pic 
def off_pic(product_pic_id):
    sql = f"""UPDATE product_pic_info set pic_status = 0 where product_pic_id = {product_pic_id} """
    return dbText.db_execute(sql)

# on shelf 
def on_product(product_id):
    sql = f"""UPDATE product_info set publish_status = 1 where product_id = {product_id} """
    return dbText.db_execute(sql)
    

# get product pics

def get_product_pics(product_id):
    sql = f"""select * from product_pic_info where pic_status = 1 and product_id = {product_id}"""
    result = dbText.query_all(sql)
    return result

def  get_product_pic_num(product_id):
    sql = f"""select count(*) as num from product_pic_info where pic_status = 1 and product_id = {product_id}"""
    result = dbText.query_one(sql)
    return result

#----------------------
# warehouse and stock related#
#-----------------------

#get all warehouse

def get_warehouse():

    sql = """ select * from warehouse_info"""
    result = dbText.query_all(sql)
    return result


# INSERT  warehouse_info
def insert_warehouse_info(warehouse_name, warehouse_phone, contact, zip_code, street, city, region, country):
    sql = f"""
    INSERT INTO warehouse_info 
    (warehouse_name, warehouse_phone, contact, zip, street, city, region, country) 
    VALUES ('{warehouse_name}', '{warehouse_phone}', '{contact}', {zip_code}, '{street}', '{city}', '{region}', '{country}');
    """
    dbText.db_execute(sql)
    return True

def insert_stock(product_id, w_id, color, size,ctn):
    sql = f"""SELECT COUNT(*) FROM warehouse_product WHERE product_id = {product_id} and color = '{color}' and size = '{size}'"""
    existing_count = dbText.query_one(sql)['COUNT(*)']
    if existing_count == 0:
        sql = f"""INSERT INTO warehouse_product (product_id,w_id, color, size,current_cnt) VALUES ('{product_id}','{w_id}', '{color}', '{size}', '{ctn}')"""
        dbText.db_execute(sql)
    else:
        sql = f"""update warehouse_product set current_cnt = '{ctn}' where product_id = {product_id} and color = '{color}' and size = '{size}' """
        dbText.db_execute(sql)
    return True
def delete_stock(product_id,color):
    sql = f"""delete from warehouse_product where product_id = {product_id} and color = '{color}'""" 
    dbText.db_execute(sql)
    return True

#----------------------
# system configuration
#-----------------------

#get all color

def get_color():

    sql = """ select * from color"""
    result = dbText.query_all(sql)
    return result

#insert color

def insert_color(name):

    sql = f""" insert into color (color_name) values('{name}')"""
    dbText.db_execute(sql)
    return True

# get shipping fee
def get_shipping_fee():
    sql = f"""select * from shipping_info_fee;"""
    result = dbText.query_all(sql)
    return result

def insert_shipping_fee(dest,code,price):

    sql = f""" insert into shipping_info_fee (ship_id,ship_mode,destination,price,code) values(1,1,'{dest}','{price}','{code}')"""
    dbText.db_execute(sql)
    return True

def delete_shipping_fee(fee_id):
    sql = f""" delete from shipping_info_fee where fee_id = '{fee_id}'"""
    dbText.db_execute(sql)
    return True

#------------------#
# order
#------------------

def get_order(order_sn):
    sql = f"""select o.*,u.user_id,u.username,u.role, p.pay_user,p.payform,p.paynumber from orders o left join users u on o.user_id = u.user_id left join payinfo p on o.order_sn = p.order_sn where o.order_sn = '{order_sn}';"""
    result = dbText.query_one(sql)
    return result


def get_order_info(order_sn):
    sql = f"""select o.*, p.pic_url from order_detail o join product_pic_info p on o.product_id = p.product_id where p.is_master= 0 and o.order_sn = '{order_sn}';"""
    result = dbText.query_all(sql)
    return result

# update order status
def update_order_status(order_sn,status):
    sql = f"""update orders set order_status = '{status}' where order_sn = '{order_sn}'"""
    print(sql)
    dbText.db_execute(sql)
    return True

# get order list 
def get_order_list(order_id,customer_name,status):
    query = f"""
    SELECT * FROM orders WHERE order_sn LIKE CONCAT('%', '{order_id}', '%')  and invoice_title LIKE CONCAT('%', '{customer_name}', '%')
    """
    
    if status != "-1":
        query += f" AND order_status = {status};"
    result = dbText.query_all(query)
    
    return result

# get shipping fee
def get_shipping_fee():
    sql = f"""select * from shipping_info_fee;"""
    result = dbText.query_all(sql)
    return result





#------------------#
# promotion
#------------------

def get_prom_list():
    sql = """select * from promotion;"""
    result = dbText.query_all(sql)
    return result

def delete_prom(p_id):
    sql = f"""delete from promotion where promotion_id = '{p_id}'"""
    dbText.db_execute(sql)
    return True

def insert_prom(name, type, start_time, end_time, value):
    sql = f"""SELECT COUNT(*)
    FROM promotion
    WHERE promotion_type = '{type}'
      AND (
        (start_time <= '{start_time}' AND end_time >= '{start_time}')
        OR (start_time <= '{end_time}' AND end_time >= '{end_time}')
        OR (start_time >= '{start_time}' AND end_time <= '{end_time}')
      );"""
    
    existing_count = dbText.query_one(sql)['COUNT(*)']
   
    if existing_count ==0:
        sql = f"""INSERT INTO promotion (promotion_name, promotion_type, start_time, end_time, value)
        VALUES ('{name}', '{type}', '{start_time}', '{end_time}', '{value}');"""
        
        dbText.db_execute(sql)
        return True
    else:
        return False

def get_discount():
    sql = """select * from promotion where promotion_type = 1"""
    result = dbText.query_all(sql)
    return result

# update promotion price on product

# def update_discount_cate(promo_id,product_id,value):
#     args = [promo_id,product_id,value,None]
#     print(args)
#     dbText.call_proc('InsertPromotionProduct',args)
#     return True


def update_discount_cate(promo_id, product_id, value):
    sql = f"""SELECT p.price 
    FROM product_info p
    WHERE p.product_id = '{product_id}';"""
    existing_price = dbText.query_one(sql)['price']

    check_sql = f"""SELECT COUNT(*)
    FROM promotion_product
    WHERE promotion_id = '{promo_id}' AND product_id = '{product_id}';"""
    existing_prod = dbText.query_one(check_sql)['COUNT(*)']
    
    discount_amount = existing_price * Decimal(value)  # 将 value 转换为 Decimal 类型并计算折扣金额

    if existing_prod > 0:
        s_sql = f"""UPDATE promotion_product 
        SET discount_amount = {discount_amount} 
        WHERE promotion_id = '{promo_id}' AND product_id = '{product_id}';"""
    else:
        s_sql = f"""INSERT INTO promotion_product (promotion_id, product_id, discount_amount)
        VALUES ('{promo_id}', '{product_id}', {discount_amount});"""
    
    dbText.db_execute(s_sql)
    return True



#------------------#
# News
#------------------#
    
def insert_news(title, content, author):
    sql = f"""
    INSERT INTO news (title, content, author, date)
    VALUES ('{title}', '{content}', '{author}', CURRENT_TIMESTAMP);
    """
    dbText.db_execute(sql)
    return True

def get_news_list():
    sql = f"""SELECT * FROM news"""
    result = dbText.query_all(sql)
    return result

def delete_news(news_id):
    sql = f"""DELETE FROM news WHERE news_id = {news_id}"""
    dbText.db_execute(sql)
    return True

def edit_news(news_id, title, content):
    sql = f"""UPDATE news SET title = '{title}', content = '{content}' WHERE news_id = {news_id}"""
    dbText.db_execute(sql)
    return True

def get_news_by_id(news_id):
    sql = f"""SELECT * FROM news WHERE news_id = {news_id}"""
    result = dbText.query_one(sql)
    return result

def update_publish_status(news_id):
    sql = f"""UPDATE news SET publish_status = 1 WHERE news_id = {news_id}"""
    dbText.db_execute(sql)


#------------------#
# chat
#------------------#

def get_waiting_customer():
    sql = f"""
    SELECT cs.session_id, cs.status,u.username FROM chat_sessions cs JOIN users u ON cs.customer_id = u.user_id order by cs.session_id desc;
    """
    result = dbText.query_all(sql)
    return result


def join_chat(session_id,user_id):
    sql = f"""UPDATE chat_sessions SET employee_id = '{user_id}', status = 'active' WHERE session_id = '{session_id}';"""
    dbText.db_execute(sql)
    return True

def insert_chat(session_id,sender_id,message):
    sql = f"""INSERT INTO chat (session_id, sender_id, chat) VALUES ('{session_id}', '{sender_id}', '{message}');"""
    dbText.db_execute(sql)
    return True

def chat_history(session_id):
    sql = f"""select c.*,u.username from chat c JOIN users u ON c.sender_id = u.user_id  where c.session_id = '{session_id}' order by chat_id asc ;"""
    result = dbText.query_all(sql)
    return result

def close_chat(session_id):
    sql = f"""UPDATE chat_sessions SET status = 'close' WHERE session_id = '{session_id}';"""
    dbText.db_execute(sql)
    return True

def get_scheduled_list():
    sql = """select * from monthly_tasks order by id desc"""
    result = dbText.query_all(sql)
    return result



#insert system message
def insert_system_message(receive_id,content,subject,user_id):
    sql = f"""INSERT INTO messagebox (subject, recipient_user_id, sender_user_id,content,status) VALUES ('{subject}', '{receive_id}', '{user_id}', '{content}',0);"""
    dbText.db_execute(sql)
    return True


# get message list
def get_message_list(user_id):
    sql = f"""select s.*,u.username from messagebox s join users u on s.recipient_user_id = u.user_id where s.sender_user_id = '{user_id}' """
    result =  dbText.query_all(sql)
    return result

# get message list
def get_message(id):
    sql = f"""select * from messagebox where id = '{id}' """
    result = dbText.query_one(sql)
    return result

def delete_message(id):
    sql = f"""delete from messagebox where id = '{id}' """
    dbText.db_execute(sql)
    return True

#------------------
# report
#------------------

def get_revenue():
    sql = "select sum(district_money) as revenue from orders"
    result = dbText.query_one(sql)
    return result['revenue']
def get_monthly_revenue(date):
    sql = f"""select sum(district_money) as monthly_revenue from orders where create_time LIKE CONCAT('%', '{date}', '%')"""
    result = dbText.query_one(sql)
    return result['monthly_revenue']
def get_products():
    sql = f"""select count(*) as products from product_info"""
    result = dbText.query_one(sql)
    return result['products']

def get_top_products(date):
    sql = sql = f"""
    SELECT 
        product_id,
        product_name,
        SUM(product_cnt) AS total
    FROM order_detail
    WHERE modified_time LIKE CONCAT('%', '{date}', '%')
    GROUP BY product_id,product_name order by total desc limit 5"""
    result = dbText.query_all(sql)
    return result

def get_orders():
    sql = "select count(*) as orders from orders where order_status = 0;"
    result = dbText.query_one(sql)
    return result['orders']
def get_orders_list():
    sql = "select * from orders order by order_id desc limit 20;"
    result = dbText.query_all(sql)
    return result

def get_new_customers(role):
    sql = f"""select * from users where role= '{role}' limit 3;"""
    result = dbText.query_all(sql)
    return result


def get_monthly_sales(year):
    sql = f"""SELECT MONTH(create_time) AS month, SUM(district_money) AS total
        FROM orders
        WHERE YEAR(create_time) = '{year}'
        GROUP BY month"""
    result =  dbText.query_all(sql)
    return result

def get_user_data(year):
    sql = f"""SELECT MONTH(createtime) AS month, COUNT(user_id) AS total
        FROM users
        WHERE YEAR(createtime) = '{year}'
        GROUP BY month"""
    result =  dbText.query_all(sql)
    return result

def get_product_data(year):
    sql = f"""SELECT MONTH(modified_time) AS month, SUM(product_cnt) AS total
        FROM order_detail
        WHERE YEAR(modified_time) = '{year}'
        GROUP BY month;
    """
    result =  dbText.query_all(sql)
    return result

def get_area_data(area):
    
    sql = f"""SELECT COALESCE(SUM(district_money), 0) AS total
        FROM orders
        WHERE  country = '{area}'
        GROUP BY country
        UNION ALL
        SELECT 0
        LIMIT 1;"""
    result =  dbText.query_one(sql)
    return result



# get refund applications

def get_refund_application_by_id(application_id):
    sql = f"SELECT u.username,u.role,app.*,p.product_name  FROM refund_applications app join users u on app.user_id = u.user_id join product_info p on app.product_id = p.product_id WHERE app.id= '{application_id}'"
    result = dbText.query_one(sql)
    return result

def get_refund_list():
    sql = """SELECT u.username,app.*, p.product_name FROM refund_applications app join users u on app.user_id = u.user_id join product_info p on app.product_id = p.product_id order by app.id desc"""
    result = dbText.query_all(sql)
    return result


def update_balance(user_id,amount,type):
    if type == 3 :
        check = get_customer(user_id, 3)['user_balance']
        amount += int(check)
    
        sql = f"""update u_customers set user_balance = '{amount}' where user_id = '{user_id}'"""
        dbText.db_execute(sql)
    elif  type ==4:
       
        check = get_customer(user_id, 4)['credit_used']
        check = check - amount
    
        sql = f"""update u_customers set user_balance = '{amount}' where user_id = '{user_id}'"""
        dbText.db_execute(sql)
    return True
def update_refund(id,status,comment,reviewer_id):
    sql =f"""update refund_applications set status = '{status}', comment = '{comment}',reviewer_id = '{reviewer_id}' where id = '{id}'"""
    dbText.db_execute(sql)
    return True
        
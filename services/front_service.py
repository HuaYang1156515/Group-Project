
from common  import hashing
from services import dbText


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

def query_items(page,per_page,item_sql):
    
    # 计算起始位置
   
    offset = (page - 1) * per_page
    # 执行分页查询
    #connection.execute("SELECT * FROM items LIMIT %s, %s", (offset, per_page))
    item_sql = item_sql + f" limit {offset},{per_page}"
    
    items = dbText.query_all(item_sql )

    return items

# get general info

def get_customer_info(user_id):
    sql = f"""SELECT * FROM u_customers WHERE user_id = '{user_id}'"""
    
    result = dbText.query_one(sql)
    return result
# get business info

def get_b_customer_info(user_id):
    sql = f"""SELECT * FROM u_business_customers WHERE user_id = '{user_id}'"""
    
    result = dbText.query_one(sql)
    return result

# get user addr
def get_customer_addr(user_id):
    sql = f"""SELECT * FROM order_customer_addr WHERE user_id = '{user_id}'"""
    
    result = dbText.query_all(sql)
    return result

# get user addr
def get_customer_addr_id(addr_id):
    sql = f"""SELECT * FROM order_customer_addr WHERE id = '{addr_id}'"""
    
    result = dbText.query_one(sql)
    return result


# delete user addr
def delete_customer_addr_id(addr_id):
    sql = f"""delete FROM order_customer_addr WHERE id = '{addr_id}'"""
    
    result = dbText.db_execute(sql)
    return result

# get get_order_list

def get_order_list(user_id,order_id,product_name):
    sql = f"""
    SELECT o.*, d.product_name FROM orders o join order_detail d on o.order_sn = d.order_sn WHERE o.order_sn LIKE CONCAT('%', '{order_id}', '%') AND d.product_name LIKE CONCAT('%', '{product_name}', '%') and o.user_id = '{user_id}'
    """
    result = dbText.query_all(sql)
    return result

# get ship fee
def  get_shipping_cost(country):
   # sql = f"""SELECT price FROM shipping_info_fee WHERE ship_id = '{selectid}' and destination like CONCAT('%', '{country}', '%')"""
    sql = f"""SELECT price FROM shipping_info_fee WHERE destination like CONCAT('%', '{country}', '%')"""
    result = dbText.query_one(sql)
    return result

# edit customer info 
def update_customer_info(user_id, first_name, last_name, phone_number,  gender):
    sql = f"""
    UPDATE u_customers SET  first_name = '{first_name}', last_name = '{last_name}', phone_number = '{phone_number}', gender = '{gender}' WHERE user_id = '{user_id}'
    """
    dbText.db_execute(sql)
    return True

# edit business customer info 
def update_b_customer_info(user_id, company_name, contact_name, phone_number):
    sql = f"""
    UPDATE u_business_customers SET  company_name = '{company_name}', contact_name = '{contact_name}', phone_number = '{phone_number}' WHERE user_id = '{user_id}'
    """
    dbText.db_execute(sql)
    return True

# edit password

def update_pwd(new_pwd,user_id):
    sql = (f"""update users set password = '{new_pwd}' where user_id = '{user_id}'""")
    return  dbText.db_execute(sql)



# get size stock of different color 

def get_color_sizes(color,product_id):
    sql = f"""SELECT DISTINCT size FROM warehouse_product WHERE color = '{color}' and product_id = {product_id}"""
    result = dbText.query_all(sql)
    return result


# insert customer address
def insert_customer_addr(user_id,zip,street,city,region,country,default):
    sql = f"""insert into order_customer_addr (user_id,zip,street,city,region,country,is_default) values ('{user_id}','{zip}','{street}','{city}','{region}','{country}','{default}')"""
   
    return  dbText.db_execute(sql)

# insert customer address
def update_customer_addr(id,zip,street,city,region,country):
    sql = f"""update order_customer_addr set zip = '{zip}',street = '{street}',city = '{city}',region = '{region}',country= '{country}' where id = '{id}'"""
   
    return  dbText.db_execute(sql)

#------------------------#
#   index   #
#------------------------#

 # first product area

def get_tab_list(sql):
    result = dbText.query_all(sql)
    return result


#------------------#
# order
#------------------

def get_order(order_sn):
    sql = f"""select o.*,u.user_id,u.username, p.pay_user,p.payform,p.paynumber from orders o left join users u on o.user_id = u.user_id left join payinfo p on o.order_sn = p.order_sn where o.order_sn = '{order_sn}';"""
    result = dbText.query_one(sql)
    return result


def get_order_info(order_sn):
    sql = f"""select o.*, p.pic_url from order_detail o join product_pic_info p on o.product_id = p.product_id where p.is_master= 0 and o.order_sn = '{order_sn}';"""
    result = dbText.query_all(sql)
    return result

#------------------------#
#   product   #
#------------------------#


# get color list
def get_color():

    sql = """   select 0,'color' as color_name
    union
    select * from color;"""
    result = dbText.query_all(sql)
    return result


# get product pics list
def get_product_pics(product_id):
    sql = f"""select * from product_pic_info where pic_status = 1 and product_id = {product_id}"""
    result = dbText.query_all(sql)
    return result

# get product_info

def get_product_info(product_id):
    sql = f""" select p.*, c.pic_url , COALESCE(pm.discount_amount, 0) as discount, (select brand_name from brand_info where brand_id = p.brand_id) as brand, 
 (select name from category where cate_id = p.one_category_id) as one_category,  (select name from category where cate_id = p.two_category_id) as two_category
 from product_info p left join product_pic_info c on p.product_id = c.product_id 
left join promotion_product pm on pm.product_id = p.product_id
 where c.is_master = 0 and p.product_id = {product_id};"""
    result = dbText.query_one(sql)
    return result

# get product comment

def get_comment(product_id):
    sql = f"""SELECT p.*, u.username FROM product_comment p join users u on p.user_id=u.user_id where p.product_id='{product_id}'"""
    result = dbText.query_all(sql)
    return result


# get product rate

def get_rate(product_id):
    sql = f"""SELECT product_id,  COALESCE(AVG(rate),0) AS a_rate,  COALESCE(COUNT(rate),0) AS count FROM product_comment WHERE product_id ='{product_id}'"""
    result = dbText.query_one(sql)
    return result

# get product stock
def get_stock(color,product_id):
    sql = f"""
    SELECT sizes.size,
       COALESCE(wp.current_cnt, 0) AS current_cnt
FROM (
    SELECT 's' AS size
    UNION ALL
    SELECT 'm'
    UNION ALL
    SELECT 'l'
    UNION ALL
    SELECT 'xl'
    UNION ALL
    SELECT 'xxl'
    UNION ALL
    SELECT 'xxxl'
) AS sizes
LEFT JOIN warehouse_product wp
    ON wp.size = sizes.size
    AND wp.color = '{color}'
    AND wp.product_id = {product_id};"""
    result = dbText.query_all(sql)
    return result


# get product size stock
def get_size_stock(color,size,product_id):
    sql = f"""SELECT COALESCE(current_cnt, 0) AS cnt
FROM warehouse_product  where color = '{color}' and product_id = {product_id} and size = '{size}';"""
   
    result = dbText.query_one(sql)
    return result


#insert shop cart
def insert_cart(user_id, product_id, qtn, price, discount,color,size):
    sql = f"""
    INSERT INTO order_cart 
    (user_id, product_id, product_amount, price, discount,color,size) 
    VALUES 
    ({user_id}, {product_id}, {qtn}, {price}, {discount},'{color}','{size}')
"""
    return  dbText.db_execute(sql)

# get cart list
def get_cart_list(user_id,type):
    # 0 : product not selected
    if type == 0:
        sql = f"""SELECT o.*, p.product_name,pic.pic_url from order_cart o join product_info p on o.product_id = p.product_id join product_pic_info pic on p.product_id = pic.product_id where pic.is_master = 0 and o.user_id = {user_id} and o.if_paid = 1;"""
    else:
        sql = f"""SELECT o.*, p.product_name,pic.pic_url from order_cart o join product_info p on o.product_id = p.product_id join product_pic_info pic on p.product_id = pic.product_id where o.selected = 1 and pic.is_master = 0 and o.user_id = {user_id} and o.if_paid = 1;"""    
    result = dbText.query_all(sql)
    return result

# get cart list
def get_user_cart_list(user_id,product_id,color,size):
    # 0 : product not selected
   
    sql = f"""SELECT o.*, p.product_name,pic.pic_url from order_cart o join product_info p on o.product_id = p.product_id join product_pic_info pic on p.product_id = pic.product_id where o.color= '{color}' and o.size='{size}' and o.product_id ='{product_id}' = pic.is_master = 0 and o.user_id = {user_id} and o.if_paid = 1;"""
    result = dbText.query_one(sql)
    return result

# delete cart
def delete_cart(cart_id,user_id):
    if cart_id == 0:
        sql =f"""delete from order_cart where user_id = '{user_id}'"""
    else:
        sql =f"""delete from order_cart where cart_id = '{cart_id}' and user_id = '{user_id}'"""
    return  dbText.db_execute(sql)

# update cart
def update_cart(cart_id,qtn):
    sql =f"""update order_cart set product_amount = {qtn} where cart_id = '{cart_id}'"""
    return  dbText.db_execute(sql)
# update cart selected

def update_select(cart_id,status):
    sql =f"""update order_cart set selected = {status} where cart_id = '{cart_id}'"""
    return  dbText.db_execute(sql)

# get customer info

def get_customer_bill_info(user_id):
    sql = f"""SELECT * from order_customer_addr WHERE user_id = {user_id};"""
    result = dbText.query_all(sql)
    return result

# get shipping info

def get_ship_info():
    sql = f"""select * from shipping_info"""
    result = dbText.query_all(sql)
    return result

def get_ship_infobyId(id):
    sql = f"""select * from shipping_info where ship_id = '{id}'"""
    result = dbText.query_one(sql)
    return result


# insert order info

def insert_order(order_sn, user_id, shipping_user, zip, street, city, region, country, payment_method, order_money, gst ,district_money, shipping_money, payment_money, shipping_comp_name, shipping_sn, order_point, invoice_title):
    sql = f"""INSERT INTO orders 
    (order_sn, user_id, shipping_user, zip, street, city, region, country, payment_method, order_money, gst, district_money, shipping_money, payment_money, shipping_comp_name, shipping_sn, order_point, invoice_title) 
    VALUES 
    ('{order_sn}', '{user_id}', '{shipping_user}', '{zip}', '{street}', '{city}', '{region}', '{country}', '{payment_method}', '{order_money}','{gst}', '{district_money}', '{shipping_money}', '{payment_money}', '{shipping_comp_name}', '{shipping_sn}', '{order_point}', '{invoice_title}')"""
    dbText.db_execute(sql)
    
    return  True

# insert order detail
def insert_order_detail(order_sn, product_id, product_name, product_cnt, product_price, order_cost, discount, color,size):
    sql = f"""INSERT INTO order_detail 
    (order_sn,product_id, product_name, product_cnt, product_price, order_cost, order_discount, color,size) 
    VALUES 
    ('{order_sn}',  '{product_id}', '{product_name}', '{product_cnt}', '{product_price}', '{order_cost}', '{discount}', '{color}', '{size}')"""
    return  dbText.db_execute(sql)

# update cart status
def update_cart_status(cart_id):
    sql =f"""update order_cart set if_paid = 0 where cart_id = {cart_id}"""
    return  dbText.db_execute(sql)

def update_stock(product_id, product_amount,color,size):
    
    cnt = get_size_stock(color,size,product_id)['cnt']
   
 
    sql = f"""update warehouse_product set current_cnt = '{cnt - product_amount}' where color = '{color}' and product_id = '{product_id}' and size = '{size}'"""
    dbText.db_execute(sql)
    return  True
# check stock
def check_stock(cart_id):
    sql = f"""select * from order_cart where cart_id = '{cart_id}'"""
    result = dbText.query_one(sql)
    cnt = get_size_stock(result['color'],result['size'],result['product_id'])['cnt']
    return cnt

# view_order details
def view_order(order_sn):
    sql = f"""SELECT 
    o.*,
    od.order_status,
    p.pic_url,
    r.status as refund_status,
    COALESCE(
        (SELECT COUNT(*)
         FROM product_comment pm
         WHERE pm.product_id = o.product_id and pm.order_sn = o.order_sn
           AND pm.user_id = (SELECT user_id FROM orders WHERE order_sn = o.order_sn)
        ), 0
    ) AS comment_count
FROM 
    order_detail o 
JOIN 
    product_pic_info p ON o.product_id = p.product_id 
JOIN 
    orders od ON od.order_sn = o.order_sn 
left join refund_applications r on r.order_sn = o.order_sn and r.product_id=o.product_id
WHERE 
    p.is_master = 0 
    AND o.order_sn = '{order_sn}'"""
    result = dbText.query_all(sql)
    return result


# view refund order details
# def get_refund_list(order_sn):
#     sql = f"""
# SELECT 
#     o.*,
#     od.order_status,
#     p.pic_url,
#     COALESCE(
#         (SELECT COUNT(*)
#          FROM product_comment pm
#          WHERE pm.product_id = o.product_id and pm.order_sn = o.order_sn
#            AND pm.user_id = (SELECT user_id FROM orders WHERE order_sn = o.order_sn)
#         ), 0
#     ) AS comment_count
# FROM 
#     order_detail o 
# JOIN 
#     product_pic_info p ON o.product_id = p.product_id 
# JOIN 
#     orders od ON od.order_sn = o.order_sn 
# WHERE 
#     p.is_master = 0 
#     AND o.order_sn = '{order_sn}' and NOT EXISTS (
#         SELECT 1 
#         FROM refund_applications ra 
#         WHERE ra.order_sn = o.order_sn 
#           AND ra.product_id = o.product_id
#     )"""
#     result = dbText.query_all(sql)
#     return result
def get_refund_list(user_id):
    sql = f"""SELECT u.username,app.*, p.product_name FROM refund_applications app join users u on app.user_id = u.user_id join product_info p on app.product_id = p.product_id where app.user_id = '{user_id}' order by app.id desc"""
    result = dbText.query_all(sql)
    return result


# get categories
def get_categories():

    sql = """
            SELECT cate_id,name
            FROM category where category_level = 1;"""
    result = dbText.query_all(sql)
    return result

# get second categories
def get_t_categories(cate_id):

    sql = f"""
            SELECT cate_id,name
            FROM category where parentid= '{cate_id}' and category_level = 2;"""
    result = dbText.query_all(sql)
    return result

#get special oder

def get_user_balance(order_sn):
    sql = f"""SELECT o.*, 
       CASE 
           WHEN u.role = 3 THEN (SELECT c.user_balance FROM u_customers c WHERE c.user_id = u.user_id) 
           WHEN u.role = 4 THEN (SELECT b.credit_limited FROM u_business_customers b WHERE b.user_id = u.user_id) 
           ELSE NULL 
       END AS balance
FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE o.order_sn = '{order_sn}';"""
    result = dbText.query_one(sql)
    return result

#balance pay

def balance_pay(order_sn,user_id,pay_user,payform,district_money):
    sql = f"""insert into payinfo (order_sn,user_id,pay_user,payform,amount) values ('{order_sn}','{user_id}','{pay_user}','{payform}','{district_money}')"""
    return  dbText.db_execute(sql)

def credit_pay(order_sn,user_id,pay_user,payform,paynumber,district_money):
    sql = f"""insert into payinfo (order_sn,user_id,pay_user,payform,paynumber,amount) values ('{order_sn}','{user_id}','{pay_user}','{payform}','{paynumber}','{district_money}')"""
    return  dbText.db_execute(sql)

def update_balance(userid,money,type):

    if type == 3:
        c_sql = f"""select * from u_customers where user_id ='{userid}'"""
        result = dbText.query_one(c_sql)
        n_balance = float(result['user_balance']) - float(money)
        sql = f"""update u_customers set user_balance= '{n_balance}' where user_id ='{userid}' ;"""
        return  dbText.db_execute(sql)

    elif type == 4:
        c_sql = f"""select * from u_business_customers where user_id ='{userid}'"""
        result = dbText.query_one(c_sql)
        n_credit_limited = result['credit_limited'] - money
        sql = f"""update u_customers set credit_limited= '{n_credit_limited}' where user_id ='{userid}';"""
        return  dbText.db_execute(sql)


# update order status

def update_order_status(order_status,type,order_sn):
    sql = f"""update orders set order_status = '{order_status}' , payment_method= '{type}' where order_sn = '{order_sn}';"""

    return  dbText.db_execute(sql)






#----------------------
# shippping
#-----------------------

# get shipping fee
def get_shipping_fee():
    sql = f"""select * from shipping_info_fee;"""
    result = dbText.query_all(sql)
    return result



#----------------------
# business
#-----------------------

def  get_app_list(user_id):
    sql = f"""select * from application where user_id = '{user_id}' """
    result = dbText.query_all(sql)
    return result

#insert cooperate client application
def insert_application(user_id,app_name, app_content):
    sql = f"""
    INSERT INTO application (user_id,app_name, app_details)
    VALUES ('{user_id}','{app_name}', '{app_content}');
    """
    dbText.db_execute(sql)
    return True  # 可以根据需要返回其他信息或错误处理


#------------------#
# News
#------------------#

def get_news():
    sql = f"""SELECT title,content,date FROM news where publish_status = 1"""
    result = dbText.query_all(sql)
    return result



#-------------
#  comment
#-------------

def insert_comment(product_id,user_id,conmment,rate):
    sql = f"""insert into product_comment (product_id,user_id,content,rate) value('{product_id}','{user_id}','{conmment}','{rate}')"""
    dbText.db_execute(sql)
    return True 



# get message list
def get_message_list(user_id):
    sql = f"""select s.*,u.username from messagebox s join users u on s.sender_user_id = u.user_id where s.recipient_user_id = '{user_id}' """
    result =  dbText.query_all(sql)
    return result

# get message list
def get_message(id):
    sql = f"""select * from messagebox where id = '{id}' """
    result = dbText.query_one(sql)
    return result


# get message list
def update_message(id):
    sql = f"""update messagebox set status = 1 where id = '{id}' """
    dbText.db_execute(sql)
    return True 


def get_order_product(order_sn,product_id,color,size):
    sql = f"""select * from order_detail where order_sn = '{order_sn}' and product_id = '{product_id}' and color = '{color}' and size = '{size}'"""
   
    result = dbText.query_one(sql)
   
    return result


def insert_refund_app(user_id,order_sn,product_id,price,color,size,qtn,refund_way,reason):
    sql = f"""insert into refund_applications (user_id,order_sn,product_id,qtn,product_price,size,color,status,refund_way,reason) values('{user_id}','{order_sn}','{product_id}','{qtn}','{price}','{size}','{color}',0,'{refund_way}','{reason}')"""
    dbText.db_execute(sql)
    return True 


def get_promotion():
    sql = f"""select * from promotion where promotion_type = 5;"""
    result = dbText.query_one(sql)
   
    return result
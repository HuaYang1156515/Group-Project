from flask import Blueprint, render_template, redirect, url_for, flash,request,abort,jsonify,session
from flask_login import login_user,current_user,login_required,logout_user
from common.validation import role_required
from common import hashing,BuyXGetY
from config import setting,send_message
from services import front_service,back_service
import re
from datetime import datetime
import pytz


frontend_page = Blueprint('frontend', __name__)



def paginate_results(total_sql,sql, page, per_page):
    total_items = front_service.query_total_items(total_sql)
    items = front_service.query_items(page, per_page, sql)
    pagination = front_service.paginate(page, per_page, total_items)
    return items, pagination

# customer login
@login_required
@frontend_page.route("/")
def dashboard():
    # first product area
    #tab one (Featured)
    tab_one_sql = """select p.*, c.pic_url , brand_info.brand_name, (p.price - COALESCE(pm.discount_amount, 0)) as discount from product_info p left join product_pic_info c on p.product_id = c.product_id 
left join promotion_product pm on pm.product_id = p.product_id left join brand_info on p.brand_id = brand_info.brand_id
 where c.is_master = 0 and p.publish_status = 1 and p.feature is not null order by p.modified_time desc limit 8;"""
    tab_one_list = front_service.get_tab_list(tab_one_sql)
  
    
    return render_template('frontend/index.html', tab_one_list= tab_one_list)

# search 

@frontend_page.route("/search",methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        text = request.form["search_text"]
        categories = front_service.get_categories()
        
        
        total = f"""SELECT 
        count(*)
    FROM 
        product_info p 
    LEFT JOIN 
        product_pic_info c ON p.product_id = c.product_id AND c.is_master = 0
    LEFT JOIN 
        promotion_product pm ON pm.product_id = p.product_id
    WHERE p.publish_status = 1 and p.product_name  LIKE '%{text}%'
    ORDER BY 
        p.modified_time;
    """
        category_sql = f"""SELECT 
        p.*, 
        c.pic_url, 
        (p.price - COALESCE(pm.discount_amount, 0)) AS discount 
    FROM 
        product_info p 
    LEFT JOIN 
        product_pic_info c ON p.product_id = c.product_id AND c.is_master = 0
    LEFT JOIN 
        promotion_product pm ON pm.product_id = p.product_id
    WHERE 
        p.publish_status = 1  and p.product_name  LIKE '%{text}%'
    ORDER BY 
        p.modified_time
    """
        per_page = 12
        page = request.args.get('page', 1, type=int)
        
        product_list, pagination = paginate_results(total ,category_sql, page, per_page)
        
    
        return render_template('frontend/categories/page_category.html',categories = categories,product_list = product_list, pagination=pagination)



# customer page account 
@login_required
@frontend_page.route("/page_account")
def page_account():
    
    if int(current_user.role) in (0,1,2):
        return redirect(url_for('backend.dashboard'))
    elif int(current_user.role) == 3:
        per_page = 20
        page = request.args.get('page', 1, type=int)
        page_log = request.args.get('page_log', 1, type=int)
        account = front_service.get_customer_info(current_user.user_id)
        address = front_service.get_customer_addr(current_user.user_id)
        #order_list = front_service.get_order_list(current_user.user_id)
        order_list , pagination = paginate_results(f"select count(*) from orders where user_id ='{current_user.user_id}'", f"SELECT * FROM orders where user_id ='{current_user.user_id}'", page, per_page)
        #items = back_service.get_point_log(current_user.user_id)
        items , pagination_log = paginate_results(f"select count(*) from customer_point_log where user_id ='{current_user.user_id}'", f"select u.username,log.* from customer_point_log log join users u on log.user_id = u.user_id where log.user_id = '{current_user.user_id}' order by log.create_time;", page_log, per_page)
        refund_list = front_service.get_refund_list(current_user.user_id)
        return render_template('frontend/page_account.html',account = account,address=address,order_list=order_list,pagination=pagination ,items= items,refund_list=refund_list,pagination_log=pagination_log)
    elif int(current_user.role) == 4:
        per_page = 20
        page = request.args.get('page', 1, type=int)
        page_log = request.args.get('page_log', 1, type=int)
        account = front_service.get_b_customer_info(current_user.user_id)
        address = front_service.get_customer_addr(current_user.user_id)
        order_list , pagination = paginate_results(f"select count(*) from orders where user_id ='{current_user.user_id}'", f"SELECT * FROM orders where user_id ='{current_user.user_id}'", page, per_page)
        app_list = front_service.get_app_list(current_user.user_id)
        items , pagination_log = paginate_results(f"select count(*) from customer_point_log where user_id ='{current_user.user_id}'", f"select u.username,log.* from customer_point_log log join users u on log.user_id = u.user_id where log.user_id = '{current_user.user_id}' order by log.create_time;", page_log, per_page)
        refund_list = front_service.get_refund_list(current_user.user_id)
        return render_template('frontend/business/page_account.html',account = account,address=address,order_list=order_list,app_list=app_list,pagination=pagination,items= items,refund_list=refund_list,pagination_log=pagination_log)
    


@login_required
@frontend_page.route("/track_order",methods=['GET', 'POST'])
def track_order():
    data = request.json
    order_id = data.get('order_id', '')
    product_name = data.get('product_name', '')
    orders = front_service.get_order_list(current_user.user_id,order_id,product_name)
    return jsonify({'orders': orders})


@frontend_page.route('/view_order_info/<int:order_sn>',methods=['GET', 'POST'])
@login_required
def view_order_info(order_sn):
    order = front_service.get_order(order_sn)
    order_info = front_service.get_order_info(order_sn)
    return render_template('frontend/order/page_order_detail.html',order = order,order_info = order_info)



# received order
@frontend_page.route('/order_received',methods=['GET', 'POST'])
@login_required
def order_received():
    data = request.json
    order_sn = data["order_sn"]
    print(order_sn)
    order = back_service.get_order(order_sn)
    if int(current_user.role) == 3:
       
        order_rate = back_service.get_order_rate()
        credit_points = order["district_money"] * order_rate
        back_service.update_g_account_credit(order["user_id"],credit_points,0)
        back_service.insert_customer_log(order["user_id"],0,order_sn,credit_points,f"Order Completed and System increase your credit_points {credit_points}")
        back_service.update_order_status(order_sn,setting.order_status[0])
        return "Success", 200
    elif int(current_user.role) == 4:
        back_service.update_order_status(order_sn,setting.order_status[0])
        return "Success", 200




# customer update account info
@login_required
@frontend_page.route("/update_customer_info",methods=['GET', 'POST'])
def update_customer_info():

    if request.method == 'POST':
        
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        gender = request.form["gender"]
        phone_number = request.form["phone_number"]
        front_service.update_customer_info(current_user.user_id, first_name, last_name, phone_number, gender)
        return redirect(url_for('frontend.page_account'))
    
    # customer update account info
@login_required
@frontend_page.route("/update_b_customer_info",methods=['GET', 'POST'])
def update_b_customer_info():

    if request.method == 'POST':
        
        company_name = request.form["comp_name"]
        contact_name = request.form["cont_name"]
      
        phone_number = request.form["phone_number"]
        front_service.update_b_customer_info(current_user.user_id, company_name, contact_name, phone_number)
        return redirect(url_for('frontend.page_account'))
    

# customer update pwd
@login_required
@frontend_page.route("/update_pwd",methods=['GET', 'POST'])
def update_pwd():
    # Check if "old pwd", "nwe pwd" and "confirm pwd" POST requests exist (user submitted form)
    if request.method == 'POST' and 'password' in request.form and 'npassword' in request.form and 'cpassword' in request.form:
        old_pwd = request.form['password']
        new_pwd = request.form['npassword']
        confirm_pwd = request.form['cpassword']
       
       
        hashed = hashing.hash_value(old_pwd)
        print(hashed)
        if hashed != current_user.password:
            flash("password is wrong")
        elif old_pwd == request.form['new_pwd']:
            flash("New password cannot be the same as old password.")
        elif new_pwd !=  confirm_pwd:
            flash("The passwords entered twice are inconsistent")
        elif not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", new_pwd):
            flash('password must contain only characters and numbers! Minimum length is 8','warning')
        else:
            hashed = hashing.hash_value(confirm_pwd)
            front_service.update_pwd(hashed,current_user.user_id)
            flash("your password updated successful! Please login again")
            logout_user()
            return redirect(url_for('login'))
    return redirect(url_for('frontend.page_account'))




# insert new address
@login_required
@frontend_page.route("/insert_customer_addr",methods=['GET', 'POST'])
def insert_customer_addr():
    if request.method == 'POST':
        zip = request.form['zip']
        street = request.form['street']
        city = request.form['city']
        region = request.form['region']
        country = request.form['country']
        front_service.insert_customer_addr(current_user.user_id,zip,street,city,region,country,0)
        flash("add new address successful")
        return redirect(url_for('frontend.page_account'))
    

# update user address
@login_required
@frontend_page.route("/update_customer_addr",methods=['GET', 'POST'])
def update_customer_addr():
    id = request.args.get('id')
    addr = front_service.get_customer_addr_id(id)
    if request.method == 'POST':
        addr_id = request.form['id']
        zip = request.form['zip']
        street = request.form['street']
        city = request.form['city']
        region = request.form['region']
        country = request.form['country']
        front_service.update_customer_addr(addr_id,zip,street,city,region,country)
        flash("add new address successful")
        return redirect(url_for('frontend.page_account'))
    return render_template('frontend/page_account_addr.html',addr = addr )

# update user address
@login_required
@frontend_page.route("/delete_customer_addr",methods=['GET', 'POST'])
def delete_customer_addr():
    id = request.args.get('id')
    front_service.delete_customer_addr_id(id)
   
    flash("delete new address successful")
    return redirect(url_for('frontend.page_account'))



#------------------------#
#   business info  #
#------------------------#

# cooperate client application submit_application
@frontend_page.route("/submit_application", methods=['GET', 'POST'])
@login_required
def submit_application():
    if request.method == 'POST':
        # 获取表单数据
    
        app_name = request.form['app_name']
       
        app_content = request.form['app_content']

        # 调用服务层函数插入申请信息
        front_service.insert_application(current_user.user_id,app_name, app_content)
        flash("Submit application successful")
        return redirect(url_for('frontend.page_account'))

    # Redirect to a different page instead of showing submit_application.html
    return redirect(url_for('frontend.page_account'))



    

#------------------------#
#   product info  #
#------------------------#

@frontend_page.route('/view_product/<int:product_id>',methods=['GET', 'POST'])
def view_product(product_id):
    color_list = front_service.get_color()
    pics = front_service.get_product_pics(product_id)
    product = front_service.get_product_info(product_id)
    comment = front_service.get_comment(product_id)
    rate = front_service.get_rate(product_id)
    if current_user.is_authenticated and current_user.role == 4:
        return render_template('frontend/business/page_product_full.html',color_list = color_list,pics = pics, product = product ,comment=comment, rate= rate)
    return render_template('frontend/product/page_product_full.html',color_list = color_list,pics = pics, product = product ,comment=comment, rate= rate)

# get special product stock
@frontend_page.route('/get_stock/',methods=['GET', 'POST'])
def get_stock():
    color = request.args.get('color')
    product_id = request.args.get('product_id')
    stock_list = front_service.get_stock(color,product_id)
    
    return jsonify(stock_list)

# get special product size stock
@frontend_page.route('/get_size_stock/',methods=['GET', 'POST'])
def get_size_stock():
    color = request.args.get('color')
    product_id = request.args.get('product_id')
    size = request.args.get('size')
    stock_list = front_service.get_size_stock(color,size,product_id)
    if stock_list:
        return jsonify(stock_list)
    else:
        return jsonify({"cnt": 0})


# insert shopcart
@login_required
@frontend_page.route('/insert_cart',methods=['GET', 'POST'])
def insert_cart():
    if request.method == 'POST':
        if not current_user.is_authenticated:  # 用户未登录
            # 保存原始的页面 URL 到会话中
            session['next_url'] = setting.url_add + request.form['product_id']
            return redirect(url_for('login'))  # 重定向到登录页面
        else:
            product_id = request.form['product_id']
            qtn = request.form['qtn']
            color = request.form['color']
            size = request.form['size'].split(':')[0]
            if color == 'color':
                flash("please choose color")   
            else:
                product = front_service.get_product_info(product_id)
                user_cart = front_service.get_user_cart_list(current_user.user_id,product_id,color,size)
                if user_cart:
                    front_service.update_cart(user_cart['cart_id'],int(qtn) + int(user_cart['product_amount'])) 
                else:
                    front_service.insert_cart(current_user.user_id, product_id, qtn, product['price'], product['discount'],color,size) 
            flash(f"add {product['product_name']} successful")
            return redirect(url_for('frontend.view_cart'))
    
# view shop cart
@login_required
@frontend_page.route('/view_cart',methods=['GET', 'POST'])
def view_cart():
    if current_user.is_authenticated:
        cart_list = front_service.get_cart_list(current_user.user_id,0)
    else:
        flash(f"please log in")
        return redirect(url_for('frontend.dashboard'))
    return render_template('frontend/product/page_shop_cart.html',cart_list = cart_list)


    
# remove shop cart
@login_required
@frontend_page.route('/delete_cart/<int:cart_id>',methods=['GET', 'POST'])
def delete_cart(cart_id):
    front_service.delete_cart(cart_id,current_user.user_id)
    return redirect(url_for('frontend.view_cart'))

# update_cart
@login_required
@frontend_page.route('/update_cart',methods=['GET', 'POST'])
def update_cart():
    if request.method == 'POST':
        cart_id_values = request.form.getlist('cart_id')
        qtn_values = request.form.getlist('qtn')
        for cart_id, qtn in zip(cart_id_values, qtn_values):
            front_service.update_cart(cart_id,qtn)
        
    return redirect(url_for('frontend.check_out'))

# update selected
@login_required
@frontend_page.route('/update_select',methods=['GET', 'POST'])
def update_select():
    if request.method == 'POST':
        data = request.json
        cart_id = data.get('cart_id')
        is_checked = data.get('is_checked')
        if is_checked:
            front_service.update_select(cart_id,1)
        else:
            front_service.update_select(cart_id,0)
    return jsonify({'message': 'Success'}), 200

# get_shipping_cost

@frontend_page.route('/get_shipping_cost',methods=['GET', 'POST'])
def get_shipping_cost():
    #selectid = request.args.get('selectid')
    addr = request.args.get('addr')
    
    if int(addr) == 0:
        return jsonify({"ship_cost": 0})
    else:
        user_addr = front_service.get_customer_addr_id(addr)
        ship_fee = front_service.get_shipping_cost(user_addr['country'])
        if ship_fee['price']:
            return jsonify({"ship_cost": ship_fee['price']})
        else:
            return jsonify({"ship_cost": 10})
    


# check out
@frontend_page.route('/check_out',methods=['GET', 'POST'])
def check_out():
    c_info = front_service.get_customer_info(current_user.user_id)
    c_addr_list = front_service.get_customer_bill_info(current_user.user_id)
    s_addr_list = front_service.get_ship_info()

 
    cart_list = front_service.get_cart_list(current_user.user_id,1)
    promotion = front_service.get_promotion()
    if promotion:
        x= int(promotion['value'])
       
    else:
        x = 3
       
    promotion_strategy = BuyXGetY.BuyXGetYFreeStrategy(x , y=1)
    promotion_price = BuyXGetY.calculate_promotion_discount(current_user.user_id, promotion_strategy)
   
    total_discount = 0
    for item in cart_list:
        total_discount += (item['price'] - item['discount']) * item['product_amount']
    
    return render_template('frontend/product/page_check_out.html',c_info =  c_info,c_addr_list=c_addr_list,cart_list=cart_list,total_discount = total_discount,s_addr_list=s_addr_list ,promotion_price = promotion_price)


# insert order
@frontend_page.route('/insert_order',methods=['GET', 'POST'])
def insert_order():
    if request.method == 'POST':
        # 定义新西兰的时区
        nz_timezone = pytz.timezone('Pacific/Auckland')

# 获取当前时间
        nz_time = datetime.now(nz_timezone)
        order_sn = nz_time.strftime('%Y%m%d%H%M%S')
       
        ship_id= 1
        addr = request.form['addr']
        if addr == "0":
            user_addr = {"zip":0,"street":"Pick Up","city":"","region":"","country":"New Zealand"}
        else:
            user_addr = front_service.get_customer_addr_id(addr)
        cart_list = front_service.get_cart_list(current_user.user_id,1)
        shipping_cost = request.form['i_ship_cost']
        discount = request.form['i_subtoal']
        ship_comp = front_service.get_ship_infobyId(ship_id)
        total = 0
        fname = request.form['fname']
        lname = request.form['lname']
        invoice_title = f"{fname} {lname}"
        promotion = front_service.get_promotion()
        if promotion:
            x= int(promotion['value'])
            
        else:
            x = 3
        
        promotion_strategy = BuyXGetY.BuyXGetYFreeStrategy(x, y=1)
        promotion_price = BuyXGetY.calculate_promotion_discount(current_user.user_id, promotion_strategy)
        for item in cart_list:
            total += (item['price'] - item['discount']) * item['product_amount']
        total = total - promotion_price
       
        front_service.insert_order(order_sn, current_user.user_id, ship_id, user_addr['zip'], user_addr['street'], user_addr['city'], user_addr['region'], user_addr['country'],0, total, 0, discount, shipping_cost, 0, ship_comp['ship_name'], order_sn, discount, invoice_title)
        
        for item in cart_list:
            cnt = front_service.get_size_stock(item['color'],item['size'],item['product_id'])['cnt']
            if int(cnt) < int(item['product_amount']):
                flash(f"{item['product_name']} out stock")
            else:
                front_service.update_stock(item['product_id'], item['product_amount'], item['color'],item['size'])
                front_service.insert_order_detail(order_sn, item['product_id'], item['product_name'], item['product_amount'], item['price'], int(item['price'] - item['discount']) * int(item['product_amount']), item['discount'], item['color'],item['size'])
                front_service.update_cart_status(item['cart_id'])
        flash("Order placed successfully")
        return redirect(url_for('frontend.view_order',order_sn = order_sn))

@frontend_page.route('/view_order/<int:order_sn>',methods=['GET', 'POST'])
def view_order(order_sn):
    order_list = front_service.view_order(order_sn)
    order = front_service.get_user_balance(order_sn)
    return render_template('frontend/product/page_order_pay.html',order_list = order_list, order = order)

@frontend_page.route('/balance_pay',methods=['GET', 'POST'])
def balance_pay():
    if request.method == 'POST':
        order_sn = request.form['order_sn']
        district_money = request.form['district_money']
        front_service.balance_pay(order_sn,current_user.user_id,current_user.username,1,district_money)
        front_service.update_balance(current_user.user_id,district_money,current_user.role)
        front_service.update_order_status(setting.order_status[2],2,order_sn)
        flash("payment successful")
        return redirect(url_for('frontend.page_account'))

@frontend_page.route('/credit_pay',methods=['GET', 'POST'])
def credit_pay():
    if request.method == 'POST':
        order_sn = request.form['order_sn']
        card_owner = request.form['card_owner']
        card_no = request.form['card_no']
        district_money = request.form['district_money']
        front_service.credit_pay(order_sn,current_user.user_id,card_owner,2,card_no,district_money)
        front_service.update_order_status(setting.order_status[2],1,order_sn)
        flash("payment successful")
        return redirect(url_for('frontend.page_account'))


# check_stock
@frontend_page.route('/check_stock',methods=['GET', 'POST'])
def check_stock():
    if request.method == 'POST':
        cart_id = request.form['cart_id']
        stock = front_service.check_stock(cart_id)
        return jsonify({'stock': stock})

#--------------------------#
# categories #
#--------------------------#

@frontend_page.route('/view_categories/<int:cate_id>/<int:t_cate_id>',methods=['GET', 'POST'])
def view_categories(cate_id,t_cate_id):
    categories = front_service.get_categories()
    
    session['cate_id'] = cate_id
    session['t_cate_id'] = t_cate_id
    total = f"""SELECT 
    count(*)
FROM 
    product_info p 
LEFT JOIN 
    product_pic_info c ON p.product_id = c.product_id AND c.is_master = 0
LEFT JOIN 
    promotion_product pm ON pm.product_id = p.product_id
WHERE 
    p.publish_status = 1 
    AND (
        CASE 
            WHEN '{cate_id}' = 0 AND '{t_cate_id}' = 0 THEN 0 = 0  -- 当 cate_id 和 t_cate_id 都为 0 时，查询全部
            WHEN '{t_cate_id}' != 0 THEN p.two_category_id = '{t_cate_id}'  -- 当 t_cate_id 不为 0 时，根据 t_cate_id 进行过滤
            ELSE p.one_category_id = '{cate_id}'  -- 否则根据 cate_id 进行过滤
        END
    )
   
ORDER BY 
    p.modified_time;
"""
    category_sql = f"""SELECT 
    p.*, 
    c.pic_url, 
    (p.price - COALESCE(pm.discount_amount, 0)) AS discount 
FROM 
    product_info p 
LEFT JOIN 
    product_pic_info c ON p.product_id = c.product_id AND c.is_master = 0
LEFT JOIN 
    promotion_product pm ON pm.product_id = p.product_id
WHERE 
    p.publish_status = 1 
    AND (
        CASE 
            WHEN '{cate_id}' = 0 AND '{t_cate_id}' = 0 THEN 0 = 0  -- 当 cate_id 和 t_cate_id 都为 0 时，查询全部
            WHEN '{t_cate_id}' != 0 THEN p.two_category_id = '{t_cate_id}'  -- 当 t_cate_id 不为 0 时，根据 t_cate_id 进行过滤
            ELSE p.one_category_id = '{cate_id}'  -- 否则根据 cate_id 进行过滤
        END
    )
ORDER BY 
    p.modified_time
"""
    per_page = 12
    page = request.args.get('page', 1, type=int)
    
    product_list, pagination = paginate_results(total ,category_sql, page, per_page)
    
  
    return render_template('frontend/categories/page_category.html',categories = categories,product_list = product_list, pagination=pagination)

@frontend_page.route('/get_t_categories', methods=['GET'])
def get_t_categories():
    cate_id = int(request.args.get('cate_id'))
    
    t_categories = front_service.get_t_categories(cate_id)
    return jsonify({'t_categories':t_categories})
#--------------------------#
# help #
#--------------------------#

@frontend_page.route('/shipping_fee')
def shipping_fee():
    fee_list = front_service.get_shipping_fee()
    return render_template('frontend/help/page_shipfee.html',fee_list= fee_list)

@frontend_page.route('/contact')
def contact():
    return render_template('frontend/help/page_contact.html')


#about page
@frontend_page.route("/page_about")
def page_about():
    return render_template('frontend/help/page_about.html')
   
#news page
@frontend_page.route("/page_news")
def page_news():
    news = front_service.get_news()
    return render_template('frontend/help/page_news.html', news=news)



# insert_comment

@frontend_page.route("/insert_comment",methods=['GET', 'POST'])
def insert_comment():
    data = request.get_json()
    product_id = data['product_id']
    rate =  data['rate']
    comment = data['comment']
        
    front_service.insert_comment(product_id,current_user.user_id,comment,int(rate))
    return "Success", 200



# system message

@frontend_page.route('/message_list/',methods=['GET', 'POST'])
def message_list():
    messages_list = front_service.get_message_list(current_user.user_id)
    return render_template('frontend/message/system_message.html',messages_list = messages_list)

@frontend_page.route('/get_system_message', methods=['GET', 'POST'])
def get_system_message():
    if request.method == 'POST':
        id = request.form.get("message_id")
        message = front_service.get_message(id)
        front_service.update_message(id)
        return jsonify(message), 200
    


@frontend_page.route('/apply_refund',methods=['GET', 'POST'])
def apply_refund():
    order_sn = request.args.get('order_sn')
    product_id = request.args.get('product_id')
    color= request.args.get('color')
    size = request.args.get('size')
    
    product_info  = front_service.get_order_product(order_sn,product_id,color,size)
   
    return render_template('frontend/product/page_order_refund.html',product_info = product_info)

@frontend_page.route('/insert_refund',methods=['GET', 'POST'])
def insert_refund():
   
    if request.method == 'POST':
        order_sn = request.form["order_sn"]
        product_id = request.form["product_id"]
        price = request.form["price"]
        
        color = request.form["color"]
        size = request.form["size"]
        qtn = request.form["return_qtn"]
        refund_way = request.form["refund_way"]
        reason = request.form["reason"]
        
             
        front_service.insert_refund_app(current_user.user_id,order_sn,product_id,price,color,size,qtn,refund_way,reason)
        
    flash("We received your refund application")
    return redirect(url_for('frontend.view_order',order_sn = order_sn))
from flask import Blueprint, render_template, redirect, url_for, flash,request,abort,jsonify,session
from flask_login import login_user,current_user,login_required,logout_user
from common.validation import role_required
from common import hashing,BuyXGetY
from config import setting,send_message
from services import front_service,back_service
import re
from datetime import datetime
import pytz


corporate_page = Blueprint('corporate', __name__)






@login_required
@corporate_page.route("/track_order",methods=['GET', 'POST'])
def track_order():
    data = request.json
    order_id = data.get('order_id', '')
    product_name = data.get('product_name', '')
    orders = front_service.get_order_list(current_user.user_id,order_id,product_name)
    return jsonify({'orders': orders})


@corporate_page.route('/view_order_info/<int:order_sn>',methods=['GET', 'POST'])
@login_required
def view_order_info(order_sn):
    order = front_service.get_order(order_sn)
    order_info = front_service.get_order_info(order_sn)
    return render_template('frontend/order/page_order_detail.html',order = order,order_info = order_info)



# received order
@corporate_page.route('/order_received',methods=['GET', 'POST'])
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




    


# get special product stock
@corporate_page.route('/get_stock/',methods=['GET', 'POST'])
def get_stock():
    color = request.args.get('color')
    product_id = request.args.get('product_id')
    stock_list = front_service.get_stock(color,product_id)
    
    return jsonify(stock_list)

# get special product size stock
@corporate_page.route('/get_size_stock/',methods=['GET', 'POST'])
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
@corporate_page.route('/insert_cart',methods=['GET', 'POST'])
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
                    front_service.insert_cart(current_user.user_id, product_id, qtn, product['price'], 0,color,size) 
            flash(f"add {product['product_name']} successful")
            return redirect(url_for('corporate.view_cart'))
    
# view shop cart
@login_required
@corporate_page.route('/view_cart',methods=['GET', 'POST'])
def view_cart():
    if current_user.is_authenticated:
        cart_list = front_service.get_cart_list(current_user.user_id,0)
    else:
        flash(f"please log in")
        return redirect(url_for('frontend.dashboard'))
    return render_template('frontend/business/page_shop_cart.html',cart_list = cart_list)


    
# remove shop cart
@login_required
@corporate_page.route('/delete_cart/<int:cart_id>',methods=['GET', 'POST'])
def delete_cart(cart_id):
    front_service.delete_cart(cart_id,current_user.user_id)
    return redirect(url_for('corporate.view_cart'))

# update_cart
@login_required
@corporate_page.route('/update_cart',methods=['GET', 'POST'])
def update_cart():
    if request.method == 'POST':
        cart_id_values = request.form.getlist('cart_id')
        qtn_values = request.form.getlist('qtn')
        for cart_id, qtn in zip(cart_id_values, qtn_values):
            front_service.update_cart(cart_id,qtn)
        
    return redirect(url_for('corporate.check_out'))

# update selected
@login_required
@corporate_page.route('/update_select',methods=['GET', 'POST'])
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

@corporate_page.route('/get_shipping_cost',methods=['GET', 'POST'])
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
@corporate_page.route('/check_out',methods=['GET', 'POST'])
def check_out():
    c_info = front_service.get_customer_info(current_user.user_id)
    c_addr_list = front_service.get_customer_bill_info(current_user.user_id)
    s_addr_list = front_service.get_ship_info()

 
    cart_list = front_service.get_cart_list(current_user.user_id,1)
    
   
    total_discount = 0
    for item in cart_list:
        total_discount += item['price'] * item['product_amount']
    
    return render_template('frontend/business/page_check_out.html',c_info =  c_info,c_addr_list=c_addr_list,cart_list=cart_list,total_discount =total_discount,s_addr_list=s_addr_list)


# insert order
@corporate_page.route('/insert_order',methods=['GET', 'POST'])
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
        promotion_strategy = BuyXGetY.BuyXGetYFreeStrategy(x=3, y=1)
        promotion_price = BuyXGetY.calculate_promotion_discount(current_user.user_id, promotion_strategy)
        for item in cart_list:
            total += item['price']  * item['product_amount']
        total = total - promotion_price
      
        front_service.insert_order(order_sn, current_user.user_id, ship_id, user_addr['zip'], user_addr['street'], user_addr['city'], user_addr['region'], user_addr['country'],0,total, 0, discount, shipping_cost, 0, ship_comp['ship_name'], order_sn, discount, invoice_title)
        
        for item in cart_list:
            front_service.insert_order_detail(order_sn, item['product_id'], item['product_name'], item['product_amount'], item['price'], int(item['price']) * int(item['product_amount']), item['discount'], item['color'],item['size'])
            front_service.update_cart_status(item['cart_id'])
            front_service.update_stock(item['product_id'], item['product_amount'], item['color'],item['size'])
        flash("Order placed successfully")
        return redirect(url_for('frontend.view_order',order_sn = order_sn))



# check_stock
@corporate_page.route('/check_stock',methods=['GET', 'POST'])
def check_stock():
    if request.method == 'POST':
        cart_id = request.form['cart_id']
        stock = front_service.check_stock(cart_id)
        return jsonify({'stock': stock})

#
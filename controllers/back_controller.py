from flask import Blueprint, render_template, redirect, url_for, flash,request,abort,jsonify,session
from flask_login import login_user,current_user,login_required,logout_user
from datetime import datetime
from common import validation,hashing
from config import setting,send_message
from services import app_service,back_service
import os
import re
from flask_socketio import SocketIO, join_room, leave_room, send, emit
import time
backend_page = Blueprint('backend', __name__)
# page function

def paginate_results(total_sql,sql, page, per_page):
    total_items = back_service.query_total_items(total_sql)
    items = back_service.query_items(page, per_page, sql)
    pagination = back_service.paginate(page, per_page, total_items)
    return items, pagination

#--------------------------#
# user part#
#--------------------------#

# backend home page
@login_required
@backend_page.route("dashboard")
def dashboard():
    
    if current_user.is_authenticated:
        revenue = back_service.get_revenue()
        current_datetime = datetime.now().strftime("%Y-%m")
        monthly_revenue = back_service.get_monthly_revenue(current_datetime)
        products = back_service.get_products()
        orders = back_service.get_orders()
        new_g_customes = back_service.get_new_customers(3)
        new_b_customes = back_service.get_new_customers(4)
        products_top = back_service.get_top_products(current_datetime)
        order_list = back_service.get_orders_list()
        return render_template('backend/index.html',revenue = revenue,monthly_revenue = monthly_revenue,products = products,orders=orders ,new_g_customes=new_g_customes,new_b_customes=new_b_customes,products_top=products_top,order_list=order_list)
    else:
        return redirect(url_for('backend.login'))





# backend login page
@backend_page.route("/login",methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('backend.dashboard'))
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
   
        account = app_service.check_username_existing(username)
        if account is not None:
            if int(account['status']) == 1:
                flash('your account does not exist!', 'warning')
            elif hashing.check_value(account['password'],password):
                if int(account['role'] in (3,4)):
                    return redirect(url_for('frontend.dashboard'))
                user = app_service.user_check(username)
                login_user(user)
                
                return redirect(url_for('backend.dashboard'))

        flash('Invalid username or password')

    return render_template('backend/page_login.html')
@backend_page.route('/insert_account', methods=['GET', 'POST'])
def insert_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = int(request.form['type'])
        status = setting.status[0]
        account = app_service.check_username_existing(username)
        if account:
            flash('Account already exists!','warning')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!','warning')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!','warning')
        elif not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", password):
            flash('password must contain only characters and numbers! Minimum length is 8','warning')
        elif not username or not password or not email:
            flash('Please fill out the form!','warning')
        else:

            app_service.create_user(username, password,role,status)

            user = app_service.user_check(username)
           
            
            back_service.insert_employee(user.user_id, 'Unknown', 'Unknown', email, role,setting.staff_default_img)
            
            flash('Registration successful!')
           # send_message.sendmessage("Welcome to join",current_user.user_id,"Support Team",f"Hi {username} ,Welcome to join our online shopping")
            return redirect(url_for('backend.account_list'))

    return render_template('backend/account/page_register_account.html')

# backend log out page
@backend_page.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('backend.login'))

# backend account list


@backend_page.route('/account_list', methods=['GET', 'POST'])
@login_required
def account_list():
    per_page = request.args.get('per_page', 10, type=int)
    page = request.args.get('page', 1, type=int)
    type = request.args.get('type', 0, type=int)

    if type == 0:
        sql = "select count(*) from users where role in (1,2)"
        items_sql = """
        select u.*,s.* from users u join u_staff s on u.user_id = s.user_id where u.role = 1
        union 
        select u.*,s.* from users u join u_managers s on u.user_id = s.user_id where u.role = 2
        """
    elif type == 1:
        sql = "select count(*) from users where role = 1"
        items_sql = "select u.*,s.* from users u join u_staff s on u.user_id = s.user_id where u.role = 1"
    elif type == 2:
        sql = "select count(*) from users where role = 2"
        items_sql = "select u.*,s.* from users u join u_managers s on u.user_id = s.user_id where u.role = 2"
   

    items, pagination = paginate_results(sql,items_sql, page, per_page)

    return render_template('backend/account/page_account_list.html', items=items, pagination=pagination)



@backend_page.route('/b_account_list', methods=['GET', 'POST'])
@login_required
def b_account_list():
    per_page = request.args.get('per_page', 10, type=int)
    page = request.args.get('page', 1, type=int)

    sql = "select count(*) from users where role = 4;"
    items_sql = """select u.*,s.* from users u join u_business_customers s on u.user_id = s.user_id where u.role = 4;"""
    

    items, pagination = paginate_results(sql,items_sql, page, per_page)

    return render_template('backend/account/page_business_list.html', items=items, pagination=pagination)

@backend_page.route('/g_account_list', methods=['GET', 'POST'])
@login_required
def g_account_list():
    per_page = request.args.get('per_page', 10, type=int)
    page = request.args.get('page', 1, type=int)

    sql = "select count(*) from users where role = 3;"
    items_sql = """select u.*,s.* from users u join u_customers s on u.user_id = s.user_id where u.role = 3;"""
    
    items, pagination = paginate_results(sql,items_sql, page, per_page)

    return render_template('backend/account/page_general_list.html', items=items, pagination=pagination)






@login_required
@backend_page.route('/view_account/<int:user_id>', methods=['GET', 'POST'])
def view_account(user_id):
    account = back_service.get_account(user_id)
    
    return render_template('backend/account/page_view_account.html', account = account)

@login_required
@backend_page.route('/view_b_account/<int:user_id>', methods=['GET', 'POST'])
def view_b_account(user_id):
    account = back_service.get_account(user_id)
    
    return render_template('backend/account/page_view_account.html', account = account)



# edit manager and staff
@login_required
@backend_page.route('/edit_account/<int:user_id>', methods=['GET', 'POST'])
def edit_account(user_id):
    account = back_service.get_account(user_id)
    session["role"] =account["role"]
    session["user_id"] = account["user_id"]
    if request.method == 'POST':
        fname = request.form['f_name']
        lname = request.form['l_name']
        gender = request.form['gender']
        phone = request.form['phone']
        email = request.form['email']
        pro_img = request.form["pro_img"]
        image = request.files['pics']
        if image:
            image.save('static/backend/imgs/people/' + image.filename)
            image_name ='/static/backend/imgs/people/' + image.filename
        else:
            image_name = pro_img
        back_service.update_account(session["user_id"],fname,lname,gender,phone,email,image_name,session["role"])
        flash("update profile successfully")
        return redirect(url_for('backend.view_account',user_id = session["user_id"]))
    return render_template('backend/account/page_edit_account.html', account = account)


# delete manager and staff
@login_required
@backend_page.route('/delete_account/<int:user_id>/<int:type>', methods=['GET', 'POST'])
def delete_account(user_id,type):
    back_service.delete_account(user_id)
    flash("block user successfully")
    if type == 1:
        return redirect(url_for('backend.account_list'))
    elif type == 3:
        return redirect(url_for('backend.g_account_list'))
    elif type == 4:
        return redirect(url_for('backend.b_account_list'))
# activate_account
@login_required
@backend_page.route('/activate_account/<int:user_id>/<int:type>', methods=['GET', 'POST'])
def activate_account(user_id,type):
    back_service.activate_account(user_id)
    flash("activate user successfully")
    if type == 1:
        return redirect(url_for('backend.account_list'))
    elif type == 3:
        return redirect(url_for('backend.g_account_list'))
    elif type == 4:
        return redirect(url_for('backend.b_account_list'))




# edit business customer
@login_required
@backend_page.route('/edit_b_account/<int:user_id>', methods=['GET', 'POST'])
def edit_b_account(user_id):
    account = back_service.get_customer(user_id,4)
    session["user_id"] = account["user_id"]
    items = back_service.get_point_log(user_id)
    session["credit"] = account["credit_limited"]
    if request.method == 'POST':
        cname = request.form['company_name']
        con_name = request.form['contact_name']
        
        phone = request.form['phone_number']
        email = request.form['email']
        credit_limited = request.form['credit_limited']
        credit_points_before = session["credit"] 
        if credit_limited != credit_points_before:
            back_service.insert_customer_log(session["user_id"],"System",0,credit_limited,f"System changed credit_points from {credit_points_before} to {credit_limited}")
        back_service.update_b_account(session["user_id"],cname,con_name,phone,email,credit_limited)
        flash("update customer successfully")
        return redirect(url_for('backend.b_account_list'))
    return render_template('backend/account/page_edit_business.html', account = account,items= items )




# edit general customer
@login_required
@backend_page.route('/edit_g_account/<int:user_id>', methods=['GET', 'POST'])
def edit_g_account(user_id):
    account = back_service.get_customer(user_id,3)
    items = back_service.get_point_log(user_id)
    session["user_id"] = account["user_id"]
    session["credit"] = account["credit_points"]
    if request.method == 'POST':
        fname = request.form['f_name']
        lname = request.form['l_name']
        gender = request.form['gender']
        phone = request.form['phone']
        email = request.form['email']
        credit_points = request.form['credit_points']
        credit_points_before = session["credit"] 
        if credit_points != credit_points_before:
            back_service.insert_customer_log(session["user_id"],"System",0,credit_points,f"System changed credit_points from {credit_points_before} to {credit_points}")
        back_service.update_g_account(session["user_id"],fname,lname,gender,phone,email,credit_points)
        flash("update profile successfully")
        return redirect(url_for('backend.g_account_list'))
    return render_template('backend/account/page_edit_general.html', account = account,items = items)






# customer update pwd
@login_required
@backend_page.route("/update_pwd",methods=['GET', 'POST'])
def update_pwd():
    # Check if "old pwd", "nwe pwd" and "confirm pwd" POST requests exist (user submitted form)
    if request.method == 'POST' and 'password' in request.form and 'npassword' in request.form and 'cpassword' in request.form:
        old_pwd = request.form['password']
        new_pwd = request.form['npassword']
        confirm_pwd = request.form['cpassword']
       
       
        hashed = hashing.hash_value(old_pwd)
       
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
            back_service.update_pwd(hashed,session["user_id"])
            flash("your password updated successful! Please login again")
            logout_user()
            return redirect(url_for('backend.dashboard'))
    


#--------------------#
#  corporate  #
#--------------------#

# cooperate client application
@backend_page.route('/CooperateClients',methods=['GET', 'POST'])
@login_required
def CooperateClients():
    app_list = back_service.get_application()
    return render_template('backend/corperate/page_CooperateClients.html',app_list=app_list)



@backend_page.route('/get_application_details',methods=['GET', 'POST'])
def get_application_details():
    app_id = int(request.args.get('application_id'))
    app = back_service.get_application_by_id(app_id)
    application_data = {
        'applicationId': app['app_id'],
        'enterpriseNumber': app['user_id'],
        'CompanyName': app['company_name'],
        'applicationName': app['app_name'],
        'submitDate': app['submit_date'].strftime('%Y-%m-%d %H:%M:%S'),  # 转换为字符串
        'applicationDetails': app['app_details'],
        'comment': app['reason']
    }
   
    return jsonify(application_data)


@backend_page.route('/update_application_status',methods=['GET', 'POST'])
def update_application_status():
    if request.method == 'POST':
        app_id = request.form.get("application_id")
        user_id = request.form.get("user_id")
        new_status = request.form.get("new_status")
        credit = request.form.get("credit")

       

        back_service.update_application_status(app_id,new_status)
        if new_status == "1":
            back_service.update_corporate_credit(user_id,credit)
            back_service.insert_customer_log(user_id,"System",0,credit,f"System changed credit points to {credit}")
        return "Success", 200
    


@backend_page.route('/update_application',methods=['GET', 'POST'])
def update_application():
    if request.method == 'POST':
        app_id =  request.form["applicationId"]
        reason =  request.form["comment"]
        back_service.update_application_comment(app_id, reason)
        return "Success", 200




#------------------------#
#   product  #
#------------------------#


#   category  #


# get categories
@backend_page.route('/categories')
@login_required
def categories():
    categories_parent_list = back_service.get_categories_parent()
    categories = back_service.get_categories()
    return render_template('backend/product/page_categories.html',categories_parent_list = categories_parent_list,categories= categories)


# insert categories
@backend_page.route('/insert_category',methods=['GET', 'POST'])
@login_required
def insert_category():
    if request.method == 'POST':
        cate_id = request.form["cate_id"]
        name = request.form["name"]
        parentid = request.form["parentid"]
        category_level = request.form["level"]
        sortorder = request.form["sortorder"]
        description = request.form["description"]
        back_service.insert_category(cate_id, parentid, category_level, name, description ,sortorder)
        flash(f'Add category {name} successful')
        return redirect(url_for('backend.categories'))
    
@backend_page.route('/delete_category',methods=['GET', 'POST'])
@login_required
def delete_category():
    cate_id = request.args.get("cate_id")
    back_service.delete_category(cate_id)
    flash('delete category successful')
    return redirect(url_for('backend.categories'))


#------------------------#
#   brand  #
#------------------------#

#brand page
@backend_page.route('/brand')
@login_required
def brand():
    brand_list = back_service.get_brand()
   
    return render_template('backend/product/page_brand.html',brand_list = brand_list)


# insert_brand
@backend_page.route('/insert_brand',methods=['GET', 'POST'])
def insert_brand():
    if request.method == 'POST':
        brand_name = request.form["brand_name"]
        brand_desc = request.form["brand_desc"]
        logo = request.files['logo']
        logo.save(setting.brand_logo_path + logo.filename)
        back_service.insert_band(brand_name, '/' + setting.brand_logo_path + logo.filename, brand_desc)
        flash(f'Add brand {brand_name} successful')
        return redirect(url_for('backend.insert_brand'))
    return render_template('backend/product/page_new_brand.html')


# insert_brand
@backend_page.route('/edit_brand',methods=['GET', 'POST'])
def edit_brand():
    brand_id = request.args.get("brand_id")
    brand_info = back_service.get_brand_info(brand_id)
    if request.method == 'POST':
        brand_id = request.form["brand_id"]
        brand_name = request.form["brand_name"]
        brand_desc = request.form["brand_desc"]
        logo_exist = request.form["logo_exist"]
        logo = request.files['logo']
        if logo:
            logo.save(setting.brand_logo_path + logo.filename)
            back_service.update_band(brand_id,brand_name, '/' + setting.brand_logo_path + logo.filename, brand_desc)
        else:
            back_service.update_band(brand_id,brand_name, logo_exist, brand_desc)
        flash(f'Add brand {brand_name} successful')
        return redirect(url_for('backend.brand'))
    return render_template('backend/product/page_edit_brand.html',brand_info=brand_info)
 



#------------------------#
#   product info  #
#------------------------#




# insert product
@backend_page.route('/insert_product',methods=['GET', 'POST'])
def insert_product():
    one_category_list  = back_service.get_one_cate()
    two_category_list  = back_service.get_two_cate()
    brand_list = back_service.get_brand()
    if request.method == 'POST':
        name = request.form['name']
        price= request.form['price']
        code= request.form['code']
        cost = request.form['cost']
        desc = request.form['desc']
        if_pm = request.form['if_pm']
        brand_id = request.form['brand']
        one_category = request.form['f_category']
        two_category = request.form['s_category']
        # color = request.form['color']
        # size = request.form['size']
        weight = request.form['weight']
        feature = request.form['feature']

        try:
            bool = back_service.insert_product(code,name, brand_id, one_category, two_category, price, if_pm, cost, feature, weight, desc)
            if bool == False:
                flash('error: product code must only')
                return redirect(url_for('backend.product_list'))
            product_id = back_service.get_product_id(code)
            pics = request.files.getlist('pics')

            for index, file in enumerate(pics):
                # 处理上传的文件，可以保存到服务器或者进行其他操作
                if file:
                    filename = f"{index}_{file.filename}"  # 为了防止文件名重复，可以使用索引作为前缀
                    file_path = setting.product_pic_path + filename
                    file.save(file_path)
                    back_service.insert_product_pic(product_id, '/' + file_path, index, index)
        
            flash(f'Add product {name} successful')
            return redirect(url_for('backend.product_list'))
        except Exception as e:
            flash({'error: product code must only'})
            return redirect(url_for('backend.product_list'))
    return render_template('backend/product/page_new_product.html', one_category_list= one_category_list,two_category_list=two_category_list,brand_list=brand_list)





# product list
@backend_page.route('/product_list',methods=['GET', 'POST'])
def product_list():
    one_category_list = back_service.get_one_cate()
    per_page = 10
    page = request.args.get('page', 1, type=int)
    
    items, pagination = paginate_results("select count(*) from product_info","select p.*, c.pic_url from product_info p left join product_pic_info c on p.product_id = c.product_id where c.is_master = 0", page, per_page)
    return render_template('backend/product/page_product_list.html', one_category_list= one_category_list,items = items,pagination=pagination)


# edit product page
@backend_page.route('/edit_product/<int:product_id>',methods=['GET', 'POST'])
def edit_product(product_id):
    one_category_list  = back_service.get_one_cate()
    two_category_list  = back_service.get_two_cate()
    brand_list = back_service.get_brand()
    pics_list = back_service.get_product_pics(product_id)
    product = back_service.get_product_info(product_id)
    return render_template('backend/product/page_edit_product.html', one_category_list= one_category_list,two_category_list=two_category_list,brand_list=brand_list,product=product,pics_list= pics_list)


# update product
@backend_page.route('/update_product',methods=['GET', 'POST'])
def update_product():
    if request.method == 'POST':
        product_id = request.form['product_id']
        name = request.form['name']
        price= request.form['price']
        code= request.form['code']
        cost = request.form['cost']
        desc = request.form['desc']
        if_pm = request.form['if_pm']
        brand_id = request.form['brand']
        one_category = request.form['f_category']
        two_category = request.form['s_category']

        weight = request.form['weight']
        feature = request.form['feature']
        
       
      
        try:
            bool = back_service.update_product(product_id,code,name, brand_id, one_category, two_category, price, if_pm, cost, feature, weight, desc)
            if bool == False:
                flash('error: product code must only')
                return redirect(url_for('backend.product_list'))

            pics = request.files.getlist('pics')
            pics_num = back_service.get_product_pic_num(product_id)
            if pics_num['num']:
                num = int(pics_num['num'])
            else:
                num = 0
            for index, file in enumerate(pics):
                # 处理上传的文件，可以保存到服务器或者进行其他操作
                if file:
                    filename = f"{index+num}_{file.filename}"  # 为了防止文件名重复，可以使用索引作为前缀
                    file_path = setting.product_pic_path + filename
                    file.save(file_path)
                    back_service.insert_product_pic(product_id, '/' + file_path, index +num, index +int(pics_num['num']))
            
            flash(f'update product {name} successful')
            return redirect(url_for('backend.product_list'))
        except Exception as e:
            flash(f'error: {e}')
            return redirect(url_for('backend.product_list'))
        return redirect(url_for('backend.product_list'))

@backend_page.route('/update_product_pics',methods=['GET', 'POST'])
def update_product_pics():
    if request == 'POST':
        pics = request.files.getlist('pics')
        product_id = product_id = request.form['product_id']
        for index, file in enumerate(pics):
            if file:
                filename = f"{index}_{file.filename}"  # 为了防止文件名重复，可以使用索引作为前缀
                file_path = setting.product_pic_path + filename
                file.save(file_path)
                back_service.update_product_pic(product_id,'/'+ setting.product_pic_path + pics.filename)


# off shelf product 
@backend_page.route('/offshelf_product/<int:product_id>',methods=['GET', 'POST'])
def offshelf_product(product_id):
    back_service.off_product(product_id)
    flash('take off shelf successful')
    return redirect(url_for('backend.product_list'))

@backend_page.route('/off_pic/<int:product_pic_id>',methods=['GET', 'POST'])
def off_pic(product_pic_id):
    back_service.off_pic(product_pic_id)
    flash('take off shelf successful')
    return redirect(url_for('backend.product_list'))
off_pic

# edit product page
@backend_page.route('/onshelf_product/<int:product_id>',methods=['GET', 'POST'])
def onshelf_product(product_id):
    back_service.on_product(product_id)
    flash('take off shelf successful')
    return redirect(url_for('backend.product_list'))




#--------------------------#
# warehouse part#
#--------------------------#

# warehouse
@backend_page.route('/warehouse')
@login_required
def warehouse():
    warehouse_list = back_service.get_warehouse()
   
    return render_template('backend/product/page_warehouse_list.html',warehouse_list = warehouse_list)


# warehouse
@backend_page.route('/insert_warehouse',methods=['GET', 'POST'])
@login_required
def insert_warehouse():
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        phone = request.form['phone']
        zip = request.form['zip']
        street = request.form['street']    
        city = request.form['city']
        region = request.form['region']
        country = request.form['country']
        back_service.insert_warehouse_info(name, phone, contact, zip, street, city, region, country)
        flash(f'added {name} successful')
        return redirect(url_for('backend.warehouse'))
    return render_template('backend/product/page_new_warehouse.html')



#--------------------------#
# stock part#
#--------------------------#


@backend_page.route('/stock_list')
@login_required
def stock_list():
   
    per_page = 10
    page = request.args.get('page', 1, type=int)
    total_sql = "select count(*) from product_info"
    item_sql = """SELECT
    p.product_id, p.product_code, p.product_name, w.color,
    SUM(CASE WHEN w.size = 'S' THEN w.current_cnt ELSE 0 END) AS S,
    SUM(CASE WHEN w.size = 'M' THEN w.current_cnt ELSE 0 END) AS M,
    SUM(CASE WHEN w.size = 'L' THEN w.current_cnt ELSE 0 END) AS L,
    SUM(CASE WHEN w.size = 'XL' THEN w.current_cnt ELSE 0 END) AS XL,
    SUM(CASE WHEN w.size = 'XXL' THEN w.current_cnt ELSE 0 END) AS XXL,
    SUM(CASE WHEN w.size = 'XXXL' THEN w.current_cnt ELSE 0 END) AS XXXL
FROM
   product_info p LEFT JOIN warehouse_product w ON p.product_id = w.product_id
GROUP BY
    p.product_id, product_code,p.product_name, w.color;
"""
    items, pagination = paginate_results(total_sql,item_sql, page, per_page)
    
    return render_template('backend/product/page_stock_list.html',stock_list = items,pagination=pagination)




@login_required
@backend_page.route('/insert_product_stock/<int:product_id>',methods=['GET', 'POST'])
def insert_product_stock(product_id):
    
    color_list = back_service.get_color()
    product = back_service.get_product_info(product_id)
    warehouse_list = back_service.get_warehouse()
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        color = request.form['color']
        w_id = int(request.form['warehouse'])
        s = request.form.get('s')
        m = request.form.get('m')
        l = request.form.get('l')
        xl = request.form.get('xl')
        xxl = request.form.get('xxl')
        xxxl = request.form.get('xxxl')
        size_values = {'s': s, 'm': m, 'l': l, 'xl': xl, 'xxl': xxl, 'xxxl': xxxl}
        for  size, value in size_values.items():
            back_service.insert_stock(product_id, w_id, color, size,value)
        flash('update successful')
        return redirect(url_for('backend.stock_list'))
    return render_template('backend/product/page_new_stock.html',color_list = color_list,product=product,warehouse_list=warehouse_list)



#delete stock
@backend_page.route('/delete_product_stock/',methods=['GET', 'POST'])
def delete_product_stock():
    product_id = request.args.get("product_id")
    color = request.args.get("color")
    back_service.delete_stock(product_id,color)
    flash('delete successful')
    return redirect(url_for('backend.stock_list'))




#--------------------------#
# order part#
#--------------------------#
@backend_page.route('/order_list')
@login_required
def order_list():
    per_page = 50
    page = request.args.get('page', 1, type=int)
    
    items, pagination = paginate_results("select count(*) from orders", "select * from orders", page, per_page)
    return render_template('backend/order/page_order_list.html',items = items,pagination=pagination)


@backend_page.route('/view_order/<int:order_sn>',methods=['GET', 'POST'])
@login_required
def view_order(order_sn):
    order = back_service.get_order(order_sn)
    order_info = back_service.get_order_info(order_sn)
    return render_template('backend/order/page_order_detail.html',order = order,order_info = order_info)


@backend_page.route('/update_order_status',methods=['GET', 'POST'])
def update_order_status():
    if request.method == 'POST':
        order_sn = request.form['order_sn']
        status =  request.form['status']
        back_service.update_order_status(order_sn,status)
        #log general user credit points change
        order = back_service.get_order(order_sn)
        if int(status) == 0 and order["role"] == 3:
           
            order_rate = back_service.get_order_rate()
            credit_points = order["district_money"] * order_rate
            back_service.update_g_account_credit(order["user_id"],credit_points,0)
            back_service.insert_customer_log(order["user_id"],0,order_sn,credit_points,f"Order Completed and System increase your credit_points {credit_points}")
            flash("Update Status Successful")
            return redirect(url_for('backend.view_order', order_sn= order_sn))
        elif int(status) == 4 and order["role"] == 3:
            credit_points = back_service.check_log(order["user_id"],order_sn)
            back_service.update_g_account_credit(order["user_id"],credit_points,1)
            back_service.insert_customer_log(order["user_id"],0,order_sn,credit_points,f"order completed and System reduce your credit_points {credit_points}")
            flash("Update Status Successful")
            return redirect(url_for('backend.view_order', order_sn= order_sn))
        flash("Update Status Successful")
        return redirect(url_for('backend.view_order', order_sn= order_sn))
    


@login_required
@backend_page.route("/track_order",methods=['GET', 'POST'])
def track_order():
    data = request.json
    order_id = data.get('order_id', '')
    customer_name = data.get('customer_name', '')
    status = data.get('status', -1)
    orders = back_service.get_order_list(order_id,customer_name,status)
  
    return jsonify({'orders': orders})

#--------------------------#
# system part#
#--------------------------#



# color
@backend_page.route('/color_config')
@login_required
def color_config():
    color_list = back_service.get_color()
   
    return render_template('backend/system/page_color.html',color_list = color_list)

# insert color
@backend_page.route('/insert_color',methods=['GET', 'POST'])
@login_required
def insert_color():
    if request.method == 'POST':
        name = request.form['color_name']
        back_service.insert_color(name)
        flash(f'added {name} successful')
        return redirect(url_for('backend.color_config'))

    



# shipping fee
@backend_page.route('/view_shipping_fee',methods=['GET', 'POST'])
@login_required
def view_shipping_fee():
    fee_list = back_service.get_shipping_fee()
    return render_template('backend/system/page_shipping_fee.html',fee_list = fee_list)

# shipping fee
@backend_page.route('/insert_shipping_fee',methods=['GET', 'POST'])
@login_required
def insert_shipping_fee():
    if request.method == 'POST':
        destination = request.form['destination']
        code,dest = destination.split('|')
        price = request.form['price']
        back_service.insert_shipping_fee(dest,code,price)
        flash(f'added {destination}  fee successful')
        return redirect(url_for('backend.view_shipping_fee'))
    return render_template('backend/system/page_insert_shipping_fee.html')
#delete shipping_fee
@backend_page.route('/delete_shipping_fee/<int:fee_id>',methods=['GET', 'POST'])
def delete_shipping_fee(fee_id):
    back_service.delete_shipping_fee(fee_id)
    flash('delete fee successful')
    return redirect(url_for('backend.view_shipping_fee'))



#--------------------------#
# promotion#
#--------------------------#

@backend_page.route('/view_promotion_list',methods=['GET', 'POST'])
def view_promotion_list():
    pro_list = back_service.get_prom_list()
  
    return render_template('backend/promotion/promotion_view_list.html',pro_list = pro_list)


#insert promotion
@backend_page.route('/insert_promotion',methods=['GET', 'POST'])
def insert_promotion():
    if request.method == 'POST':
        name = request.form['name']
        type = request.form['type']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        value = request.form['value']
       
        status_code = back_service.insert_prom(name, type, start_time, end_time, value)
      
        if status_code == True:
            flash(f"add {name} successful")
        elif status_code == False:
            flash(f"Promotion {name} exists")
        return redirect(url_for('backend.view_promotion_list'))

    return render_template('backend/promotion/promotion_new.html')


@backend_page.route('/delete_prom',methods=['GET', 'POST'])
@login_required
def delete_prom():
    p_id = request.args.get("p_id")
    
    back_service.delete_prom(p_id)
    flash('delete successful')
    return redirect(url_for('backend.view_promotion_list'))



# set product discount price
@backend_page.route('/view_discount_product',methods=['GET', 'POST'])
def view_discount_product():
    discount  = back_service.get_discount()
    one_category_list = back_service.get_one_cate()
    two_category_list = back_service.get_two_cate()
    per_page = 20
    page = request.args.get('page', 1, type=int)
    
    items, pagination = paginate_results("select count(*) from product_info where publish_status = 1","select p.*, COALESCE(pm.discount_amount, 0.00) AS discount_amount, c.pic_url from product_info p left join product_pic_info c on p.product_id = c.product_id left join promotion_product pm on p.product_id = pm.product_id where c.is_master = 0 and publish_status = 1", page, per_page)
   
    return render_template('backend/promotion/promotion_product_setting.html',discount = discount,one_category_list=one_category_list,two_category_list=two_category_list,items = items, pagination=pagination)
    
    


@backend_page.route('/prom_view_category',methods=['GET', 'POST'])
def prom_view_category():
    if request.method == 'POST':
        one_category_sel = request.form['f_category']
        two_category_sel = request.form['s_category']
        
        discount  = back_service.get_discount()
        one_category_list = back_service.get_one_cate()
        two_category_list = back_service.get_two_cate()
        per_page = 20
        page = request.args.get('page', 1, type=int)
        sql = f"""select count(*) from product_info p where p.publish_status = 1 and ('{one_category_sel}' = '0' OR  p.one_category_id = '{one_category_sel}' AND ('{two_category_sel}' = '0' OR  p.two_category_id = '{two_category_sel}'))"""
        t_sql = f"""select p.*,COALESCE(pm.discount_amount, 0.00) AS discount_amount, c.pic_url from product_info p left join product_pic_info c on p.product_id = c.product_id left join promotion_product pm on p.product_id = pm.product_id where c.is_master = 0 and p.publish_status = 1 and (('{one_category_sel}' = '0' OR  p.one_category_id = '{one_category_sel}') AND ('{two_category_sel}' = '0' OR  p.two_category_id = '{two_category_sel}'))""" 
        
        items, pagination = paginate_results(sql,t_sql, page, per_page)
        return render_template('backend/promotion/promotion_product_setting.html',discount = discount,one_category_list=one_category_list,two_category_list=two_category_list,items = items, pagination=pagination)

        
@backend_page.route('/set_prom_price/',methods=['GET', 'POST'])
def set_prom_price():
    if request.method == 'POST':
        value,prom_id = request.form['discount'].split('|')
       
        selected_product_ids = request.form.getlist('selected_cart_ids')
        for product_id in selected_product_ids:
            back_service.update_discount_cate(prom_id,product_id,value)
        flash("update successful")
    return redirect(url_for('backend.view_discount_product'))
    
#--------------------------#
# News
#--------------------------#

@backend_page.route('/news', methods=['GET', 'POST'])
def publish_news():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = request.form['author']
        back_service.insert_news(title, content, author)
        flash("New created successful")
    return render_template('backend/news/news_publish.html')

@backend_page.route('/news_list',methods=['GET', 'POST'])
def news_list():
    news_list = back_service.get_news_list()
    return render_template('backend/news/news_list.html',news_list=news_list)

@backend_page.route('/push_to_homepage/<int:news_id>', methods=['POST'])
def push_to_homepage(news_id):
    # 处理推送到主页的逻辑
    back_service.update_publish_status(news_id)
    return redirect(url_for('backend.news_list'))


# @backend_page.route('/edit_news/<int:news_id>', methods=['GET', 'POST'])
# def edit_news(news_id):
#     if request.method == 'POST':
#         title = request.form['title']
#         content = request.form['content']
        
#         if back_service.edit_news(news_id, title, content):
#             flash('News edited successfully.', 'success')
#         else:
#             flash('Error editing news.', 'danger')
        
#         return redirect(url_for('backend.news_list'))
    
#     # 如果是GET请求，获取当前新闻的数据
#     news_item = back_service.get_news_by_id(news_id)
#     if news_item:
#         return render_template('backend/news/edit_news.html', news=news_item)
#     else:
#         flash('News not found.', 'danger')
#         return redirect(url_for('backend.news_list'))

@backend_page.route('/delete_news/<int:news_id>', methods=['POST'])
def delete_news(news_id):
    if back_service.delete_news(news_id):
        flash('News deleted successfully.', 'success')
    else:
        flash('Error deleting news.', 'danger')
    
    return redirect(url_for('backend.news_list'))


#---------------------
# chat
#--------------------



@backend_page.route('/send_message', methods=['POST'])
def send_message():
    session_id = request.json['session_id']
    
    message = request.json['message']
    back_service.insert_chat(session_id,current_user.user_id,message)
    return jsonify({'status': 'success'})
    

@backend_page.route('/chat', methods=['GET'])
def chat():
    return render_template('backend/chat/page_chat.html')



@backend_page.route('/waiting_customers', methods=['GET'])
def waiting_customers():
    # 模拟长轮询，等待最多10秒来获取新的等待客户
    order = {"waiting": 1, "active": 2, "close": 3}
    for _ in range(10):
       
        waiting_customers = back_service.get_waiting_customer() # get waiting customer list
        waiting_customers = sorted(waiting_customers, key=lambda x: order[x["status"]])  
        if waiting_customers:
            return jsonify(waiting_customers), 200
        time.sleep(1)
    
    # 没有等待客户时返回空列表
    return jsonify([]), 200

@backend_page.route('/join_chat', methods=['POST'])
def join_chat():
    session_id = request.json['session_id']
    
    back_service.join_chat(session_id,current_user.user_id)
    
    return jsonify({'success': True})


@backend_page.route('/get_user_id')
def get_user_id():
    
    return jsonify({'user_id': current_user.user_id}), 200


@backend_page.route('/chat_history', methods=['GET', 'POST'])

def chat_history():
    session_id = request.json['session_id']
    
   
    chat_history = back_service.chat_history(session_id)
        
    if chat_history:
        return jsonify(chat_history), 200
        
        
    
    # 如果没有新消息则返回一个空列表
    return jsonify([]), 200



@backend_page.route('/close_chat', methods=['GET', 'POST'])
def close_chat():
    data = request.json
    session_id = data['session_id']

    if back_service.close_chat(session_id):
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'failure', 'message': 'Invalid session_id'})
    



@backend_page.route('/scheduled_task', methods=['GET', 'POST'])
def scheduled_task():
    scheduled_list = back_service.get_scheduled_list()
    return render_template('backend/system/page_scheduled_list.html',scheduled_list=scheduled_list)



# system message

@backend_page.route('/send_system_message',methods=['GET', 'POST'])
def send_system_message():
    if request.method == 'POST':
        receive_id = request.form.get("user_id")
        content = request.form.get("content")
        subject = request.form.get("subject")
        back_service.insert_system_message(receive_id,content,subject,current_user.user_id)
        return jsonify({'success': True}),200
    

@backend_page.route('/message_list/',methods=['GET', 'POST'])
def message_list():
    messages_list = back_service.get_message_list(current_user.user_id)
    return render_template('backend/chat/page_view_message.html',messages_list = messages_list)

@backend_page.route('/get_system_message', methods=['GET', 'POST'])
def get_system_message():
    if request.method == 'POST':
        id = request.form.get("message_id")
        message = back_service.get_message(id)
        return jsonify(message), 200
    
@backend_page.route('/delete_system_message', methods=['GET', 'POST'])
def delete_system_message():
    if request.method == 'POST':
        id = request.form.get("message_id")
        message = back_service.delete_message(id)
        return jsonify(message), 200



#--------------------
# statistic
#--------------------
@backend_page.route('/chart_data', methods=['GET'])
def chart_data():
    current_year = datetime.now().year
    # get monthly sales
    
    sales_data = back_service.get_monthly_sales(current_year)

    sales = [0] * 12
    for data in sales_data:
        sales[data['month'] - 1] = data['total']

    # get monthly users
    
    user_data = back_service.get_user_data(current_year)


    users = [0] * 12
    for data in user_data:
        users[data['month'] - 1] = data['total']

    # get monthly product

    product_data = back_service.get_product_data(current_year)

    products = [0] * 12
    for data in product_data:
        products[data['month'] - 1] = data['total']


    return jsonify({
        'sales': sales,
        'users': users,
        'products': products
    })

@backend_page.route('/area_data', methods=['GET'])
def area_data():
    Au = back_service.get_area_data('Australia')                    
    NZ = back_service.get_area_data('New Zealand')  
    USA = back_service.get_area_data('USA (US)')                                       
    EU= back_service.get_area_data('European Union(EU)')  
    return jsonify({
        'AU': Au,
        'NZ': NZ,
        'USA': USA,
        'EU':EU    
        })


@backend_page.route('/popular_products', methods=['GET','POST'])
def popular_products():
    one_category_list = back_service.get_one_cate()
    per_page = 10
    page = request.args.get('page', 1, type=int)
    current_datetime = datetime.now().strftime("%Y-%m")
    
    count_sql = f"""SELECT COUNT(product_info.product_name) AS count
FROM order_detail 
JOIN product_info ON order_detail.product_id = product_info.product_id 
WHERE order_detail.modified_time LIKE '%{current_datetime}%' 
GROUP BY order_detail.product_id 
ORDER BY count DESC"""
    item_sql = f"""SELECT product_info.product_name, 
       COUNT(order_detail.product_cnt) AS cnt 
FROM order_detail 
JOIN product_info ON order_detail.product_id = product_info.product_id 
WHERE order_detail.modified_time LIKE '%{current_datetime}%' 
GROUP BY order_detail.product_id 
ORDER BY cnt DESC"""
    total_items = back_service.query_t_total_items(count_sql)['count']
    items = back_service.query_items(page, per_page, item_sql )
    pagination = back_service.paginate(page, per_page, total_items)
   
    if request.method == 'POST':
        cate_id = request.form['f_category']
       
        date_obj = request.form['date_p']
        
        date = date_obj[:7]
       
        total_items_sql = f"""SELECT COUNT(product_info.product_name) AS count FROM order_detail JOIN product_info ON order_detail.product_id = product_info.product_id WHERE order_detail.modified_time LIKE '%{date}%' AND (
      product_info.one_category_id = '{cate_id}' OR '{cate_id}' = '0'
  ) GROUP BY order_detail.product_id ORDER BY count DESC"""
        
        total_items = back_service.query_t_total_items(total_items_sql)['count']
        
        items = back_service.query_items(page, per_page, f"""SELECT product_info.product_name, order_detail.product_id, COUNT(order_detail.product_cnt) AS cnt FROM order_detail JOIN product_info ON order_detail.product_id = product_info.product_id 
WHERE order_detail.modified_time LIKE '%{current_datetime}%'  AND (
      product_info.one_category_id = '{cate_id}' OR '{cate_id}' = '0'
  )
GROUP BY order_detail.product_id 
ORDER BY cnt DESC""" )
        pagination = back_service.paginate(page, per_page, total_items)
        
        return render_template('backend/statistics/page_product_list.html', one_category_list= one_category_list,items = items,pagination=pagination)
    return render_template('backend/statistics/page_product_list.html', one_category_list= one_category_list,items = items,pagination=pagination)




#----------------
# refund
#----------------
@backend_page.route('/get_refund_app_details',methods=['GET', 'POST'])
def get_refund_app_details():
    app_id = int(request.args.get('application_id'))
    app = back_service.get_refund_application_by_id(app_id)
    return jsonify(app)

@backend_page.route('/refund_applications',methods=['GET', 'POST'])
def refund_applications():
    refund_list = back_service.get_refund_list()
    return render_template('backend/refund/page_refund_apps.html',refund_list = refund_list)


@backend_page.route('/update_refund_status',methods=['GET', 'POST'])
def update_refund_status():
    data = request.json
    app_id = int(data.get('application_id'))
    comment = data.get('comment')
    status = data.get('new_status')
    order = back_service.get_refund_application_by_id(app_id)
    refund_price = int(order["product_price"])* int(order['qtn'])
    if int(status) == 1 and order["role"] == 3 and order["refund_way"] == 1:
        
        rate = back_service.get_order_rate()
        credit_points = rate * refund_price
        back_service.update_g_account_credit(order["user_id"],credit_points,1)
        back_service.insert_customer_log(order["user_id"],0,order["order_sn"],credit_points,f"order completed and System reduce your credit_points {credit_points}")
        back_service.update_refund(app_id,1,comment,current_user.user_id)
        return jsonify("success"), 200
    elif int(status) == 1 and order["role"] == 3 and order["refund_way"] == 2:
        rate = back_service.get_order_rate()
        credit_points = rate * refund_price
        back_service.update_g_account_credit(order["user_id"],credit_points,1)
        back_service.insert_customer_log(order["user_id"],0,order["order_sn"],credit_points,f"order completed and System reduce your credit_points {credit_points}")
        back_service.update_balance(order["user_id"],refund_price,3)
        back_service.update_refund(app_id,1,comment,current_user.user_id)
        return jsonify("success"), 200
    elif int(status) == 1 and order["role"] == 4:
        back_service.insert_customer_log(order["user_id"],0,order["order_sn"],refund_price,f"order completed and System refund your credit {refund_price}")
        back_service.update_balance(order["user_id"],refund_price,4)
        back_service.update_refund(app_id,1,comment,current_user.user_id)
        return jsonify("success"), 200
    elif int(status) == 2:
        back_service.update_refund(app_id,2,comment,current_user.user_id)
        return jsonify("success"), 200
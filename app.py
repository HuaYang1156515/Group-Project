
from flask_login import LoginManager
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from flask import Flask,render_template,Blueprint, render_template, redirect, url_for, flash,request,session,jsonify
from flask_login import login_user, logout_user, login_required, current_user,LoginManager
from controllers import back_controller,front_controller,corpor_controller
from services import app_service
from common import hashing
from config import setting,send_message
from datetime import datetime, timezone
import re
import time

import mysql.connector
from mysql.connector import Error

app = Flask(__name__,template_folder="templates", static_folder="static")


# Other configurations...

# Set up Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Set the login view


app.register_blueprint(back_controller.backend_page, url_prefix="/backend")
app.register_blueprint(front_controller.frontend_page, url_prefix="/frontend")
app.register_blueprint(corpor_controller.corporate_page, url_prefix="/corporate")
# set secret_key
app.secret_key = setting.secret_key
#socketio = SocketIO(app,cors_allowed_origins="*")
#back_controller.socketio.init_app(app)
# get local time


@login_manager.user_loader
def load_user(user_id):

    User = app_service.userid_check(user_id)
    return User

@app.context_processor
def inject_message_count():
   categories =  app_service.get_categories ()
   
  
   cart_list =[]
   message_count = 0
   cart_count = 0
   if current_user.is_authenticated:
       cart_list = app_service.get_cart_list(current_user.user_id)
       message_count = app_service.get_message_count(current_user.user_id)
       cart_count = app_service.get_cart_count(current_user.user_id)
   return {'categories_list': categories,'cart_list':cart_list,'message_count':message_count,'cart_count':cart_count}

@app.route("/")
def home():
 
    return redirect(url_for('frontend.dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
   
        account = app_service.check_username_existing(username)
        if account is not None:
            if int(account['status']) == 1:
                flash('your account does not exist!', 'warning')
            elif hashing.check_value(account['password'],password):
                # member = app_service.query_member_info(account['user_id'])
                # if member and  member['due'] and member['due'] < date.today():
                #     app_service.update_member_status(setting.status[1],account['user_id'])
                user = app_service.user_check(username)
                login_user(user)
                if int(account['role'] in (0,1,2)):
                    return redirect(url_for('backend.dashboard'))
                next_url = session.pop('next_url', None)  # 获取并移除保存的 next_url
                if next_url:
                    return redirect(next_url)  # 重定向到保存的 next_url
                else:
                    return redirect(url_for('frontend.page_account'))
                

        flash('Invalid username or password')

    return render_template('frontend/page_login_register.html')

# customer register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        source = request.form['source']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if source =="general":
            role = setting.roles[3]
        elif source =="corporate":
            role = setting.roles[4]
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
           
            login_user(user)
            if source =="general":
                app_service.insert_customer(current_user.user_id, 'Unknown', 'Unknown', email)
            elif source =="corporate":
                app_service.insert_b_customer(current_user.user_id, 'Unknown', 'Unknown', email)
            flash('Registration successful! You can update your profile before you purchese')
           # send_message.sendmessage("Welcome to join",current_user.user_id,"Support Team",f"Hi {username} ,Welcome to join our online shopping")
            next_url = session.pop('next_url', None)  # 获取并移除保存的 next_url
            if next_url:
                return redirect(next_url)  # 重定向到保存的 next_url
            else:
                return redirect(url_for('frontend.page_account'))
            

    return render_template('frontend/page_login_register.html')


# backend log out page
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))




#-----------------
# chat
#----------------
@login_required
@app.route('/start_chat/', methods=['GET', 'POST'])
def start_chat():
    user_id = current_user.user_id
    print(user_id)   
    session_id = app_service.insert_session(user_id)
  
    return jsonify({'session_id': session_id})


@login_required
@app.route('/send_message',methods=['POST'])
def send_message():
    data = request.get_json()
    session_id = data['session_id']
    
    message = data['message']
    user_id = current_user.user_id
    
    app_service.insert_chat(session_id,user_id,message)
    
    return jsonify({'status': 'success'})


@login_required
@app.route('/get_user_id', methods=['GET', 'POST'])
def get_user_id():
    user_id = current_user.user_id
    
    return jsonify({'user_id': user_id})

@login_required
@app.route('/chat_history', methods=['POST'])
def chat_history():
    data = request.get_json()
    session_id = data.get('session_id')
    
    # 将 JSON 中的时间字符串转换为带有时区信息的 datetime 对象
   
    # 模拟长轮询，等待最多10秒来获取新消息
   
    chat_history = app_service.chat_history(session_id)
        
    if chat_history:
        return jsonify(chat_history), 200
        
       
    
    # 如果没有新消息则返回一个空列表
    return jsonify([]), 200


@app.route('/close_chat', methods=['GET', 'POST'])
def close_chat():
    data = request.json
    session_id = data['session_id']

    if app_service.close_chat(session_id):
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'failure', 'message': 'Invalid session_id'})
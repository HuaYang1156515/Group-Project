from functools import wraps
from flask import abort
from flask_login import current_user
from flask import render_template,redirect,url_for,flash
from datetime import datetime


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role != 'admin':
            abort(403)  # Forbidden
        return func(*args, **kwargs)
    return wrapper



def tutor_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'tutor':
            abort(403)  # Forbidden
        return func(*args, **kwargs)
    return wrapper





def role_required(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.role not in roles:
                return render_template('login.html')
            return func(*args, **kwargs)
        return wrapper
    return decorator


def membership_required(status):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(status)
            if current_user.is_active == status:
                flash("your have to pay membership fee before you make a booking!")
                return redirect(url_for('member.payment'))
            return func(*args, **kwargs)
        return wrapper
    return decorator


def calculate_age(date_of_birth):
    # 将字符串转换为 datetime 对象
    birth_date = datetime.strptime(date_of_birth, "%Y-%m-%d")
    # 获取当前日期
    current_date = datetime.now()
    # 计算年龄
    age = current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
    return age




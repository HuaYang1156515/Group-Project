from datetime import datetime
import time
import pytz
salt = '123456'
roles = [0,1,2,3,4] #Role: 0-administrator, 1-employee,2-managers,3-ordinary customers, 4-business customers',
status = ['0','1']  #0: normal  1:block
order_status = [0,1,2,3,4] #Role: 0-completed, 1-unpaid,2-confirmed and Prepare,3-delivery , 4-cancel,
secret_key = '123456'
payment_method = [0,1,2,3,4] # 0 - unpaid, 1, online bank 2, balance, 3,credit_limited 4,check
current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#order_sn = int(time.time())

brand_logo_path = 'static/frontend/imgs/brand/'
product_pic_path = 'static/frontend/imgs/product/'
staff_default_img = '/static/backend/imgs/people/head.png'

# url_add= "http://127.0.0.1:5000/frontend/view_product/"
url_add= "https://peixuanhan888.pythonanywhere.com/view_product/"  # pythananywhere address
#promotion Role:  1-Discount,2-Spend and Save,3-Promo Code , 4-Gold Members Only, 5,Buy and Save


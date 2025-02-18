DROP SCHEMA IF EXISTS BsmpDB;
CREATE SCHEMA BsmpDB;
USE BsmpDB;
-----------------------------
-- Table structure for user
-------------------------------

-- user entity
CREATE TABLE IF NOT EXISTS users (
  user_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'User id',
  username varchar(50) NOT NULL COMMENT 'Username',
  password varchar(255) NOT NULL ,
  role int NOT NULL COMMENT 'Role: 0-administrator, 1-staff,2-managers,3-ordinary customers, 4-business customers',
  createtime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  updatetime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  status varchar(20) COMMENT 'Role: 0-normal, 1-block'
) COMMENT='users';

-- customers entity
CREATE TABLE IF NOT EXISTS u_customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone_number VARCHAR(20),
    email VARCHAR(255),
    gender VARCHAR(2) DEFAULT '0' COMMENT '1-male,2-female,3-unknown',
    credit_points INT NOT NULL DEFAULT '0' COMMENT 'users credit points',
    credit_points_used INT NOT NULL DEFAULT '0' COMMENT 'Credit points consumed by the user',
    customer_level TINYINT NOT NULL DEFAULT '1' COMMENT '1-normal customer, 2-Silver Card, 3-Gold Card',
    user_balance DECIMAL(8,2) NOT NULL DEFAULT '0.00' COMMENT 'balance',
    modified_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Modified Time',
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)  COMMENT='customers info';

-- Table structure for business user
CREATE TABLE IF NOT EXISTS u_business_customers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    company_name VARCHAR(100),
    contact_name VARCHAR(100),
    phone_number VARCHAR(20),
    email VARCHAR(255),
    credit_limited int NOT NULL DEFAULT '0' comment 'business users credit points',
    credit_used int NOT NULL DEFAULT '0' ,
    modified_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Modified Time',
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)COMMENT='business customers info';

-- Table structure for staff
CREATE TABLE IF NOT EXISTS u_staff (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    gender VARCHAR(2) COMMENT '1-male,2-female,3-unknown',
    position VARCHAR(100),
    phone_number VARCHAR(20),
    email VARCHAR(255),
    pro_img VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)COMMENT='staff';

-- Table structure for managers
CREATE TABLE IF NOT EXISTS u_managers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    gender VARCHAR(2) COMMENT '1-male,2-female,3-unknown',
    position VARCHAR(100),
    phone_number VARCHAR(20),
    email VARCHAR(255),
    pro_img VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)COMMENT='managers';

-- Table structure for admins
CREATE TABLE IF NOT EXISTS u_admins (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    gender VARCHAR(2) COMMENT '1-male,2-female,3-unknown',
    position VARCHAR(100),
    phone_number VARCHAR(20),
    email VARCHAR(255),
    pro_img VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)COMMENT='admins';


-- Table structure for customer_level_inf

CREATE TABLE IF NOT EXISTS customer_level_inf (
 level_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Membership Level ID',
  level_name varchar(10) NOT NULL COMMENT 'Membership Level Name',
  point int NOT NULL DEFAULT 0 COMMENT 'Points for this Level',
  product_id int NOT NULL DEFAULT 0 COMMENT 'free product for this Level',
  modified_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Modified Time'
) COMMENT='Customer customer_level_inf Table';

-- Table structure for customer address

CREATE TABLE IF NOT EXISTS order_customer_addr (
  id int PRIMARY KEY AUTO_INCREMENT COMMENT 'Auto-increment primary key ID',
  user_id int NOT NULL COMMENT 'Auto-increment ID from user table',
  zip smallint NOT NULL COMMENT 'Zip Code',
  street VARCHAR(255) NOT NULL COMMENT 'Province ID from area table',
  city VARCHAR(255) NOT NULL COMMENT 'City ID from area table',
  region VARCHAR(255) NOT NULL COMMENT 'District ID from area table',
  country VARCHAR(255) NOT NULL COMMENT 'Specific Address including door number',
  is_default tinyint NOT NULL COMMENT 'Default Address Indicator',
  modified_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Modified Time',
  FOREIGN KEY (user_id) REFERENCES users(user_id)
) COMMENT='Customer Address Table';

-- Table structure for point_log

CREATE TABLE IF NOT EXISTS customer_point_log (
  id int PRIMARY KEY AUTO_INCREMENT COMMENT 'Point Log ID',
  user_id int  NOT NULL COMMENT 'User ID',
  source tinyint  NOT NULL COMMENT 'Point Source: 0 Order',
  refer_number int  NOT NULL DEFAULT '0' COMMENT 'Related order number from Point Source',
  change_point smallint  NOT NULL DEFAULT '0' COMMENT 'Changed Points',
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Point Log Creation Time',
  FOREIGN KEY (user_id) REFERENCES users(user_id)
) COMMENT='Customer Points Log Table';

-- Table structure for customer_balance_log

CREATE TABLE IF NOT EXISTS customer_balance_log (
  balance_id int PRIMARY KEY NOT NULL AUTO_INCREMENT COMMENT 'Balance Log ID',
  user_id int NOT NULL COMMENT 'User ID',
  source tinyint  NOT NULL DEFAULT '1' COMMENT 'Record Source: 1 Order, 2 Return Order, 3-gift card',
  source_sn int  NOT NULL COMMENT 'Related Document ID',
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Record Creation Time',
  amount decimal(8,2) NOT NULL DEFAULT '0.00' COMMENT 'Amount Changed',
  FOREIGN KEY (user_id) REFERENCES users(user_id)
) COMMENT='Customer Balance Change Table';



-- Table structure for customer message

CREATE TABLE IF NOT EXISTS messagebox (
    id INT PRIMARY KEY AUTO_INCREMENT,
    subject VARCHAR(255) NOT NULL COMMENT 'message title',
    recipient_user_id VARCHAR(255), 
    sender_user_id VARCHAR(255) COMMENT 'sender userid',
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(10)
);



--Table structure for product



-- Table structure for brand

CREATE TABLE IF NOT EXISTS brand_info (
  brand_id int PRIMARY KEY AUTO_INCREMENT COMMENT 'Brand ID',
  brand_name varchar(50) NOT NULL COMMENT 'Brand Name',
  brand_logo varchar(100) DEFAULT NULL COMMENT 'Brand Logo image',
  brand_desc text DEFAULT NULL COMMENT 'Brand Description',
  brand_status tinyint NOT NULL DEFAULT '1' COMMENT 'Brand Status, 0 Disabled, 1 Enabled',
  brand_order tinyint NOT NULL DEFAULT '0' COMMENT 'sort by',
  modified_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Modified Time'
)  COMMENT='Brand Information Table';


-- Table structure for category

CREATE TABLE IF NOT EXISTS category (
  cate_id int PRIMARY KEY NOT NULL COMMENT 'Category Id',
  parentid varchar(64) DEFAULT NULL COMMENT 'Parent category id, when id=0 indicates root node, primary category',
  category_level tinyint  NOT NULL DEFAULT '1' COMMENT 'Category Level',
  name varchar(50) DEFAULT NULL COMMENT 'Category name',
  status int DEFAULT '1' COMMENT 'Category status: 1-normal, 2-abandoned',
  description varchar(255) COMMENT 'Category description',
  sortorder int DEFAULT NULL COMMENT 'Sort order, display order of the same category, natural order if the values are equal',
  createtime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  updatetime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time'
) COMMENT='product category';

-- Table structure for product info

CREATE TABLE IF NOT EXISTS product_info (
  product_id int PRIMARY KEY  AUTO_INCREMENT COMMENT 'Product ID',
  product_code char(16) NOT NULL COMMENT 'Product Code',
  product_name varchar(50) NOT NULL COMMENT 'Product Name',
  brand_id int NOT NULL COMMENT 'Brand ID',
  one_category_id int NOT NULL COMMENT 'First-level Category ID',
  two_category_id int NOT NULL COMMENT 'Second-level Category ID',
  price decimal(8,2) NOT NULL COMMENT 'Selling Price',
  if_promotion int DEFAULT '0' COMMENT 'product status: 0-normal, 1-promotion',
  cost decimal(8,2) NOT NULL COMMENT 'product cost',
  publish_status tinyint NOT NULL DEFAULT '1' COMMENT 'Publish Status: 0 Off-shelf, 1 On-shelf',
  feature VARCHAR(255) DEFAULT NULL,
  weight float DEFAULT NULL COMMENT 'Product Weight',
  color varchar(50) DEFAULT NULL,
  size varchar(50) DEFAULT NULL,
  descript text NOT NULL COMMENT 'Product Description',
  indate timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Entry Time of the Product',
  modified_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Modified Time',
  FOREIGN KEY (brand_id) REFERENCES brand_info(brand_id)
)  COMMENT='Product Information Table';

-- Table structure for product image

CREATE TABLE IF NOT EXISTS product_pic_info (
  product_pic_id int PRIMARY KEY AUTO_INCREMENT COMMENT 'Product Picture ID',
  product_id int NOT NULL COMMENT 'Product ID',
  pic_desc varchar(50) DEFAULT NULL COMMENT 'Picture Description',
  pic_url varchar(200) NOT NULL COMMENT 'Picture URL',
  is_master tinyint NOT NULL DEFAULT '0' COMMENT 'Is Main Picture: 0 Yes, 1 No',
  pic_order tinyint NOT NULL DEFAULT '0' COMMENT 'Picture sort by',
  pic_status tinyint NOT NULL DEFAULT '1' COMMENT 'Is Picture Valid: 0 Invalid, 1 Valid',
  modified_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Modified Time',
  FOREIGN KEY (product_id) REFERENCES product_info(product_id)
)  COMMENT='Product Picture Information Table';

-- Table structure for product comment

CREATE TABLE IF NOT EXISTS product_comment (
  comment_id int PRIMARY KEY  AUTO_INCREMENT COMMENT 'Comment ID',
  product_id int NOT NULL COMMENT 'Product ID',
  user_id int NOT NULL COMMENT 'Customer user ID',
  content varchar(300) NOT NULL COMMENT 'Comment Content',
  rate INT NULL DEFAULT 0,
  audit_status tinyint NOT NULL DEFAULT 0 COMMENT 'Audit Status: 0 Not Audited, 1 Audited',
  audit_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Comment Time',
  modified_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Modified Time',
  FOREIGN KEY (product_id) REFERENCES product_info(product_id)
)  COMMENT='Product Comment Table';




-- Table structure for order



-- Table structure for order 


CREATE TABLE IF NOT EXISTS orders (
  order_id int PRIMARY KEY AUTO_INCREMENT COMMENT 'Order ID',
  order_sn bigint NOT NULL COMMENT 'Order Number DD/MM/YYYY HH:mm:ss',
  user_id int NOT NULL COMMENT 'Customer ID',
  shipping_user varchar(10) NOT NULL COMMENT 'Recipient Name',
  zip smallint NOT NULL COMMENT 'Zip Code',
  street VARCHAR(255) NOT NULL COMMENT 'Province ID from area table',
  city VARCHAR(255) NOT NULL COMMENT 'City ID from area table',
  region VARCHAR(255) NOT NULL COMMENT 'District ID from area table',
  country VARCHAR(255) NOT NULL COMMENT 'Specific Address including door number',
  payment_method tinyint NOT NULL COMMENT 'Payment Method: 1 Online Banking, 2 Balance, 3 unpaid',
  order_money decimal(8,2) NOT NULL COMMENT 'Order Amount',
  district_money decimal(8,2) NOT NULL DEFAULT '0.00' COMMENT 'Discount Amount',
  shipping_money decimal(8,2) NOT NULL DEFAULT '0.00' COMMENT 'Shipping Amount',
  payment_money decimal(8,2) NOT NULL DEFAULT '0.00' COMMENT 'Payment Amount',
  shipping_comp_name varchar(10) DEFAULT NULL COMMENT 'Courier Company Name',
  shipping_sn varchar(50) DEFAULT NULL COMMENT 'Courier Number',
  create_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Order Time',
  shipping_time datetime DEFAULT NULL COMMENT 'Shipping Time',
  pay_time datetime DEFAULT NULL COMMENT 'Payment Time',
  receive_time datetime DEFAULT NULL COMMENT 'Receipt Time',
  order_status tinyint NOT NULL DEFAULT '1' COMMENT 'Order Status',
  order_point int NOT NULL DEFAULT '0' COMMENT 'Order Points',
  invoice_title varchar(100) DEFAULT NULL COMMENT 'Invoice Title',
  modified_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Modified Time',
  KEY (order_sn),  -- 添加索引
  FOREIGN KEY (user_id) REFERENCES users(user_id)
)  COMMENT='Order Master Table';

-- Table structure for order_detail 

CREATE TABLE IF NOT EXISTS order_detail (
  order_detail_id int PRIMARY KEY AUTO_INCREMENT COMMENT 'Auto-increment Primary Key ID, Order Detail Table ID',
  order_sn bigint NOT NULL COMMENT 'Order sn ',
  product_id int NOT NULL COMMENT 'Order Product ID',
  product_name varchar(50) NOT NULL COMMENT 'Product Name',
  product_cnt int NOT NULL DEFAULT '1' COMMENT 'Quantity of Purchased Products',
  product_price decimal(8,2) NOT NULL COMMENT 'Unit Price of Purchased Products',
  order_cost decimal(8,2) NOT NULL DEFAULT '0.00' COMMENT 'order total Cost Price',
  order_discount decimal(8,2) NOT NULL DEFAULT '0.00' COMMENT 'Discount Apportioned Amount',
  color varchar(50) COMMENT 'Product Weight',
  size varchar(50),
  w_id int NOT NULL DEFAULT '1' COMMENT 'Warehouse ID',
  modified_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Modified Time',
  FOREIGN KEY (order_sn) REFERENCES orders(order_sn),
  FOREIGN KEY (product_id) REFERENCES product_info(product_id)
)  COMMENT='Order Detail Table';


-- Table structure for order cart
CREATE TABLE IF NOT EXISTS order_cart (
  cart_id int PRIMARY KEY AUTO_INCREMENT COMMENT 'Cart ID',
  user_id int NOT NULL COMMENT 'User ID',
  product_id int NOT NULL COMMENT 'Product ID',
  product_amount int NOT NULL COMMENT 'Quantity of Product Added to Cart',
  price decimal(8,2) NOT NULL COMMENT 'Product Price',
  discount decimal(8,2),
  color varchar(50),
  size varchar(50),
  if_paid int NOT NULL DEFAULT '1'  COMMENT '0-paid, 1-unpaid',
  selected INT NULL DEFAULT '0' ,
  add_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Time Product Added to Cart',
  modified_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Modified Time',
  FOREIGN KEY (product_id) REFERENCES product_info(product_id)
)  COMMENT='Shopping Cart Table';




-- Table structure for payinfo
CREATE TABLE IF NOT EXISTS payinfo (
  payid int PRIMARY KEY AUTO_INCREMENT,
  order_sn bigint DEFAULT NULL COMMENT 'Order sn',
  user_id int DEFAULT NULL COMMENT 'User id',
  pay_user varchar(200),
  payform int DEFAULT NULL COMMENT 'Payment platform: 1,debt card 2,credit card',
  paynumber varchar(200) DEFAULT NULL COMMENT 'Payment serial number',
  amount decimal(8,2) DEFAULT '0.00',
  status varchar(20) DEFAULT 0 COMMENT 'Payment status',
  createtime datetime DEFAULT NULL COMMENT 'Creation time',
  updatetime datetime DEFAULT NULL COMMENT 'Update time',

FOREIGN KEY (order_sn) REFERENCES orders(order_sn),
FOREIGN KEY (user_id) REFERENCES users(user_id)
) COMMENT='payinfo';

-- Table structure for warehouse

CREATE TABLE warehouse_info (
  w_id int PRIMARY KEY AUTO_INCREMENT COMMENT 'Warehouse ID',
  
  warehouse_name varchar(255) NOT NULL COMMENT 'Warehouse Name',
  warehouse_phone varchar(255) NOT NULL COMMENT 'Warehouse Phone',
  contact varchar(50) NOT NULL COMMENT 'Warehouse Contact Person',
  zip int NOT NULL COMMENT 'Zip Code',
  street VARCHAR(255) NOT NULL COMMENT 'Province ID from area table',
  city VARCHAR(255) NOT NULL COMMENT 'City ID from area table',
  region VARCHAR(255) NOT NULL COMMENT 'District ID from area table',
  country VARCHAR(255) NOT NULL COMMENT 'Specific Address including door number',
  warehouse_status tinyint NOT NULL DEFAULT '1' COMMENT 'Warehouse Status: 0 Disabled, 1 Enabled',
  modified_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Modified Time'
)  COMMENT='Warehouse Information Table';

-- Table structure for product warehouse

CREATE TABLE IF NOT EXISTS warehouse_product (
  id int PRIMARY KEY AUTO_INCREMENT COMMENT 'Warehouse Product ID',
  product_id int COMMENT 'Product ID',
  w_id int NOT NULL COMMENT 'Warehouse ID',
  color varchar(50) DEFAULT 'black' comment 'color',
  size varchar(50) DEFAULT 's' comment 'size',
  current_cnt int NOT NULL DEFAULT '0' COMMENT 'Current Product Quantity',
  modified_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Modified Time',
  FOREIGN KEY (w_id) REFERENCES warehouse_info(w_id)
)  COMMENT='Warehouse Product Table';

-- Table structure for shipping info 
CREATE TABLE IF NOT EXISTS shipping_info (
  ship_id int PRIMARY KEY AUTO_INCREMENT COMMENT 'Primary Key ID',
  ship_name varchar(20) NOT NULL COMMENT 'Logistics Company Name',
  ship_contact varchar(20) NOT NULL COMMENT 'Logistics Company Contact Person',
  telphone varchar(20) NOT NULL COMMENT 'Logistics Company Contact Telephone',
  modified_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Modified Time'
)  COMMENT='Shipping Information Table';


-- Table structure for shipping fess 
CREATE TABLE IF NOT EXISTS shipping_info_fee (
  fee_id int PRIMARY KEY AUTO_INCREMENT COMMENT 'Primary Key ID',
  ship_id int NOT NULL COMMENT 'Company id',
  ship_mode varchar(30) NOT NULL COMMENT '1-standard, 2-fast',
  destination varchar(30) NOT NULL COMMENT '1-domestic, 2-Canada, 3- United State,4-other Countries',
  price decimal(8,2) NOT NULL DEFAULT '0.00' COMMENT 'Delivery Price',
  modified_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Modified Time',
  FOREIGN KEY (ship_id) REFERENCES shipping_info(ship_id)
)  COMMENT='Shipping fee';



-- Table structure for promotions



-- Table structure for promotion
CREATE TABLE IF NOT EXISTS promotion (
  promotion_id int PRIMARY KEY AUTO_INCREMENT COMMENT 'Promotion ID',
  promotion_name varchar(100) NOT NULL COMMENT 'Promotion Name',
  promotion_type tinyint NOT NULL COMMENT 'Promotion Type: 1 Discount, 2 Coupon, 3 Bundle Offer, etc.',
  start_time datetime NOT NULL COMMENT 'Start Time of Promotion',
  end_time datetime NOT NULL COMMENT 'End Time of Promotion',
  value DECIMAL(4,2) NULL DEFAULT 1,
  promotion_status tinyint NOT NULL DEFAULT '0' COMMENT 'Promotion Status: 0 Inactive, 1 Active',
  created_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation Time',
  modified_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last Modified Time'
) COMMENT='promotion';

-- Table structure for promotion product

CREATE TABLE IF NOT EXISTS promotion_product (
  promotion_product_id int PRIMARY KEY AUTO_INCREMENT COMMENT 'Promotion Product ID',
  promotion_id int NOT NULL COMMENT 'Promotion ID',
  product_id int NOT NULL COMMENT 'Product ID',
  discount_amount decimal(8,2) NOT NULL DEFAULT '0.00' COMMENT 'Discount Amount for the Product',
  FOREIGN KEY (promotion_id) REFERENCES promotion(promotion_id),
  FOREIGN KEY (product_id) REFERENCES product_info(product_id)
) COMMENT='promotion product';


-- Table structure for promotion rule


CREATE TABLE IF NOT EXISTS promotion_rule (
  promotion_rule_id int PRIMARY KEY AUTO_INCREMENT COMMENT 'Promotion Rule ID',
  promotion_id int NOT NULL COMMENT 'Promotion ID',
  rule_type tinyint NOT NULL COMMENT 'Rule Type: 1 Min Purchase Amount, 2 Min Purchase Quantity, etc.',
  rule_value decimal(8,2) NOT NULL COMMENT 'Rule Value',
  FOREIGN KEY (promotion_id) REFERENCES promotion(promotion_id)
) COMMENT='promotion rule';



-- Table structure for slide


CREATE TABLE IF NOT EXISTS home_slide (
  slide_id int PRIMARY KEY AUTO_INCREMENT COMMENT 'slide ID',
  first_con varchar(255) COMMENT 'first line content',
  second_con varchar(255) COMMENT 'second line content',
  third_con varchar(255) COMMENT 'third line content',
  fouth_con varchar(255) COMMENT 'fouth line content',
  slide_image varchar(255) COMMENT 'image url',
  redirect_url varchar(255) COMMENT 'redirect url'
) COMMENT='index page slide table';


CREATE TABLE IF NOT EXISTS color (
  color_id int PRIMARY KEY AUTO_INCREMENT COMMENT ' color ID',
  color_name varchar(50)
) COMMENT='color';


-- 2024-05-17
CREATE TABLE IF NOT EXISTS  application (
    app_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id int NOT NULL,
    app_name VARCHAR(255) NOT NULL,
    submit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    app_details TEXT,
    reason VARCHAR(255),
    status TINYINT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);


-- 2024-05-29
CREATE TABLE news (
    news_id INT AUTO_INCREMENT PRIMARY KEY,
    title TEXT,
    content TEXT,
    author VARCHAR(255),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    publish_status TINYINT(1) NOT NULL DEFAULT 0
);

-- chat_sessions table
CREATE TABLE chat_sessions (
    session_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    employee_id INT,
    status VARCHAR(20) DEFAULT 'waiting',
    FOREIGN KEY (customer_id) REFERENCES users(user_id),
    FOREIGN KEY (employee_id) REFERENCES users(user_id)
);


-- messages table
CREATE TABLE chat (
    chat_id INT PRIMARY KEY AUTO_INCREMENT,
    session_id INT,
    sender_id INT,
    chat TEXT,
    sender_name VARCHAR(50) NULL DEFAULT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id),
    FOREIGN KEY (sender_id) REFERENCES users(user_id)
);


-- scheduled tasks
CREATE TABLE monthly_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    month_year VARCHAR(7)
);

CREATE TABLE refund_applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id int,
    order_sn bigint,
    product_id int,
    order_amount int,
    status int,
    refund_way int,
    reason varchar(300),
    comment varchar(300),
    reviewer_id varchar(300),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	
);
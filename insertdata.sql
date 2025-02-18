ALTER TABLE product_info DROP INDEX ux_ordersn;

ALTER TABLE u_managers ADD COLUMN `pro_img` VARCHAR(255) NULL DEFAULT NULL AFTER `email`;
ALTER TABLE u_staff ADD COLUMN `pro_img` VARCHAR(255) NULL DEFAULT NULL AFTER `email`;

ALTER TABLE u_managers DROP COLUMN `title`;

ALTER TABLE `bsmpdb`.`warehouse_info` 
CHANGE COLUMN `Region` `region` VARCHAR(255) NOT NULL COMMENT 'District ID from area table' ;
-- 2024-05-6
ALTER TABLE `bsmpdb`.`warehouse_info` 
CHANGE COLUMN `warehouse_name` `warehouse_name` VARCHAR(255) NOT NULL COMMENT 'Warehouse Name' ,
CHANGE COLUMN `warehouse_phone` `warehouse_phone` VARCHAR(255) NOT NULL COMMENT 'Warehouse Phone' ,
CHANGE COLUMN `contact` `contact` VARCHAR(50) NOT NULL COMMENT 'Warehouse Contact Person' ;
ALTER TABLE `bsmpdb`.`warehouse_info` 
CHANGE COLUMN `zip` `zip` INT NOT NULL COMMENT 'Zip Code' ;

-- 2024-05-07 
ALTER TABLE `bsmpdb`.`order_cart` 
ADD COLUMN `color` VARCHAR(45) NULL AFTER `price`,
ADD COLUMN `size` VARCHAR(45) NULL AFTER `color`;
ADD COLUMN `discount` DECIMAL(8,2) NULL AFTER `price`;

-- 2024-05-10 
ALTER TABLE `bsmpdb`.`order_customer_addr` 
CHANGE COLUMN `Region` `region` VARCHAR(255) NOT NULL COMMENT 'District ID from area table' ;

ALTER TABLE `bsmpdb`.`order_cart` 
ADD COLUMN `selected` INT NULL DEFAULT '0' AFTER `if_paid`;


ALTER TABLE `bsmpdb`.`order_detail` 
ADD COLUMN `size` VARCHAR(45) NULL AFTER `color`,
CHANGE COLUMN `fee_money` `order_discount` DECIMAL(8,2) NOT NULL DEFAULT '0.00' COMMENT 'Discount Apportioned Amount' AFTER `order_cost`,
CHANGE COLUMN `weight` `color` VARCHAR(50) NULL COMMENT 'Product Weight' ;

-- 2024-05-11 
ALTER TABLE `bsmpdb`.`orders` 
CHANGE COLUMN `order_status` `order_status` TINYINT NOT NULL DEFAULT '1' COMMENT 'Order Status' ;

ALTER TABLE shipping_info_fee ADD COLUMN `code` VARCHAR(45) NULL AFTER `price`;
-- pleae update order_detail table


insert into shipping_info (ship_name,ship_contact,telphone) values ('BsmpPost','bp','02111111');
insert into shipping_info_fee (ship_id,ship_mode,destination,price) values (1,'standard','Canada','60'),(1,'standard','Australia','40'),(1,'standard','New Zealand','10');


insert into users(username,password,role,status) values('admin','2daceebc4e31654d326ae7889b397ed50ff7e5afff374d1f89525865fd87efe0',0,'0');
insert into u_admins (user_id,first_name,last_name,gender,position,phone_number,email) values('1','admin','admin',1,'administrator','111111111','admin@gmail.com');


-- 2024-05-17
CREATE TABLE application (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    enterprise_number VARCHAR(255) NOT NULL,
    application_name VARCHAR(255) NOT NULL,
    submit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    application_details TEXT,
    status TINYINT DEFAULT 0
);

-- 2024-05-18
ALTER TABLE application
ADD COLUMN comment TEXT;




--2024-05-18

ALTER TABLE `order_customer_addr` CHANGE COLUMN `zip` `zip` INT NOT NULL COMMENT 'Zip Code' ;

ALTER TABLE promotion  ADD COLUMN `value` DECIMAL(4,2) NULL DEFAULT 1 after `end_time`;



-- 2024-05-20

please drop payinfo and update order_sn

ALTER TABLE `order_detail` DROP FOREIGN KEY `order_detail_ibfk_1`;
ALTER TABLE `order_detail` CHANGE COLUMN `order_sn` `order_sn` BIGINT NOT NULL COMMENT 'Order sn ' ;


ALTER TABLE `order_detail` ADD CONSTRAINT `order_detail_ibfk_1` FOREIGN KEY (`order_sn`) REFERENCES `orders` (`order_sn`);



-- 2024-05-22

ALTER TABLE u_business_customers ADD COLUMN `credit_used` INT NULL DEFAULT '0' AFTER `credit_limited`;


-- 2024-05-24
ALTER TABLE customer_point_log  ADD COLUMN `reason` VARCHAR(255) NULL DEFAULT '' AFTER `create_time`;
ALTER TABLE customer_point_log CHANGE COLUMN `source` `source` VARCHAR(50) NOT NULL COMMENT 'Point Source: 0 Order' ;

-- 2024-05-27
CREATE TABLE IF NOT EXISTS  application (
    app_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id int NOT NULL,
    app_name VARCHAR(255) NOT NULL,
    submit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    app_details TEXT,
    reason VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    status TINYINT DEFAULT 0
);

update u_business_customers

-- 2024-05-29
CREATE TABLE news (
    news_id INT AUTO_INCREMENT PRIMARY KEY,
    title TEXT,
    content TEXT,
    author VARCHAR(255),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    publish_status TINYINT(1) NOT NULL DEFAULT 0
);

-- 2024-05-30
ALTER TABLE news
ADD COLUMN publish_status TINYINT(1) NOT NULL DEFAULT 0;



--2024-05- 28

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
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id),
    FOREIGN KEY (sender_id) REFERENCES users(user_id)
);





ALTER TABLE `product_comment` DROP COLUMN `title`;
ALTER TABLE `product_comment` ADD COLUMN `rate` INT NULL DEFAULT 0 AFTER `content`;


ALTER TABLE `customer_point_log` CHANGE COLUMN `refer_number` `refer_number` BIGINT NOT NULL DEFAULT '0' COMMENT 'Related order number from Point Source' ;



ALTER TABLE `bsmpdb`.`product_comment` ADD COLUMN `order_sn` BIGINT NULL AFTER `comment_id`;


ALTER TABLE `refund_applications` ADD COLUMN `qtn` INT NULL AFTER `product_id`,ADD COLUMN `size` VARCHAR(45) NULL AFTER `product_price`,ADD COLUMN `color` VARCHAR(45) NULL AFTER `size`,CHANGE COLUMN `order_amount` `product_price` INT NULL DEFAULT NULL ;


ALTER TABLE `orders` ADD COLUMN `gst` DECIMAL(8,2) NULL DEFAULT '0.00' AFTER `shipping_money`;

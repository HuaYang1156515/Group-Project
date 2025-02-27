

# Belmont Station Merino & Possum

Welcome to the Belmont Station Merino & Possum online system! This application is designed to upgrade and streamline the management system for Belmont Station Merino & Possum, a clothing company in New Zealand. The company specializes in merino and possum merino products, aiming to provide high-quality products and services to its customers.

## Features

- User authentication and authorization
- Management of customers, orders, and inventory
- User-friendly homepage for product showcasing and promotion
- Seamless payment processing
- Comprehensive reporting and data analysis
- Real-time notification system
- Customer loyalty points system
- Support for international orders and various shipping options
- Corporate client bulk order management and credit limit management
- Detailed return and exchange policies and contact information


## Tech Stack

- Flask 
- MySQL 
- Bootstrap 
- JavaScript 
- Sass 
- HTML 


## Project Structure

The project follows the following directory structure:

- **/common:** Common functionalities and utility modules.
- **/config:** Configuration files and settings.
- **/controllers:** Contains controllers for handling different functionalities.
- **/models:** Modules for defining database models.
- **/services:** Modules for various services.
- **/static:** Contains static files such as CSS, JS, images, fonts, and SASS files.
- **/templates:** Holds HTML templates for rendering views.
- **app.py:** The main entry point for the Flask application.
- **requirements.txt:** Lists the required Python packages.
- **README.md:** This file, providing an overview of the project.
- **.gitignore:** Specifies files and directories that Git should ignore.
- **BsmpDB.sql:** SQL script for the database schema.
- **ERD.pdf:** Entity-Relationship Diagram in PDF format.
- **erd.png** Entity-Relationship Diagram in PNG format.
- **insertdata.sql:** SQL script for inserting initial data.


    - COMP639S1_PROJECT_2_GROUP_K
      - /common
        - __pycache__
        - BuyXGetY.py
        - hashing.py
        - strategy.py
        - validation.py
      - /config
        - __pycache__
        - connect.py
        - send_message.py
        - setting.py
      - /controllers
        - __pycache__
        - back_controller.py
        - front_controller.py
      - /models
        - __pycache__
        - user_model.py
      - /services
        - __pycache__
        - app_service.py
        - back_service.py
        - dbText.py
        - front_service.py
      - /static
        - /backend
          - /css
          - /fonts
          - /imgs
          - /js
          - /sass
        - /frontend
          - /css
          - /fonts
          - /imgs
          - /js
          - /sass
      - /templates
        - /backend
          - /account
          - /chat
          - /corporate
          - /news
          - /order
          - /product
          - /promotion
          - /system
          - base.html
          - index.html
          - page_login.html
        - /frontend
          - /business
          - /categories
          - /help
          - /order
          - /product
          - base.html
          - index.html
          - page_account_addr.html
          - page_account.html
          - page_login_register.html
          - product.html
      - .gitignore
      - app.py
      - BsmpDB.sql
      - ERD.pdf
      - erd.png
      - insertdata.sql
      - README.md
      - requirements.txt
    

## Validation

- User Input Validation: Verification methods have been added to ensure that user inputs meet specific criteria, such as a minimum password length of 8 characters, consisting of both letters and numbers.
- Address Validation: Validation is in place to ensure that the addresses added by users are real and valid.
- Stock Availability: During order creation, validation ensures that stock is available when items are added to the cart and during the checkout process.
- User Access Control Validation: When users log in, they are directed to their respective dashboards based on their roles, such as admin, manager, staff, and customer.
- Data Format Validation: Ensuring all prices are in New Zealand dollars.
- Date and Time: All dates and times must follow the New Zealand format.
- Refund Validation: When users request a refund, the inputted quantity must be less than or equal to the purchased quantity. 
- User Identity Validation: When users make a purchase and payment, user identity verification is conducted. Normal customers can enjoy benefits such as redeeming credit points, getting discounts, or buy two get one free offers. However, corporate customers do not receive these benefits.

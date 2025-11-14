🛍️ Soko Hub - Online Marketplace MVP
Soko Hub is a minimal, fully-functional online marketplace built with Django where vendors can list products and customers can browse and purchase them. This MVP demonstrates a complete e-commerce workflow with role-based access control.

🚀 Live Demo
Coming soon...

📋 Project Overview
Soko Hub is built with a focus on simplicity and core functionality. It provides:

Vendor Features: Register, list products, manage inventory, view orders

Customer Features: Browse products, view details, place orders, track purchases

Admin Features: Full Django admin interface for management

🎯 Core User Stories
As a Vendor:
✅ I can register and list products for sale

✅ I can see orders for my products

✅ I can manage my product inventory

As a Customer:
✅ I can browse available products

✅ I can view product details

✅ I can place orders for products

🛠️ Tech Stack
Backend: Django 4.x

Database: SQLite (Development) / PostgreSQL (Production-ready)

Frontend: Bootstrap 5, HTML5, CSS3

Authentication: Django Built-in Auth with Custom User Model

File Handling: Django Media Files for product images

Forms: Django Crispy Forms with Bootstrap 5

📁 Project Structure
text
sokohub/
├── accounts/          # User authentication & profiles
├── products/          # Product catalog & vendor dashboard
├── orders/            # Order management & checkout
├── templates/         # HTML templates
├── static/           # CSS, JS, images
├── media/            # Uploaded product images
└── sokohub/          # Project settings
🏗️ Core Models
User: Custom user model with vendor/customer roles

Product: Products with inventory, pricing, and vendor association

Order: Customer orders with status tracking

OrderItem: Individual items within orders

🚀 Quick Start
Prerequisites
Python 3.8+

pip

Virtual Environment

Installation
Clone the repository

bash
git clone https://github.com/yourusername/soko-hub.git
cd soko-hub
Set up virtual environment

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies

bash
pip install -r requirements.txt
Run migrations

bash
python manage.py makemigrations
python manage.py migrate
Create superuser

bash
python manage.py createsuperuser
Run development server

bash
python manage.py runserver
Access the application

Main site: http://127.0.0.1:8000

Admin panel: http://127.0.0.1:8000/admin

👥 User Roles & Features
Vendor Account
Register as vendor

Add/edit products

Manage inventory

View customer orders

Vendor dashboard with analytics

Customer Account
Register as customer

Browse product catalog

View product details

Place orders

View order history

🎨 Key Pages
Homepage: Featured products and marketplace introduction

Product Listing: Browse all available products with search/sort

Product Detail: Detailed product view with purchase option

Vendor Dashboard: Overview of products and orders

Checkout: Simple one-page checkout process

Order Confirmation: Order summary and tracking

User Authentication: Clean login/registration pages

🔒 Security Features
Custom user model with role-based permissions

Django built-in authentication

Form validation and CSRF protection

Vendor/customer access control decorators

Secure file upload handling

📈 MVP Success Metrics
✅ Functional Requirements Met:

Two user types can register and login

Vendors can add and manage products

Customers can browse and purchase products

Order system works end-to-end

Role-based navigation and access control

✅ Technical Requirements Met:

Django project with 3 modular apps

Database with proper relationships

Clean, responsive Bootstrap UI

No critical errors or bugs

🚫 Out of Scope (Post-MVP)
Payment integration

Shopping cart (single product checkout)

Email notifications

Reviews and ratings

Advanced search/filters

Admin dashboard customization

Password reset functionality

Mobile app

🤝 Contributing
Fork the repository

Create your feature branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some AmazingFeature')

Push to the branch (git push origin feature/AmazingFeature)

Open a Pull Request

📝 License
This project is licensed under the MIT License - see the LICENSE.md file for details.

👨‍💻 Developer
Your Name

GitHub: @yourusername

Email: your.email@example.com

🙏 Acknowledgments
Django documentation and community

Bootstrap for the responsive UI components

Font Awesome for icons

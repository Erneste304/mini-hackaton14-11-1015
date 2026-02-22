# 🛍️ Soko Hub — Rwanda's Online Marketplace

> **Soko Hub** is a fully-functional online marketplace built with Django where vendors can list products and customers can browse, purchase, and manage their orders. This project demonstrates a complete e-commerce workflow with role-based access control, a simulated payment system, and a vendor approval flow.

---

## 🚀 Live Demo

> Coming soon... *(Deployment in progress)*

---

## 📋 Project Overview

Soko Hub is built with a focus on simplicity and core functionality. It provides distinct roles for vendors and customers, with a complete end-to-end order lifecycle.

| Role | Capabilities |
|------|-------------|
| 🏪 **Vendor** | Register, list products, manage inventory, receive order notifications, review & approve transactions |
| 🛒 **Customer** | Browse products, place orders, select payment method, simulate payment, track order history |
| 🔑 **Admin** | Full Django admin interface for user and content management |

---

## 🎯 Core User Stories

**As a Vendor:**
- ✅ Register and manage my business profile
- ✅ Add, edit, and delete products with images and stock control
- ✅ Receive real-time notifications for new paid orders
- ✅ View full transaction details before approving
- ✅ Approve or cancel customer orders

**As a Customer:**
- ✅ Browse and search available products by category
- ✅ Add products to cart or checkout directly
- ✅ Select a payment method (MTN Mobile Money, Tigo Cash, or Virtual Card)
- ✅ Simulate payment and await vendor approval
- ✅ View detailed order history and payment status
- ✅ Update my profile with personal information and preferences

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 5.x (Python) |
| **Database** | SQLite (Development) / PostgreSQL (Production-ready) |
| **Frontend** | Bootstrap 5, HTML5, CSS3 |
| **Forms** | Django Crispy Forms with Bootstrap 5 |
| **Authentication** | Django Built-in Auth with Custom User Model |
| **File Handling** | Django Media Files for product & profile images |
| **Icons** | Font Awesome 6 |

---

## 📁 Project Structure

```
mini-hackaton14-11-1015/
│
├── sokohub/                        # Django project root
│   │
│   ├── accounts/                   # User management & profiles
│   │   ├── models.py               # Custom User model (vendor/customer roles)
│   │   ├── views.py                # Login, register, profile update
│   │   ├── forms.py                # Registration & Profile forms
│   │   ├── decorators.py           # Role-based access decorators
│   │   └── urls.py
│   │
│   ├── products/                   # Product catalog & vendor tools
│   │   ├── models.py               # Product model with categories & stock
│   │   ├── views.py                # Product CRUD, vendor dashboard
│   │   └── urls.py
│   │
│   ├── orders/                     # Order lifecycle management
│   │   ├── models.py               # Order, OrderItem, payment fields
│   │   ├── views.py                # Checkout, payment, approval, order detail
│   │   ├── forms.py                # Checkout form with payment method
│   │   └── urls.py
│   │
│   ├── cart/                       # Shopping cart session management
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   │
│   ├── notifications/              # In-app notification system
│   │   ├── models.py               # Notification model with target_url
│   │   ├── views.py                # Mark as read & redirect
│   │   └── urls.py
│   │
│   ├── templates/                  # HTML templates (per app)
│   │   ├── base.html               # Global layout with nav, footer & app links
│   │   ├── accounts/
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   └── profile.html        # Profile + Privacy settings
│   │   ├── orders/
│   │   │   ├── checkout.html
│   │   │   ├── order_confirmation.html
│   │   │   ├── order_detail.html   # Customer order status view
│   │   │   ├── customer_orders.html
│   │   │   ├── vendor_orders.html
│   │   │   └── transaction_detail.html  # Vendor review & approve
│   │   └── includes/
│   │       └── notifications_dropdown.html
│   │
│   ├── static/                     # CSS, JavaScript, images
│   ├── media/                      # Uploaded files (product & profile images)
│   └── sokohub/                    # Project settings & main URLs
│       ├── settings.py
│       ├── urls.py
│       └── context_processors.py
│
├── Venv/                           # Python virtual environment
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🏗️ Core Models

| Model | Description |
|-------|-------------|
| `User` | Custom user model with `vendor` / `customer` role, phone, profile picture, location |
| `Product` | Products with category, stock level, price, vendor association, and images |
| `Order` | Customer orders with `payment_method`, `payment_status`, `transaction_id`, and approval status |
| `OrderItem` | Individual line items within an order |
| `Notification` | In-app alerts with a `target_url` for direct page linking |

---

## 💳 Order Status Flow

```
pending  ──►  paid  ──►  approved
                │
                └──►  cancelled
```

- **Pending**: Order placed, payment not yet made.
- **Paid**: Customer simulated payment. Vendor is notified.
- **Approved**: Vendor reviewed and confirmed the transaction.
- **Cancelled**: Either party cancelled the order.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- `pip`
- Virtual Environment

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Erneste304/mini-hackaton14-11-1015.git
cd mini-hackaton14-11-1015

# 2. Set up a virtual environment
python -m venv Venv
source Venv/bin/activate        # Linux/Mac
Venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply database migrations
cd sokohub
python manage.py makemigrations
python manage.py migrate

# 5. Create a superuser (admin)
python manage.py createsuperuser

# 6. Run the development server
python manage.py runserver
```

### Access

| Page | URL |
|------|-----|
| Main Site | http://127.0.0.1:8000 |
| Admin Panel | http://127.0.0.1:8000/admin |
| My Profile | http://127.0.0.1:8000/accounts/profile/ |

---

## 👥 User Roles & Features

### 🏪 Vendor Account
- Register with a vendor account type
- Add, edit, and delete products with images and stock control
- Receive in-app notifications when a customer pays for an order
- Click the notification to go directly to the **Transaction Detail** page
- Approve or cancel the transaction
- View overall vendor order history

### 🛒 Customer Account
- Register with a customer account type
- Browse the product catalog by category
- Add items to cart and checkout single or multiple items
- Choose from available payment methods: **MTN Mobile Money**, **Tigo Cash**, **Virtual Card**
- Simulate the payment process
- View the status of all past orders with detailed transaction info
- Update profile: name, email, phone, address, profile picture

---

## 🎨 Key Pages

| Page | Who Sees It | Description |
|------|------------|-------------|
| Homepage | Everyone | Featured products and marketplace hero section |
| Product Listing | Everyone | Browse all products with filters |
| Checkout | Customer | Select items, delivery info, and payment method |
| Order Confirmation | Customer | View order summary and trigger payment |
| Order Detail | Customer | View payment status, items, and transaction ID |
| My Orders | Customer | Order history with links to detail pages |
| Transaction Detail | Vendor | Full order review, payment info, approve/cancel |
| Vendor Orders | Vendor | Overview of all orders for the vendor's products |
| My Profile | Both | Update personal info, picture, and privacy settings |
| Notifications | Both | Real-time alert dropdown with direct order links |

---

## 🔒 Security Features

- Custom user model with role-based permissions (`vendor_required`, `customer_required` decorators)
- Django built-in authentication with CSRF protection
- Form validation on all input forms
- Secure file upload handling for product and profile images
- Session-based cart management

---

## 📈 Feature Status

| Feature | Status |
|---------|--------|
| User Registration (Vendor/Customer) | ✅ Done |
| Product CRUD (Vendor) | ✅ Done |
| Shopping Cart | ✅ Done |
| Checkout with Payment Method Selection | ✅ Done |
| Simulated Payment Flow | ✅ Done |
| Vendor Order Approval | ✅ Done |
| In-App Notifications with Deep Links | ✅ Done |
| User Profile Editing | ✅ Done |
| Privacy & Security Settings | ✅ Done |
| App Store Footer Links | ✅ Done |
| Payment Gateway Integration | 🔜 Post-MVP |
| Email Notifications | 🔜 Post-MVP |
| Product Reviews & Ratings | 🔜 Post-MVP |
| Password Reset Flow | 🔜 Post-MVP |
| Mobile App | 🔜 Post-MVP |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Developer

**Erneste304Tech**

- 🐙 GitHub: [@Erneste304](https://github.com/Erneste304)
- 📧 Email: support@sokohub.rw
- 🌍 Location: Kigali, Rwanda

---

## 🙏 Acknowledgments

- [Django](https://djangoproject.com) — The web framework for perfectionists with deadlines.
- [Bootstrap 5](https://getbootstrap.com) — Responsive UI components.
- [Font Awesome](https://fontawesome.com) — Beautiful icons.
- The open-source community for their incredible tools and libraries.

---

> *© 2026 Soko Hub by Erneste304Tech. All rights reserved.*

# EcoHub - Your Dynamic E-commerce Platform

## Introduction:

Welcome to EcoHub, a comprehensive Django-powered E-commerce website. This platform enables users to effortlessly sell products, ensuring a seamless and secure shopping experience.

## Features:

- OAuth2 Integration: Sign in with Google, Facebook, and Twitter for a hassle-free experience.
- Cart and Wishlist: Enjoy intuitive shopping with dynamic cart and wishlist functionalities.
- Order Email Services: Stay informed with efficient order email notifications.
- PayPal Integration: Secure transactions through seamless PayPal payment integration.
- Custom Admin Panel: Take control with a dynamic admin panel, allowing changes to categories, banners, products, and templates.
- Order Management: Effortlessly manage and track orders to enhance your business efficiency.

## Getting Started:

1. Clone the repository:

```sh
git clone https://github.com/hrushikesh009/Ecommerce-Hub.git
```

2. Install dependencies:

```sh
pip install -r requirements.txt
```

3. Database setup:

   - Configure your database settings in `settings.py`.
   - Run migrations:

```sh
python manage.py makemigrations
python manage.py migrate
```

4. Set up OAuth2:

   - Obtain API keys from Google, Facebook, and Twitter.
   - Update the keys in `settings.py`.

5. Run the server:

```sh
python manage.py runserver
```

6. Access the application:

Visit [http://localhost:8000/](http://localhost:8000/) in your browser.

## Customization:

Explore the dynamic admin panel at [http://localhost:8000/admin/](http://localhost:8000/admin/) to customize categories, banners, products, and templates.

## Order Management:

Effortlessly manage and track orders in the admin panel for enhanced business efficiency.

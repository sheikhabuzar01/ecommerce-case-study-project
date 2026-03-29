# NOVU Ecommerce Store

A simple ecommerce website built with **Python Flask**, **HTML**, **CSS**, and **JavaScript**.

## Features
- Product listing with category filter & search
- Product detail page with related products
- Shopping cart (add, update, remove items)
- Checkout form with order confirmation
- Fully responsive dark-themed UI

## Project Structure
```
ecommerce/
├── app.py                  # Flask backend
├── requirements.txt
├── templates/
│   ├── base.html           # Shared layout + navbar
│   ├── index.html          # Home / product listing
│   ├── product.html        # Product detail
│   ├── cart.html           # Shopping cart
│   ├── checkout.html       # Checkout form
│   └── success.html        # Order confirmation
└── static/
    ├── css/style.css
    └── js/main.js
```

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python app.py

# 3. Open in browser
# http://127.0.0.1:5000
```

## API Endpoints
| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Home page (supports `?category=` and `?search=`) |
| GET | `/product/<id>` | Product detail |
| GET | `/cart` | Cart page |
| GET/POST | `/checkout` | Checkout |
| POST | `/api/cart/add` | Add item to cart |
| POST | `/api/cart/remove` | Remove item |
| POST | `/api/cart/update` | Update quantity |
| GET | `/api/cart/count` | Get cart item count |

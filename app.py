from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json

app = Flask(__name__)
app.secret_key = "ecommerce_secret_key_2024"

# ── Sample product data ──────────────────────────────────────────────────────
PRODUCTS = [
    {"id": 1, "name": "Wireless Headphones", "price": 79.99,  "category": "Electronics",
     "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80",
     "description": "Premium sound quality with 30-hour battery life.", "stock": 15},
    {"id": 2, "name": "Running Sneakers",    "price": 59.99,  "category": "Footwear",
     "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80",
     "description": "Lightweight and comfortable for every run.", "stock": 20},
    {"id": 3, "name": "Leather Backpack",    "price": 89.99,  "category": "Bags",
     "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&q=80",
     "description": "Genuine leather with multiple compartments.", "stock": 10},
    {"id": 4, "name": "Smart Watch",         "price": 149.99, "category": "Electronics",
     "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&q=80",
     "description": "Track fitness, notifications & more.", "stock": 8},
    {"id": 5, "name": "Sunglasses",          "price": 34.99,  "category": "Accessories",
     "image": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=400&q=80",
     "description": "UV400 protection with polarised lenses.", "stock": 25},
    {"id": 6, "name": "Yoga Mat",            "price": 29.99,  "category": "Sports",
     "image": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400&q=80",
     "description": "Non-slip, eco-friendly, 6mm thick.", "stock": 30},
    {"id": 7, "name": "Coffee Maker",        "price": 49.99,  "category": "Kitchen",
     "image": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&q=80",
     "description": "Brew the perfect cup every morning.", "stock": 12},
    {"id": 8, "name": "Denim Jacket",        "price": 69.99,  "category": "Clothing",
     "image": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=400&q=80",
     "description": "Classic fit, premium denim.", "stock": 18},
]

# ── Helpers ──────────────────────────────────────────────────────────────────
def get_cart():
    return session.get("cart", {})

def save_cart(cart):
    session["cart"] = cart
    session.modified = True

def cart_total(cart):
    total = 0
    for pid, qty in cart.items():
        p = next((x for x in PRODUCTS if x["id"] == int(pid)), None)
        if p:
            total += p["price"] * qty
    return round(total, 2)

def cart_count(cart):
    return sum(cart.values())

# ── Routes ───────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    category = request.args.get("category", "All")
    search   = request.args.get("search", "").lower()
    products = PRODUCTS
    if category and category != "All":
        products = [p for p in products if p["category"] == category]
    if search:
        products = [p for p in products if search in p["name"].lower() or search in p["description"].lower()]
    categories = ["All"] + sorted({p["category"] for p in PRODUCTS})
    return render_template("index.html", products=products, categories=categories,
                           active_category=category, search=search,
                           cart_count=cart_count(get_cart()))

@app.route("/product/<int:pid>")
def product_detail(pid):
    product = next((p for p in PRODUCTS if p["id"] == pid), None)
    if not product:
        return redirect(url_for("index"))
    related = [p for p in PRODUCTS if p["category"] == product["category"] and p["id"] != pid][:3]
    return render_template("product.html", product=product, related=related,
                           cart_count=cart_count(get_cart()))

@app.route("/cart")
def cart():
    c = get_cart()
    items = []
    for pid, qty in c.items():
        p = next((x for x in PRODUCTS if x["id"] == int(pid)), None)
        if p:
            items.append({**p, "qty": qty, "subtotal": round(p["price"] * qty, 2)})
    return render_template("cart.html", items=items, total=cart_total(c),
                           cart_count=cart_count(c))

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    c = get_cart()
    if not c:
        return redirect(url_for("cart"))
    items = []
    for pid, qty in c.items():
        p = next((x for x in PRODUCTS if x["id"] == int(pid)), None)
        if p:
            items.append({**p, "qty": qty, "subtotal": round(p["price"] * qty, 2)})
    if request.method == "POST":
        save_cart({})
        return render_template("success.html", total=cart_total(c))
    return render_template("checkout.html", items=items, total=cart_total(c),
                           cart_count=cart_count(c))

# ── API endpoints ────────────────────────────────────────────────────────────
@app.route("/api/cart/add", methods=["POST"])
def api_cart_add():
    data = request.get_json()
    pid  = str(data.get("product_id"))
    qty  = int(data.get("quantity", 1))
    cart = get_cart()
    cart[pid] = cart.get(pid, 0) + qty
    save_cart(cart)
    return jsonify({"success": True, "cart_count": cart_count(cart), "cart_total": cart_total(cart)})

@app.route("/api/cart/remove", methods=["POST"])
def api_cart_remove():
    pid  = str(request.get_json().get("product_id"))
    cart = get_cart()
    cart.pop(pid, None)
    save_cart(cart)
    return jsonify({"success": True, "cart_count": cart_count(cart), "cart_total": cart_total(cart)})

@app.route("/api/cart/update", methods=["POST"])
def api_cart_update():
    data = request.get_json()
    pid  = str(data.get("product_id"))
    qty  = int(data.get("quantity", 1))
    cart = get_cart()
    if qty <= 0:
        cart.pop(pid, None)
    else:
        cart[pid] = qty
    save_cart(cart)
    return jsonify({"success": True, "cart_count": cart_count(cart), "cart_total": cart_total(cart)})

@app.route("/api/cart/count")
def api_cart_count():
    cart = get_cart()
    return jsonify({"count": cart_count(cart)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

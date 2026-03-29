import json
import pytest
from app import app, PRODUCTS, cart_total, cart_count


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def add_item(client, product_id, quantity=1):
    return client.post(
        "/api/cart/add",
        data=json.dumps({"product_id": product_id, "quantity": quantity}),
        content_type="application/json",
    ).get_json()


def cart_post(client, route, product_id, **kwargs):
    return client.post(
        f"/api/cart/{route}",
        data=json.dumps({"product_id": product_id, **kwargs}),
        content_type="application/json",
    ).get_json()


# ── Helpers ───────────────────────────────────────────────

def test_cart_count():
    assert cart_count({}) == 0
    assert cart_count({"1": 3}) == 3
    assert cart_count({"1": 2, "2": 5}) == 7

def test_cart_total():
    assert cart_total({}) == 0.0
    assert cart_total({"1": 2}) == 159.98   # $79.99 × 2
    assert cart_total({"1": 1, "2": 1}) == 139.98
    assert cart_total({"999": 5}) == 0.0    # invalid product


# ── Pages ─────────────────────────────────────────────────

def test_home(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Wireless Headphones" in res.data

def test_category_filter(client):
    res = client.get("/?category=Electronics")
    assert b"Smart Watch" in res.data
    assert b"Running Sneakers" not in res.data

def test_search(client):
    assert b"Yoga Mat" in client.get("/?search=yoga").data
    assert b"No products found" in client.get("/?search=xyzxyz").data

def test_product_detail(client):
    assert client.get("/product/1").status_code == 200
    assert client.get("/product/9999").status_code == 302  # redirect

def test_cart_page(client):
    assert client.get("/cart").status_code == 200

def test_checkout_redirect_when_empty(client):
    assert client.get("/checkout").status_code == 302

def test_checkout_with_items(client):
    add_item(client, 1)
    assert client.get("/checkout").status_code == 200


# ── Cart API ──────────────────────────────────────────────

def test_add_to_cart(client):
    data = add_item(client, 1, quantity=2)
    assert data["success"] is True
    assert data["cart_count"] == 2
    assert data["cart_total"] == 159.98

def test_add_accumulates(client):
    add_item(client, 1)
    data = add_item(client, 1)
    assert data["cart_count"] == 2

def test_remove_from_cart(client):
    add_item(client, 1)
    data = cart_post(client, "remove", 1)
    assert data["cart_count"] == 0

def test_update_cart(client):
    add_item(client, 1)
    assert cart_post(client, "update", 1, quantity=5)["cart_count"] == 5
    assert cart_post(client, "update", 1, quantity=0)["cart_count"] == 0

def test_cart_count_api(client):
    assert client.get("/api/cart/count").get_json()["count"] == 0
    add_item(client, 1, quantity=3)
    assert client.get("/api/cart/count").get_json()["count"] == 3


# ── Checkout ──────────────────────────────────────────────

def test_checkout_flow(client):
    add_item(client, 1)
    res = client.post("/checkout", data={"first_name": "John"})
    assert res.status_code == 200
    assert b"Order Placed" in res.data
    assert client.get("/api/cart/count").get_json()["count"] == 0


# ── Product data ──────────────────────────────────────────

def test_product_data():
    ids = [p["id"] for p in PRODUCTS]
    assert len(ids) == len(set(ids))                        # unique IDs
    assert all(p["price"] > 0 for p in PRODUCTS)           # positive prices
    assert all(p["stock"] >= 0 for p in PRODUCTS)          # non-negative stock
    required = {"id", "name", "price", "category", "image", "description", "stock"}
    assert all(required.issubset(p.keys()) for p in PRODUCTS)
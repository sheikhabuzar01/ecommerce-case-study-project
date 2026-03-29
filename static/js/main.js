// ── Cart badge update ────────────────────────────────────
function updateBadge(count) {
  const badge = document.getElementById("cart-badge");
  if (badge) {
    badge.textContent = count;
    badge.style.transform = "scale(1.4)";
    setTimeout(() => badge.style.transform = "scale(1)", 200);
  }
}

// ── Toast notification ───────────────────────────────────
function showToast(msg) {
  const t = document.getElementById("toast");
  if (!t) return;
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 2500);
}

// ── Add to cart (global) ─────────────────────────────────
async function addToCart(productId, qty = 1) {
  try {
    const res = await fetch("/api/cart/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId, quantity: qty }),
    });
    const data = await res.json();
    if (data.success) {
      updateBadge(data.cart_count);
      showToast("✓ Added to cart!");
    }
  } catch (err) {
    showToast("Something went wrong.");
  }
}

// ── Refresh badge on load ────────────────────────────────
(async function () {
  try {
    const res  = await fetch("/api/cart/count");
    const data = await res.json();
    updateBadge(data.count);
  } catch (_) {}
})();

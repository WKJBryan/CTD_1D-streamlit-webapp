# CTD 1D — Streamlit App (Customer & Cashier • Inventory‑Based Dynamic Pricing)
## How the piecewise dynamic pricing works (hidden from customer)

Let each item i have **remaining ratio** `r_i = stock_now_i / stock_initial_i`. Compute the mean of remaining ratios across all items: `r̄`. Define the item’s **scarcity delta** `Δ = r̄ − r_i`. Larger positive `Δ` ⇒ this item is relatively more depleted.

**Markup tiers (guaranteed 5–20%):**

* `Δ ≤ 0.00` → **+5%** (not scarcer than average)
* `0.00 < Δ ≤ 0.10` → **+8%**
* `0.10 < Δ ≤ 0.20` → **+12%**
* `0.20 < Δ ≤ 0.30` → **+17%**
* `Δ  > 0.30` → **+20%** (much scarcer than average)

These numbers are easy to tune in one table.

---

## `app.py` (drop‑in)

```python
# app.py — CTD 1D Streamlit (Customer & Cashier • Inventory‑Based Dynamic Pricing)
# -------------------------------------------------------------------------------
# • Two tabs: Customer (shop) and Cashier (stock dashboard)
# • Dynamic price rises 5%→20% as an item’s remaining stock ratio falls vs others
# • Compulsory service charge 10% and GST 9% at checkout
# • Uses only Streamlit; all state kept in st.session_state

import streamlit as st

# -----------------------------
# Constants
# -----------------------------
SERVICE_RATE = 0.10  # compulsory
GST_RATE = 0.09      # compulsory

# Local image (use same image for demo; replace with your own file paths if needed)
DEFAULT_IMAGE = "./7619c712-e3d7-471d-8cc3-d03d4c0509bd.png"

# -----------------------------
# App state init
# -----------------------------

def init_state():
    if "products" not in st.session_state:
        # Each product: id, name, base_price, stock_init, stock_now, img
        st.session_state.products = [
            {"id": "umb_normal", "name": "Normal Umbrella", "base": 15.00, "stock_init": 40, "stock_now": 40, "img": DEFAULT_IMAGE},
            {"id": "umb_love",   "name": "Love Umbrella",   "base": 20.00, "stock_init": 30, "stock_now": 30, "img": DEFAULT_IMAGE},
            {"id": "umb_totoro", "name": "Totoro Umbrella", "base": 50.00, "stock_init": 10, "stock_now": 10, "img": DEFAULT_IMAGE},
        ]
    if "cart" not in st.session_state:
        st.session_state.cart = []  # {id, name, unit, qty}
    if "orders" not in st.session_state:
        st.session_state.orders = []  # archival receipts

# -----------------------------
# Pricing helpers (hidden from customers)
# -----------------------------

def remaining_ratio(p):
    if p["stock_init"] <= 0:
        return 0.0
    return max(0.0, p["stock_now"] / p["stock_init"])


def avg_remaining_ratio(products):
    if not products:
        return 0.0
    return sum(remaining_ratio(p) for p in products) / len(products)


def scarcity_delta(p, rbar):
    # Δ = r̄ − r_i (positive means this item is scarcer than average)
    return rbar - remaining_ratio(p)


def tiered_markup(delta):
    # Piecewise tiers: guarantees 5%..20%
    if delta <= 0.00:
        return 0.05
    elif delta <= 0.10:
        return 0.08
    elif delta <= 0.20:
        return 0.12
    elif delta <= 0.30:
        return 0.17
    else:
        return 0.20


def effective_unit_price(p, rbar):
    """Base price with hidden scarcity markup; customers see only the final number."""
    m = tiered_markup(scarcity_delta(p, rbar))
    return round(p["base"] * (1.0 + m), 2)

# -----------------------------
# Cart & totals
# -----------------------------

def add_to_cart(prod_id, qty):
    if qty <= 0:
        return
    # Find product
    p = next((x for x in st.session_state.products if x["id"] == prod_id), None)
    if not p:
        return
    # Clamp by available stock
    qty = min(qty, p["stock_now"])
    if qty <= 0:
        return
    # Effective unit at time of adding (locks current price)
    rbar = avg_remaining_ratio(st.session_state.products)
    unit = effective_unit_price(p, rbar)
    st.session_state.cart.append({"id": p["id"], "name": p["name"], "unit": unit, "qty": int(qty)})


def compute_subtotal(cart):
    return sum(item["unit"] * item["qty"] for item in cart)


def finalize_checkout():
    if not st.session_state.cart:
        return None
    # Reduce stock
    for item in st.session_state.cart:
        p = next((x for x in st.session_state.products if x["id"] == item["id"]), None)
        if p:
            p["stock_now"] = max(0, p["stock_now"] - item["qty"])
    # Totals with compulsory charges
    subtotal = compute_subtotal(st.session_state.cart)
    service = subtotal * SERVICE_RATE
    taxable = subtotal + service
    gst = taxable * GST_RATE
    grand = taxable + gst
    receipt = {
        "lines": st.session_state.cart.copy(),
        "subtotal": round(subtotal, 2),
        "service": round(service, 2),
        "gst": round(gst, 2),
        "grand": round(grand, 2),
    }
    st.session_state.orders.append(receipt)
    st.session_state.cart = []
    return receipt

# -----------------------------
# UI components
# -----------------------------

def product_card(p, rbar, key_prefix=""):
    # Card-like layout: image, name, dynamic price, qty, button
    with st.container(border=True):
        cols = st.columns([1, 2])
        with cols[0]:
            try:
                st.image(p["img"], use_column_width=True)
            except Exception:
                st.markdown("(image)")
        with cols[1]:
            st.markdown(f"### {p['name']}")
            price = effective_unit_price(p, rbar)
            st.markdown(f"**${price:.2f}**")
            st.markdown(f"Stock: {p['stock_now']} left")
            q = st.number_input("Qty", min_value=0, max_value=p["stock_now"], step=1, key=f"qty_{key_prefix}_{p['id']}")
            if st.button("Add to cart", key=f"add_{key_prefix}_{p['id']}"):
                add_to_cart(p["id"], q)
                st.success("Added to cart.")


def cart_panel():
    st.subheader("Your cart")
    if not st.session_state.cart:
        st.info("Cart is empty.")
        return
    rows = []
    for i, item in enumerate(st.session_state.cart):
        rows.append({
            "Item": item["name"],
            "Unit": f"${item['unit']:.2f}",
            "Qty": item["qty"],
            "Line": f"${item['unit']*item['qty']:.2f}",
        })
    st.table(rows)

    subtotal = compute_subtotal(st.session_state.cart)
    service = subtotal * SERVICE_RATE
    gst = (subtotal + service) * GST_RATE
    grand = subtotal + service + gst

    st.markdown("### Total")
    st.write({
        "Subtotal": f"${subtotal:.2f}",
        "Service (10%)": f"${service:.2f}",
        "GST (9%)": f"${gst:.2f}",
        "Grand Total": f"${grand:.2f}",
    })

    if st.button("Checkout"):
        receipt = finalize_checkout()
        if receipt:
            st.success("Payment successful. Thank you!")
            st.markdown("#### Receipt")
            st.write({
                "Subtotal": f"${receipt['subtotal']:.2f}",
                "Service (10%)": f"${receipt['service']:.2f}",
                "GST (9%)": f"${receipt['gst']:.2f}",
                "Grand Total": f"${receipt['grand']:.2f}",
            })


def cashier_dashboard():
    st.subheader("Cashier • Stock & Pricing Dashboard")
    prods = st.session_state.products
    rbar = avg_remaining_ratio(prods)

    # Quick stock table (with current dynamic price, but no markup details)
    rows = []
    for p in prods:
        rows.append({
            "Item": p["name"],
            "Base": f"${p['base']:.2f}",
            "Now/Init": f"{p['stock_now']}/{p['stock_init']}",
            "Dynamic Price": f"${effective_unit_price(p, rbar):.2f}",
        })
    st.table(rows)

    st.markdown("### Restock")
    cols = st.columns(len(prods))
    for i, p in enumerate(prods):
        with cols[i]:
            st.markdown(f"**{p['name']}**")
            amt = st.number_input("Add units", min_value=0, step=1, key=f"restock_{p['id']}")
            if st.button("Restock", key=f"btn_restock_{p['id']}"):
                p["stock_now"] += int(amt)
                p["stock_init"] += int(amt)  # keep ratio logic stable for fresh stock added
                st.success("Restocked.")

    if st.session_state.orders:
        st.markdown("### Recent Receipts")
        for i, r in enumerate(reversed(st.session_state.orders[-5:]), 1):
            st.markdown(f"**Order #{len(st.session_state.orders)-i+1}**")
            st.write(r)

# -----------------------------
# Main
# -----------------------------

def main():
    init_state()

    st.set_page_config(page_title="Shop — CTD 1D")
    st.title("Shop")

    tabs = st.tabs(["Customer", "Cashier"])

    with tabs[0]:
        st.subheader("Select your umbrella:")
        prods = st.session_state.products
        rbar = avg_remaining_ratio(prods)
        cols = st.columns(len(prods))
        for i, p in enumerate(prods):
            with cols[i]:
                product_card(p, rbar, key_prefix="cust")
        st.divider()
        cart_panel()

    with tabs[1]:
        cashier_dashboard()

if __name__ == "__main__":
    main()


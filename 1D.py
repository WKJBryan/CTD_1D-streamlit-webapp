# app.py — CTD 1D Baseline Streamlit App (no extra imports)
# --------------------------------------------------------
# Baseline:
#   • Add items (name, unit price, quantity)
#   • Compute final price = sum(unit_price * quantity)
#   • Show subtotal and grand total
# Enhancements (optional, controlled by checkboxes):
#   • Itemized receipt (more information)
#   • Promo code (more features)
# Only import Streamlit; no other imports used.

import streamlit as st

# ------------------------------
# Optional: promo code examples (feature enhancement)
# ------------------------------
ORDER_LEVEL_DISCOUNTS = {
    # code -> percent off (0.10 == 10%)
    "WELCOME5": 0.05,
    "STUDENT10": 0.10,
}

# ------------------------------
# Pure-Python core logic (lists + dicts)
# ------------------------------

def compute_subtotal(items):
    subtotal = 0.0
    for it in items:
        subtotal += it["unit_price"] * it["quantity"]
    return subtotal


def apply_order_level_discount(subtotal, promo_code):
    # Returns (discount_amount, applied_rate)
    code = (promo_code or "").strip().upper()
    rate = ORDER_LEVEL_DISCOUNTS.get(code, 0.0)
    return subtotal * rate, rate


def final_amount(subtotal_after_promo, svc_on, svc_rate, tax_on, tax_rate):
    # Returns (service_charge, tax, grand_total) — service applied before tax
    service_charge = subtotal_after_promo * svc_rate if svc_on else 0.0
    base_plus_svc = subtotal_after_promo + service_charge
    tax = base_plus_svc * tax_rate if tax_on else 0.0
    grand_total = base_plus_svc + tax
    return service_charge, tax, grand_total

# ------------------------------
# Streamlit UI
# ------------------------------

st.set_page_config(page_title="Price Calculator", page_icon="💸")
st.title("💸 Final Calculator")

# Keep cart in session_state as a list of dicts
if "cart" not in st.session_state:
    st.session_state.cart = []  # each item: {"name": str, "unit_price": float, "quantity": int}

# --- Input form (baseline) ---
st.subheader("Add Item")
with st.form("add_item_form", clear_on_submit=True):
    name = st.text_input("Item name", placeholder="e.g., Widget A")
    unit_price = st.number_input("Unit price", min_value=0.0, step=0.10, format="%.2f")
    quantity = st.number_input("Quantity", min_value=0, step=1)
    submitted = st.form_submit_button("Add to cart")

if submitted:
    if not name.strip():
        st.warning("Please enter an item name.")
    elif quantity == 0:
        st.warning("Quantity must be at least 1.")
    else:
        st.session_state.cart.append({
            "name": name.strip(),
            "unit_price": float(unit_price),
            "quantity": int(quantity)
        })
        st.success("Added: {} × {}".format(name.strip(), int(quantity)))

# Cart preview
if st.session_state.cart:
    st.subheader("Current Items")
    table_rows = []
    for it in st.session_state.cart:
        line_total = it["unit_price"] * it["quantity"]
        table_rows.append({
            "Item": it["name"],
            "Unit Price": "$%.2f" % it["unit_price"],
            "Qty": it["quantity"],
            "Line Total": "$%.2f" % line_total,
        })
    st.table(table_rows)

    if st.button("Clear cart"):
        st.session_state.cart = []
        st.experimental_rerun()

# --- Totals (baseline controls) ---
st.subheader("Totals")
col1, col2 = st.columns(2)
with col1:
    svc_on = st.checkbox("Apply service charge", value=False)
    svc_rate = st.number_input("Service charge rate", min_value=0.0, max_value=1.0, value=0.0, step=0.01, format="%.2f")
with col2:
    tax_on = st.checkbox("Apply tax", value=False)
    tax_rate = st.number_input("Tax rate", min_value=0.0, max_value=1.0, value=0.0, step=0.01, format="%.2f")

# --- Optional enhancements ---
st.divider()
st.caption("Optional enhancements — off by default to keep baseline minimal.")

enh_info = st.checkbox("Enhancement A: Show itemized receipt (more information)", value=False)
enh_promo = st.checkbox("Enhancement B: Enable promo code (more features)", value=False)

promo_code = ""
if enh_promo:
    promo_code = st.text_input("Promo code (optional)", placeholder="e.g., WELCOME5")

# --- Compute and display ---
items = st.session_state.cart
if items:
    subtotal = compute_subtotal(items)

    promo_amt = 0.0
    promo_rate = 0.0
    if enh_promo:
        promo_amt, promo_rate = apply_order_level_discount(subtotal, promo_code)

    subtotal_after_promo = subtotal - promo_amt

    svc_amt, tax_amt, grand_total = final_amount(
        subtotal_after_promo, svc_on, svc_rate, tax_on, tax_rate
    )

    st.markdown("### Results")
    results = {
        "Subtotal": "$%.2f" % subtotal,
        "Promo": ("-$%.2f (%d%%)" % (promo_amt, int(promo_rate * 100))) if (enh_promo and promo_amt > 0) else "$0.00",
        "Service Charge": "$%.2f" % svc_amt if svc_on else "$0.00",
        "Tax": "$%.2f" % tax_amt if tax_on else "$0.00",
        "Grand Total": "$%.2f" % grand_total,
    }
    st.write(results)

    if enh_info:
        st.markdown("### Itemized Receipt (enhancement)")
        receipt_rows = []
        for it in items:
            receipt_rows.append({
                "Item": it["name"],
                "Qty": it["quantity"],
                "Unit": "$%.2f" % it["unit_price"],
                "Line": "$%.2f" % (it["unit_price"] * it["quantity"]),
            })
        st.write(receipt_rows)
else:
    st.info("Add at least one item to compute totals.")


## Run Commands (local)

# pip install streamlit
# streamlit run app.py
# or
# python -m streamlit run app.py




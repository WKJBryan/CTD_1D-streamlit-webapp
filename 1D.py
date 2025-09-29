import streamlit as st
from io import StringIO

# ---------- Config ----------
GST_RATE = 0.09          # adjustable (e.g., Singapore 9%)
SERVICE_CHARGE_RATE = 0.10

CATALOG = {
    "FDM PLA (per gram)": {"price": 0.15, "category": "print"},
    "Resin (per ml)":     {"price": 0.30, "category": "print"},
    "Slicing Service":    {"price": 5.00, "category": "service"},
    "Post-process (per item)": {"price": 2.50, "category": "service"},
}

# Per-item bulk tiers: qty threshold -> percentage off (0.10 == 10%)
BULK_DISCOUNTS = {
    "FDM PLA (per gram)": [(500, 0.10), (1000, 0.15)],
    "Resin (per ml)":     [(300, 0.08), (800, 0.12)],
}

ORDER_LEVEL_DISCOUNTS = {
    # promo code -> percent off
    "STUDENT10": 0.10,
    "WELCOME5": 0.05,
}

def bulk_discount_rate(item_name: str, qty: int) -> float:
    tiers = BULK_DISCOUNTS.get(item_name, [])
    rate = 0.0
    for threshold, pct in tiers:
        if qty >= threshold:
            rate = max(rate, pct)
    return rate

def compute_line(name: str, qty: int):
    unit = CATALOG[name]["price"]
    pre = unit * qty
    disc_rate = bulk_discount_rate(name, qty)
    disc_amt = pre * disc_rate
    line_total = pre - disc_amt
    return {
        "item": name,
        "qty": qty,
        "unit_price": unit,
        "pre_discount": pre,
        "discount": disc_amt,
        "line_total": line_total
    }

def apply_order_level_discount(subtotal: float, promo: str) -> float:
    promo = (promo or "").strip().upper()
    rate = ORDER_LEVEL_DISCOUNTS.get(promo, 0.0)
    return subtotal * rate, rate

def apply_service_and_gst(amount: float, svc_on: bool, gst_on: bool):
    svc = amount * SERVICE_CHARGE_RATE if svc_on else 0.0
    amt_plus_svc = amount + svc
    gst = amt_plus_svc * GST_RATE if gst_on else 0.0
    return svc, gst, amt_plus_svc + gst

def reward_points(final_amount: float) -> int:
    # Simple rule-of-thumb: 1 pt per $10 spent (floor)
    return int(final_amount // 10)

# ---------- UI ----------
st.set_page_config(page_title="3D Print Shop POS", page_icon="🧰")
st.title("🧰 3D Print Shop POS (CTD 1D)")

st.sidebar.header("Settings")
apply_service = st.sidebar.checkbox("Apply Service Charge (10%)", value=True)
apply_gst = st.sidebar.checkbox("Apply GST (9%)", value=True)
promo_code = st.sidebar.text_input("Promo Code (optional)").strip().upper()
member = st.sidebar.checkbox("Member? (extra 2% off order)", value=False)

st.markdown("### Order")
quantities = {}
cols = st.columns(2)
for i, name in enumerate(CATALOG.keys()):
    with cols[i % 2]:
        q = st.number_input(f"{name} (qty)", min_value=0, step=1, value=0, key=f"qty_{i}")
        quantities[name] = int(q)

# Validate non-negative integers (number_input already enforces)
lines = []
for name, qty in quantities.items():
    if qty > 0:
        lines.append(compute_line(name, qty))

if st.button("Calculate"):
    if not lines:
        st.warning("Add at least one item.")
    else:
        # Sort lines by line_total desc
        lines.sort(key=lambda d: d["line_total"], reverse=True)

        pre_subtotal = sum(d["pre_discount"] for d in lines)
        item_discounts = sum(d["discount"] for d in lines)
        subtotal_after_items = pre_subtotal - item_discounts

        # Order-level discounts (promo + member)
        promo_amt, promo_rate = apply_order_level_discount(subtotal_after_items, promo_code)
        member_amt = subtotal_after_items * 0.02 if member else 0.0

        subtotal_after_order = subtotal_after_items - promo_amt - member_amt

        svc_amt, gst_amt, grand_total = apply_service_and_gst(subtotal_after_order, apply_service, apply_gst)
        points = reward_points(grand_total)

        # ---------- Display ----------
        st.markdown("### Itemized Receipt")
        st.write([{
            "Item": d["item"],
            "Qty": d["qty"],
            "Unit": f"${d['unit_price']:.2f}",
            "Pre-Disc": f"${d['pre_discount']:.2f}",
            "Disc": f"-${d['discount']:.2f}",
            "Line": f"${d['line_total']:.2f}",
        } for d in lines])

        st.markdown("### Totals")
        st.write({
            "Pre-Subtotal": f"${pre_subtotal:.2f}",
            "Item Discounts": f"-${item_discounts:.2f}",
            "Promo Applied": f"-${promo_amt:.2f} ({int(promo_rate*100)}%)" if promo_amt else "$0.00",
            "Member Discount": f"-${member_amt:.2f}" if member_amt else "$0.00",
            "Subtotal": f"${subtotal_after_order:.2f}",
            "Service Charge": f"${svc_amt:.2f}" if apply_service else "$0.00",
            "GST": f"${gst_amt:.2f}" if apply_gst else "$0.00",
            "Grand Total": f"${grand_total:.2f}",
            "Reward Points (est.)": f"{points} pts"
        })

        # Export (enhancement: info + feature)
        buff = StringIO()
        buff.write("=== 3D Print Shop Receipt ===\n")
        for d in lines:
            buff.write(f"{d['item']} x{d['qty']}: ${d['line_total']:.2f}\n")
        buff.write("\n")
        buff.write(f"Pre-Subtotal: ${pre_subtotal:.2f}\n")
        buff.write(f"Item Discounts: -${item_discounts:.2f}\n")
        if promo_amt: buff.write(f"Promo: -${promo_amt:.2f}\n")
        if member_amt: buff.write(f"Member: -${member_amt:.2f}\n")
        buff.write(f"Subtotal: ${subtotal_after_order:.2f}\n")
        if apply_service: buff.write(f"Service Charge: ${svc_amt:.2f}\n")
        if apply_gst: buff.write(f"GST: ${gst_amt:.2f}\n")
        buff.write(f"Grand Total: ${grand_total:.2f}\n")
        buff.write(f"Reward Points: {points} pts\n")
        st.download_button("Download Receipt (.txt)", data=buff.getvalue(), file_name="receipt.txt")
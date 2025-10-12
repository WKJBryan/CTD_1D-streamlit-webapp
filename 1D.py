import streamlit as st


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
"Subtotal (dynamic prices)": "$%.2f" % subtotal,
"Promo": ("-$%.2f (%d%%)" % (promo_amt, int(round(promo_rate * 100)))) if (enh_promo and promo_amt > 0) else "$0.00",
"Service Charge": "$%.2f" % svc_amt if svc_on else "$0.00",
"Tax": "$%.2f" % tax_amt if tax_on else "$0.00",
"Grand Total": "$%.2f" % grand_total,
}
st.write(results)


if enh_info:
st.markdown("### Itemized Receipt (enhancement)")
receipt_rows = []
for it in items:
eff_unit, markup = dynamic_unit_price(
it["unit_price"], it["popularity"], it["stock"], it["expires_today"]
)
receipt_rows.append({
"Item": it["name"],
"Qty": it["quantity"],
"Base Unit": "$%.2f" % it["unit_price"],
"Markup": "+%d%%" % int(round(markup * 100)),
"Expires Today": "Yes" if it["expires_today"] else "No",
"Eff. Unit": "$%.2f" % eff_unit,
"Line": "$%.2f" % (eff_unit * it["quantity"]),
})
st.write(receipt_rows)
else:
st.info("Add at least one item to compute total")


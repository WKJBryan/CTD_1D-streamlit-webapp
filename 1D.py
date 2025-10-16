import streamlit as st
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
p["stock_init"] += int(amt) # keep ratio logic stable for fresh stock added
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


st.set_page_config(page_title="Umbrella Shop — CTD 1D", page_icon="🌂")
st.title("🌂 Umbrella Shop")


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

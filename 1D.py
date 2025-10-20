import streamlit as st

# --- INITIAL SETUP & DATA ---
# Using session state to hold data, so it persists across user interactions.
def initialize_session_state():
    """Sets up the initial state for the inventory and cart if not already present."""
    if 'inventory' not in st.session_state:
        # The inventory is now stocked with 1kg filament rolls.
        st.session_state.inventory = {
            "PLA Filament (Black, 1kg)": {"base_price": 22.00, "initial_stock": 200, "current_stock": 150},
            "PLA Filament (White, 1kg)": {"base_price": 22.00, "initial_stock": 200, "current_stock": 180},
            "PETG Filament (Blue, 1kg)": {"base_price": 28.00, "initial_stock": 120, "current_stock": 70},
            "ABS Filament (Red, 1kg)": {"base_price": 25.00, "initial_stock": 100, "current_stock": 95},
        }
    if 'cart' not in st.session_state:
        st.session_state.cart = {}

# --- DYNAMIC PRICING LOGIC ---
# This is the core feature demonstrating complex logic.
def get_dynamic_price(item_name):
    """
    Calculates the price of an item based on its stock scarcity relative to other items.
    This fulfills the requirement to have a pricing strategy to demonstrate programming skills.
    """
    inventory = st.session_state.inventory
    
    # 1. Calculate the 'remaining stock ratio' for each item.
    ratios = []
    for item_data in inventory.values():
        if item_data["initial_stock"] > 0:
            ratio = item_data["current_stock"] / item_data["initial_stock"]
            ratios.append(ratio)
            
    # 2. Calculate the average ratio across all items.
    avg_ratio = sum(ratios) / len(ratios) if ratios else 0
    
    # 3. Find the specific item's ratio.
    item_data = inventory[item_name]
    item_ratio = item_data["current_stock"] / item_data["initial_stock"] if item_data["initial_stock"] > 0 else 0
    
    # 4. Calculate the scarcity delta.
    scarcity_delta = avg_ratio - item_ratio
    
    # 5. Apply markup based on the piecewise tiers.
    markup = 0.05
    if scarcity_delta > 0.30:
        markup = 0.20
    elif scarcity_delta > 0.20:
        markup = 0.17
    elif scarcity_delta > 0.10:
        markup = 0.12
    elif scarcity_delta > 0.00:
        markup = 0.08
        
    final_price = item_data["base_price"] * (1 + markup)
    return final_price, markup

# --- RECEIPT GENERATION ---
def generate_receipt_markdown(cart):
    """Generates a markdown formatted string for the receipt."""
    # Removed datetime import, so no timestamp is included.
    receipt_md = f"# Purchase Receipt\n\n---\n\n"
    receipt_md += "| Item | Qty | Unit Price | Total |\n"
    receipt_md += "|:-----|:---:|-----------:|------:|\n"
    
    subtotal = 0.0
    for item_name, quantity in cart.items():
        price, _ = get_dynamic_price(item_name)
        item_total = price * quantity
        subtotal += item_total
        receipt_md += f"| {item_name} | {quantity} | ${price:.2f} | ${item_total:.2f} |\n"
        
    service_charge = subtotal * 0.10
    gst = (subtotal + service_charge) * 0.09
    total_price = subtotal + service_charge + gst
    
    receipt_md += "\n---\n\n"
    receipt_md += f"**Subtotal:** `${subtotal:.2f}`\n\n"
    receipt_md += f"**Service Charge (10%):** `${service_charge:.2f}`\n\n"
    receipt_md += f"**GST (9%):** `${gst:.2f}`\n\n"
    receipt_md += f"### **Total Payable:** `${total_price:.2f}`\n\n"
    receipt_md += "--- \n\n*Thank you for your purchase!*"
    
    return receipt_md

# --- UI RENDERING FUNCTIONS ---
def draw_cashier_ui():
    """Displays the inventory management dashboard for the cashier."""
    st.header("🏪 Cashier Dashboard")
    st.write("Live inventory and pricing status.")
    
    inventory = st.session_state.inventory
    
    display_data = []
    for name, data in inventory.items():
        price, markup = get_dynamic_price(name)
        display_data.append({
            "Item": name,
            "Base Price": f"${data['base_price']:.2f}",
            "Initial Stock": data['initial_stock'],
            "Stock Left": data['current_stock'],
            "Dynamic Markup": f"{markup:.0%}",
            "Current Price": f"${price:.2f}"
        })
    
    st.table(display_data)

    if st.button("Reset All Stock to Initial Values"):
        for name in inventory:
            st.session_state.inventory[name]["current_stock"] = st.session_state.inventory[name]["initial_stock"]
        st.success("All stock has been reset!")
        st.rerun()

def draw_customer_ui():
    """Displays the shopping interface for the customer."""
    st.header("🛍️ Welcome to Uni-Print!")

    inventory = st.session_state.inventory
    cart = st.session_state.cart
    
    st.subheader("Our Products")
    for item_name, item_data in inventory.items():
        if item_data["current_stock"] > 0:
            col1, col2 = st.columns([3, 2])
            with col1:
                dynamic_price, _ = get_dynamic_price(item_name)
                st.markdown(f"**{item_name}**")
                st.caption(f"Price: `${dynamic_price:.2f}` | Stock: `{item_data['current_stock']}` available")
            with col2:
                quantity = st.number_input("Quantity", min_value=0, max_value=item_data["current_stock"], value=0, key=f"qty_{item_name}")
                if st.button("Add to Cart", key=f"add_{item_name}"):
                    if quantity > 0:
                        cart[item_name] = cart.get(item_name, 0) + quantity
                        st.session_state.inventory[item_name]['current_stock'] -= quantity
                        st.success(f"Added {quantity} x {item_name} to your cart.")
                        st.rerun()

    st.divider()
    st.subheader("🛒 Your Shopping Cart")
    
    if not cart:
        st.info("Your cart is empty.")
    else:
        subtotal = 0.0
        for item_name, quantity in cart.items():
            price, _ = get_dynamic_price(item_name)
            item_total = price * quantity
            subtotal += item_total
            st.write(f"- {item_name}: {quantity} x ${price:.2f} = **${item_total:.2f}**")
        
        st.divider()
        
        service_charge = subtotal * 0.10
        gst = (subtotal + service_charge) * 0.09
        total_price = subtotal + service_charge + gst
        
        st.markdown(f"""
        | Description | Amount |
        | :--- | ---: |
        | **Subtotal** | **${subtotal:.2f}** |
        | Service Charge (10%) | ${service_charge:.2f} |
        | GST (9%) | ${gst:.2f} |
        | ### **Total Price** | ### **${total_price:.2f}** |
        """)

        # --- ACTION BUTTONS ---
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Check-out", use_container_width=True):
                st.session_state.cart.clear()
                st.warning("Checked Out.")
                st.rerun()
        with col2:
            receipt_content = generate_receipt_markdown(cart)
            st.download_button(
                label="📄 Download Receipt",
                data=receipt_content,
                file_name="receipt.md", # Changed to a static filename
                mime="text/markdown",
                use_container_width=True
            )

# --- MAIN APP LOGIC ---
st.set_page_config(layout="centered")
st.title("Filament Store Point-of-Sale System")

initialize_session_state()

with st.sidebar:
    st.header("Select View")
    app_mode = st.radio("Choose UI:", ("Customer", "Cashier"), label_visibility="collapsed")

if app_mode == "Customer":
    draw_customer_ui()
else:
    draw_cashier_ui()



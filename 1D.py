import streamlit as st

# --- INITIAL SETUP & DATA ---
# Using session state to hold data, so it persists across user interactions.
def initialize_session_state():
    """Sets up the initial state for the inventory and cart if not already present."""
    if 'inventory' not in st.session_state:
        # Data is stored in one place for easy updates, as per the brief's advice.
        st.session_state.inventory = {
            "Classic Black Umbrella": {"base_price": 25.00, "initial_stock": 100, "current_stock": 80},
            "Compact Travel Umbrella": {"base_price": 20.00, "initial_stock": 150, "current_stock": 95},
            "Golf Pro Umbrella": {"base_price": 40.00, "initial_stock": 75, "current_stock": 70},
            "Bubble Dome Umbrella": {"base_price": 30.00, "initial_stock": 90, "current_stock": 50},
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
        # Avoid division by zero if initial stock is 0 for some reason.
        if item_data["initial_stock"] > 0:
            ratio = item_data["current_stock"] / item_data["initial_stock"]
            ratios.append(ratio)
            
    # 2. Calculate the average ratio across all items.
    avg_ratio = sum(ratios) / len(ratios) if ratios else 0
    
    # 3. Find the specific item's ratio.
    item_data = inventory[item_name]
    item_ratio = item_data["current_stock"] / item_data["initial_stock"] if item_data["initial_stock"] > 0 else 0
    
    # 4. Calculate the scarcity delta: a positive value means the item is scarcer than average.
    scarcity_delta = avg_ratio - item_ratio
    
    # 5. Apply markup based on the piecewise tiers. This uses if/elif/else logic.
    markup = 0.05  # Default 5% markup
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

# --- UI RENDERING FUNCTIONS ---
def draw_cashier_ui():
    """Displays the inventory management dashboard for the cashier."""
    st.header("🏪 Cashier Dashboard")
    st.write("Live inventory and pricing status.")
    
    inventory = st.session_state.inventory
    
    # Prepare data for display
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
    st.header("🛍️ Welcome to the Umbrella Store!")

    inventory = st.session_state.inventory
    cart = st.session_state.cart
    
    # --- Product Selection ---
    st.subheader("Our Products")
    for item_name, item_data in inventory.items():
        if item_data["current_stock"] > 0:
            col1, col2 = st.columns([3, 2])
            
            with col1:
                dynamic_price, _ = get_dynamic_price(item_name)
                st.markdown(f"**{item_name}**")
                st.caption(f"Price: `${dynamic_price:.2f}` | Stock: `{item_data['current_stock']}` available")
            
            with col2:
                # Use a unique key for each number_input
                quantity = st.number_input("Quantity", min_value=0, max_value=item_data["current_stock"], value=0, key=f"qty_{item_name}")
                if st.button("Add to Cart", key=f"add_{item_name}"):
                    if quantity > 0:
                        cart[item_name] = cart.get(item_name, 0) + quantity
                        # Update stock (simple implementation)
                        st.session_state.inventory[item_name]['current_stock'] -= quantity
                        st.success(f"Added {quantity} x {item_name} to your cart.")
                        st.rerun()

    # --- Cart and Checkout ---
    st.divider()
    st.subheader("🛒 Your Shopping Cart")
    
    if not cart:
        st.info("Your cart is empty.")
    else:
        subtotal = 0.0
        
        # Display an itemized list, an optional enhancement mentioned in the brief.
        for item_name, quantity in cart.items():
            price, _ = get_dynamic_price(item_name) # Price is recalculated in case it changed
            item_total = price * quantity
            subtotal += item_total
            st.write(f"- {item_name}: {quantity} x ${price:.2f} = **${item_total:.2f}**")
        
        st.divider()
        
        # Calculate final price with compulsory surcharges.
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
        
        if st.button("Clear Cart"):
            # This simple implementation doesn't return items to stock.
            st.session_state.cart.clear()
            st.warning("Cart cleared.")
            st.rerun()


# --- MAIN APP LOGIC ---
st.set_page_config(layout="centered")
st.title("Dynamic Pricing Point-of-Sale System")

# Initialize state on first run.
initialize_session_state()

# Use a sidebar radio to switch between the two UIs.
with st.sidebar:
    st.header("Select View")
    app_mode = st.radio("Choose UI:", ("Customer", "Cashier"), label_visibility="collapsed")

if app_mode == "Customer":
    draw_customer_ui()
else:
    draw_cashier_ui()

import streamlit as st
import razorpay
from streamlit.components.v1 import html

# Set page title and icon
st.set_page_config(page_title="Buy Me a Coffee ☕", page_icon="☕", layout="centered")

# Initialize Razorpay client (use your test/live keys)
client = razorpay.Client(auth=(st.secrets["razorpay"]["key_id"], st.secrets["razorpay"]["key_secret"]))

# Title
st.title(":blue[☕ Buy Me a Coffee!]")
st.markdown("""
    If you find this project helpful, consider supporting me with a small donation!  
    Every coffee keeps me motivated to build more cool stuff. 😊  
""")

# Amount selection
amount = st.selectbox(
    "Select donation amount (₹)", 
    options=[50, 100, 200, 500, 1000], 
    index=1
)

# Razorpay checkout button (JavaScript embedded)
def razorpay_checkout(amount):
    checkout_js = f"""
    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <button id="rzp-button" style="
        background: #FF813F;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 16px;
    ">Pay ₹{amount}</button>
    <script>
    var options = {{
        "key": "{st.secrets['razorpay']['key_id']}",  // Replace with your key or use st.secrets
        "amount": "{amount * 100}",  // Amount in paise (e.g., ₹100 = 10000 paise)
        "currency": "INR",
        "name": "Autism Prediction Project",
        "description": "Donation for the project",
        "image": "https://img.icons8.com/emoji/48/000000/teacup-without-handle.png",
        "prefill": {{
            "name": "{st.session_state.get('name', 'User')}",
            "email": "{st.session_state.get('email', 'user@example.com')}",
        }},
        "theme": {{"color": "#FF813F"}},
        "handler": function(response) {{
            alert("Payment successful! ID: " + response.razorpay_payment_id);
        }}
    }};
    var rzp = new Razorpay(options);
    document.getElementById('rzp-button').onclick = function(e) {{
        rzp.open();
        e.preventDefault();
    }}
    </script>
    """
    html(checkout_js, height=500)

# Trigger payment button
if st.button("Donate via Razorpay"):
    razorpay_checkout(amount)

# Alternative: Payment Link (no JavaScript)
st.markdown("---")
st.markdown("**Prefer UPI or other methods?**")
if st.button("Generate Payment Link"):
    payment_link = client.payment_link.create({
        "amount": amount * 100,
        "currency": "INR",
        "description": "Donation for Autism Prediction Project",
    })
    st.success(f"Click here to pay: [Payment Link]({payment_link['short_url']})")

# Sidebar logout
# Sidebar
with st.sidebar:
    if st.session_state.get("logged_in", False):
        st.success(f"Logged in as {st.session_state.username}")
        if st.sidebar.button("Logout"):
            st.switch_page("pages/8Logout.py")


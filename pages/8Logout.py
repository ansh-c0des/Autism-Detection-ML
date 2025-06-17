# 6Logout.py
import streamlit as st

st.set_page_config(page_title="Logout", layout="centered")

# Auth Check
if not st.session_state.get("logged_in", False):
    st.error("You are not logged in")
    st.stop()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

st.title("🔒 Logout Confirmation")
st.write("Are you sure you want to logout?")

col1, col2 = st.columns(2)

with col1:
    if st.button("✅ Yes, Logout"):
        # Clear session state
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("You have been logged out.")
        st.toast("Redirecting to login...", icon="🔄")
        st.switch_page("Register.py")

with col2:
    if st.button("❌ No, Go Back"):
        # Redirect to default page (you can enhance this to go back to the previous page)
        st.switch_page("pages/3Dashboard.py")

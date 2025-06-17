import streamlit as st  

# Auth Check
if not st.session_state.get("logged_in", False):
    st.error("Please log in to access the contact page.")
    st.stop()

st.title(":mailbox: :blue[Get In Touch With Us!]")

# Sidebar logout
with st.sidebar:
    if st.session_state.get("logged_in", False):
        st.success(f"Logged in as {st.session_state.username}")
        if st.sidebar.button("Logout"):
            st.switch_page("pages/8Logout.py")



contact_form = """
<form action="https://formsubmit.co/ansh.g@somaiya.edu" method="POST">
     <input type="hidden" name="_captcha" value="false">
     <input type="text" name="name" placeholder="Your name" required>
     <input type="email" name="email" placeholder="Your email" required>
     <textarea name="message" placeholder="Your message here"></textarea>
     <button type="submit">Send</button>
</form>
"""

st.markdown(contact_form, unsafe_allow_html=True)

# Use Local CSS File
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


local_css("style.css")
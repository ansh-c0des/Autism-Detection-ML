import streamlit as st
import pandas as pd
import time
import hashlib
from streamlit_option_menu import option_menu
import re
import sqlite3
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
import os
import requests
import toml
from urllib.parse import urlencode

st.set_page_config(layout="wide")

# SESSION INIT
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Load secrets from .streamlit/secrets.toml
secrets_path = os.path.join(".streamlit", "secrets.toml")
secrets = toml.load(secrets_path)

# Access the Google OAuth credentials
GOOGLE_CLIENT_ID = secrets["google"]["client_id"]
GOOGLE_CLIENT_SECRET = secrets["google"]["client_secret"]

REDIRECT_URI = "http://localhost:8501"  # change if deployed

# DB Setup
conn = sqlite3.connect('data.db')
c = conn.cursor()

def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)')
    conn.commit()

def add_userdata(username, password):
    c.execute('INSERT INTO userstable(username, password) VALUES (?, ?)', (username, password))
    conn.commit()

def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username = ? AND password = ?', (username, password))
    return c.fetchall()

def check_user_exists(username):
    c.execute('SELECT * FROM userstable WHERE username = ?', (username,))
    return c.fetchone() is not None

# Password Hashing
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# Google OAuth2 Flow
def get_google_auth_url():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

def fetch_google_token(code):
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    response = requests.post("https://oauth2.googleapis.com/token", data=data)
    return response.json()

def fetch_user_info(token):
    id_info = id_token.verify_oauth2_token(token["id_token"], google.auth.transport.requests.Request(), GOOGLE_CLIENT_ID)
    return id_info

# Sidebar Logic
with st.sidebar:
    if st.session_state.logged_in:
        st.success(f"Welcome {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
    else:
        selected = option_menu(
            menu_title="Start Here!",
            options=["Signup", "Login", "Login with Google"],
            icons=["person-plus-fill", "box-arrow-in-right", "google"],
            menu_icon="person-circle",
            default_index=0
        )

# Signup
if not st.session_state.logged_in and selected == "Signup":
    st.title(":iphone: :blue[Create New Account]")
    new_user = st.text_input("Username", key="signup_username")
    new_password = st.text_input("Password", type='password', key="signup_password")

    username_valid = re.match(r'^[a-zA-Z0-9_]+$', new_user) if new_user else False

    if new_user:
        st.markdown("✅ Username is valid" if username_valid else "<span style='color:red;'>❌ Invalid username.</span>", unsafe_allow_html=True)

    pass_length = len(new_password) >= 8
    pass_number = any(char.isdigit() for char in new_password)
    pass_special = any(char in "!@#$%^&*()-_=+[{]}\|;:'\",<.>/?`~" for char in new_password)

    st.markdown(f"<span style='color:{'green' if pass_length else 'red'};'>• At least 8 characters</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{'green' if pass_number else 'red'};'>• Contains a number</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{'green' if pass_special else 'red'};'>• Contains a special character</span>", unsafe_allow_html=True)

    if st.button("Signup"):
        if not new_user or not new_password:
            st.warning("Username and Password cannot be empty.")
        elif not username_valid:
            st.warning("Invalid username format.")
        elif not (pass_length and pass_number and pass_special):
            st.warning("Password does not meet the required rules.")
        else:
            create_usertable()
            if check_user_exists(new_user):
                st.warning("Username already exists.")
            else:
                add_userdata(new_user, make_hashes(new_password))
                st.success("Account created! Go to Login.")

# Login
elif not st.session_state.logged_in and selected == "Login":
    st.title(":calling: :blue[Login Section]")
    username = st.text_input("User Name")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        create_usertable()
        hashed_pswd = make_hashes(password)
        result = login_user(username, hashed_pswd)
        prog = st.progress(0)
        for per_comp in range(100):
            time.sleep(0.01)
            prog.progress(per_comp + 1)
        if result:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Logged In as {username}")
            st.switch_page("pages/3Dashboard.py")
        else:
            st.warning("Incorrect Username/Password")


# Google Sign-In
elif not st.session_state.logged_in and selected == "Login with Google":
    col1, col2 = st.columns([1, 10])
    with col1:
        st.image("image\Google_Icons-09-512.webp", width=300)
    with col2:
        st.title(":blue[Login with Google]")
    query_params = st.query_params 

    if "code" not in query_params:
        auth_url = get_google_auth_url()
        st.markdown(f"[Click here to Login with Google]({auth_url})")
    else:
        code = query_params["code"][0]
        tokens = fetch_google_token(code)
        user_info = fetch_user_info(tokens)

        if user_info:
            email = user_info["email"]
            st.session_state.logged_in = True
            st.session_state.username = email
            st.success(f"Logged in as {email}")
            st.switch_page("pages/3Dashboard.py")
        else:
            st.warning("Google authentication failed. Try again.")

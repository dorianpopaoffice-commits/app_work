import streamlit as st
from time import sleep
from navigation import make_sidebar

# Sidebar
make_sidebar()

# Title
st.title("Welcome to ...")
st.write("Please log in to continue.")

# Username & password
username = st.text_input("Username")
password = st.text_input("Password", type="password")

# Valid users
valid_users = {
    "BEIA": "123456789",
    "user1": "password1",
    "user2": "password2",
}

# Login button
if st.button("Log in", type="primary"):
    if username in valid_users and password == valid_users[username]:
        st.session_state.logged_in = True
        st.success("Logged in successfully!")
        sleep(0.5)
        st.switch_page("pages/page11.py")
    else:
        st.error("Incorrect username or password")



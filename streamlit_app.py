import streamlit as st
import bcrypt
import time
from navigation import make_sidebar

# Configurare pagină și ascundere navigare automată
st.set_page_config(
    page_title="Acces Data Center",
    page_icon="🔐",
    layout="centered"
)

st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ================================
# USER STORAGE (hashed passwords)
# ================================
valid_users = {
    "test": bcrypt.hashpw("123456789".encode(), bcrypt.gensalt()),
    "user1": bcrypt.hashpw("password1".encode(), bcrypt.gensalt()),
    "user2": bcrypt.hashpw("password2".encode(), bcrypt.gensalt()),
}

# ================================
# RATE LIMIT / PROTECȚIE BRUTE FORCE
# ================================
if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0
if "lock_until" not in st.session_state:
    st.session_state.lock_until = 0

current_time = time.time()
if current_time < st.session_state.lock_until:
    st.error("🔒 Prea multe încercări. Reîncearcă peste câteva secunde.")
    st.stop()

# ================================
# SIDEBAR
# ================================
# După make_sidebar(), adaugă:
st.session_state.current_page = "main"
make_sidebar()

# ================================
# INTERFAȚĂ LOGIN
# ================================
st.title("🔐 Secure Login")
st.write("Introduceți datele de autentificare.")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

# ================================
# LOGICĂ LOGIN
# ================================
def verify_user(user, pwd):
    """Returnează True dacă parola este corectă."""
    if user not in valid_users:
        return False
    hashed_password = valid_users[user]
    return bcrypt.checkpw(pwd.encode(), hashed_password)

if st.button("Log in", type="primary"):
    if verify_user(username, password):
        st.session_state.logged_in = True
        st.session_state.failed_attempts = 0
        st.success("Autentificare reușită!")
        time.sleep(0.5)
        st.switch_page("pages/page2.py")
    else:
        st.session_state.failed_attempts += 1
        if st.session_state.failed_attempts >= 5:
            st.session_state.lock_until = time.time() + 10
            st.error("⛔ Prea multe încercări greșite. Contul este blocat 10 secunde.")
        else:
            st.error("❌ Username sau parolă greșită.")

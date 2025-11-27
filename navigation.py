import streamlit as st
from time import sleep

def make_sidebar():
    with st.sidebar:
        st.write("")
        st.write("")
        if st.session_state.get("logged_in", False):
            # Verifică pe ce pagină suntem și folosește prefixe diferite
            current_page = st.session_state.get("current_page", "main")
            
            if st.button("📄 Extragere date", use_container_width=True, key=f"btn_page2_{current_page}"):
                st.switch_page("pages/page2.py")
            
            if st.button("📊 Vizualizare date", use_container_width=True, key=f"btn_page3_{current_page}"):
                st.switch_page("pages/page3.py")
            
            st.write("")
            st.divider()
            
            if st.button("🚪 Log out", use_container_width=True, key=f"btn_logout_{current_page}"):
                logout()
        else:
            pass

def logout():
    st.session_state.logged_in = False
    st.info("Logged out successfully!")
    sleep(0.5)
    st.switch_page("streamlit_app.py")

import streamlit as st
from time import sleep


def make_sidebar():
    with st.sidebar:
        st.write("")
        st.write("")

        if st.session_state.get("logged_in", False):

            st.page_link("pages/page2.py", label="Dashboard")

       
            with st.expander("Multimodal Pattern Detection", expanded=True):
                st.page_link("pages/page2.py", label="Biometric Recognition")
                st.write("")

            if st.button("Log out"):
                logout()

        else:
            # Dacă nu este logat, ne asigurăm că rămâne pe pagina principală
            pass


def logout():
    st.session_state.logged_in = False
    st.info("Logged out successfully!")
    sleep(0.5)
    st.switch_page("streamlit_app.py")


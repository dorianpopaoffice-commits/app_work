import streamlit as st
import mysql.connector
import pandas as pd
import streamlit as st
from navigation import make_sidebar

# Configurare pagină și ascundere navigare automată
st.set_page_config(
    page_title="Vizualizare Date",
    page_icon="📊",
    layout="wide"
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

# Verificare autentificare
if not st.session_state.get("logged_in", False):
    st.warning("⚠️ Trebuie să fii autentificat!")
    st.stop()
# După make_sidebar(), adaugă:
st.session_state.current_page = "page3"
make_sidebar()


# ... restul codului tău
# ---- FUNCȚIE CONECTARE MYSQL ----
def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="ParolaNoua!",
        database="acces3"
    )

# ---- ÎNCĂRCARE DATE DIN BAZĂ ----
def load_data():
    conn = get_mysql_connection()
    df = pd.read_sql("SELECT * FROM documente ORDER BY creat_la DESC", conn)
    conn.close()
    return df

# ---- INTERFAȚĂ STREAMLIT ----
st.title("📋 Vizualizare Documente OCR")
st.write("Aici poți vedea toate documentele procesate și salvate în baza de date.")

# Încărcăm datele
df = load_data()

st.subheader("🔍 Căutare înregistrări")
search = st.text_input("Caută după nume, CNP, țară sau tip document:")

if search:
    df = df[
        df["numar_document"].str.contains(search, case=False, na=False) |
        df["nume"].str.contains(search, case=False, na=False) |
        df["cnp"].str.contains(search, case=False, na=False) |
        df["tara"].str.contains(search, case=False, na=False) |
        df["tip_document"].str.contains(search, case=False, na=False)
    ]

# Filtru ultimele persoane adăugate
st.subheader("⏳ Ultimele înregistrări")
nr = st.number_input("Afișează ultimele X persoane:", min_value=1, max_value=500, value=10)

df_recent = df.head(nr)

# Afișare rezultate
st.subheader("📄 Rezultate")
st.dataframe(df_recent)

# Export
st.subheader("📥 Exportare date")
csv = df_recent.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Descarcă CSV",
    data=csv,
    file_name="inregistrari_recente.csv",
    mime="text/csv"
)

import streamlit as st
import mysql.connector
import cv2
import numpy as np
import os

from mrz_reader import mrz_reader
from mrz_reader import parse_mrz_romania
from navigation import make_sidebar

# Configurare pagină (TREBUIE SĂ FIE PRIMUL)
st.set_page_config(
    page_title="Extragere Date",
    page_icon="📄",
    layout="wide"
)

# Ascunde navigarea automată
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

# Marchează pagina curentă
st.session_state.current_page = "page2"

# Apelează sidebar O SINGURĂ DATĂ!
make_sidebar()



def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="ParolaNoua!",
        database="acces3"
    )


def init_mysql():
    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documente (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tip_document VARCHAR(50),
            tara VARCHAR(50),
            nume VARCHAR(20),
            prenume VARCHAR(50),
            sex VARCHAR(10),
            cnp VARCHAR(50),
            serie_document VARCHAR(10),
            numar_document VARCHAR(50),
            data_nasterii VARCHAR(20),
            data_expirarii VARCHAR(20),
            creat_la TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def insert_data(tip_document, extracted):
    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO documente (
            tip_document, tara, nume, prenume, sex, cnp, serie_document, numar_document, data_nasterii, data_expirarii
        )
        VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        tip_document,
        extracted.get("tara"),
        extracted.get('nume') ,
        extracted.get('prenume'),
        extracted.get("sex"),
        extracted.get("cnp"),
        extracted.get("serie_document"),
        extracted.get("numar_document"),
        extracted.get("data_nasterii"),
        extracted.get("data_expirarii"),
    ))

    conn.commit()
    conn.close()

# ---------------------------------------
#               INIT DATABASE
# ---------------------------------------
init_mysql()

# ---------------------------------------
#   FACE EXTRACTION (Cascade Haar)
# ---------------------------------------

output_directory = "/home/me2/app_work/data_face"

def extract_faces(file_path, cnp=None):
    image = cv2.imread(file_path)
    if image is None:
        return False
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    faces = face_cascade.detectMultiScale(gray, 1.15, 5)
    if len(faces) == 0:
        return False
    
    if cnp:
        for i, (x, y, w, h) in enumerate(faces):
            face = image[y:y + h, x:x + w]
            suffix = f"_{i+1}" if len(faces) > 1 else ""
            filename = f"{cnp}{suffix}.jpg"
            cv2.imwrite(os.path.join(output_directory, filename), face)
    else:
        for i, (x, y, w, h) in enumerate(faces):
            face = image[y:y + h, x:x + w]
            cv2.imwrite(os.path.join(output_directory, f"face_{i+1}.jpg"), face)
    return True

# ---------------------------------------
#          MRZ READER (EASY OCR)
# ---------------------------------------
mrz_reader_instance = mrz_reader()
mrz_reader_instance.load()
mrz_reader_instance.facedetect = True
mrz_reader_instance.skewness = False
mrz_reader_instance.delete_shadows = True
mrz_reader_instance.clear_background = True

# ---------------------------------------
#               STREAMLIT UI
# ---------------------------------------
# ȘTERS: make_sidebar() - ERA AICI AL DOILEA APEL!

st.title("📄 Extragere date și fată")

use_camera = st.checkbox("Enable camera")
picture = st.camera_input("Take a picture", disabled=not use_camera)
uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

doc_type = st.radio("Select Document Type:", [
    "Pașaport (ROU)",
    "Carte Identitate (ROU)"
])

if uploaded or picture:
    img_bytes = uploaded.read() if uploaded else picture.getvalue()
    img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    
    if img is None:
        st.error("Invalid image.")
        st.stop()
    
    temp_path = "temp_image.jpg"
    with open(temp_path, "wb") as f:
        f.write(img_bytes)
    
    st.image(img_bytes, caption="Input Image", use_container_width=True)
    
    if st.button("Extract Data & Face", key="extract_btn"):
        with st.spinner("Processing..."):
            mrz_raw, face = mrz_reader_instance.predict(img)
            
            if "ID" in mrz_raw:
                mrz_raw = "ID" + mrz_raw.split("ID", 1)[1]
            
            st.subheader("MRZ brut")
            st.code(mrz_raw)
            
            extracted = parse_mrz_romania(mrz_raw)
            st.subheader("📌 Extracted Data")
            for key, value in extracted.items():
                st.write(f"**{key}:** {value}")
            
            insert_data(doc_type, extracted)
            st.success("✅ Data saved successfully into MySQL.")
            
            cnp = extracted.get("cnp", None)
            face_extracted = extract_faces(temp_path, cnp=cnp)
            
            if face_extracted:
                st.success("✅ Face extracted successfully!")
                if cnp:
                    face_file = os.path.join(output_directory, f"{cnp}.jpg")
                    if os.path.exists(face_file):
                        st.image(face_file, caption=f"Extracted Face - CNP: {cnp}", width=200)
                else:
                    face_files = [f for f in os.listdir(output_directory) if f.startswith("face_")]
                    if face_files:
                        latest_face = os.path.join(output_directory, face_files[-1])
                        st.image(latest_face, caption="Extracted Face", width=200)
            else:
                st.warning("⚠️ No faces detected in the image.")
    
    if os.path.exists(temp_path):
        os.remove(temp_path)

import streamlit as st
import mysql.connector
import cv2
import numpy as np
import os

from mrz_reader import mrz_reader, pass_md, pass_rou, id_card_rou
from navigation import make_sidebar

# ---------------------------------------
#       MySQL DATABASE CONNECTION
# ---------------------------------------
def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",           # ← modifică după nevoie
        password="ParolaNoua!",   # ← parola MySQL
        database="acces"
    )

def init_mysql():
    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INT AUTO_INCREMENT PRIMARY KEY,
            document_type VARCHAR(50),
            country VARCHAR(50),
            name VARCHAR(150),
            sex VARCHAR(10),
            cnp VARCHAR(50),
            birth_date VARCHAR(50),
            expiry_date VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def insert_data(document_type, extracted):
    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO documents (document_type, country, name, sex, cnp, birth_date, expiry_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        document_type,
        extracted.get("Country"),
        extracted.get("Name"),
        extracted.get("Sex"),
        extracted.get("CNP"),
        extracted.get("Birth Date"),
        extracted.get("Expiry Date")
    ))

    conn.commit()
    conn.close()


# Initialize database
init_mysql()

# ---------------------------------------
#       FACE EXTRACTION
# ---------------------------------------
output_directory = "/home/razvan/ControlUI-STREAMLIT-main/data_face"

def extract_faces(file_path):
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

    for i, (x, y, w, h) in enumerate(faces):
        face = image[y:y + h, x:x + w]
        cv2.imwrite(os.path.join(output_directory, f"face_{i+1}.jpg"), face)

    return True

# ---------------------------------------
#         MRZ READER SETUP
# ---------------------------------------
mrz_reader_instance = mrz_reader()
mrz_reader_instance.load()

mrz_reader_instance.facedetect = True
mrz_reader_instance.skewness = False
mrz_reader_instance.delete_shadows = True
mrz_reader_instance.clear_background = True

# ---------------------------------------
#         STREAMLIT UI
# ---------------------------------------
make_sidebar()

app_choice = st.sidebar.selectbox("Select an Application", [
    "Extracted Information",
    "Process Image"
])

# ---------------------------------------
#      EXTRACTED INFORMATION (MRZ)
# ---------------------------------------
if app_choice == "Extracted Information":
    st.title("Extract ID / Passport Information")

    use_camera = st.checkbox("Enable camera")
    picture = st.camera_input("Take a picture", disabled=not use_camera)
    uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

    doc_type = st.radio("Select Document Type:", [
        "Passport (MD)", "Passport (ROU)", "ID Card (ROU)"
    ])

    if uploaded or picture:
        img_bytes = uploaded.read() if uploaded else picture.getvalue()
        img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)

        if img is None:
            st.error("Invalid image.")
            st.stop()

        mrz_raw, face = mrz_reader_instance.predict(img)

        # parse data
        if doc_type == "Passport (MD)":
            result = pass_md(mrz_raw)
        elif doc_type == "Passport (ROU)":
            result = pass_rou(mrz_raw)
        else:
            result = id_card_rou(mrz_raw)

        st.subheader("Extracted Data")
        for key, value in result.items():
            st.write(f"**{key}:** {value}")

        insert_data(doc_type, result)
        st.success("Data saved to MySQL database successfully.")

# ---------------------------------------
#        PROCESS IMAGE (EXTRACT FACE)
# ---------------------------------------
elif app_choice == "Process Image":
    st.title("Process Image – Face Extraction")

    use_camera = st.checkbox("Enable camera")
    picture = st.camera_input("Take a picture", disabled=not use_camera)
    uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

    if picture or uploaded:
        img_bytes = picture.getvalue() if picture else uploaded.read()
        temp_path = "temp_image.jpg"

        with open(temp_path, "wb") as f:
            f.write(img_bytes)

        st.image(img_bytes, caption="Input Image", use_column_width=True)

        if st.button("Extract Faces"):
            with st.spinner("Processing..."):
                ok = extract_faces(temp_path)

            if ok:
                st.success("Faces extracted successfully!")
            else:
                st.error("No faces detected in the image.")


"""
@author: razvanbr
"""
import os
import sys
sys.path.append('./')
from FaceDetection import FaceDetection
from SegmentationMRZ_DL import SegmentationMRZ_DL
from TextRecognition import TextRecognition
import pytesseract
import cv2
import pytesseract
import numpy as np
import matplotlib.pyplot as plt
import re

output_directory = "/home/razvan/ControlUI-STREAMLIT-main/data_face"

class mrz_reader:
    
    def __init__(self, facedetection_protxt="./face_detector/deploy.prototxt",
                 facedetection_caffemodel="./face_detector/res10_300x300_ssd_iter_140000.caffemodel",
                 mrzdetection_model="./mrz_detector/mrz_seg.tflite",
                 tesseract_exe=r"/usr/bin/tesseract"):
        self.facedetection_protxt=facedetection_protxt
        self.facedetection_caffemodel=facedetection_caffemodel
        self.mrzdetection_model=mrzdetection_model
        self.tesseract_exe=tesseract_exe
        self.facedetect=True
        self.skewness=False
        self.delete_shadows=True
        self.clear_background=True
        self.IsLoad=False
        
    def load(self,tesseract_models="mrz+OCRB"):
        pytesseract.pytesseract.tesseract_cmd =self.tesseract_exe
        self.facedetection=FaceDetection(self.facedetection_protxt,
                                    self.facedetection_caffemodel)
        self.mrzdetection=SegmentationMRZ_DL(self.mrzdetection_model)
        self.text_recognition=TextRecognition(tesseract_models)
        self.IsLoad=True


    def predict(self,img):
        if self.IsLoad:
            self.img_dl=self.mrzdetection.predict(img)
            self.mrz_dl,self.threshdl=self.text_recognition.recognize(self.img_dl,
                                                                      self.skewness,
                                                                      self.delete_shadows,
                                                                      self.clear_background)
            if self.facedetect==True:
                self.face=self.facedetection.detect_face(img,.1)
                return self.mrz_dl,self.face
            return self.mrz_dl
        else:
            print("Firstly, You must compile models")

def pass_md(input_string):
    # Define regular expressions for each piece of information
    country_match = re.search(r'PA(\w{3})', input_string)
    seria_numar_match = re.findall(r'<<<<<<<<<<<<<<<<<<<<<<<<<(.*?)MDA', input_string)
    sex_match = re.search(r'([MF])\d+<', input_string)
    expiry_date_match = re.findall(r'[MF](\d{6})', input_string)
    cnp_match = re.search(r'(\d{13})<', input_string)

    # Extract information using regular expressions
    country = country_match.group(1) if country_match else None
    index_rou = input_string.find(country) if country else None
    index_less_than = input_string.find("<", index_rou + 3) if index_rou else None
    name = input_string[index_rou + 3 : index_less_than] if index_rou and index_less_than else None
    sex = sex_match.group(1) if sex_match else None
    cnp = cnp_match.group(1) if cnp_match else None

    # Define a function to convert sex code to a more readable format
    def convert_sex(sex_code):
        if sex_code == 'M':
            return 'Masculin'
        elif sex_code == 'F':
            return 'Feminin'
        else:
            return None

    sex = convert_sex(sex) if sex else None
    expiry_date = expiry_date_match[0] if expiry_date_match else None

    # Return the extracted information as a dictionary
    return {
        "Country": country,
        "Name": name,
        "Series": seria_numar_match[0] if seria_numar_match else None,
        "Sex": sex,
        "Expiry Date": expiry_date,
        "CNP": cnp,
    }

    return extracted_info

def id_card_rou(input_string):
    # Define regular expressions for each piece of information
    country_match = re.search(r'ID(\w{3})', input_string)
    name_match = re.findall(r'<<<(.*?)<', input_string)
    sex_match = re.search(r'([MF])\d{13}', input_string)
    expiry_date_match = re.search(r'[MF](\d{6})', input_string)
    data_nasterii_match = re.search(r'ROU(\d{6})', input_string)

    # Extract information using regular expressions
    country = country_match.group(1)
    index_rou = input_string.find(country)
    index_less_than = input_string.find("<", index_rou + 3)
    name = input_string[index_rou + 3: index_less_than]

    sex = sex_match.group(1)

    data_nasterii = data_nasterii_match.group(1)
       
    year = int(data_nasterii[:2])
    month = data_nasterii[2:4]
    day = data_nasterii[4:]

    # Determine the full year based on the first two digits
    if year >= 0 and year <= 99:
        if sex == 'M':  # Assuming 'M' for males born in 1900-1999
            year += 1900
        else:           # Assuming 'F' for females born in 2000-2099
            year += 2000

    formatted_date = f"{year:04d}-{month}-{day}"
    sex_cnp = input_string[-8:-7]
    last_seven_digits_except_last = input_string[-7:-1]
    cnp = sex_cnp + data_nasterii + last_seven_digits_except_last

    # Map sex to human-readable values
    if sex == 'M':
        sex = 'male'
    elif sex == 'F':
        sex = 'female'

    # Extract the series number
    #seria_numar = re.findall(r'(\d{9})', input_string)
    #series_number = seria_numar[0] if seria_numar else None

    # Extract the expiry date
    expiry_date = expiry_date_match.group(1)
    if country == 'ROU':
    	country = 'Romanian'

    return {
        "Country": country,
        "Name": name,
        "Series_number": name_match[0],
        "Sex": sex,
        "Expiry Date": expiry_date,
        "CNP": cnp,
        "Data nasterii": formatted_date
    }

def process_image(file_path):
    image = cv2.imread(file_path)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Convert the image to grayscale for face detection
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


    # Perform face detection
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.15, minNeighbors=5)

    for i, (x, y, w, h) in enumerate(faces):
        # Crop the detected face from the image
        face = image[y:y + h, x:x + w]

        # Save the detected face as an image file
        output_file = os.path.join(output_directory, f"face_{i + 1}.jpg")
        cv2.imwrite(output_file, face)
        plt.imshow(cv2.cvtColor(face, cv2.COLOR_BGR2RGB))
        plt.title(f"Detected Face {i + 1}")
        plt.show()

def pass_rou(input_string):
    # Define regular expressions for each piece of information
    country_match = re.search(r'PE(\w{3})', input_string)
    series_pattern = r'(\d{9})'
    sex_match = re.search(r'([MF])\d+<', input_string)
    expiry_date_match = re.findall(r'[MF](\d{6})', input_string)
    cnp_match = re.search(r'(\d{13})<', input_string)

    # Extract information using regular expressions
    country = country_match.group(1)
    index_rou = input_string.find(country)
    index_less_than = input_string.find("<", index_rou + 3)
    name = input_string[index_rou + 3: index_less_than]
    series = re.search(series_pattern, input_string).group(1)
    sex = sex_match.group(1)
    cnp = cnp_match.group(1)

    # Map sex to human-readable values
    if sex == 'M':
        sex = 'Masculin'
    elif sex == 'F':
        sex = 'Feminin'

    return {
        "Country": country,
        "Name": name,
        "Series": series,
        "Sex": sex,
        "Expiry Date": expiry_date_match[0],
        "CNP": cnp
    }

mrz_reader_instance = mrz_reader()  # Create an instance of the mrz_reader class
mrz_reader_instance.load()

# If you want to detect the face
mrz_reader_instance.facedetect = True

# Before tesseract, check skewness
mrz_reader_instance.skewness = False

# Before tesseract, delete shadows
mrz_reader_instance.delete_shadows = True

# Before tesseract, clear background
mrz_reader_instance.clear_background = True


mrz_reader_instance.load()
'''mrz_dl, face = mrz_reader_instance.predict("C:\BEIA\pass_md.jpg")

print("MRZ Result:", mrz_dl)

result = pass_md(mrz_dl)

for key, value in result.items():
    if value:
        print(f"{key}: {value}")'''

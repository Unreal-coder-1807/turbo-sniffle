import streamlit as st
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import os
from pathlib import Path
from rail_utils.face_encoder import encode_image_array
from rail_utils.matcher import match_face

# UI config
st.set_page_config(page_title="Passenger Verification", layout="centered")
st.markdown("""
    <h1 style='text-align: center; color: #2196F3;'>🧍‍♂️ Verify Passenger Identity</h1>
    <p style='text-align: center;'>Verify passenger identity using uploaded or webcam image.</p>
    <hr>
""", unsafe_allow_html=True)

# Mock train list
train_options = {
    "12345 - Rajdhani Express": "12345",
    "12346 - Shatabdi Express": "12346",
    "12347 - Duronto Express": "12347",
    "12349 - Vande Bharat Express": "12349",
    "12348 - Garib Rath Express": "12348"
}

# Input: Train and Coach
col1, col2 = st.columns(2)
with col1:
    train_display = st.selectbox("🚆 Select Train", list(train_options.keys()))
    train_id = train_options[train_display]

with col2:
    coach = st.selectbox("🚪 Select Coach", ["A1", "A2", "B1", "B2", "C1", "C2", "S1", "S2", "GEN", "SL"])

travel_date = st.date_input("📅 Travel Date")

# DB Path
db_path = Path(__file__).parent / f"train_dbs/train_{train_id}_{travel_date}.db"

# Check if database exists
if not db_path.exists():
    st.error(f"Database for Train {train_id} on {travel_date} not found. Please register passengers first.")
    st.stop()

# Image Source
st.subheader("📸 Choose Image Source")
source = st.radio("Select input method", ["Webcam", "Upload from Device"])
image = None

# Initialize session state
if "verify_frame" not in st.session_state:
    st.session_state.verify_frame = None
if "verify_triggered" not in st.session_state:
    st.session_state.verify_triggered = False

# Webcam input
if source == "Webcam":
    captured = st.camera_input("Capture Passenger Image", key="verify_cam")
    if captured:
        image_bytes = captured.getvalue()
        image = np.array(Image.open(BytesIO(image_bytes)).convert('RGB'))
        st.image(image, caption="Captured Image", use_container_width=True)
        st.session_state.verify_frame = image
        st.session_state.verify_triggered = True

# Upload input
elif source == "Upload from Device":
    uploaded_file = st.file_uploader("Upload Passenger Image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image_bytes = uploaded_file.read()
        image = np.array(Image.open(BytesIO(image_bytes)).convert('RGB'))
        st.image(image, caption="Uploaded Image", use_container_width=True)
        st.session_state.verify_frame = image
        st.session_state.verify_triggered = True

# Face verification
if st.session_state.verify_triggered and st.session_state.verify_frame is not None:
    image = st.session_state.verify_frame
    st.info("🔄 Encoding face...")

    encoding = encode_image_array(image)

    if encoding is None:
        st.error("❌ No face detected in the image.")
        st.session_state.verify_triggered = False
    else:
        st.success("✅ Face encoded. Searching in database...")
        try:
            result = match_face(encoding, str(db_path))

            if result["match"]:
                st.success("🎯 Match Found! Passenger Authorized.")

                col1, col2 = st.columns(2)
                with col1:
                    st.image(image, caption="Current Image", use_container_width=True)
                with col2:
                    stored_image = Image.open(BytesIO(result["image"]))
                    st.image(stored_image, caption="Matched Record", use_container_width=True)

                st.markdown(f"""
                <div style="background-color:#4169e1;padding:10px;border-radius:5px;">
                    <strong>👤 Name:</strong> {result['name']}<br>
                    <strong>🎂 Age:</strong> {result['age']}<br>
                    <strong>🆔 Aadhar:</strong> {result['aadhar']}<br>
                    <strong>🚻 Gender:</strong> {result['gender']}<br>
                    <strong>🚪 Coach:</strong> {result['coach']}<br>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("🚫 No matching record found for this passenger.")

        except Exception as e:
            st.error("💥 Error while accessing train database.")
            st.code(str(e))

    st.session_state.verify_triggered = False

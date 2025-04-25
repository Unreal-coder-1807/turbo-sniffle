import streamlit as st
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import os
from rail_utils.face_encoder import encode_image_array
from rail_utils.matcher import match_face
from pathlib import Path

# UI config
st.set_page_config(page_title="Train Face Authorization", layout="centered")
st.markdown("""
    <h1 style='text-align: center; color: #4CAF50;'>🚆 Passenger Face Verification</h1>
    <p style='text-align: center;'>Upload a photo or capture one via webcam to authorize boarding.</p>
    <hr>
""", unsafe_allow_html=True)

# Train info
col1, col2 = st.columns(2)
with col1:
    # Train list: (train_no, train_name)
    TRAIN_LIST = [
        ("12345", "Rajdhani Express"),
        ("12346", "Shatabdi Express"),
        ("12347", "Duronto Express"),
        ("12348", "Garib Rath"),
        ("12349", "Vande Bharat")
    ]

    train_options = [f"{no} - {name}" for no, name in TRAIN_LIST]
    selected_train = st.selectbox("🚆 Select Train", train_options)

    # Extract train number from selection
    train_id = selected_train.split(" - ")[0]

    # Static coach list for now
    coach_list = ["A1", "A2", "B1", "B2", "S1", "S2", "SL", "GEN"]
    selected_coach = st.selectbox("🚪 Select Coach", coach_list)



with col2:
    travel_date = st.date_input("Travel Date")

db_rel_path = f"train_dbs/train_{train_id}_{travel_date}.db"
base_dir = Path(__file__).parent
db_path = base_dir / f"train_dbs/train_{train_id}_{travel_date}.db"
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Image selection
st.subheader("📸 Choose Image Source")
source = st.radio("Select input method", ["Webcam", "Upload from Device"])
image = None

# Initialize session state
if "captured_frame" not in st.session_state:
    st.session_state.captured_frame = None
if "processing_started" not in st.session_state:
    st.session_state.processing_started = False

# Webcam section
if source == "Webcam":
    captured = st.camera_input("Take a picture", key="webcam_input")
    if captured is not None:
        image_bytes = captured.getvalue()
        image = np.array(Image.open(BytesIO(image_bytes)).convert('RGB'))
        st.image(image, caption="Captured Image", use_container_width=True)
        st.session_state.captured_frame = image
        st.session_state.processing_started = True

# Upload from file
elif source == "Upload from Device":
    uploaded_file = st.file_uploader("Upload a face image", type=["jpg", "jpeg", "png"], accept_multiple_files=False)
    if uploaded_file is not None:
        image_bytes = uploaded_file.read()
        image = np.array(Image.open(BytesIO(image_bytes)).convert('RGB'))
        st.image(image, caption="Uploaded Image", use_container_width=True)
        st.session_state.processing_started = True
        st.session_state.captured_frame = image

# Encode and match only when ready
if st.session_state.processing_started and st.session_state.captured_frame is not None:
    image = st.session_state.captured_frame

    # Collect Metadata
    st.subheader("🧾 Enter Passenger Details")
    name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=1, max_value=120, step=1)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    aadhaar = st.text_input("Aadhaar Number (12 digits)", max_chars=12)

    if aadhaar and (not aadhaar.isdigit() or len(aadhaar) != 12):
        st.error("🚫 Aadhaar must be a 12-digit numeric value.")

    # Train ID Validation
    if not (train_id.isdigit() and len(train_id) == 5):
        st.warning("Please enter a valid 5-digit Train Number.")
    elif not (aadhaar.isdigit() and len(aadhaar) == 12):
        st.warning("Please enter a valid 12-digit Aadhaar number.")
    elif name and aadhaar:
        # Encode Image
        st.info("🔄 Encoding face...")
        encoding = encode_image_array(image)

        if encoding is None:
            st.error("❌ No face detected in the image.")
            st.session_state.processing_started = False
        else:
            st.success("✅ Face encoded successfully.")
            # Save to DB
            try:
                from rail_utils.db_manager import insert_passenger  # 👈 assume you have this
                print("DB path:", db_path)
                insert_passenger(
                    db_path=str(db_path),
                    name=name,
                    age=age,
                    gender=gender,
                    aadhaar=aadhaar,
                    encoding=encoding,
                    image=image,
                    coach = selected_coach
                )

                print("DB path:", db_path)
                st.success("✅ Passenger saved successfully!")
            except Exception as e:
                st.error("❌ Error saving to database.")
                st.code(str(e))
        st.session_state.processing_started = False

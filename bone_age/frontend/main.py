#!/usr/bin/env python3

import streamlit as st
import pydicom
from PIL import Image
import numpy as np
import time
import io
from fpdf import FPDF
import os

st.set_page_config(page_title="Bone-Ager", layout="centered")

st.title("🦴 Bone-Ager")
st.subheader("An automatic paediatric bone age assessment tool")

# User input section
st.text_input("What is your name?", key="name")
option = st.selectbox("What is the gender?", ("Female", "Male", "Unknown"))
st.write("You selected:", option)

# Sidebar links
st.sidebar.markdown(
    """
    <h3 style='margin-bottom:0'>
        <a href='https://github.com/jjjaden-hash/DESN2000-BINF-M13B_GAMMA' target='_blank' style='text-decoration:none; color:white;'>🌐 Our GitHub</a>
    </h3>
    <h3 style='margin-bottom:0'>
        <a href='https://www.google.com' target='_blank' style='text-decoration:none; color:white;'>ℹ️ About Us</a>
    </h3>
    <h3 style='margin-bottom:0'>
        <a href='https://www.google.com' target='_blank' style='text-decoration:none; color:white;'>📞 Contact Us</a>
    </h3>
    """,
    unsafe_allow_html=True
)


# Upload section
uploaded_file = st.file_uploader(
    "📤 Upload X-ray image (JPEG, PNG, or DICOM)",
    type=["jpeg", "jpg", "png", "dcm"]
)

# Utility: normalize pixel values to 0-255 for display
def normalize_to_uint8(image):
    if np.max(image) == np.min(image):
        return np.zeros_like(image, dtype=np.uint8)
    image = image.astype(np.float32)
    image = 255 * (image - np.min(image)) / (np.max(image) - np.min(image))
    return image.astype(np.uint8)

# Placeholder model function
def estimate_bone_age(image_array):
    # TODO: Replace with actual model logic
    return 120

# Main logic
if uploaded_file is not None:
    st.success("✅ File uploaded successfully!")
    file_ext = uploaded_file.name.lower().split(".")[-1]

    st.info("Analyzing image...")
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.01)
        progress_bar.progress(i + 1)
    st.success("✅ Analysis complete")

    # Display image and prediction
    col1, col2 = st.columns([1, 2])  # Smaller image, larger result area

    with col1:
        if file_ext == "dcm":
            dicom_data = pydicom.dcmread(uploaded_file)
            for tag in ["PatientName", "PatientID", "PatientBirthDate"]:
                if tag in dicom_data:
                    dicom_data.data_element(tag).value = ""
            image = dicom_data.pixel_array
            image = normalize_to_uint8(image)
            st.image(image, caption="DICOM Image", width=200)
        else:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", width=200)
            image = np.array(image)

    with col2:
        bone_age = estimate_bone_age(image)
        confidence_low = max(0, bone_age - 1.5)
        confidence_high = min(216, bone_age + 1.5)

        st.markdown(f"""
        <div style="font-size:28px; font-weight:bold; color:#f0f0f0;">
            🧠 Estimated Bone Age:
        </div>
        <div style="font-size:36px; font-weight:bold; color:#f0f0f0;">
            {bone_age:.1f} months
        </div>
        <div style="font-size:18px; color:#aaaaaa;">
            95% CI: {confidence_low:.1f} – {confidence_high:.1f} months
        </div>
        """, unsafe_allow_html=True)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        patient_name = st.session_state.get("name", "patient")
        pdf.cell(200, 10, txt="Bone-Ager Report", ln=True, align='C')
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Patient Name: {patient_name}", ln=True)
        pdf.cell(200, 10, txt=f"Gender: {option}", ln=True)
        pdf.cell(200, 10, txt=f"Estimated Bone Age: {bone_age:.1f} years", ln=True)

        pdf_bytes = io.BytesIO()
        pdf.output(pdf_bytes)
        pdf_bytes.seek(0)

        safe_filename = f"{patient_name.strip().replace(' ', '_')}_report.pdf"

        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name=safe_filename,
            mime="application/pdf"
        )

            
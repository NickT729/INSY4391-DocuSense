import streamlit as st
import google.generativeai as genai
import pdfplumber
import pytesseract
from PIL import Image
import sqlite3
import os
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
import re
import matplotlib.pyplot as plt
import numpy as np

# Set page config (must be the first Streamlit command)
st.set_page_config(
    page_title="DocuSense",
    page_icon="🏥",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Custom CSS with explicit constraints and positioning
st.markdown("""
    <style>
    /* Reset default margins and padding */
    .stApp {
        background-color: #FFFFFF !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Header container with fixed dimensions */
    .header-container {
        max-width: 1200px !important;
        width: 100% !important;
        margin: 0 auto !important;
        padding: 2rem 0 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        position: relative !important;
    }

    /* Image containers with fixed dimensions */
    [data-testid="column"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 0 !important;
    }

    /* Ensure images maintain aspect ratio and size */
    .stImage {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    .stImage > img {
        width: 350px !important;
        height: auto !important;
        object-fit: contain !important;
        margin: 0 auto !important;
    }

    /* Center text container */
    .header-text {
        text-align: center !important;
        padding: 3rem 0 !important;
        margin: 0 auto !important;
        width: 100% !important;
        position: relative !important;
    }

    .header-text h1 {
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
        color: black !important;
        font-weight: bold !important;
    }

    .header-text p {
        font-size: 1.1rem !important;
        color: black !important;
        margin: 0 !important;
    }

    /* Navigation button styling */
    .stButton > button {
        background-color: white !important;
        color: black !important;
        border: 1px solid #CCCCCC !important;
        border-radius: 10px !important;
        padding: 0.5rem 0.5rem !important;
        width: 100% !important;
        min-width: fit-content !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        min-height: 0 !important;
        line-height: 1.2 !important;
        font-size: 0.9rem !important;
        white-space: nowrap !important;
        margin: 0 !important;
    }

    /* Style the button container for minimal spacing */
    [data-testid="stHorizontalBlock"] > div {
        padding: 0 8px !important;
    }

    /* Navigation container */
    [data-testid="stHorizontalBlock"] {
        gap: 8px !important;
        padding: 0 16px !important;
        margin: 0.5rem auto 1.5rem auto !important;
        max-width: 800px !important;
        display: flex !important;
        justify-content: center !important;
    }

    /* Remove any extra spacing from column containers */
    [data-testid="column"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Create the header layout with fixed ratios
st.markdown('<div class="header-container">', unsafe_allow_html=True)

# Create three columns with specific ratios
left_col, middle_col, right_col = st.columns([0.4, 0.6, 0.4])

# Left doctor image
with left_col:
    st.image("images/fdoc.png")

# Center text
with middle_col:
    st.markdown("""
        <div class="header-text">
            <h1>DocuSense</h1>
            <p>AI medical analysis assistant</p>
        </div>
    """, unsafe_allow_html=True)

# Right doctor image
with right_col:
    st.image("images/doctor b.png")

st.markdown('</div>', unsafe_allow_html=True)

# Navigation using columns with proper spacing
col1, col2, col3, col4, col5 = st.columns([0.8, 1.4, 0.9, 0.8, 0.8])

with col1:
    if st.button("🔴 Home", use_container_width=True):
        st.session_state.page = "Home"
with col2:
    if st.button("📁 Upload Documents", use_container_width=True):
        st.session_state.page = "Upload Documents"
with col3:
    if st.button("➕ Analysis", use_container_width=True):
        st.session_state.page = "Analysis"
with col4:
    if st.button("💬 Chat", use_container_width=True):
        st.session_state.page = "Chat"
with col5:
    if st.button("📋 History", use_container_width=True):
        st.session_state.page = "History"

# Initialize page state if not exists
if 'page' not in st.session_state:
    st.session_state.page = "Home" 
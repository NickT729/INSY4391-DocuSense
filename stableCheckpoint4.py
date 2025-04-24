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
    page_icon="",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def get_db_connection():
    return sqlite3.connect('healthgenai.db')

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS documents
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  file_name TEXT,
                  upload_time TIMESTAMP,
                  content TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS summaries
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  doc_id INTEGER,
                  summary_text TEXT,
                  created_at TIMESTAMP,
                  FOREIGN KEY(doc_id) REFERENCES documents(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  question TEXT,
                  answer TEXT,
                  created_at TIMESTAMP)''')
    
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Initialize session state for theme if not exists
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'  # Set light as default

# Update theme based on URL parameter
if 'theme' in st.query_params:
    st.session_state.theme = st.query_params['theme']

# Custom CSS for theme
st.markdown("""
    <style>
    /* Main app styling */
    .stApp {
        background-color: #FFFFFF;
        color: black;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1rem;
    }
    
    .main-header img {
        width: 80px;
        height: 80px;
        margin-bottom: 0.5rem;
    }
    
    /* Button styling */
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
    
    .stButton > button:hover {
        background-color: #F0F0F0 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
    }

    .stButton > button:active {
        background-color: #E0E0E0 !important;
        transform: translateY(0) !important;
    }

    /* Style the button container for minimal spacing */
    [data-testid="stHorizontalBlock"] > div {
        padding: 0 2px !important;
    }

    /* Add specific spacing after Upload Documents button */
    [data-testid="stHorizontalBlock"] > div:nth-child(2) {
        margin-right: 16px !important;
    }

    [data-testid="stHorizontalBlock"] {
        gap: 0 !important;
        padding: 0 !important;
        margin: 0.5rem auto 1.5rem auto !important;
        max-width: 670px !important;
        display: flex !important;
        justify-content: center !important;
    }

    /* Remove any extra spacing from column containers */
    [data-testid="column"] {
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Ensure buttons maintain light theme */
    .stButton > button > div {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    /* Override any Streamlit default button styles */
    .stButton button:focus {
        box-shadow: none !important;
        outline: none !important;
    }

    .stButton button::selection {
        background: transparent !important;
    }
    
    /* Remove extra padding from main container */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 0;
    }
    
    /* Card styling */
    .card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        color: black;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        color: black;
    }
    
    .user-message {
        background-color: white;
    }
    
    .assistant-message {
        background-color: #f0f0f0;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        padding: 1rem 0;
        color: black;
        font-size: 0.9rem;
        margin-top: 2rem;
    }

    /* Disclaimer styling */
    .disclaimer {
        text-align: center;
        color: black;
        font-size: 0.9rem;
        font-style: italic;
        margin-top: 2rem;
        padding: 0 1rem;
    }

    /* Override Streamlit's default text colors */
    p, h1, h2, h3, h4, h5, h6, li {
        color: black !important;
    }

    .stMarkdown {
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

# Custom CSS for header container
st.markdown("""
    <style>
    .header-container {
        max-width: 800px !important;
        margin: 0 auto 0 12rem !important;
        padding: 0 !important;
        position: relative !important;
    }

    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0 !important;
    }

    /* Ensure images maintain proper size */
    .stImage > img {
        width: 300px !important;
        height: auto !important;
        display: block !important;
    }

    /* Custom text positioning */
    .title-text {
        position: absolute !important;
        left: 450px !important;
        top: -200px !important;
        text-align: left !important;
        z-index: 1000 !important;
        display: block !important;
    }
    </style>
""", unsafe_allow_html=True)

# Header container with matching width
container = st.container()
with container:
    col1, _ = st.columns([0.4, 0.6])
    with col1:
        try:
            st.image("images/doctor b.png", width=300)
        except:
            st.error("Could not load image")
    
    # Add title text outside the columns
    st.markdown("""
        <div class="title-text">
            <h1 style="color: black !important; margin: 0 !important; font-size: 2.5rem !important; padding-bottom: 0.5rem !important;">DocuSense</h1>
            <p style="color: black !important; margin: 0 !important;">AI medical analysis assistant</p>
        </div>
    """, unsafe_allow_html=True)

[REST OF THE FILE CONTENT REMAINS THE SAME] 
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

# Initialize session state if not exists
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'  # Set light as default

# Initialize session state for analysis and upload
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None
if 'current_upload' not in st.session_state:
    st.session_state.current_upload = None
if 'current_summary' not in st.session_state:
    st.session_state.current_summary = None
if 'current_lab_results' not in st.session_state:
    st.session_state.current_lab_results = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def clear_all_data():
    st.session_state.current_analysis = None
    st.session_state.current_upload = None
    st.session_state.current_summary = None
    st.session_state.current_lab_results = None
    st.rerun()

def clear_chat_history():
    st.session_state.chat_history = []
    st.rerun()

# Update theme based on URL parameter
if 'theme' in st.query_params:
    st.session_state.theme = st.query_params['theme']

# Custom CSS with explicit constraints and positioning
st.markdown("""
    <style>
    /* Reset default margins and padding */
    .stApp {
        background-color: #FFFFFF !important;
        margin: 0 !important;
        padding: 0 !important;
        min-height: 100vh !important;
        position: relative !important;
        display: flex !important;
        flex-direction: column !important;
        color: black !important;
    }
    
    /* Ensure all text elements are black by default */
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, span, div {
        color: black !important;
    }

    /* File uploader text color */
    .stUploadedFileData, .uploadedFileName {
        color: black !important;
    }

    /* Ensure input labels and text are black */
    .stTextInput label, .stFileUploader label {
        color: black !important;
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
        flex-shrink: 0 !important;
    }

    /* Image containers with fixed dimensions */
    [data-testid="column"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 0 !important;
        margin: 0 !important;
        position: relative !important;
    }

    /* Ensure images maintain aspect ratio and size */
    .stImage {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        position: relative !important;
    }

    .stImage > img {
        width: 350px !important;
        height: auto !important;
        object-fit: contain !important;
        margin: 0 auto !important;
        display: block !important;
    }

    /* Center text container */
    .header-text {
        text-align: center !important;
        padding: 3rem 0 !important;
        margin: 0 auto !important;
        width: 100% !important;
        position: relative !important;
        flex-shrink: 0 !important;
    }

    .header-text h1 {
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
        color: black !important;
        font-weight: bold !important;
        line-height: 1.2 !important;
    }

    .header-text p {
        font-size: 1.1rem !important;
        color: black !important;
        margin: 0 !important;
        line-height: 1.5 !important;
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
        position: relative !important;
    }

    /* Ensure button text is black */
    .stButton > button > div > p {
        color: black !important;
    }

    /* Style the button container for minimal spacing */
    [data-testid="stHorizontalBlock"] > div {
        padding: 0 8px !important;
        position: relative !important;
    }

    /* Navigation container */
    [data-testid="stHorizontalBlock"] {
        gap: 8px !important;
        padding: 0 16px !important;
        margin: 0.5rem auto 1.5rem auto !important;
        max-width: 800px !important;
        display: flex !important;
        justify-content: center !important;
        position: relative !important;
        flex-shrink: 0 !important;
    }

    /* Disclaimer styling */
    .disclaimer {
        text-align: center !important;
        color: black !important;
        font-size: 0.9rem !important;
        font-style: italic !important;
        margin: 2rem auto !important;
        padding: 0 1rem !important;
        max-width: 800px !important;
        position: relative !important;
        flex-shrink: 0 !important;
    }

    /* Footer styling */
    .footer {
        text-align: center !important;
        padding: 1rem 0 !important;
        color: black !important;
        font-size: 0.9rem !important;
        margin-top: 1rem !important;
        width: 100% !important;
        position: relative !important;
        bottom: 0 !important;
        flex-shrink: 0 !important;
    }

    /* Main content area */
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        position: relative !important;
        flex: 1 0 auto !important;
    }

    /* File uploader styling */
    .stFileUploader {
        width: 100% !important;
    }

    .uploadedFile {
        background-color: white !important;
        color: black !important;
        border-radius: 4px !important;
        padding: 8px !important;
        margin: 8px 0 !important;
    }

    /* Style the file uploader drop zone */
    .stFileUploader > div:first-child {
        background-color: #1E1E1E !important;
        border: 2px dashed #666666 !important;
        padding: 1rem !important;
    }

    /* Make drag and drop text and cloud icon WHITE */
    .stFileUploader [data-testid="stFileUploadDropzone"] {
        background-color: #1E1E1E !important;
        color: white !important;
    }

    /* Style the upload icon to be WHITE */
    .stFileUploader [data-testid="stFileUploadDropzone"] svg {
        fill: white !important;
    }

    /* Make the "Drag and drop file here" text WHITE */
    .stFileUploader [data-testid="stFileUploadDropzone"] div {
        color: white !important;
    }

    /* Make the file type text below WHITE */
    .stFileUploader > div > small {
        color: white !important;
    }

    /* Style the black box text to be WHITE */
    .element-container:has(pre) {
        color: white !important;
        background-color: #1E1E1E !important;
        padding: 1rem !important;
        border-radius: 4px !important;
    }

    .element-container:has(pre) pre {
        color: white !important;
        background-color: #1E1E1E !important;
    }

    .element-container:has(pre) code {
        color: white !important;
        background-color: #1E1E1E !important;
    }

    /* Make sure the Browse files button remains visible */
    .stFileUploader button {
        background-color: white !important;
        color: black !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 0.5rem 1rem !important;
    }

    /* Ensure the file details section remains readable */
    .uploadedFile {
        background-color: white !important;
        color: black !important;
        border-radius: 4px !important;
        padding: 8px !important;
        margin: 8px 0 !important;
    }

    /* Style the file uploader status text */
    .stFileUploader > div > span {
        color: black !important;
    }

    /* Style the file type text */
    .stFileUploader > div > small {
        color: #666666 !important;
    }

    /* Style the browse files button */
    .stFileUploader button {
        background-color: white !important;
        color: black !important;
        border: 1px solid #CCCCCC !important;
        border-radius: 4px !important;
    }

    /* Fix any remaining dark text in the uploader */
    .stFileUploader, .stFileUploader * {
        color: black !important;
    }

    /* Ensure JSON output is readable */
    .stJson {
        background-color: white !important;
        color: black !important;
    }

    /* Override Streamlit's default dark styling */
    [data-testid="stFileUploadDropzone"] {
        color: white !important;
        background-color: #1E1E1E !important;
    }
    
    [data-testid="stFileUploadDropzone"] > div {
        color: white !important;
    }
    
    [data-testid="stFileUploadDropzone"] svg {
        fill: white !important;
    }
    
    /* Force white text in the black box */
    .json-object {
        color: white !important;
        background-color: #1E1E1E !important;
    }
    
    pre {
        color: white !important;
        background-color: #1E1E1E !important;
    }
    
    code {
        color: white !important;
        background-color: #1E1E1E !important;
    }
    
    /* Override any dark text in dark areas */
    .stMarkdown div[data-testid="stMarkdownContainer"] pre {
        color: white !important;
    }
    
    /* Ensure file upload text is white */
    .st-emotion-cache-1eqt3ay {
        color: white !important;
    }
    
    .st-emotion-cache-1gulkj5 {
        color: white !important;
    }
    
    /* Override any Streamlit emotion classes that might be causing issues */
    .st-emotion-cache-* {
        color: inherit !important;
    }

    /* Chat interface styling */
    .chat-interface {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        padding: 0;
        margin: 0;
    }
    
    .chat-container {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #E0E0E0;
        margin: 0;
        min-height: 50px;
        max-height: 500px;
        overflow-y: auto;
    }
    
    .chat-message {
        display: flex;
        flex-direction: column;
        padding: 15px 20px;
        margin: 10px 0;
        border-radius: 15px;
        font-size: 16px;
        line-height: 1.5;
        max-width: 85%;
    }
    
    .chat-message.user {
        background-color: #E3F2FD;
        margin-left: auto;
        margin-right: 0;
        color: #000000;
    }
    
    .chat-message.assistant {
        background-color: #F5F5F5;
        margin-right: auto;
        margin-left: 0;
        color: #000000;
    }
    
    .chat-sender {
        font-weight: bold;
        margin-bottom: 5px;
        font-size: 14px;
    }
    
    .chat-content {
        margin: 5px 0;
    }
    
    .chat-time {
        font-size: 12px;
        color: #666666;
        margin-top: 5px;
        align-self: flex-end;
    }
    
    .input-container {
        background-color: white;
        padding: 1rem;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        margin: 0;
    }

    .stTextArea textarea {
        font-size: 16px;
        padding: 12px;
        border-radius: 10px;
        min-height: 100px;
        resize: none;
    }

    /* Remove extra padding and margins from Streamlit containers */
    .stButton, .stTextArea {
        margin: 0 !important;
        padding: 0 !important;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        margin: 0 !important;
    }

    /* Hide empty elements */
    .empty-container {
        display: none !important;
    }

    div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
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

def process_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        try:
            file_details = {"Filename": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": f"{uploaded_file.size / 1024:.2f} KB"}
            st.write(file_details)
            
            # Process PDF files
            if uploaded_file.type == "application/pdf":
                with pdfplumber.open(uploaded_file) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text()
                return text
            
            # Process image files
            elif uploaded_file.type.startswith('image/'):
                image = Image.open(uploaded_file)
                text = pytesseract.image_to_string(image)
                return text
            
            # Process text files
            elif uploaded_file.type == "text/plain":
                text = uploaded_file.getvalue().decode("utf-8")
                return text
            
            else:
                st.error(f"Unsupported file format: {uploaded_file.type}")
                return None
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            return None

def generate_summary(text):
    model = genai.GenerativeModel('gemini-1.5-pro')
    prompt = f"""Please provide a clear, concise summary of this medical document in plain language. 
    Focus on key findings, diagnoses, and recommendations. Make it easy for a non-medical professional to understand.
    
    Document text:
    {text}
    """
    response = model.generate_content(prompt)
    return response.text

def extract_lab_results(text):
    # Define reference ranges
    reference_ranges = {
        'WBC': {'min': 4.0, 'max': 10.0, 'unit': 'x 10^9/L'},
        'RBC': {'min': 4.0, 'max': 5.5, 'unit': 'x 10^12/L'},
        'Hemoglobin': {'min': 13.0, 'max': 17.0, 'unit': 'g/dL'},
        'Platelets': {'min': 150, 'max': 350, 'unit': 'x 10^9/L'},
        'Glucose': {'min': 70, 'max': 100, 'unit': 'mg/dL'},
        'Cholesterol': {'min': 0, 'max': 200, 'unit': 'mg/dL'},
        'HDL': {'min': 40, 'max': 60, 'unit': 'mg/dL'},
        'LDL': {'min': 0, 'max': 130, 'unit': 'mg/dL'}
    }
    
    # Updated regex patterns to match sample format
    patterns = {
        'WBC': r'White Blood Cells:\s*([\d.]+)\s*x10\^9/L',
        'RBC': r'Red Blood Cells:\s*([\d.]+)\s*x10\^12/L',
        'Hemoglobin': r'Hemoglobin:\s*([\d.]+)\s*g/dL',
        'Platelets': r'Platelets:\s*([\d.]+)\s*x10\^9/L',
        'Glucose': r'Glucose.*?:\s*([\d.]+)\s*mg/dL',
        'Cholesterol': r'Cholesterol:\s*([\d.]+)\s*mg/dL',
        'HDL': r'HDL:\s*([\d.]+)\s*mg/dL',
        'LDL': r'LDL:\s*([\d.]+)\s*mg/dL'
    }
    
    results = {}
    for test, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            value = float(match.group(1))
            ref_range = reference_ranges[test]
            status = 'Normal'
            if value < ref_range['min']:
                status = 'Low'
            elif value > ref_range['max']:
                status = 'High'
            
            results[test] = {
                'value': value,
                'unit': ref_range['unit'],
                'min': ref_range['min'],
                'max': ref_range['max'],
                'status': status
            }
    
    if results:
        # Create DataFrame
        df = pd.DataFrame.from_dict(results, orient='index')
        
        # Set dark theme for matplotlib
        plt.style.use('dark_background')
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.patch.set_facecolor('#2D2D2D')
        ax.set_facecolor('#2D2D2D')
        
        # Plot bars
        tests = list(results.keys())
        values = [results[test]['value'] for test in tests]
        x = np.arange(len(tests))
        
        # Plot bars with colors based on status
        colors = ['#FF4B4B' if results[test]['status'] == 'High' 
                 else '#3B82F6' if results[test]['status'] == 'Low'
                 else '#10B981' for test in tests]
        
        bars = ax.bar(x, values, color=colors)
        
        # Add reference range lines
        for i, test in enumerate(tests):
            ax.hlines(y=results[test]['min'], xmin=i-0.4, xmax=i+0.4, 
                     colors='#808080', linestyles='--', alpha=0.5)
            ax.hlines(y=results[test]['max'], xmin=i-0.4, xmax=i+0.4, 
                     colors='#808080', linestyles='--', alpha=0.5)
        
        # Customize plot
        ax.set_xticks(x)
        ax.set_xticklabels(tests, rotation=45, ha='right', color='white')
        ax.set_title('Lab Test Results', color='white', pad=20)
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#FF4B4B', label='High'),
            Patch(facecolor='#3B82F6', label='Low'),
            Patch(facecolor='#10B981', label='Normal'),
        ]
        ax.legend(handles=legend_elements, facecolor='#2D2D2D', labelcolor='white')
        
        plt.tight_layout()
        
        return df, fig
    
    return pd.DataFrame(), None

def chat_with_docs(question, doc_content=None):
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    if doc_content:
        prompt = f"""As a medical AI assistant, please answer the following question based on the provided medical document. 
        If the answer cannot be found in the document, provide general medical information and clearly state that it's not from the document.
        
        Document content: {doc_content}
        
        Question: {question}
        """
    else:
        prompt = f"""As a medical AI assistant, please answer the following question based on general medical knowledge.
        Provide accurate, helpful information while being clear that this is general advice.
        
        Question: {question}
        """
    
    response = model.generate_content(prompt)
    return response.text

# Page content based on navigation
if st.session_state.page == "Home":
    st.markdown("""
        <h1 style='text-align: center; font-size: 2.5rem; margin-bottom: 1.5rem; color: black;'>Welcome to DocuSense</h1>
        
        <p style='text-align: center; font-size: 1.2rem; margin-bottom: 1.5rem; color: black;'>
            DocuSense is your intelligent medical data analysis assistant. Our platform helps you:
        </p>

        <div style='max-width: 600px; margin: 0 auto; text-align: center;'>
            <ul style='list-style: none; padding: 0; margin: 1.5rem 0;'>
                <li style='margin: 1rem 0; font-size: 1.1rem; color: black;'>
                    📁 Upload and analyze medical documents
                </li>
                <li style='margin: 1rem 0; font-size: 1.1rem; color: black;'>
                    📊 Visualize your test results
                </li>
                <li style='margin: 1rem 0; font-size: 1.1rem; color: black;'>
                    💬 Get instant answers to your medical questions
                </li>
                <li style='margin: 1rem 0; font-size: 1.1rem; color: black;'>
                    📋 Track your medical history
                </li>
            </ul>
        </div>

        <p style='text-align: center; font-size: 1.2rem; margin-top: 2rem; color: black;'>
            ✨ Get started by uploading your medical documents or asking questions about your health.
        </p>
    """, unsafe_allow_html=True)

elif st.session_state.page == "Upload Documents":
    st.markdown("""
        <h1 style='color: black; margin-bottom: 1rem;'>📁 Upload Documents</h1>
    """, unsafe_allow_html=True)
    
    # Add clear button at the top
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🗑️ Clear", key="upload_clear", use_container_width=True):
            clear_all_data()
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'png', 'jpg', 'jpeg', 'txt']
    )
    
    # Process new file upload
    if uploaded_file is not None and (st.session_state.current_upload is None or 
        uploaded_file.name != st.session_state.current_upload.get('name')):
        
        file_details = {
            "name": uploaded_file.name,
            "type": uploaded_file.type,
            "size": f"{uploaded_file.size / 1024:.2f} KB"
        }
        st.session_state.current_upload = file_details
        
        with st.spinner('Processing document...'):
            text = process_uploaded_file(uploaded_file)
            if text:
                try:
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute('''INSERT INTO documents (file_name, upload_time, content)
                               VALUES (?, ?, ?)''', 
                            (uploaded_file.name, datetime.now(), text))
                    doc_id = c.lastrowid
                    
                    summary = generate_summary(text)
                    c.execute('''INSERT INTO summaries (doc_id, summary_text, created_at)
                               VALUES (?, ?, ?)''',
                            (doc_id, summary, datetime.now()))
                    
                    conn.commit()
                    conn.close()
                    
                    # Store results in session state
                    st.session_state.current_summary = summary
                    st.session_state.current_lab_results = extract_lab_results(text)
                    st.session_state.current_analysis = {
                        'summary': summary,
                        'lab_results': st.session_state.current_lab_results
                    }
                
                except sqlite3.Error as e:
                    st.error(f"Database error: {e}")
                    st.info("Please try again. If the error persists, restart the application.")
    
    # Display current upload information if it exists
    if st.session_state.current_upload is not None:
        st.markdown("""
            <div style='background-color: white; padding: 1rem; border-radius: 4px; border: 1px solid #CCCCCC; margin: 1rem 0;'>
                <h3 style='color: black; margin-bottom: 0.5rem;'>File Details:</h3>
                <ul style='color: black; list-style-type: none; padding: 0; margin: 0;'>
                    <li style='color: black; margin: 4px 0;'>📄 <strong>Filename:</strong> {}</li>
                    <li style='color: black; margin: 4px 0;'>📋 <strong>File Type:</strong> {}</li>
                    <li style='color: black; margin: 4px 0;'>📦 <strong>Size:</strong> {}</li>
                </ul>
            </div>
        """.format(
            st.session_state.current_upload['name'],
            st.session_state.current_upload['type'],
            st.session_state.current_upload['size']
        ), unsafe_allow_html=True)
        
        if st.session_state.current_summary:
            st.markdown("""
                <div style='background-color: white; padding: 1rem; border-radius: 4px; border: 1px solid #CCCCCC; margin: 1rem 0;'>
                    <h3 style='color: black; margin-bottom: 1rem;'>📄 Summary</h3>
                    <p style='color: black;'>{}</p>
                </div>
            """.format(st.session_state.current_summary), unsafe_allow_html=True)
            
            if st.session_state.current_lab_results and st.session_state.current_lab_results[0] is not None:
                df, fig = st.session_state.current_lab_results
                if not df.empty:
                    st.markdown("""
                        <div style='background-color: white; padding: 1rem; border-radius: 4px; border: 1px solid #CCCCCC; margin: 1rem 0;'>
                            <h3 style='color: black; margin-bottom: 0.5rem;'>🔬 Lab Results</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.dataframe(df.style.applymap(
                        lambda x: 'color: #FF4B4B' if x == 'High' else 'color: #3B82F6' if x == 'Low' else 'color: #10B981',
                        subset=['status']
                    ))
                    if fig:
                        st.pyplot(fig)

elif st.session_state.page == "Analysis":
    st.markdown("""
        <h1 style='color: black; margin-bottom: 1rem;'>📊 Analysis</h1>
    """, unsafe_allow_html=True)
    
    # Add clear button at the top
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🗑️ Clear", key="analysis_clear", use_container_width=True):
            clear_all_data()
    
    if st.session_state.current_analysis is None:
        st.info("No documents have been analyzed yet. Please upload a document first.")
    else:
        # Display the stored analysis
        summary = st.session_state.current_analysis['summary']
        df, fig = st.session_state.current_analysis['lab_results']
        
        st.markdown("""
        <div class="card">
            <h3>📄 Document Summary</h3>
            <p>{}</p>
        </div>
        """.format(summary), unsafe_allow_html=True)
        
        if not df.empty:
            st.markdown("""
            <div class="card">
                <h3>🔬 Lab Results Analysis</h3>
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(df.style.applymap(
                lambda x: 'color: #FF4B4B' if x == 'High' else 'color: #3B82F6' if x == 'Low' else 'color: #10B981',
                subset=['status']
            ))
            if fig:
                st.pyplot(fig)

elif st.session_state.page == "Chat":
    st.markdown('<div class="chat-interface">', unsafe_allow_html=True)

    # Header with title and clear button in a single row
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown("<h1 style='color: black; margin: 0 0 1rem 0;'>💬 Chat with DocuSense</h1>", unsafe_allow_html=True)
    with col2:
        if st.button("🗑️ Clear Chat", key="chat_clear", use_container_width=True):
            clear_chat_history()
    
    # Get the current session's document content only
    doc_content = None
    if st.session_state.current_upload and st.session_state.current_summary:
        doc_content = {
            'content': st.session_state.current_summary,
            'lab_results': st.session_state.current_lab_results
        }
    
    if not doc_content:
        st.info("Please upload a medical document in the Upload Documents page to enable chat functionality.")
        st.stop()

    # Chat input form
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Type your message:",
            key="user_input",
            height=100,
            placeholder="Ask me about the medical report..."
        )
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.form_submit_button(
                "Send Message",
                use_container_width=True
            )

        if submit_button and user_input:
            current_time = datetime.now().strftime("%I:%M %p")
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input,
                "time": current_time
            })
            
            with st.spinner('Thinking...'):
                answer = chat_with_docs(user_input, doc_content['content'])
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer,
                    "time": datetime.now().strftime("%I:%M %p")
                })
            
            st.rerun()

    # Display chat history
    if len(st.session_state.chat_history) > 0:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"""
                    <div class="chat-message user">
                        <div class="chat-sender">You</div>
                        <div class="chat-content">{message["content"]}</div>
                        <div class="chat-time">{message["time"]}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="chat-message assistant">
                        <div class="chat-sender">DocuSense</div>
                        <div class="chat-content">{message["content"]}</div>
                        <div class="chat-time">{message["time"]}</div>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "History":
    st.markdown("""
        <h1 style='color: black; margin-bottom: 1rem;'>📋 Document History</h1>
    """, unsafe_allow_html=True)
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get all documents and their summaries
    c.execute('''SELECT d.file_name, d.upload_time, s.summary_text
                 FROM documents d
                 JOIN summaries s ON d.id = s.doc_id
                 ORDER BY d.upload_time DESC''')
    documents = c.fetchall()
    
    if documents:
        for doc in documents:
            st.markdown(f"""
            <div class="card">
                <h3>📄 {doc[0]}</h3>
                <p><em>Uploaded on {doc[1]}</em></p>
                <p>{doc[2]}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No documents found in history.")
    
    st.markdown("---")
    
    st.title("💬 Chat History")
    c.execute('SELECT question, answer, created_at FROM chat_history ORDER BY created_at DESC')
    chats = c.fetchall()
    
    if chats:
        for chat in chats:
            st.markdown(f"""
            <div class="chat-container">
                <div class="chat-message user-message">
                    <strong>You:</strong> {chat[0]}
                </div>
                <div class="chat-message assistant-message">
                    <strong>DocuSense:</strong> {chat[1]}
                </div>
                <em>Asked on {chat[2]}</em>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No chat history found.")
    
    conn.close()

# Add disclaimer and footer
st.markdown("""
    <div class="disclaimer">
        This is a demo application. Always consult with your healthcare provider for medical advice.
    </div>
    <div class="footer">
        © 2025 DocuSense - AI Healthcare Assistant
    </div>
""", unsafe_allow_html=True) 
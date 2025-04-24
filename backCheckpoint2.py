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

    .stImage > img {
        width: 300px !important;
        height: auto !important;
    }

    .title-container {
        position: relative !important;
        text-align: center !important;
        padding-top: 3rem !important;
        margin-left: -8rem !important;
        width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

# Custom CSS for header container
st.markdown("""
    <style>
    .header-container {
        max-width: 800px;
        margin: 0 auto 0 12rem;  /* Added left margin to shift everything left */
        padding: 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header container with matching width
container = st.container()
with container:
    col1, col2 = st.columns([0.4, 0.6])
    with col1:
        try:
            st.image("images/doctor b.png", width=300)
        except:
            st.error("Could not load image")
    with col2:
        st.markdown("""
            <div style="text-align: center; padding-top: 5.5rem; margin-left: -12.5rem;">
                <h1 style="color: black; margin: 0; font-size: 2.5rem;">DocuSense</h1>
                <p style="color: black; margin: 0.5rem 0 0 0;">AI medical analysis assistant</p>
            </div>
        """, unsafe_allow_html=True)

# Navigation using columns with minimal spacing
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
            file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
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
        
        <div class='disclaimer' style='color: black;'>This is a demo application. Always consult with your healthcare provider for medical advice.</div>
    """, unsafe_allow_html=True)

elif st.session_state.page == "Upload Documents":
    st.title("📁 Upload Documents")
    
    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'png', 'jpg', 'jpeg', 'txt'])
    
    if uploaded_file is not None:
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
                    
                    st.markdown("""
                    <div class="card">
                        <h3>📄 Summary</h3>
                        <p>{}</p>
                    </div>
                    """.format(summary), unsafe_allow_html=True)
                    
                    # Display lab results if found
                    df, fig = extract_lab_results(text)
                    if not df.empty:
                        st.markdown("""
                        <div class="card">
                            <h3>🔬 Lab Results</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        st.dataframe(df.style.applymap(
                            lambda x: 'color: #FF4B4B' if x == 'High' else 'color: #3B82F6' if x == 'Low' else 'color: #10B981',
                            subset=['status']
                        ))
                        if fig:
                            st.pyplot(fig)
                
                except sqlite3.Error as e:
                    st.error(f"Database error: {e}")
                    st.info("Please try again. If the error persists, restart the application.")

elif st.session_state.page == "Analysis":
    st.title("📊 Analysis")
    
    # Get the most recent document
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''SELECT d.content, s.summary_text 
                 FROM documents d 
                 JOIN summaries s ON d.id = s.doc_id 
                 ORDER BY d.upload_time DESC 
                 LIMIT 1''')
    result = c.fetchone()
    conn.close()
    
    if result:
        doc_content, summary = result
        
        st.markdown("""
        <div class="card">
            <h3>📄 Document Summary</h3>
            <p>{}</p>
        </div>
        """.format(summary), unsafe_allow_html=True)
        
        df, fig = extract_lab_results(doc_content)
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
    else:
        st.info("No documents found. Please upload a document first.")

elif st.session_state.page == "Chat":
    st.title("💬 Chat with DocuSense")
    
    # Get the most recent document content
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT content FROM documents ORDER BY upload_time DESC LIMIT 1')
    result = c.fetchone()
    doc_content = result[0] if result else None
    conn.close()
    
    question = st.text_input("Ask a question about your medical documents:")
    
    if st.button("Ask", use_container_width=True):
        if question:
            with st.spinner('Thinking...'):
                answer = chat_with_docs(question, doc_content)
                
                # Save to chat history
                conn = get_db_connection()
                c = conn.cursor()
                c.execute('''INSERT INTO chat_history (question, answer, created_at)
                           VALUES (?, ?, ?)''',
                        (question, answer, datetime.now()))
                conn.commit()
                conn.close()
                
                st.markdown("""
                <div class="chat-message user-message">
                    <strong>You:</strong> {}
                </div>
                <div class="chat-message assistant-message">
                    <strong>DocuSense:</strong> {}
                </div>
                """.format(question, answer), unsafe_allow_html=True)
        else:
            st.warning("Please enter a question.")

elif st.session_state.page == "History":
    st.title("📋 Document History")
    
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

# Footer
st.markdown("""
<div class="footer">
    © 2025 DocuSense - AI Healthcare Assistant
</div>
""", unsafe_allow_html=True) 
# 🏥 DocuSense - AI Healthcare Assistant

DocuSense is an AI-powered application that simplifies medical reports using plain language summaries, charts, definitions, and a chatbot.

## Features

- 📄 Upload and process medical documents (PDFs, images, text)
- 🤖 AI-powered summarization using Google's Gemini API
- 📊 Visualization of test results
- 📚 Medical term definitions
- 💬 Interactive Q&A chatbot

## Setup Instructions

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Tesseract OCR:
   - Windows: Download and install from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - Add Tesseract to your system PATH

4. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```
   Then add your Gemini API key to the `.env` file

5. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Upload medical documents (PDFs, images, or text files)
2. View AI-generated summaries
3. Interact with the chatbot for questions about your documents
4. View visualizations of test results

## Technologies Used

- Streamlit for the web interface
- Google Gemini API for AI processing
- PDFplumber for PDF parsing
- Tesseract OCR for image text extraction
- SQLite for data storage
- Plotly for visualizations

## License

MIT License 
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.units import inch

def create_sample_pdf():
    # Create a new PDF file
    c = canvas.Canvas("sample_medical_report.pdf", pagesize=letter)
    
    # Set font and size
    c.setFont("Helvetica", 12)
    
    # Add content
    content = [
        "PATIENT MEDICAL REPORT",
        "",
        "Patient Name: John Doe",
        "Date of Birth: 01/15/1980",
        "Date of Visit: 03/15/2024",
        "MRN: 12345678",
        "",
        "CHIEF COMPLAINT:",
        "Patient presents with fatigue, occasional chest pain, and concerns about recent blood work results.",
        "",
        "HISTORY OF PRESENT ILLNESS:",
        "Patient reports increasing fatigue over the past 3 months. Denies significant weight changes. Reports occasional chest pain not associated with exertion. Recent lifestyle changes include reduced physical activity and dietary changes.",
        "",
        "PHYSICAL EXAMINATION:",
        "Vital Signs:",
        "- Blood Pressure: 135/85 mmHg (Elevated)",
        "- Heart Rate: 82 bpm",
        "- Temperature: 98.6°F",
        "- Respiratory Rate: 16/min",
        "- Weight: 185 lbs (↑5 lbs from last visit)",
        "- Height: 5'10\"",
        "- BMI: 26.5 (Overweight)",
        "",
        "LABORATORY RESULTS:",
        "",
        "Complete Blood Count (CBC):",
        "- WBC: 11.5 x 10^9/L (High) [Reference: 4.0-10.0]",
        "- RBC: 4.2 x 10^12/L (Normal) [Reference: 4.0-5.5]",
        "- Hemoglobin: 13.2 g/dL (Normal) [Reference: 13.0-17.0]",
        "- Platelets: 385 x 10^9/L (High) [Reference: 150-350]",
        "- Neutrophils: 75% (High) [Reference: 40-60]",
        "- Lymphocytes: 15% (Low) [Reference: 20-40]",
        "",
        "Comprehensive Metabolic Panel:",
        "- Glucose: 126 mg/dL (High) [Reference: 70-100]",
        "- HbA1c: 6.4% (High) [Reference: <5.7]",
        "- BUN: 22 mg/dL (High) [Reference: 7-20]",
        "- Creatinine: 1.3 mg/dL (High) [Reference: 0.7-1.2]",
        "- ALT: 45 U/L (High) [Reference: 7-35]",
        "- AST: 42 U/L (High) [Reference: 8-33]",
        "",
        "Lipid Panel:",
        "- Total Cholesterol: 245 mg/dL (High) [Reference: <200]",
        "- HDL: 38 mg/dL (Low) [Reference: >40]",
        "- LDL: 165 mg/dL (High) [Reference: <130]",
        "- Triglycerides: 210 mg/dL (High) [Reference: <150]",
        "",
        "Thyroid Function:",
        "- TSH: 4.8 mIU/L (High) [Reference: 0.4-4.0]",
        "- Free T4: 0.9 ng/dL (Low Normal) [Reference: 0.8-1.8]",
        "- Free T3: 2.8 pg/mL (Normal) [Reference: 2.3-4.2]",
        "",
        "Inflammatory Markers:",
        "- CRP: 3.8 mg/L (High) [Reference: <3.0]",
        "- ESR: 28 mm/hr (High) [Reference: 0-22]",
        "",
        "IMPRESSION:",
        "1. Pre-diabetes with elevated fasting glucose",
        "2. Dyslipidemia with elevated cholesterol and triglycerides",
        "3. Subclinical hypothyroidism",
        "4. Mild hypertension",
        "5. Elevated liver enzymes",
        "6. Inflammatory markers elevation",
        "",
        "RECOMMENDATIONS:",
        "1. Initiate lifestyle modifications:",
        "   - Mediterranean diet",
        "   - 150 minutes/week moderate exercise",
        "   - Weight loss goal: 10-15 lbs",
        "2. Start Metformin 500mg daily for pre-diabetes",
        "3. Begin Atorvastatin 20mg daily for dyslipidemia",
        "4. Recheck thyroid function in 6 weeks",
        "5. Blood pressure monitoring twice weekly",
        "6. Follow-up in 3 months with repeat labs",
        "7. Referral to nutritionist",
        "",
        "Physician: Dr. Sarah Smith, MD",
        "Signature: ___________________",
        "Date: 03/15/2024"
    ]
    
    # Set starting position
    y = 750
    x = 50
    
    # Add each line of content
    for line in content:
        if y < 50:  # If we reach the bottom of the page
            c.showPage()  # Create a new page
            y = 750  # Reset y position
            c.setFont("Helvetica", 12)  # Reset font
        
        # Make headers bold
        if line.endswith(":") or line == "PATIENT MEDICAL REPORT":
            c.setFont("Helvetica-Bold", 14)
            c.drawString(x, y, line)
            c.setFont("Helvetica", 12)
        else:
            c.drawString(x, y, line)
        y -= 15
    
    # Save the PDF
    c.save()

if __name__ == "__main__":
    create_sample_pdf()
    print("PDF file created successfully!") 
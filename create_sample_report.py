from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def create_medical_report():
    doc = SimpleDocTemplate(
        "sample_medical_report2.pdf",
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30
    ))
    styles.add(ParagraphStyle(
        name='CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=24
    ))
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12
    ))

    # Title
    elements.append(Paragraph("MEDICAL LABORATORY REPORT", styles['CustomTitle']))
    
    # Patient Info
    patient_info = [
        ["Date:", "March 15, 2024"],
        ["Patient ID:", "12345"],
        ["Name:", "John Smith"],
        ["DOB:", "05/15/1980"]
    ]
    
    t = Table(patient_info, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    # CBC Section
    elements.append(Paragraph("COMPLETE BLOOD COUNT (CBC)", styles['CustomHeading']))
    
    cbc_data = [
        ["Test", "Result", "Reference Range"],
        ["White Blood Cells:", "8.5 x10^9/L", "4.0-10.0"],
        ["Red Blood Cells:", "5.2 x10^12/L", "4.0-5.5"],
        ["Hemoglobin:", "14.5 g/dL", "13.0-17.0"],
        ["Platelets:", "280 x10^9/L", "150-350"]
    ]
    
    t = Table(cbc_data, colWidths=[2.5*inch, 2*inch, 2*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
    ]))
    elements.append(t)

    # Metabolic Panel Section
    elements.append(Paragraph("METABOLIC PANEL", styles['CustomHeading']))
    
    metabolic_data = [
        ["Test", "Result", "Reference Range"],
        ["Glucose:", "95 mg/dL", "70-100"],
        ["Cholesterol:", "185 mg/dL", "0-200"],
        ["HDL:", "55 mg/dL", "40-60"],
        ["LDL:", "115 mg/dL", "0-130"]
    ]
    
    t = Table(metabolic_data, colWidths=[2.5*inch, 2*inch, 2*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
    ]))
    elements.append(t)

    # Physician's Notes
    elements.append(Paragraph("PHYSICIAN'S NOTES", styles['CustomHeading']))
    elements.append(Paragraph(
        "Patient's blood work shows all values within normal ranges. The cholesterol profile is particularly good, "
        "with HDL and LDL at optimal levels. Continue current diet and exercise regimen.",
        styles['CustomBody']
    ))

    # Recommendations
    elements.append(Paragraph("RECOMMENDATIONS", styles['CustomHeading']))
    recommendations = [
        "1. Maintain current healthy lifestyle",
        "2. Regular exercise (30 minutes, 5 times per week)",
        "3. Follow-up visit in 6 months",
        "4. Continue balanced diet rich in fruits and vegetables"
    ]
    for rec in recommendations:
        elements.append(Paragraph(rec, styles['CustomBody']))

    # Signature
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("This report has been electronically verified and signed by:", styles['CustomBody']))
    elements.append(Paragraph("Dr. Sarah Johnson, MD", styles['CustomBody']))
    elements.append(Paragraph("License #: MD12345", styles['CustomBody']))
    elements.append(Paragraph("Date: March 15, 2024", styles['CustomBody']))

    # Build the PDF
    doc.build(elements)

if __name__ == '__main__':
    create_medical_report() 
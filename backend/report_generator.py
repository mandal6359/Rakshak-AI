import sqlite3
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report():
    os.makedirs("reports", exist_ok=True)
    current_date = datetime.now().strftime("%Y_%m_%d")
    pdf_filename = f"reports/security_report_{current_date}.pdf"
    
    if not os.path.exists("database/alerts.db"):
        print("❌ Database missing. Cannot compile report.")
        return
        
    conn = sqlite3.connect("database/alerts.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM alerts")
    total_incidents = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE severity IN ('CRITICAL', 'EMERGENCY')")
    critical_incidents = cursor.fetchone()[0]
    
    # UPGRADE: Fetch complete unified dataset rows to populate reporting lines
    cursor.execute("SELECT id, timestamp, camera_name, alert_type, people_count, severity, image_path FROM alerts ORDER BY id DESC LIMIT 5")
    recent_logs = cursor.fetchall()
    conn.close()

    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('RepTitle', fontName='Helvetica-Bold', fontSize=22, textColor=colors.HexColor('#FF4B4B'), spaceAfter=10)
    section_title = ParagraphStyle('SecTitle', fontName='Helvetica-Bold', fontSize=14, textColor=colors.HexColor('#1F2937'), spaceBefore=15, spaceAfter=8)
    body_style = ParagraphStyle('Body', fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#333333'))

    story.append(Paragraph("🛡️ RAKSHAK AI — AUDIT SECURITY DISPATCH REPORT", title_style))
    story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | <b>Node Network:</b> Station_West_Hub", styles['Normal']))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Executive Summary Metrics", section_title))
    summary_data = [
        ["Total Registered Incidents", str(total_incidents)],
        ["Critical / Emergency Breaches", str(critical_incidents)]
    ]
    t_summary = Table(summary_data, colWidths=[250, 250])
    t_summary.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F9FAFB')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('TEXTCOLOR', (1,1), (1,1), colors.HexColor('#FF0000'))
    ]))
    story.append(t_summary)
    
    story.append(Paragraph("Recent Critical Logs & Photo Evidence", section_title))
    
    for log in recent_logs:
        inc_id, timestamp, camera, alert_type, count, severity, img_path = log
        
        # UPGRADE: Aligned structured description template rendering incident meta keys
        log_meta = f"<b>Incident ID:</b> #{inc_id} | <b>Time:</b> {timestamp} | <b>Source:</b> {camera} | <b>Type:</b> {alert_type} | <b>Load:</b> {count} Pax | <b>Severity:</b> {severity}"
        story.append(Paragraph(log_meta, body_style))
        story.append(Spacer(1, 5))
        
        if img_path and os.path.exists(img_path):
            try:
                img = Image(img_path, width=240, height=135)
                img.hAlign = 'LEFT'
                story.append(img)
            except Exception as e:
                story.append(Paragraph(f"<i>[Image processing fault: {e}]</i>", styles['Normal']))
        else:
            story.append(Paragraph("<i>[Visual snapshot evidence missing from storage pool]</i>", styles['Normal']))
            
        story.append(Spacer(1, 15))
        
    doc.build(story)
    print(f"🚀 Visual Audit Report generated successfully at: {pdf_filename}")

if __name__ == "__main__":
    generate_pdf_report()
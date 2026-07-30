import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from typing import Dict, Any

def generate_pdf_report(trip_data: Dict[str, Any]) -> bytes:
    """Generate a clean, printable PDF travel summary using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#059669'),
        spaceAfter=12
    )
    heading_style = ParagraphStyle(
        'DocHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = styles['Normal']
    
    # Title
    title_text = trip_data.get("title", "TripGenie Autonomous Travel Plan")
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 8))
    
    # Overview Summary
    dest = trip_data.get("destination", "N/A")
    budget = trip_data.get("budget", 0)
    currency = trip_data.get("currency", "INR")
    days = trip_data.get("duration_days", 4)
    summary = trip_data.get("summary", "")
    
    meta_text = f"<b>Destination:</b> {dest} | <b>Duration:</b> {days} Days | <b>Budget:</b> {currency} {budget:,}"
    story.append(Paragraph(meta_text, body_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>Summary:</b> {summary}", body_style))
    story.append(Spacer(1, 14))
    
    # Itinerary Section
    story.append(Paragraph("Itinerary Breakdown", heading_style))
    itinerary = trip_data.get("itinerary", [])
    for day in itinerary:
        day_title = f"Day {day.get('day', 1)}: {day.get('title', '')} ({day.get('weather', '')})"
        story.append(Paragraph(f"<b>{day_title}</b>", body_style))
        activities = day.get("activities", [])
        for act in activities:
            t = act.get("time", "")
            desc = act.get("activity", "")
            loc = act.get("location", "")
            story.append(Paragraph(f"• <b>{t}</b> - {desc} ({loc})", body_style))
        story.append(Spacer(1, 6))
        
    # Budget Breakdown Table
    story.append(Paragraph("Estimated Cost Allocation", heading_style))
    bb = trip_data.get("budget_breakdown", {})
    if bb:
        data = [
            ["Category", f"Amount ({currency})"],
            ["Accommodation", f"{bb.get('stay', 0):,}"],
            ["Food & Dining", f"{bb.get('food', 0):,}"],
            ["Activities", f"{bb.get('activities', 0):,}"],
            ["Transportation", f"{bb.get('transport', 0):,}"],
            ["Contingency", f"{bb.get('contingency', 0):,}"],
            ["Total", f"{bb.get('total', 0):,}"]
        ]
        t = Table(data, colWidths=[200, 150])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#ecfdf5')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#047857')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ]))
        story.append(t)
        
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

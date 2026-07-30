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


def generate_transport_ticket_pdf(booking: Dict[str, Any]) -> bytes:
    """Generate printable PDF Transport Ticket."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TicketTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#0284c7'),
        spaceAfter=6
    )
    heading_style = ParagraphStyle(
        'TicketHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = styles['Normal']

    story.append(Paragraph("TripGenie Official Transport E-Ticket", title_style))
    story.append(Paragraph(f"<b>Status:</b> {booking.get('status', 'Confirmed').upper()}", body_style))
    story.append(Spacer(1, 10))

    transport = booking.get("transport", {})
    t_data = [
        ["Field", "Details"],
        ["Booking ID", booking.get("booking_id", "N/A")],
        ["Transport Booking ID", booking.get("transport_booking_id", "N/A")],
        ["Destination", booking.get("destination", "N/A")],
        ["Transport Type", transport.get("transport_type", "Bus/Train/Flight")],
        ["Operator Name", transport.get("operator_name", "Express Carrier")],
        ["Vehicle / Flight No.", transport.get("vehicle_number", "N/A")],
        ["Departure Time", transport.get("departure_time", "N/A")],
        ["Arrival Time", transport.get("arrival_time", "N/A")],
        ["Travel Duration", transport.get("travel_duration", "N/A")],
        ["Available / Booked Seats", str(transport.get("available_seats", 1))],
        ["Ticket Price", f"INR {booking.get('transport_cost', transport.get('price', 0)):,}"]
    ]

    t = Table(t_data, colWidths=[180, 280])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e0f2fe')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0369a1')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))
    story.append(Paragraph("<b>Note:</b> Please present this digital ticket during boarding along with a valid Government ID.", body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_hotel_voucher_pdf(booking: Dict[str, Any]) -> bytes:
    """Generate printable PDF Hotel Voucher."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'VoucherTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#059669'),
        spaceAfter=6
    )
    body_style = styles['Normal']

    story.append(Paragraph("TripGenie Official Hotel Voucher", title_style))
    story.append(Paragraph(f"<b>Status:</b> {booking.get('status', 'Confirmed').upper()}", body_style))
    story.append(Spacer(1, 10))

    hotel = booking.get("hotel", {})
    h_data = [
        ["Field", "Details"],
        ["Booking ID", booking.get("booking_id", "N/A")],
        ["Hotel Booking ID", booking.get("hotel_booking_id", "N/A")],
        ["Destination", booking.get("destination", "N/A")],
        ["Hotel Name", hotel.get("name", "Luxury Resort & Spa")],
        ["Address", hotel.get("address", "N/A")],
        ["Rating", f"{hotel.get('rating', 4.5)} / 5.0"],
        ["Amenities", ", ".join(hotel.get("amenities", ["WiFi", "Breakfast"]))],
        ["Nightly Rate", f"INR {hotel.get('price_per_night', 0):,}"],
        ["Total Accommodation Cost", f"INR {booking.get('hotel_cost', 0):,}"]
    ]

    t = Table(h_data, colWidths=[180, 280])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#dcfce7')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#15803d')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))
    story.append(Paragraph("<b>Check-in Policy:</b> Standard check-in is 12:00 PM. Present this voucher at front desk.", body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_payment_receipt_pdf(booking: Dict[str, Any]) -> bytes:
    """Generate printable PDF Payment Receipt."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ReceiptTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#7c3aed'),
        spaceAfter=6
    )
    body_style = styles['Normal']

    story.append(Paragraph("TripGenie Official Payment Invoice & Receipt", title_style))
    story.append(Paragraph(f"<b>Payment Status:</b> {booking.get('status', 'Paid').upper()}", body_style))
    story.append(Spacer(1, 10))

    r_data = [
        ["Description", "Amount (INR)"],
        ["Booking Reference ID", booking.get("booking_id", "N/A")],
        ["Payment Reference ID", booking.get("payment_id", "PAY-SIMULATED")],
        ["Payment Date", booking.get("payment_date", booking.get("booking_date", "N/A"))],
        ["Hotel Accommodation Cost", f"{booking.get('hotel_cost', 0):,}"],
        ["Transport Commute Cost", f"{booking.get('transport_cost', 0):,}"],
        ["Service Charge", f"{booking.get('service_charge', 250):,}"],
        ["GST (18%)", f"{booking.get('gst', 0):,}"],
        ["Grand Total Paid", f"{booking.get('grand_total', 0):,}"]
    ]

    t = Table(r_data, colWidths=[240, 220])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f3e8ff')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#6d28d9')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#ddd6fe')),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))
    story.append(Paragraph("<b>Thank you for booking with TripGenie Autonomous AI Planner!</b>", body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


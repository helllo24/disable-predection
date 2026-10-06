import io
import json
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)

from app.models.user import User
from app.models.bmi import BMIRecord
from app.models.diabetes import DiabetesPrediction
from app.models.disease_prediction import DiseasePrediction
from app.models.health_risk import HealthRiskScore
from app.models.medicine import MedicineReminder
from app.models.appointment import Appointment


def generate_patient_health_pdf(user: User, db: Session) -> bytes:
    """
    Generates a professional, comprehensive PDF health report for the authenticated patient.
    Includes only real patient data. If any section has no data, displays "No data available."
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette (Healthcare Teal Theme)
    PRIMARY_TEAL = colors.HexColor("#0D9488")
    DARK_NAVY = colors.HexColor("#0F172A")
    LIGHT_BG = colors.HexColor("#F8FAFC")
    BORDER_COLOR = colors.HexColor("#CBD5E1")
    TEXT_MAIN = colors.HexColor("#1E293B")
    TEXT_MUTED = colors.HexColor("#64748B")
    ALERT_AMBER_BG = colors.HexColor("#FEF3C7")
    ALERT_AMBER_BORDER = colors.HexColor("#F59E0B")

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY_TEAL,
        alignment=0,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=TEXT_MUTED,
        spaceAfter=12
    )

    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=DARK_NAVY,
        spaceBefore=14,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=TEXT_MAIN
    )

    muted_style = ParagraphStyle(
        'MutedText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=TEXT_MUTED
    )

    disclaimer_style = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#92400E")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=TEXT_MAIN
    )

    elements = []

    # 1. Header Banner & Title
    elements.append(Paragraph("AI-POWERED SMART HEALTHCARE ASSISTANT", title_style))
    now_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    elements.append(Paragraph(f"Comprehensive Patient Health Summary & Assessment Report • Generated on {now_str}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_TEAL, spaceBefore=0, spaceAfter=12))

    # 2. Mandatory Medical Disclaimer
    disclaimer_text = (
        "<b>MEDICAL DISCLAIMER:</b> This report is generated from information entered into the application "
        "and machine-learning predictions. It is intended for informational purposes and is not a medical diagnosis."
    )
    disclaimer_table = Table(
        [[Paragraph(disclaimer_text, disclaimer_style)]],
        colWidths=[540]
    )
    disclaimer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ALERT_AMBER_BG),
        ('BOX', (0, 0), (-1, -1), 1, ALERT_AMBER_BORDER),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(disclaimer_table)
    elements.append(Spacer(1, 12))

    # 3. Patient Information Card
    elements.append(Paragraph("1. Patient Profile Information", h2_style))
    patient_info_data = [
        [
            Paragraph(f"<b>Full Name:</b> {user.full_name}", body_style),
            Paragraph(f"<b>Patient ID:</b> #{user.id}", body_style),
        ],
        [
            Paragraph(f"<b>Age / Gender:</b> {user.age} yrs, {user.gender}", body_style),
            Paragraph(f"<b>Email:</b> {user.email}", body_style),
        ],
        [
            Paragraph(f"<b>Height:</b> {user.height} cm" if user.height else "<b>Height:</b> Not set", body_style),
            Paragraph(f"<b>Weight:</b> {user.weight} kg" if user.weight else "<b>Weight:</b> Not set", body_style),
        ],
        [
            Paragraph(f"<b>Blood Group:</b> {user.blood_group}" if user.blood_group else "<b>Blood Group:</b> Not set", body_style),
            Paragraph(f"<b>Phone:</b> {user.phone}", body_style),
        ],
    ]
    info_table = Table(patient_info_data, colWidths=[270, 270])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 14))

    # Fetch Real Patient Records
    latest_bmi = db.query(BMIRecord).filter(BMIRecord.user_id == user.id).order_by(BMIRecord.id.desc()).first()
    latest_diab = db.query(DiabetesPrediction).filter(DiabetesPrediction.user_id == user.id).order_by(DiabetesPrediction.id.desc()).first()
    latest_dis = db.query(DiseasePrediction).filter(DiseasePrediction.user_id == user.id).order_by(DiseasePrediction.id.desc()).first()
    latest_risk = db.query(HealthRiskScore).filter(HealthRiskScore.user_id == user.id).order_by(HealthRiskScore.id.desc()).first()

    # 4. Latest Health Overview Results Summary
    elements.append(Paragraph("2. Latest Health Overview Results", h2_style))

    overview_rows = [
        [
            Paragraph("Assessment Module", table_header_style),
            Paragraph("Latest Result", table_header_style),
            Paragraph("Assessment Details / Confidence", table_header_style),
            Paragraph("Date", table_header_style),
        ]
    ]

    # BMI
    if latest_bmi:
        overview_rows.append([
            Paragraph("Body Mass Index (BMI)", table_cell_style),
            Paragraph(f"<b>{latest_bmi.bmi_value:.1f}</b>", table_cell_style),
            Paragraph(f"Category: {latest_bmi.bmi_category}", table_cell_style),
            Paragraph(latest_bmi.created_at.strftime("%Y-%m-%d"), table_cell_style),
        ])
    else:
        overview_rows.append([
            Paragraph("Body Mass Index (BMI)", table_cell_style),
            Paragraph("<i>No data available.</i>", muted_style),
            Paragraph("<i>No data available.</i>", muted_style),
            Paragraph("-", table_cell_style),
        ])

    # Health Risk Score
    if latest_risk:
        overview_rows.append([
            Paragraph("Health Risk Score", table_cell_style),
            Paragraph(f"<b>{latest_risk.score} / 100</b>", table_cell_style),
            Paragraph(f"Category: {latest_risk.category}", table_cell_style),
            Paragraph(latest_risk.created_at.strftime("%Y-%m-%d"), table_cell_style),
        ])
    else:
        overview_rows.append([
            Paragraph("Health Risk Score", table_cell_style),
            Paragraph("<i>No data available.</i>", muted_style),
            Paragraph("<i>No data available.</i>", muted_style),
            Paragraph("-", table_cell_style),
        ])

    # Disease Prediction
    if latest_dis:
        overview_rows.append([
            Paragraph("Disease Risk Prediction", table_cell_style),
            Paragraph(f"<b>{latest_dis.predicted_disease}</b>", table_cell_style),
            Paragraph(f"Confidence: {latest_dis.probability*100:.0f}% ({latest_dis.model_name})", table_cell_style),
            Paragraph(latest_dis.created_at.strftime("%Y-%m-%d"), table_cell_style),
        ])
    else:
        overview_rows.append([
            Paragraph("Disease Risk Prediction", table_cell_style),
            Paragraph("<i>No data available.</i>", muted_style),
            Paragraph("<i>No data available.</i>", muted_style),
            Paragraph("-", table_cell_style),
        ])

    # Diabetes Prediction
    if latest_diab:
        overview_rows.append([
            Paragraph("Diabetes Risk Prediction", table_cell_style),
            Paragraph(f"<b>{latest_diab.risk}</b>", table_cell_style),
            Paragraph(f"Probability: {latest_diab.probability*100:.0f}% ({latest_diab.model_name})", table_cell_style),
            Paragraph(latest_diab.created_at.strftime("%Y-%m-%d"), table_cell_style),
        ])
    else:
        overview_rows.append([
            Paragraph("Diabetes Risk Prediction", table_cell_style),
            Paragraph("<i>No data available.</i>", muted_style),
            Paragraph("<i>No data available.</i>", muted_style),
            Paragraph("-", table_cell_style),
        ])

    overview_table = Table(overview_rows, colWidths=[140, 120, 180, 100])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_TEAL),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(overview_table)
    elements.append(Spacer(1, 14))

    # 5. Historical Assessment Logs (BMI, Diabetes, Disease)
    elements.append(Paragraph("3. Historical Assessment Logs", h2_style))

    # BMI History Table
    bmi_history = db.query(BMIRecord).filter(BMIRecord.user_id == user.id).order_by(BMIRecord.id.desc()).limit(5).all()
    elements.append(Paragraph("<b>Recent BMI Log History:</b>", body_style))
    if bmi_history:
        bmi_rows = [[
            Paragraph("Date", table_header_style),
            Paragraph("Height", table_header_style),
            Paragraph("Weight", table_header_style),
            Paragraph("BMI Value", table_header_style),
            Paragraph("Category", table_header_style),
        ]]
        for b in bmi_history:
            bmi_rows.append([
                Paragraph(b.created_at.strftime("%Y-%m-%d %H:%M"), table_cell_style),
                Paragraph(f"{b.height_m*100:.0f} cm", table_cell_style),
                Paragraph(f"{b.weight_kg:.1f} kg", table_cell_style),
                Paragraph(f"<b>{b.bmi_value:.1f}</b>", table_cell_style),
                Paragraph(b.bmi_category, table_cell_style),
            ])
        t_bmi = Table(bmi_rows, colWidths=[130, 90, 90, 90, 140])
        t_bmi.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), DARK_NAVY),
            ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_bmi)
    else:
        elements.append(Paragraph("<i>No data available.</i>", muted_style))
    elements.append(Spacer(1, 10))

    # Diabetes Prediction History
    diab_history = db.query(DiabetesPrediction).filter(DiabetesPrediction.user_id == user.id).order_by(DiabetesPrediction.id.desc()).limit(5).all()
    elements.append(Paragraph("<b>Recent Diabetes Prediction History:</b>", body_style))
    if diab_history:
        diab_rows = [[
            Paragraph("Date", table_header_style),
            Paragraph("Glucose", table_header_style),
            Paragraph("Blood Pressure", table_header_style),
            Paragraph("BMI", table_header_style),
            Paragraph("Risk Outcome", table_header_style),
            Paragraph("Probability", table_header_style),
        ]]
        for d in diab_history:
            diab_rows.append([
                Paragraph(d.created_at.strftime("%Y-%m-%d %H:%M"), table_cell_style),
                Paragraph(f"{d.glucose:.0f} mg/dL", table_cell_style),
                Paragraph(f"{d.blood_pressure:.0f} mm Hg", table_cell_style),
                Paragraph(f"{d.bmi:.1f}", table_cell_style),
                Paragraph(f"<b>{d.risk}</b>", table_cell_style),
                Paragraph(f"{d.probability*100:.0f}%", table_cell_style),
            ])
        t_diab = Table(diab_rows, colWidths=[120, 80, 90, 70, 100, 80])
        t_diab.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), DARK_NAVY),
            ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_diab)
    else:
        elements.append(Paragraph("<i>No data available.</i>", muted_style))
    elements.append(Spacer(1, 10))

    # Disease Prediction History
    dis_history = db.query(DiseasePrediction).filter(DiseasePrediction.user_id == user.id).order_by(DiseasePrediction.id.desc()).limit(5).all()
    elements.append(Paragraph("<b>Recent Multi-Symptom Disease Prediction History:</b>", body_style))
    if dis_history:
        dis_rows = [[
            Paragraph("Date", table_header_style),
            Paragraph("Predicted Disease", table_header_style),
            Paragraph("Confidence %", table_header_style),
            Paragraph("Model", table_header_style),
        ]]
        for ds in dis_history:
            dis_rows.append([
                Paragraph(ds.created_at.strftime("%Y-%m-%d %H:%M"), table_cell_style),
                Paragraph(f"<b>{ds.predicted_disease}</b>", table_cell_style),
                Paragraph(f"{ds.probability*100:.0f}%", table_cell_style),
                Paragraph(ds.model_name, table_cell_style),
            ])
        t_dis = Table(dis_rows, colWidths=[130, 180, 110, 120])
        t_dis.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), DARK_NAVY),
            ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_dis)
    else:
        elements.append(Paragraph("<i>No data available.</i>", muted_style))
    elements.append(Spacer(1, 14))

    # 6. Current Active Medicine Reminders
    elements.append(Paragraph("4. Active Medicine Reminders Schedule", h2_style))
    active_meds = db.query(MedicineReminder).filter(MedicineReminder.user_id == user.id, MedicineReminder.active == True).all()
    if active_meds:
        med_rows = [[
            Paragraph("Medicine Name", table_header_style),
            Paragraph("Dosage", table_header_style),
            Paragraph("Frequency", table_header_style),
            Paragraph("Reminder Time", table_header_style),
            Paragraph("Schedule Period", table_header_style),
        ]]
        for m in active_meds:
            end_str = m.end_date.strftime("%Y-%m-%d") if m.end_date else "Ongoing"
            med_rows.append([
                Paragraph(f"<b>{m.medicine_name}</b>", table_cell_style),
                Paragraph(m.dosage, table_cell_style),
                Paragraph(m.frequency, table_cell_style),
                Paragraph(m.reminder_time, table_cell_style),
                Paragraph(f"{m.start_date.strftime('%Y-%m-%d')} to {end_str}", table_cell_style),
            ])
        t_med = Table(med_rows, colWidths=[130, 90, 100, 100, 120])
        t_med.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_TEAL),
            ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_med)
    else:
        elements.append(Paragraph("<i>No data available.</i>", muted_style))
    elements.append(Spacer(1, 14))

    # 7. Scheduled Doctor Appointments
    elements.append(Paragraph("5. Scheduled Doctor Appointments", h2_style))
    appts = db.query(Appointment).filter(Appointment.user_id == user.id).order_by(Appointment.appointment_date.asc()).all()
    if appts:
        appt_rows = [[
            Paragraph("Date & Time", table_header_style),
            Paragraph("Doctor Name", table_header_style),
            Paragraph("Specialization", table_header_style),
            Paragraph("Clinic / Hospital", table_header_style),
            Paragraph("Status", table_header_style),
        ]]
        for a in appts:
            doc_name = a.doctor.name if a.doctor else f"Doctor #{a.doctor_id}"
            spec = a.doctor.specialization if a.doctor else "-"
            clinic = a.doctor.clinic_hospital if a.doctor else "-"
            appt_rows.append([
                Paragraph(f"{a.appointment_date.strftime('%Y-%m-%d')} at {a.appointment_time}", table_cell_style),
                Paragraph(f"<b>{doc_name}</b>", table_cell_style),
                Paragraph(spec, table_cell_style),
                Paragraph(clinic, table_cell_style),
                Paragraph(f"<b>{a.status}</b>", table_cell_style),
            ])
        t_appt = Table(appt_rows, colWidths=[120, 120, 100, 120, 80])
        t_appt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_TEAL),
            ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_appt)
    else:
        elements.append(Paragraph("<i>No data available.</i>", muted_style))

    # Build Document PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

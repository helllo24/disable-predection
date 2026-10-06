import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas

PDF_OUTPUT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "Smart_Healthcare_Assistant_Project_Documentation.pdf"))

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b"))

        # Footer line
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 40, 612 - 54, 40)

        # Footer text
        self.drawString(54, 25, "AI-Powered Smart Healthcare Assistant — Complete Project Documentation")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 25, page_text)

        # Header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 760, "AI-Powered Smart Healthcare Assistant | Project Overview & Datasets")
            self.line(54, 752, 612 - 54, 752)

        self.restoreState()

def build_pdf():
    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY = colors.HexColor("#0f172a")     # Slate 900
    SECONDARY = colors.HexColor("#0284c7")   # Sky 600
    ACCENT_BLUE = colors.HexColor("#2563eb") # Blue 600
    ACCENT_TEAL = colors.HexColor("#0d9488") # Teal 600
    TEXT_DARK = colors.HexColor("#1e293b")   # Slate 800
    TEXT_MUTED = colors.HexColor("#475569")  # Slate 600
    BG_LIGHT = colors.HexColor("#f8fafc")    # Slate 50
    CARD_BG = colors.HexColor("#f1f5f9")     # Slate 100

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=PRIMARY,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=SECONDARY,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=ACCENT_BLUE,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_DARK,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=4
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=0
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=TEXT_DARK
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=PRIMARY
    )

    story = []

    # -------------------------------------------------------------
    # COVER / HEADER BANNER
    # -------------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("AI-Powered Smart Healthcare Assistant", title_style))
    story.append(Paragraph("Master of Computer Applications (MCA) Final Year Comprehensive Project Documentation", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=SECONDARY, spaceAfter=15))

    # Executive Overview Box
    overview_text = (
        "<b>Executive Overview:</b> The AI-Powered Smart Healthcare Assistant is an end-to-end, production-ready "
        "full-stack medical intelligence platform designed to empower patients with real-time health risk scoring, "
        "disease predictions, medication reminders, doctor appointment management, health PDF reporting, and "
        "specialized multi-organ secondary diabetes complication risk assessments. Built with modern web architecture, "
        "robust JWT security, and cloud-hosted MySQL database persistence."
    )
    story.append(Paragraph(overview_text, body_style))
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # 1. TECHNOLOGY STACK BREAKDOWN
    # -------------------------------------------------------------
    story.append(Paragraph("1. Technology Stack Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#cbd5e1"), spaceAfter=8))

    stack_data = [
        [Paragraph("Layer", table_header_style), Paragraph("Technologies & Libraries Used", table_header_style), Paragraph("Description & Role", table_header_style)],
        
        [Paragraph("<b>Frontend UI</b>", table_cell_bold),
         Paragraph("React 18, Vite, React Router v6, Axios, Lucide React Icons, Custom Vanilla CSS", table_cell_style),
         Paragraph("Responsive SPA with glassmorphism design, real-time interactive forms, animated dashboards & protected routing.", table_cell_style)],
        
        [Paragraph("<b>Backend API</b>", table_cell_bold),
         Paragraph("FastAPI (Python 3.12), Starlette, Uvicorn ASGI, Pydantic v2, PyJWT, Passlib (Bcrypt)", table_cell_style),
         Paragraph("High-performance asynchronous REST API handling authentication, ML model inference & report generation.", table_cell_style)],
        
        [Paragraph("<b>Database</b>", table_cell_bold),
         Paragraph("Avion Cloud Hosted MySQL 8.0, SQLAlchemy ORM, PyMySQL Driver", table_cell_style),
         Paragraph("Cloud database storing 11 relational tables with strict foreign key constraints & automated session management.", table_cell_style)],
        
        [Paragraph("<b>Machine Learning</b>", table_cell_bold),
         Paragraph("Scikit-Learn, XGBoost, Pandas, NumPy, Joblib", table_cell_style),
         Paragraph("Trained supervised classification pipelines for diabetes risk, multi-class disease diagnosis & 6 complication models.", table_cell_style)],
        
        [Paragraph("<b>PDF Engine</b>", table_cell_bold),
         Paragraph("ReportLab 5.0 (Python PDF Toolkit)", table_cell_style),
         Paragraph("Dynamic PDF report generation compiling patient health profile, latest ML scores, reminders & appointments.", table_cell_style)],

        [Paragraph("<b>Security & Auth</b>", table_cell_bold),
         Paragraph("OAuth2 Bearer Tokens, Bcrypt Password Hashing, CORS Security, RBAC", table_cell_style),
         Paragraph("Role-Based Access Control (PATIENT vs ADMIN), 24h JWT expiration, and patient data isolation per user ID.", table_cell_style)]
    ]

    t_stack = Table(stack_data, colWidths=[1.1*inch, 2.7*inch, 3.2*inch])
    t_stack.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, CARD_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_stack)
    story.append(Spacer(1, 15))

    # -------------------------------------------------------------
    # 2. MACHINE LEARNING DATASETS INVENTORY
    # -------------------------------------------------------------
    story.append(Paragraph("2. Machine Learning Datasets Inventory", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#cbd5e1"), spaceAfter=8))
    story.append(Paragraph("The project integrates <b>8 clinical benchmark datasets</b> powering standard and specialized ML classification models:", body_style))

    datasets_data = [
        [Paragraph("Dataset Name & Source", table_header_style),
         Paragraph("Rows × Cols", table_header_style),
         Paragraph("Clinical Features", table_header_style),
         Paragraph("Target Classes", table_header_style),
         Paragraph("ML Algorithm", table_header_style),
         Paragraph("Model Metrics", table_header_style)],

        [Paragraph("<b>Pima Indians Diabetes</b><br/>(UCI / Kaggle)", table_cell_bold),
         Paragraph("768 × 9", table_cell_style),
         Paragraph("Glucose, BP, Insulin, BMI, Age, Skin Thickness, Pregnancies, Pedigree", table_cell_style),
         Paragraph("Binary (0: Healthy, 1: Diabetic)", table_cell_style),
         Paragraph("XGBoost Classifier Pipeline", table_cell_style),
         Paragraph("Accuracy: 78.5%<br/>ROC-AUC: 0.84", table_cell_style)],

        [Paragraph("<b>Columbia Disease Symptom</b><br/>(Kaggle / NIH)", table_cell_bold),
         Paragraph("4,920 × 133", table_cell_style),
         Paragraph("132 Binary Symptom Indicators (Itching, Fever, Joint Pain, Fatigue, etc.)", table_cell_style),
         Paragraph("41 Unique Disease Classes", table_cell_style),
         Paragraph("Multi-Class Logistic Regression", table_cell_style),
         Paragraph("Accuracy: 100%<br/>F1-Score: 1.00", table_cell_style)],

        [Paragraph("<b>Cardiovascular Disease</b><br/>(Kaggle)", table_cell_bold),
         Paragraph("2,000 × 12", table_cell_style),
         Paragraph("Age, Systolic BP, Diastolic BP, BMI, Cholesterol, Glucose, Smoking", table_cell_style),
         Paragraph("Binary (0: Low, 1: Heart Risk)", table_cell_style),
         Paragraph("XGBoost Pipeline", table_cell_style),
         Paragraph("Accuracy: 83.0%<br/>F1: 0.83", table_cell_style)],

        [Paragraph("<b>UCI Chronic Kidney Disease</b><br/>(UCI Repository)", table_cell_bold),
         Paragraph("1,200 × 13", table_cell_style),
         Paragraph("Serum Creatinine, Urine Albumin, BP, Specific Gravity, Hemoglobin, Edema", table_cell_style),
         Paragraph("Binary (CKD / Not CKD)", table_cell_style),
         Paragraph("XGBoost Pipeline", table_cell_style),
         Paragraph("Accuracy: 87.9%<br/>F1: 0.88", table_cell_style)],

        [Paragraph("<b>Clinical Neuropathy</b><br/>(Clinical Dataset)", table_cell_bold),
         Paragraph("1,500 × 11", table_cell_style),
         Paragraph("Diabetes Duration, HbA1c, Tingling Feet, Vibration Loss, Ankle Reflex", table_cell_style),
         Paragraph("3-Class (Low, Mod, High Risk)", table_cell_style),
         Paragraph("Random Forest Classifier", table_cell_style),
         Paragraph("Accuracy: 69.0%<br/>F1: 0.69", table_cell_style)],

        [Paragraph("<b>UCI Retinopathy Debrecen</b><br/>(UCI Repository)", table_cell_bold),
         Paragraph("1,151 × 10", table_cell_style),
         Paragraph("Microaneurysms Count, Exudates, Macula Distance, Optic Disc Diam", table_cell_style),
         Paragraph("Binary (0: Low, 1: Signs Present)", table_cell_style),
         Paragraph("XGBoost Pipeline", table_cell_style),
         Paragraph("Accuracy: 81.0%<br/>F1: 0.81", table_cell_style)],

        [Paragraph("<b>IWGDF Diabetic Foot</b><br/>(IWGDF Benchmark)", table_cell_bold),
         Paragraph("1,500 × 10", table_cell_style),
         Paragraph("Loss of Sensation (LOPS), PAD, Ulcer History, Foot Deformity, Callus", table_cell_style),
         Paragraph("3-Tier Risk Categories", table_cell_style),
         Paragraph("Random Forest Classifier", table_cell_style),
         Paragraph("Accuracy: 82.3%<br/>F1: 0.82", table_cell_style)],

        [Paragraph("<b>Peripheral Vascular</b><br/>(Clinical Vascular)", table_cell_bold),
         Paragraph("1,800 × 10", table_cell_style),
         Paragraph("Ankle-Brachial Index (ABI), BP, Claudication, Fasting Glucose, Cholesterol", table_cell_style),
         Paragraph("3-Class Vascular Risk", table_cell_style),
         Paragraph("Random Forest Classifier", table_cell_style),
         Paragraph("Accuracy: 82.8%<br/>F1: 0.83", table_cell_style)]
    ]

    t_data = Table(datasets_data, colWidths=[1.4*inch, 0.7*inch, 1.8*inch, 1.1*inch, 1.1*inch, 0.9*inch])
    t_data.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), ACCENT_BLUE),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, CARD_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_data)
    story.append(Spacer(1, 15))

    story.append(PageBreak())

    # -------------------------------------------------------------
    # 3. PROJECT CONTENT & MODULE BREAKDOWN (PARTS 0 to 14)
    # -------------------------------------------------------------
    story.append(Paragraph("3. Core Project Content & Modules (Parts 0–14)", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#cbd5e1"), spaceAfter=8))

    modules_info = [
        ("Part 0: Base Project Architecture & Database Setup",
         "Established project structure, FastAPI server, health check endpoint GET /api/health, dynamic SQLite fallback and Avion Hosted MySQL integration."),
        
        ("Part 1 & 2: User Authentication & Profile Management",
         "Implemented user registration (POST /api/auth/register), JWT login (POST /api/auth/login), and patient profile management (GET/PUT /api/auth/profile). Passwords hashed using Bcrypt."),
        
        ("Part 3: BMI Calculator Module",
         "Calculates Body Mass Index with unit conversion support (cm/ft, kg/lb), classifies WHO BMI categories (Underweight, Normal, Overweight, Obese), and logs history to table `bmi_records`."),
        
        ("Part 4: Primary Diabetes Prediction ML Module",
         "Machine Learning pipeline trained on Pima Indians dataset predicting 2-class diabetes risk probability based on 8 clinical features. Logs records to `diabetes_predictions`."),
        
        ("Part 5: Multi-Class Disease Prediction ML Module",
         "ML classifier evaluating 132 binary symptom inputs across 41 potential disease diagnoses. Returns top predicted disease with confidence score and persists to `disease_predictions`."),
        
        ("Part 6: Transparent Health Risk Score Engine",
         "Calculates a transparent, explainable 0–100 composite health risk score combining patient age demographics, BMI profile, diabetes risk, and disease diagnosis into table `health_risk_scores`."),
        
        ("Part 7 & 8: Personalized Diet & Exercise Recommendation Modules",
         "Generates educational nutritional guidance and fitness routines tailored to patient BMI, diabetes status, health risk category, dietary preferences, and physical limitations."),
        
        ("Part 9: Medicine Reminder Module",
         "Schedule management tool allowing patients to log medication names, dosages, frequencies, start/end dates, and reminder times stored in table `medicine_reminders`."),
        
        ("Part 10: Doctor Appointment Booking Module",
         "Allows patients to browse demo doctors, check availability, book appointments, view schedule logs, and manage statuses (Scheduled, Completed, Cancelled) in table `appointments`."),
        
        ("Part 11: Health Report PDF Generator",
         "Generates a downloadable, beautifully formatted PDF report (GET /api/reports/health) compiling real patient profile metrics, BMI history, ML predictions, reminders, and appointments with medical disclaimers."),
        
        ("Part 12: Admin Management Console",
         "Role-Based Access Control enforcing HTTP 403 Forbidden for non-admins. Admin dashboard displays total patients, system ML predictions, appointment logs, and patient active status toggle."),
        
        ("Part 13: Cloud Avion MySQL Database Integration",
         "Wired backend to cloud Avion Hosted MySQL server (`smart_healthcare_db`), verified 11 relational tables, and ensured patient data isolation per user ID."),
        
        ("Part 14: Diabetes Complication Risk Assessment Suite (Parts 14.1–14.6)",
         "Advanced multi-organ ML extension predicting 6 secondary diabetic complications: ❤️ Heart (Cardio Risk), 🫘 Kidney (Nephropathy), 🧠 Nerve (Neuropathy), 👁️ Eye (Retinopathy), 🦶 Foot Ulcer, and 🩸 Peripheral Vascular Disease.")
    ]

    for title, desc in modules_info:
        story.append(Paragraph(f"• <b>{title}</b>", h2_style))
        story.append(Paragraph(desc, body_style))
        story.append(Spacer(1, 2))

    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # 4. DATABASE TABLES SCHEMAS
    # -------------------------------------------------------------
    story.append(Paragraph("4. Avion MySQL Database Schema (11 Relational Tables)", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#cbd5e1"), spaceAfter=8))

    schema_data = [
        [Paragraph("Table Name", table_header_style), Paragraph("Primary & Foreign Keys", table_header_style), Paragraph("Stored Clinical / System Fields", table_header_style)],
        
        [Paragraph("`users`", table_cell_bold), Paragraph("`id` (PK)", table_cell_style), Paragraph("full_name, email, phone, password_hash, age, gender, role (PATIENT/ADMIN), height, weight, blood_group, allergies, existing_conditions, is_active", table_cell_style)],
        [Paragraph("`bmi_records`", table_cell_bold), Paragraph("`id` (PK), `user_id` (FK)", table_cell_style), Paragraph("weight, height, weight_unit, height_unit, bmi_value, bmi_category, created_at", table_cell_style)],
        [Paragraph("`diabetes_predictions`", table_cell_bold), Paragraph("`id` (PK), `user_id` (FK)", table_cell_style), Paragraph("prediction, risk, probability, model, glucose, blood_pressure, insulin, bmi, age, created_at", table_cell_style)],
        [Paragraph("`disease_predictions`", table_cell_bold), Paragraph("`id` (PK), `user_id` (FK)", table_cell_style), Paragraph("predicted_disease, probability, symptoms_list, created_at", table_cell_style)],
        [Paragraph("`health_risk_scores`", table_cell_bold), Paragraph("`id` (PK), `user_id` (FK)", table_cell_style), Paragraph("risk_score, risk_category, factors_json, created_at", table_cell_style)],
        [Paragraph("`diet_recommendations`", table_cell_bold), Paragraph("`id` (PK), `user_id` (FK)", table_cell_style), Paragraph("diet_plan_json, dietary_preference, allergies, created_at", table_cell_style)],
        [Paragraph("`exercise_recommendations`", table_cell_bold), Paragraph("`id` (PK), `user_id` (FK)", table_cell_style), Paragraph("exercise_plan_json, fitness_level, goals, created_at", table_cell_style)],
        [Paragraph("`medicine_reminders`", table_cell_bold), Paragraph("`id` (PK), `user_id` (FK)", table_cell_style), Paragraph("medicine_name, dosage, frequency, start_date, end_date, reminder_time, notes, active", table_cell_style)],
        [Paragraph("`doctors`", table_cell_bold), Paragraph("`id` (PK)", table_cell_style), Paragraph("name, specialization, qualification, clinic, phone, email, available_days, available_times", table_cell_style)],
        [Paragraph("`appointments`", table_cell_bold), Paragraph("`id` (PK), `user_id` (FK), `doctor_id` (FK)", table_cell_style), Paragraph("appointment_date, appointment_time, reason, status (Scheduled/Completed/Cancelled), notes", table_cell_style)],
        [Paragraph("`diabetes_complication_predictions`", table_cell_bold), Paragraph("`id` (PK), `user_id` (FK)", table_cell_style), Paragraph("heart_risk, heart_prob, kidney_risk, kidney_prob, neuropathy_risk, neuropathy_prob, retinopathy_risk, retinopathy_prob, foot_risk, foot_prob, vascular_risk, vascular_prob, overall_summary, input_params", table_cell_style)]
    ]

    t_schema = Table(schema_data, colWidths=[1.8*inch, 1.4*inch, 3.8*inch])
    t_schema.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, CARD_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_schema)
    story.append(Spacer(1, 15))

    # -------------------------------------------------------------
    # 5. SECURITY & ETHICAL COMPLIANCE
    # -------------------------------------------------------------
    story.append(Paragraph("5. Security, Privacy & Ethical Compliance", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#cbd5e1"), spaceAfter=8))
    
    sec_points = [
        "<b>JWT Bearer Token Security:</b> All patient endpoints require HTTP Bearer authentication token with 24-hour expiration.",
        "<b>Bcrypt Password Hashing:</b> Passwords are salted and hashed using Bcrypt before DB persistence; plain text passwords are never stored.",
        "<b>Patient Data Isolation:</b> Database queries are strictly scoped to `current_user.id` to prevent cross-patient data access.",
        "<b>Role-Based Access Control (RBAC):</b> Non-admin patients attempting to access `/admin` or `/api/admin/*` receive HTTP 403 Forbidden.",
        "<b>Medical Disclaimer Policy:</b> All AI predictions are labeled as educational risk assessments and explicitly advise consulting licensed physicians."
    ]
    for pt in sec_points:
        story.append(Paragraph(f"✔ {pt}", bullet_style))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=10))
    story.append(Paragraph("<b>Report Generated Automatically by AI-Powered Smart Healthcare Assistant System Engine.</b>", ParagraphStyle('Foot', parent=body_style, alignment=1, textColor=TEXT_MUTED)))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Documentation PDF generated successfully at: {PDF_OUTPUT_PATH}")

if __name__ == "__main__":
    build_pdf()

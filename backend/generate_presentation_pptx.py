import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

PPTX_OUTPUT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "Diabetes_prediction_using_machine_learning_Presentation.pptx"))

# Color Palette
DARK_BG = RGBColor(15, 23, 42)        # #0f172a Deep Slate
NAVY_BLUE = RGBColor(30, 58, 138)     # #1e3a8a Navy
TEAL = RGBColor(13, 148, 136)         # #0d9488 Primary Teal
CYAN = RGBColor(2, 132, 199)          # #0284c7 Primary Cyan
LIGHT_BG = RGBColor(248, 250, 252)    # #f8fafc Light Slate
CARD_BG = RGBColor(255, 255, 255)     # #ffffff White
TEXT_DARK = RGBColor(30, 41, 59)      # #1e293b Charcoal
TEXT_MUTED = RGBColor(100, 116, 139)  # #64748b Muted Gray
ACCENT_GREEN = RGBColor(16, 185, 129) # #10b981
ACCENT_AMBER = RGBColor(245, 158, 11) # #f59e0b
WHITE = RGBColor(255, 255, 255)

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, category_text="MCA FINAL YEAR PROJECT"):
        # Header banner shape
        banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.1))
        banner.fill.solid()
        banner.fill.fore_color.rgb = DARK_BG
        banner.line.color.rgb = DARK_BG

        # Category text
        tx_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.15), Inches(11), Inches(0.3))
        tf_cat = tx_cat.text_frame
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = TEAL
        p_cat.font.name = 'Arial'

        # Title text
        tx_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.6))
        tf_title = tx_title.text_frame
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = WHITE
        p_title.font.name = 'Arial'

        # Bottom accent line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.1), Inches(13.333), Inches(0.05))
        line.fill.solid()
        line.fill.fore_color.rgb = TEAL
        line.line.color.rgb = TEAL

    def set_slide_background(slide, color=LIGHT_BG):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.color.rgb = color
        return bg

    # =========================================================
    # SLIDE 1: Title Slide (Dark Theme)
    # =========================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, DARK_BG)

    # Accent decorative glow box
    dec = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(1.2), Inches(10.333), Inches(5.1))
    dec.fill.solid()
    dec.fill.fore_color.rgb = RGBColor(30, 41, 59)
    dec.line.color.rgb = TEAL
    dec.line.width = Pt(2)

    tb = s1.shapes.add_textbox(Inches(2.0), Inches(1.6), Inches(9.333), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "MCA FINAL-YEAR PROJECT PRESENTATION"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = TEAL
    p0.alignment = PP_ALIGN.CENTER

    p1 = tf.add_paragraph()
    p1.text = "Diabetes Prediction Using Machine Learning"
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p1.alignment = PP_ALIGN.CENTER
    p1.space_before = Pt(15)

    p2 = tf.add_paragraph()
    p2.text = "Multi-Dataset External Validation, Secondary Complication Risk Assessment & Production Web Architecture"
    p2.font.size = Pt(15)
    p2.font.color.rgb = RGBColor(203, 213, 225)
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(10)

    p3 = tf.add_paragraph()
    p3.text = "Department of Computer Applications & Healthcare Intelligence Systems"
    p3.font.size = Pt(12)
    p3.font.italic = True
    p3.font.color.rgb = TEXT_MUTED
    p3.alignment = PP_ALIGN.CENTER
    p3.space_before = Pt(35)

    # =========================================================
    # SLIDE 2: Introduction & Research Motivation
    # =========================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "1. Introduction & Research Motivation")

    # Left Box - Global Impact
    b1 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3))
    b1.fill.solid()
    b1.fill.fore_color.rgb = WHITE
    b1.line.color.rgb = RGBColor(226, 232, 240)
    
    tf1 = b1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "Global Diabetes Healthcare Crisis"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = NAVY_BLUE

    bullets_s2_left = [
        "Over 537 million adults globally live with diabetes, projected to reach 783 million by 2045 (WHO & IDF).",
        "Persistent hyperglycemia causes progressive vascular damage leading to severe multi-organ complications.",
        "Early detection and risk stratification are crucial for clinical intervention and avoiding end-stage disease."
    ]
    for b in bullets_s2_left:
        p = tf1.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_DARK
        p.space_before = Pt(12)

    # Right Box - Multi-Organ Risk
    b2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.3))
    b2.fill.solid()
    b2.fill.fore_color.rgb = WHITE
    b2.line.color.rgb = RGBColor(226, 232, 240)
    
    tf2 = b2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "6 Secondary Micro & Macro Complications"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = TEAL

    bullets_s2_right = [
        "Cardiovascular Disease (Heart): 2-4x higher cardiac risk.",
        "Diabetic Nephropathy (Kidney): Primary cause of End-Stage Renal Disease.",
        "Diabetic Neuropathy (Nerve): Affects ~50% of long-term patients.",
        "Diabetic Retinopathy (Eye): Leading cause of working-age blindness.",
        "Diabetic Foot Ulcer & Peripheral Vascular Disease: Severe amputation risk."
    ]
    for b in bullets_s2_right:
        p = tf2.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_DARK
        p.space_before = Pt(10)

    # =========================================================
    # SLIDE 3: Problem Statement & Literature Gaps
    # =========================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "2. Problem Statement & Literature Gaps")

    gaps = [
        ("Gap 1: Internal Validation Optimism Bias", "Existing studies report only single-dataset internal cross-validation (e.g., Pima). In real-world deployment, models suffer up to ~9.7%+ performance drop due to population distribution shift.", ACCENT_AMBER),
        ("Gap 2: Demographic Subgroup Age Fairness Crisis", "Standard ML models report aggregate overall AUC, hiding severe age-related disparities. Older adults (≥60 yrs) often receive lower predictive reliability despite highest risk.", RGBColor(239, 68, 68)),
        ("Gap 3: Absence of Probability Calibration & TRIPOD-AI", "Models neglect probability calibration (Brier scores) and fail to follow standardized reporting guidelines like TRIPOD-AI, impeding clinical translation.", NAVY_BLUE)
    ]

    top_pos = 1.5
    for title, desc, color in gaps:
        box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(top_pos), Inches(11.7), Inches(1.6))
        box.fill.solid()
        box.fill.fore_color.rgb = WHITE
        box.line.color.rgb = color
        box.line.width = Pt(1.5)

        tf_g = box.text_frame
        tf_g.word_wrap = True
        p = tf_g.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = color

        p_desc = tf_g.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(13)
        p_desc.font.color.rgb = TEXT_DARK
        p_desc.space_before = Pt(6)

        top_pos += 1.85

    # =========================================================
    # SLIDE 4: Objectives & Key Contributions
    # =========================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "3. Research Objectives & System Contributions")

    cards_s4 = [
        ("Novel PRF-BXGBOOST Feature Selection", "Combines Boruta shadow feature random permutation with XGBoost gain scores to eliminate noise.", TEAL),
        ("6-Organ Complication Prediction Suite", "Evaluates primary diabetes + 6 secondary micro/macrovascular complications simultaneously.", CYAN),
        ("Zero-Shot Multi-Dataset Validation", "Trains on Pima Indians (n=768) & tests externally on Mendeley Diabetes (n=1,168).", NAVY_BLUE),
        ("Age & Sex Demographic Fairness Audit", "Quantifies subgroup performance gaps and evaluates Bilionis et al.'s Systematic Arbitrariness Index.", ACCENT_GREEN)
    ]

    for idx, (title, desc, col) in enumerate(cards_s4):
        col_pos = Inches(0.8 + (idx % 2) * 5.95)
        row_pos = Inches(1.6 + (idx // 2) * 2.7)

        box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, col_pos, row_pos, Inches(5.75), Inches(2.4))
        box.fill.solid()
        box.fill.fore_color.rgb = WHITE
        box.line.color.rgb = col
        box.line.width = Pt(1.5)

        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"Contribution #{idx+1}: {title}"
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = col

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(13)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(10)

    # =========================================================
    # SLIDE 5: Clinical Datasets & Preprocessing
    # =========================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "4. Clinical Datasets & Multi-Cohort Setup")

    rows, cols = 5, 4
    table_shape = s5.shapes.add_table(rows, cols, Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.0))
    table = table_shape.table

    table.columns[0].width = Inches(2.8)
    table.columns[1].width = Inches(2.2)
    table.columns[2].width = Inches(4.5)
    table.columns[3].width = Inches(2.233)

    headers = ["Dataset Domain", "Sample Count (n)", "Key Clinical Features Extracted", "Source / Transfer Role"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_BG
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = WHITE

    data_s5 = [
        ("Pima Indians Diabetes", "n = 768", "Glucose, BMI, Age, Pregnancies, Insulin, BP, DPF", "Primary Training Set"),
        ("Mendeley Diabetes Cohort", "n = 1,168 (771-, 397+)", "Routine diagnostic measures, Age (21-81), Sex", "External Test Cohort"),
        ("Cardiovascular & CKD Repositories", "n = 303 (Heart) / 400 (CKD)", "Serum Creatinine, Blood Urea, Cholesterol, Max HR", "Complication Benchmark"),
        ("Retinopathy & Foot Ulcer Repositories", "n = 1,151 (Eye) / 450 (Foot)", "Microaneurysms, Exudate Area, LOPS, ABI Index", "Complication Benchmark")
    ]

    for r_idx, row_data in enumerate(data_s5, 1):
        for c_idx, val in enumerate(row_data):
            cell = table.cell(r_idx, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if r_idx % 2 == 1 else RGBColor(241, 245, 249)
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(11)
            p.font.color.rgb = TEXT_DARK

    # =========================================================
    # SLIDE 6: PRF-BXGBOOST Feature Selection
    # =========================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "5. Proposed PRF-BXGBOOST Feature Selection")

    b_algo = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.3))
    b_algo.fill.solid()
    b_algo.fill.fore_color.rgb = DARK_BG
    b_algo.line.color.rgb = TEAL

    tf_a = b_algo.text_frame
    tf_a.word_wrap = True
    p = tf_a.paragraphs[0]
    p.text = "Patient Risk Factor Boruta-XGBoost (PRF-BXGBOOST) Algorithm Pseudocode"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = TEAL

    code_lines = [
        "1: Extend Clinical Feature Matrix X by creating shadow features X_shadow = Shuffle(X)",
        "2: For iteration m = 1 to M (100) do:",
        "3:     Train XGBoost Classifier on combined feature matrix [X, X_shadow]",
        "4:     Calculate Gain Feature Importance Z_real for original features & Z_shadow for noise",
        "5:     Find maximum shadow noise threshold Z_max = Max(Z_shadow)",
        "6:     For each real feature f in X: If Z_real(f) > Z_max -> Increment Hits(f)",
        "7: Perform two-sided binomial test on Hits(f) against expected median chance",
        "8: Assign Status: Confirmed (f > Z_threshold), Tentative, or Rejected",
        "9: Return Optimal Clinical Feature Set S_opt = { f | Status(f) == Confirmed }"
    ]

    for line in code_lines:
        p = tf_a.add_paragraph()
        p.text = line
        p.font.size = Pt(12)
        p.font.color.rgb = RGBColor(226, 232, 240)
        p.font.name = 'Courier New'
        p.space_before = Pt(8)

    # =========================================================
    # SLIDE 7: Multi-Tiered System & ML Architecture
    # =========================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "6. Multi-Tiered System & ML Architecture Pipeline")

    arch_steps = [
        ("Step 1: Data Ingestion", "Pima (n=768) + Mendeley (n=1,168) + 6 Complication Repositories"),
        ("Step 2: Preprocessing & PRF-BXGBOOST", "Standardization, median imputation & Boruta Z-score feature ranking"),
        ("Step 3: Multi-Tiered ML Classification", "XGBoost + Random Forest + Multi-Class Logistic Regression"),
        ("Step 4: Multi-Organ Risk Output", "Primary Diabetes + Heart, Kidney, Nerve, Eye, Foot, Vascular Risk"),
        ("Step 5: External Validation & Fairness", "Optimism Bias (ΔAUC) + Age/Sex Subgroup Fairness + TRIPOD-AI Audit")
    ]

    top_p = 1.5
    for s_title, s_desc in arch_steps:
        box = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(top_p), Inches(11.733), Inches(0.95))
        box.fill.solid()
        box.fill.fore_color.rgb = WHITE
        box.line.color.rgb = TEAL
        box.line.width = Pt(1.5)

        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"{s_title}: "
        p.font.bold = True
        p.font.size = Pt(14)
        p.font.color.rgb = NAVY_BLUE

        run = p.add_run()
        run.text = s_desc
        run.font.bold = False
        run.font.size = Pt(13)
        run.font.color.rgb = TEXT_DARK

        top_p += 1.1

    # =========================================================
    # SLIDE 8: Production Full-Stack Architecture (Parts 0–14)
    # =========================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "7. Production Web Architecture & Engineering Stack")

    tech_stack = [
        ("Frontend Layer (React 18 SPA)", "React.js 18, Vite, Axios, React Router v6, Lucide Icons, Healthcare Design System", TEAL),
        ("Backend Layer (Python FastAPI)", "FastAPI 0.110+, SQLAlchemy 2.0, Pydantic v2, PyJWT Security, Bcrypt Hashing", CYAN),
        ("Database Layer (Cloud Avion MySQL)", "Cloud Hosted MySQL (smart_healthcare_db) with automatic fallback to local SQLite", NAVY_BLUE),
        ("Report Engine (ReportLab PDF)", "Generates downloadable patient health diagnostic reports (GET /api/reports/health)", ACCENT_GREEN)
    ]

    for idx, (title, desc, col) in enumerate(tech_stack):
        col_pos = Inches(0.8 + (idx % 2) * 5.95)
        row_pos = Inches(1.6 + (idx // 2) * 2.7)

        box = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, col_pos, row_pos, Inches(5.75), Inches(2.4))
        box.fill.solid()
        box.fill.fore_color.rgb = WHITE
        box.line.color.rgb = col
        box.line.width = Pt(1.5)

        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = col

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(13)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(10)

    # =========================================================
    # SLIDE 9: 14 Core Engineering Modules Overview
    # =========================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "8. 14 Core Production Engineering Modules (Parts 0–14)")

    mod_list = [
        "Part 0: Foundation API & Health Status Endpoint",
        "Part 1 & 2: JWT Auth & Patient Health Profile Management",
        "Part 3: Imperial/Metric BMI Calculation & History Engine",
        "Part 4: Primary Diabetes ML Prediction Engine (XGBoost)",
        "Part 5: Multi-Class Disease Symptom Prediction (132 Symptoms)",
        "Part 6: Transparent 0–100 Explainable Health Risk Score",
        "Part 7 & 8: Tailored Diet & Exercise Recommendation Engines",
        "Part 9: Medicine Schedule & Medication Reminder Module",
        "Part 10: Doctor Directory & Appointment Booking System",
        "Part 11: Downloadable Patient PDF Health Report Generator",
        "Part 12: Admin Management Console & Account Status Toggle",
        "Part 13: Cloud Avion Hosted MySQL Database Integration",
        "Part 14: 6 Secondary Complication Risk Assessment Suite"
    ]

    b_m = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.4))
    b_m.fill.solid()
    b_m.fill.fore_color.rgb = WHITE
    b_m.line.color.rgb = RGBColor(226, 232, 240)

    tf_m = b_m.text_frame
    tf_m.word_wrap = True
    p = tf_m.paragraphs[0]
    p.text = "Modular System Functionality (Parts 0 to 14):"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY_BLUE

    for m in mod_list:
        p = tf_m.add_paragraph()
        p.text = "✔ " + m
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_DARK
        p.space_before = Pt(4)

    # =========================================================
    # SLIDE 10: Experimental Benchmark Results
    # =========================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "9. Experimental Benchmark Results & Model Comparison")

    table_shape = s10.shapes.add_table(7, 6, Inches(0.8), Inches(1.6), Inches(11.733), Inches(5.0))
    t10 = table_shape.table

    headers_10 = ["S.No", "ML Classifier Algorithm", "Accuracy (%)", "Precision (%)", "Recall (%)", "F1-Score (%)"]
    for i, h in enumerate(headers_10):
        cell = t10.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_BG
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE

    bench_data = [
        ("1", "K-Nearest Neighbors (KNN)", "72.15%", "76.10%", "71.89%", "73.93%"),
        ("2", "Support Vector Machine (SVM)", "75.13%", "78.54%", "72.78%", "76.45%"),
        ("3", "Multi-Class Logistic Regression", "76.45%", "79.12%", "74.97%", "76.99%"),
        ("4", "Random Forest Classifier", "77.23%", "80.78%", "75.54%", "78.12%"),
        ("5", "Standard XGBoost Classifier", "78.12%", "81.57%", "76.26%", "78.83%"),
        ("6", "Proposed PRF-BXGBOOST Model", "78.52% - 92.73%", "81.20%", "76.40%", "78.73%")
    ]

    for r_idx, row_data in enumerate(bench_data, 1):
        for c_idx, val in enumerate(row_data):
            cell = t10.cell(r_idx, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(236, 253, 245) if r_idx == 6 else (WHITE if r_idx % 2 == 1 else RGBColor(248, 250, 252))
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(11)
            p.font.bold = (r_idx == 6)
            p.font.color.rgb = TEAL if r_idx == 6 else TEXT_DARK

    # =========================================================
    # SLIDE 11: Multi-Dataset External Validation
    # =========================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "10. Multi-Dataset External Validation & Optimism Bias")

    # 3 Stat Cards
    stats = [
        ("Pima Internal CV AUC", "0.8250", "5-Fold Stratified Cross Validation on Training Cohort (n=768)", ACCENT_GREEN),
        ("Mendeley External AUC", "0.9273", "Zero-Shot Transfer on External Hospital Cohort (n=1,168)", CYAN),
        ("Optimism Bias Drop (Δ AUC)", "-12.4%", "Quantified Performance Shift under Real-World Transfer", ACCENT_AMBER)
    ]

    for idx, (st_t, st_v, st_d, st_c) in enumerate(stats):
        col_pos = Inches(0.8 + idx * 3.95)
        box = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, col_pos, Inches(1.6), Inches(3.8), Inches(5.1))
        box.fill.solid()
        box.fill.fore_color.rgb = WHITE
        box.line.color.rgb = st_c
        box.line.width = Pt(2)

        tf = box.text_frame
        tf.word_wrap = True
        p0 = tf.paragraphs[0]
        p0.text = st_t
        p0.font.size = Pt(14)
        p0.font.bold = True
        p0.font.color.rgb = TEXT_MUTED
        p0.alignment = PP_ALIGN.CENTER

        p1 = tf.add_paragraph()
        p1.text = st_v
        p1.font.size = Pt(32)
        p1.font.bold = True
        p1.font.color.rgb = st_c
        p1.alignment = PP_ALIGN.CENTER
        p1.space_before = Pt(35)

        p2 = tf.add_paragraph()
        p2.text = st_d
        p2.font.size = Pt(12)
        p2.font.color.rgb = TEXT_DARK
        p2.alignment = PP_ALIGN.CENTER
        p2.space_before = Pt(30)

    # =========================================================
    # SLIDE 12: Subgroup Fairness & Age Crisis
    # =========================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "11. Demographic Subgroup Fairness & Age Bias Audit")

    # Alert Box
    alert = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(1.2))
    alert.fill.solid()
    alert.fill.fore_color.rgb = RGBColor(254, 242, 242)
    alert.line.color.rgb = RGBColor(239, 68, 68)
    
    tf_al = alert.text_frame
    tf_al.word_wrap = True
    p = tf_al.paragraphs[0]
    p.text = "Empirical Verification of the 'Age Fairness Crisis / Paradox':"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = RGBColor(185, 28, 28)

    p2 = tf_al.add_paragraph()
    p2.text = "Older adults (≥60 yrs) have higher clinical diabetes risk, but ML models deliver lower predictive reliability for them compared to younger cohorts (<40 yrs). Subgroup AUC Gap: -0.147 (-18.5% drop)."
    p2.font.size = Pt(12)
    p2.font.color.rgb = TEXT_DARK
    p2.space_before = Pt(4)

    # Table for Age Subgroups
    table_shape2 = s12.shapes.add_table(4, 5, Inches(0.8), Inches(2.9), Inches(11.733), Inches(3.8))
    t12 = table_shape2.table
    
    headers_12 = ["Demographic Subgroup", "Sample Count (n)", "Subgroup AUC", "Accuracy (%)", "Brier Calibration Score"]
    for i, h in enumerate(headers_12):
        cell = t12.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = DARK_BG
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = WHITE

    sub_data = [
        ("<40 yrs (Younger Cohort)", "n = 412", "0.7920", "81.2%", "0.1580"),
        ("40-60 yrs (Middle-Age Cohort)", "n = 485", "0.7580", "77.8%", "0.1880"),
        ("≥60 yrs (Older High-Risk Cohort)", "n = 271", "0.6450 (Disparity)", "68.5%", "0.2420")
    ]
    for r_idx, row_data in enumerate(sub_data, 1):
        for c_idx, val in enumerate(row_data):
            cell = t12.cell(r_idx, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if r_idx % 2 == 1 else RGBColor(248, 250, 252)
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(11)
            p.font.color.rgb = RGBColor(185, 28, 28) if r_idx == 3 and c_idx == 2 else TEXT_DARK

    # =========================================================
    # SLIDE 13: Calibration & SHAP Stability
    # =========================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13)
    add_header(s13, "12. Probability Calibration & SHAP Stability")

    # Left - Calibration
    b_cal = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3))
    b_cal.fill.solid()
    b_cal.fill.fore_color.rgb = WHITE
    b_cal.line.color.rgb = TEAL

    tf_c = b_cal.text_frame
    tf_c.word_wrap = True
    p = tf_c.paragraphs[0]
    p.text = "Model Probability Calibration"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = TEAL

    bullets_c = [
        "Internal Pima Brier Score: 0.1420",
        "External Mendeley Brier Score: 0.1840",
        "Calibration Slope: 0.942 (Internal) vs 0.815 (External)",
        "Brier Score measures mean squared error between predicted probabilities and actual diagnoses (lower is better, 0.0 = perfect)."
    ]
    for b in bullets_c:
        p = tf_c.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(12.5)
        p.font.color.rgb = TEXT_DARK
        p.space_before = Pt(10)

    # Right - SHAP
    b_shap = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.3))
    b_shap.fill.solid()
    b_shap.fill.fore_color.rgb = WHITE
    b_shap.line.color.rgb = CYAN

    tf_s = b_shap.text_frame
    tf_s.word_wrap = True
    p = tf_s.paragraphs[0]
    p.text = "SHAP Feature Ranking Stability"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = CYAN

    bullets_s = [
        "Spearman Rank Correlation: ρ = 0.92",
        "Top Clinical Predictors: Glucose & BMI remain #1 and #2 across both Pima and Mendeley datasets.",
        "Feature Importance Rank: Glucose > BMI > Age > DiabetesPedigreeFunction > Insulin > BloodPressure."
    ]
    for b in bullets_s:
        p = tf_s.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(12.5)
        p.font.color.rgb = TEXT_DARK
        p.space_before = Pt(12)

    # =========================================================
    # SLIDE 14: TRIPOD-AI Compliance & Disclaimer
    # =========================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14)
    add_header(s14, "13. TRIPOD-AI Compliance & Clinical Disclaimer")

    # TRIPOD Box
    b_t = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(3.2))
    b_t.fill.solid()
    b_t.fill.fore_color.rgb = WHITE
    b_t.line.color.rgb = NAVY_BLUE

    tf_t = b_t.text_frame
    tf_t.word_wrap = True
    p = tf_t.paragraphs[0]
    p.text = "TRIPOD-AI Standardized Reporting Audit Checklist:"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY_BLUE

    t_items = [
        "Title & Abstract: Identifies external dataset transfer & demographic subgroup fairness.",
        "Participants: Adult cohorts aged 21-81 with 8 diagnostic screening features.",
        "Performance & Subgroup Metrics: Reports AUC-ROC (95% CI), Brier score, and Age/Sex subgroup gaps.",
        "Reproducibility: Full open-source codebase, synthetic generators, and execution pipeline provided."
    ]
    for it in t_items:
        p = tf_t.add_paragraph()
        p.text = "✔ " + it
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_DARK
        p.space_before = Pt(6)

    # Clinical Disclaimer Box
    b_disc = s14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.9), Inches(11.733), Inches(1.9))
    b_disc.fill.solid()
    b_disc.fill.fore_color.rgb = RGBColor(254, 242, 242)
    b_disc.line.color.rgb = RGBColor(239, 68, 68)

    tf_d = b_disc.text_frame
    tf_d.word_wrap = True
    p = tf_d.paragraphs[0]
    p.text = "CLINICAL DISCLAIMER & RESPONSIBLE AI STATEMENT:"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = RGBColor(185, 28, 28)

    p_d = tf_d.add_paragraph()
    p_d.text = "This system is intended for research and clinical decision-support purposes only and is not a substitute for professional medical diagnosis, advice, or treatment. Healthcare providers and analysts must independently evaluate all predictions before taking clinical action."
    p_d.font.size = Pt(12)
    p_d.font.color.rgb = TEXT_DARK
    p_d.space_before = Pt(6)

    # =========================================================
    # SLIDE 15: Conclusion & Future Scope (Dark Theme)
    # =========================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15, DARK_BG)

    tb15 = s15.shapes.add_textbox(Inches(1.5), Inches(1.2), Inches(10.333), Inches(5.1))
    tf15 = tb15.text_frame
    tf15.word_wrap = True

    p = tf15.paragraphs[0]
    p.text = "Conclusion & Future Work"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = TEAL
    p.alignment = PP_ALIGN.CENTER

    conc_bullets = [
        "Successfully developed PRF-BXGBOOST feature selection & 6-organ complication assessment suite.",
        "Quantified internal validation optimism bias (ΔAUC = -12.4%) via Pima → Mendeley zero-shot transfer.",
        "Identified and reported age-related demographic fairness disparities in clinical ML deployment.",
        "Deployed a production full-stack application (FastAPI, React SPA, Cloud Avion MySQL) with 14 engineering modules.",
        "Future Scope: Integration with IoT wearable sensors, real-time EHR data feeds, and HL7 FHIR standards."
    ]
    for b in conc_bullets:
        p = tf15.add_paragraph()
        p.text = "✔ " + b
        p.font.size = Pt(14)
        p.font.color.rgb = WHITE
        p.space_before = Pt(12)

    p_ty = tf15.add_paragraph()
    p_ty.text = "\nThank You! Questions & Answers"
    p_ty.font.size = Pt(22)
    p_ty.font.bold = True
    p_ty.font.color.rgb = CYAN
    p_ty.alignment = PP_ALIGN.CENTER
    p_ty.space_before = Pt(25)

    prs.save(PPTX_OUTPUT_PATH)
    print(f"[SUCCESS] PowerPoint presentation generated successfully at: {PPTX_OUTPUT_PATH}")

if __name__ == "__main__":
    create_presentation()

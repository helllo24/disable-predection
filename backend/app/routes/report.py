from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.pdf_report_service import generate_patient_health_pdf

router = APIRouter(prefix="/api/reports", tags=["Patient Health Reports"])

@router.get("/health")
def download_patient_health_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates and returns a downloadable PDF health summary report based ONLY on real data stored
    for the authenticated patient. A patient can only generate and download their own report.
    """
    pdf_bytes = generate_patient_health_pdf(user=current_user, db=db)
    
    filename = f"Health_Report_Patient_{current_user.id}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )

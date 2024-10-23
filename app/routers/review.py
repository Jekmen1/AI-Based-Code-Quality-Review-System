from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from models.review import CodeReview
from database import get_db
from services.analyzer import analyze_code

router = APIRouter()

@router.post("/review/")
async def upload_code(file: UploadFile = File(...), db: Session = Depends(get_db)):
    code = (await file.read()).decode('utf-8')

    comments = analyze_code(code)

    code_review = CodeReview(file_name=file.filename, code=code, review_comments=str(comments))
    db.add(code_review)
    db.commit()
    db.refresh(code_review)

    return {
        "filename": file.filename,
        "review_comments": comments
    }


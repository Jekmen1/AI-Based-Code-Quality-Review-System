from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from models.review import CodeReview
from database import get_db
from services.analyzer import run_pylint, get_ai_review, analyze_code

router = APIRouter()

@router.post("/review/pylint/")
async def upload_code_pylint(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.py'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a Python file.")
    code = (await file.read()).decode('utf-8')
    # print(code)
    print(analyze_code(code))

    pylint_comments = run_pylint(code)
    print(pylint_comments)
    code_review = CodeReview(file_name=file.filename, code=code, review_comments=str(pylint_comments))
    db.add(code_review)
    db.commit()
    db.refresh(code_review)

    return {
        "filename": file.filename,
        "review_comments": pylint_comments
    }


@router.post("/review/ai/")
async def upload_code_ai(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.py'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a Python file.")
    code = (await file.read()).decode('utf-8')

    ai_review = get_ai_review(code)

    code_review = CodeReview(file_name=file.filename, code=code, review_comments=ai_review)
    db.add(code_review)
    db.commit()
    db.refresh(code_review)

    return {
        "filename": file.filename,
        "review_comments": ai_review
    }

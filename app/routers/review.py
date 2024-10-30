from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from models.review import CodeReview
from database import get_db
from services.analyzer import get_ai_review
import subprocess
import ast
import os

router = APIRouter()

def analyze_syntax(code: str) -> list:
    errors = []
    try:
        ast.parse(code)
    except SyntaxError as e:
        errors.append({
            'line': e.lineno,
            'message': e.msg,
            'type': 'SyntaxError'
        })
    return errors

def run_pylint_code(code: str) -> dict:
    errors = analyze_syntax(code)
    if errors:
        return {'errors': errors}

    temp_file_path = 'temp_code.py'
    try:
        with open(temp_file_path, 'w') as temp_file:
            temp_file.write(code)

        result = subprocess.run(
            ['pylint', temp_file_path, '--output-format=json'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        if result.stdout:
            pylint_errors = eval(result.stdout.decode())
            for error in pylint_errors:
                errors.append({
                    'line': error.get('line'),
                    'column': error.get('column'),
                    'message': error.get('message'),
                    'type': error.get('type', 'PylintError')
                })

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    return {'errors': errors}

@router.post("/review/pylint/")
async def upload_code_pylint(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.py'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a Python file.")

    code = (await file.read()).decode('utf-8')
    pylint_output = run_pylint_code(code)

    code_review = CodeReview(
        file_name=file.filename,
        code=code,
        review_comments=str(pylint_output)
    )

    db.add(code_review)
    db.commit()
    db.refresh(code_review)

    response = {
        "static_analysis": {
            "errors": pylint_output['errors'],
            "summary": f"Your code has {len(pylint_output['errors'])} issues."
        },
    }

    return response

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

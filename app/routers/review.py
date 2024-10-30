from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from models.review import CodeReview
from database import get_db
from services.analyzer import get_ai_review
import subprocess
import ast

router = APIRouter()



def analyze_syntax(code: str) -> list:
    errors = []
    lines = code.splitlines()
    for lineno, line in enumerate(lines, start=1):
        try:
            ast.parse(line)
        except SyntaxError as e:
            errors.append({
                'line': lineno,
                'column': e.offset,
                'message': e.msg,
                'type': 'SyntaxError'
            })
    return errors


def run_pylint_code(code: str) -> dict:
    with open('temp_code.py', 'w') as temp_file:
        temp_file.write(code)

    result = subprocess.run(['pylint', 'temp_code.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = result.stdout.decode()
    errors = []

    syntax_errors = analyze_syntax(code)
    if syntax_errors:
        errors.extend(syntax_errors)
    else:
        for line in output.split('\n'):
            if line.startswith('temp_code.py:'):
                parts = line.split(':')
                error = {
                    'line': int(parts[1]),
                    'column': int(parts[2]),
                    'message': parts[3].strip(),
                    'type': parts[4].split()[0] if len(parts) > 4 else 'Unknown'
                }
                errors.append(error)

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

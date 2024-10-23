import subprocess
import google.generativeai as genai

genai.configure(api_key="key")

model = genai.GenerativeModel("gemini-1.5-flash")

def run_pylint(code: str) -> dict:
    with open('temp_code.py', 'w') as f:
        f.write(code)
    result = subprocess.run(['pylint', 'temp_code.py'], stdout=subprocess.PIPE)
    output = result.stdout.decode()

    errors = []
    score = "N/A"
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
        elif 'rated at' in line:
            score = line.split('rated at')[1].strip().split(' ')[0]

    return {
        'errors': errors,
        'score': score
    }


def get_ai_review(code: str) -> str:
    try:
        # Generate content from the model
        response = model.generate_content(
            f"Analyze the following code and provide feedback:\n\n{code}",
            generation_config=genai.types.GenerationConfig(
                candidate_count=1,
                stop_sequences=["x"],
                max_output_tokens=200,
                temperature=1.0
            )
        )

        print("AI Response:", response)

        if response.candidates and hasattr(response.candidates[0], 'content'):
            ai_content = response.candidates[0].content
            if hasattr(ai_content, 'parts') and len(ai_content.parts) > 0:
                return ai_content.parts[0].text
            else:
                return "No valid parts in AI response."
        else:
            return "No AI feedback available."
    except Exception as e:
        return f"AI review failed: {str(e)}"


def analyze_code(code: str) -> dict:
    pylint_output = run_pylint(code)
    ai_review = get_ai_review(code)

    return {
        "static_analysis": {
            "errors": pylint_output['errors'],
            "score": pylint_output['score'],
            "summary": f"Your code has {len(pylint_output['errors'])} issues."
        },
        "ai_review": ai_review
    }

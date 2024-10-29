import subprocess
import google.generativeai as genai


genai.configure(api_key="key")

model = genai.GenerativeModel("gemini-1.5-pro-001")


def run_pylint(code: str) -> dict:
    with open('temp_code.py', 'w') as f:
        f.write(code)
    result = subprocess.run(['pylint', "temp_code.py"], stdout=subprocess.PIPE)
    output = result.stdout.decode()

    errors = []
    for line in output.split('\n'):
        if line.startswith('temp_code.py:'):
            parts = line.split(':')
            error = {
                'line': int(parts[1]),
                'message': parts[3].strip(),
                'type': parts[4].split()[0] if len(parts) > 4 else 'Unknown'
            }
            errors.append(error)




    return {
        'errors': errors,
    }


def get_ai_review(code: str) -> str:
    try:
        response = model.generate_content(
            f"Analyze the following code and provide feedback:\n\n{code}",
            generation_config=genai.types.GenerationConfig(
                temperature=1,
                top_p=0.95,
                top_k=64,
                max_output_tokens=2000,
                response_mime_type="text/plain"
            )
        )

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

    return {
        "static_analysis": {
            "errors": pylint_output['errors'],
            "summary": f"Your code has {len(pylint_output['errors'])} issues."
        },

    }


        "ai_review": ai_review
    }


import subprocess
import google.generativeai as genai

genai.configure(api_key="key")

model = genai.GenerativeModel("gemini-1.5-flash")

def run_pylint(code: str) -> str:
    with open('temp_code.py', 'w') as f:
        f.write(code)
    result = subprocess.run(['pylint', 'temp_code.py'], stdout=subprocess.PIPE)
    return result.stdout.decode()

def get_ai_review(code: str) -> str:
    try:
        response = model.generate_content(
            f"Analyze the following code and provide feedback:\n\n{code}",
            generation_config=genai.types.GenerationConfig(
                candidate_count=1,
                stop_sequences=["x"],
                max_output_tokens=200,
                temperature=1.0
            )
        )

        print(response)

        if response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'text'):
                return candidate.text
            elif hasattr(candidate, 'content'):
                return candidate.content
            else:
                return "No valid content field in AI response."
        else:
            return "No AI feedback available."
    except Exception as e:
        return f"AI review failed: {str(e)}"




def analyze_code(code: str) -> str:
    pylint_output = run_pylint(code)

    ai_review = get_ai_review(code)
    return f"Static Analysis:\n{pylint_output}\nAI Review:\n{ai_review}"
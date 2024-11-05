import subprocess
import google.generativeai as genai


genai.configure(api_key="key")

model = genai.GenerativeModel("gemini-1.5-pro-001")



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









import json
import time

from google import genai
from django.conf import settings
from .prompt import PROMPT, QUESTION_PROMPT

client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)

def clean_json_response(text):
    """Helper to clean markdown wrapping from Gemini JSON response"""
    text = text.strip()
    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()
    return text

def generate_assessment_tasks(skill):
    """
    Generates exactly 5 practical coding tasks for the given skill.
    Handles Gemini API calls, retries, and JSON parsing.
    """
    prompt = f"""
{QUESTION_PROMPT}

SKILL:
{skill.name}

SKILL DESCRIPTION:
{skill.description}
"""

    for attempt in range(3):
        try:
            # response = client.models.generate_content(
            #     model="gemini-2.5-flash",
            #     contents=prompt,
            # )
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
            )
            text = clean_json_response(response.text)
            return json.loads(text)
        except Exception as e:
            if attempt == 2:
                print(f"Failed to generate tasks after 3 attempts: {e}")
                raise e
            time.sleep(2 ** attempt)

def evaluate_assessment_batch(assessment, submissions):
    """
    Evaluates all 5 answers in a single batch request to Gemini.
    Reduces latency, token usage, and cost while improving evaluation context.
    """
    # Build the assessment data text
    assessment_data = ""
    for i, sub in enumerate(submissions, 1):
        assessment_data += f"Question {i}\n"
        assessment_data += f"Title: {sub.task.title}\n"
        assessment_data += f"Difficulty: {sub.task.difficulty}\n"
        assessment_data += f"Question:\n{sub.task.question}\n\n"
        assessment_data += f"Candidate Answer:\n{sub.answer}\n"
        assessment_data += "-" * 60 + "\n\n"
    
    candidate_name = assessment.user.get_full_name() or assessment.user.username
    
    prompt = PROMPT.format(
        skill_name=assessment.skill.name,
        candidate_name=candidate_name,
        passing_score=assessment.skill.passing_score,
        assessment_data=assessment_data
    )

    for attempt in range(3):
        try:
            # response = client.models.generate_content(
            #     model="gemini-2.5-flash",
            #     contents=prompt,
            # )
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
            )
            text = clean_json_response(response.text)
            return json.loads(text)
        except Exception as e:
            if attempt == 2:
                print(f"Failed to evaluate batch after 3 attempts: {e}")
                raise e
            time.sleep(2 ** attempt)
import json
import time

from google import genai
from django.conf import settings
from .prompt import PROMPT, QUESTION_PROMPT

client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)



def generate_assessment_tasks(skill):

    prompt = f"""
{QUESTION_PROMPT}

SKILL:
{skill.name}

SKILL DESCRIPTION:
{skill.description}
"""

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )

            text = response.text.strip()

            if text.startswith("```"):
                text = text.replace("```json", "")
                text = text.replace("```", "")
                text = text.strip()

            return json.loads(text)

        except Exception as e:

            if attempt == 2:
                raise e

            time.sleep(2 ** attempt)


def evaluate_submission(task, answer):

    prompt = f"""
{PROMPT}

TASK TITLE:
{task.title}

TASK DESCRIPTION:
{task.question}

CANDIDATE ANSWER:
{answer}
"""

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )

            text = response.text.strip()

            # In case Gemini returns ```json ... ```
            if text.startswith("```"):
                text = text.replace("```json", "")
                text = text.replace("```", "")
                text = text.strip()

            result = json.loads(text)

            return result

        except Exception as e:

            if attempt == 2:
                raise e

            time.sleep(2 ** attempt)
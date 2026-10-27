import os
import re
import json

from dotenv import load_dotenv
from anthropic import Anthropic


# Load environment variables
load_dotenv()

# Create Anthropic client
client = Anthropic(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api"
)


def validate_pan_card(pan_str: str) -> bool:
    """
    Validate Indian PAN format.

    Format:
    5 letters + 4 numbers + 1 letter
    Example: ABCDE1234F
    """

    pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$"

    return bool(re.match(pattern, pan_str))


def execute_milestone_pipeline(raw_resume_text: str):

    prompt = f"""
Extract data inside <data> tags as strict JSON matching these keys:
'full_name', 'pan_card', 'skills'.

Return only valid JSON.

Text:
{raw_resume_text}
"""

    response = client.messages.create(
        model="anthropic/claude-3-haiku",
        max_tokens=400,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    raw_output = response.content[0].text.strip()

    try:
        # Convert Claude response to JSON
        data = json.loads(raw_output)

        # Get PAN number
        pan = data.get("pan_card", "")

        # Validate PAN
        is_valid_pan = validate_pan_card(pan)

        return {
            "status": "SUCCESS" if is_valid_pan else "VALIDATION_FAILED",
            "extracted_data": data,
            "pan_valid": is_valid_pan
        }

    except json.JSONDecodeError as e:

        return {
            "status": "PARSING_ERROR",
            "error": str(e)
        }


if __name__ == "__main__":

    sample_text = """
    Candidate Name: Test Candidate.
    PAN: ABCDE1234F.
    Role: GenAI Systems Engineer.
    Skills: Python, GenAI, APIs.
    """

    result = execute_milestone_pipeline(sample_text)

    print(
        "Milestone 1 Test Output:",
        json.dumps(result, indent=2)
    )
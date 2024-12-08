from openai import OpenAI
import os
from dotenv import load_dotenv
from utils import log_info, log_error

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = OpenAI(api_key=api_key)

def classify_email(content):
    """
    Classify email content using the updated OpenAI API.

    Args:
        content (str): The email content to classify.

    Returns:
        str: The classification result.
    """
    try:
        log_info("Sending content to OpenAI chat.completions.create API...")

        # Define the messages for the classification
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant trained to classify emails into the following categories: "
                           "'Job Application', 'Interview Invitation', 'Assessment Invite', 'Rejection', or 'Other'. "
                           "Provide only the classification."
            },
            {
                "role": "user",
                "content": f"Email Content: {content}\n\nWhat is the classification?"
            }
        ]

        # Call the OpenAI chat completions endpoint
        response = client.chat.completions.create(
            model="gpt-4o",  # Use the correct model
            messages=messages,
        )

        # Extract and return the classification
        classification = response.choices[0].message.content.strip()
        log_info(f"Classification result: {classification}")
        return classification

    except Exception as e:
        log_error(f"An unexpected error occurred during classification: {str(e)}")
        return "Error"

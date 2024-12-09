from openai import OpenAI
import os
from dotenv import load_dotenv
from utils import log_info, log_error
import json

JOB_APPLICATIONS_FILE = "job_applications.json"

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
                "content": (
                    "You are a helpful assistant trained to classify emails into the following categories: "
                    "'Job Application', 'Interview Invitation', 'Assessment Invite', 'Rejection', or 'Other'. "
                    "If the classification is not 'Other', always provide a JSON object with the following format:\n"
                    "{\n"
                    "  \"classification\": \"<classification>\",\n"
                    "  \"company\": \"<company>\",\n"
                    "  \"position\": \"<position>\"\n"
                    "}\n"
                    "If the classification is 'Other', respond with exactly this: {\"classification\": \"Other\"}"
                )
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
        response_content = response.choices[0].message.content.strip()
        log_info(f"Classification result: {response_content}")
        try:
            result = json.loads(response_content)  # Parse the JSON response
            if result.get("classification", "").lower() != "other":
                save_job_application(
                    company=result.get("company", "Unknown"),
                    position=result.get("position", "Unknown"),
                    classification=result.get("classification", "Unknown")
                )
        except json.JSONDecodeError:
            log_error(f"Failed to decode response as JSON: {response_content}")

        return response_content

    except Exception as e:
        log_error(f"An unexpected error occurred during classification: {str(e)}")
        return "Error"
    

def initialize_json_file():
    """
    Ensure the job applications JSON file exists and is properly initialized.
    """
    if not os.path.exists(JOB_APPLICATIONS_FILE):
        with open(JOB_APPLICATIONS_FILE, "w") as file:
            json.dump([], file)

def save_job_application(company, position, classification):
    """
    Save job application details to the JSON file.

    Args:
        company (str): The company name.
        position (str): The job position.
        classification (str): The classification of the email.
    """
    try:
        with open(JOB_APPLICATIONS_FILE, "r+") as file:
            # Load existing data
            data = json.load(file)

            # Append the new application
            data.append({
                "company": company,
                "position": position,
                "classification": classification
            })

            # Write updated data back to the file
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()  # Ensure old content is removed

        log_info(f"Saved job application: Company={company}, Position={position}, Classification={classification}")

    except Exception as e:
        log_error(f"Failed to save job application: {str(e)}")

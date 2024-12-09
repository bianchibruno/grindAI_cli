from openai import OpenAI
import os
import json
import re
from dotenv import load_dotenv
from utils import log_info, log_error

JOB_APPLICATIONS_FILE = "job_applications.json"

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = OpenAI(api_key=api_key)

def parse_response_content(response_content):
    """
    Parse the response content from OpenAI and return a dictionary.

    Args:
        response_content (str): The raw response content from OpenAI.

    Returns:
        dict: A parsed dictionary containing the classification, company, and position.
    """
    # log_info(f"Raw Response Content: {response_content}")

    # Step 1: Strip whitespace
    cleaned_content = response_content.strip()
    # log_info(f"Cleaned Content: {cleaned_content}")

    try:
        # Step 2: Parse the cleaned content as JSON
        result = json.loads(cleaned_content)
        # log_info(f"Parsed JSON: {result}")
        return result
    except json.JSONDecodeError as e:
        log_error(f"JSONDecodeError: {e}")

        # Step 3: Attempt to extract JSON-like content using regex
        log_info("Attempting to extract JSON content using regex...")
        match = re.search(r'\{.*\}', cleaned_content, re.DOTALL)
        if match:
            extracted_content = match.group(0)
            log_info(f"Extracted JSON Content: {extracted_content}")
            try:
                result = json.loads(extracted_content)
                log_info(f"Parsed JSON After Extraction: {result}")
                return result
            except json.JSONDecodeError as e_inner:
                log_error(f"Failed to parse extracted JSON: {e_inner}")

    # Return an empty result if parsing fails
    return {"classification": "Error", "company": "Unknown", "position": "Unknown"}


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
                    "You are a helpful assistant trained to classify emails and extract job application details. "
                    "Your tasks are as follows:\n"
                    "1. Classify the email into one of these categories: 'Job Application', 'Interview Invitation', "
                    "'Assessment Invite', 'Rejection', or 'Other'.\n"
                    "2. If the classification is not 'Other', extract the company name and the job position.\n"
                    "3. Always respond with a valid JSON object in this format:\n"
                    "{\n"
                    "  \"classification\": \"<classification>\",\n"
                    "  \"company\": \"<company>\",\n"
                    "  \"position\": \"<position>\"\n"
                    "}\n"
                    "4. If the classification is 'Other', respond with this exact JSON object:\n"
                    "{ \"classification\": \"Other\" }\n"
                    "Do not include any additional text, explanations, or formatting such as Markdown."
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

        # Parse the response content
        result = parse_response_content(response_content)

        # Save job application if classification is not "Other"
        if result.get("classification", "").lower() != "other":
            save_job_application(
                company=result.get("company", "Unknown"),
                position=result.get("position", "Unknown"),
                classification=result.get("classification", "Unknown")
            )

        return result

    except Exception as e:
        log_error(f"An unexpected error occurred during classification: {str(e)}")
        return {"classification": "Error", "company": "Unknown", "position": "Unknown"}


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

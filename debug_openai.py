# from openai import OpenAI
# client = OpenAI()

# response = client.chat.completions.create(
#     messages=[{
#         "role": "user",
#         "content": "Say this is a test",
#     }],
#     model="gpt-4o",
# )

# print(response.choices[0].message.content)

from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = OpenAI(api_key=api_key)

def classify_email_debug(content):
    """
    Classify email content using the updated OpenAI API.

    Args:
        content (str): The email content to classify.

    Returns:
        str: The classification result.
    """
    try:
        print("INFO: Sending content to OpenAI chat.completions.create API...")

        # Define the messages as per the updated API documentation
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant trained to classify emails into one of these categories: "
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
            model="gpt-4o",
            messages=messages,
        )

        # Extract and return the classification from the response
        classification = response.choices[0].message.content.strip()
        print(f"INFO: Classification result: {classification}")
        return classification

    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {str(e)}")
        return "Error"

def main():
    print("Welcome to the OpenAI Email Classification Debug Tool!")
    print("Enter email content below, or type 'exit' to quit.\n")

    while True:
        email_content = input("Enter email content: ")
        if email_content.lower() == "exit":
            print("Exiting the debug tool. Goodbye!")
            break

        classification = classify_email_debug(email_content)
        print(f"Classification: {classification}\n")

if __name__ == "__main__":
    main()

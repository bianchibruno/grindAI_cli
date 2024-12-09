import json
import re

def parse_response_content(response_content):
    """
    Parse the response content from OpenAI and return a dictionary.

    Args:
        response_content (str): The raw response content from OpenAI.

    Returns:
        dict: A parsed dictionary containing the classification, company, and position.
    """


    # Step 1: Strip whitespace
    cleaned_content = response_content.strip()
    # print(f"Cleaned Content: {cleaned_content}")

    try:
        # Step 2: Parse the cleaned content as JSON
        result = json.loads(cleaned_content)
        print(f"Parsed JSON: {result}")
        return result
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")

        # Step 3: Attempt to extract JSON-like content using regex
        print("Attempting to extract JSON content using regex...")
        match = re.search(r'\{.*\}', cleaned_content, re.DOTALL)
        if match:
            extracted_content = match.group(0)
            print(f"Extracted JSON Content: {extracted_content}")
            try:
                result = json.loads(extracted_content)
                print(f"Parsed JSON After Extraction: {result}")
                return result
            except json.JSONDecodeError as e_inner:
                print(f"Failed to parse extracted JSON: {e_inner}")

    # Return an empty result if parsing fails
    return {"classification": "Error", "company": "Unknown", "position": "Unknown"}


# Test cases
if __name__ == "__main__":
    test_responses = [
        # Valid JSON
        '{ "classification": "Rejection", "company": "Oxford University", "position": "Mathematics" }',

        # JSON with leading/trailing whitespace
        '   { "classification": "Interview Invitation", "company": "Amazon", "position": "Software Engineer" }   ',

        '{"classification": "Interview Invitation","company": "University of Cambridge","position": "PGCE Maths program"}',

        # JSON wrapped in Markdown-style formatting
        '```json\n{ "classification": "Job Application", "company": "Google", "position": "Backend Developer" }\n```',

        # Invalid JSON
        '{ "classification": "Rejection", "company": "Microsoft", "position": "AI Researcher"',

        # Non-JSON string
        'This is not JSON at all!'
    ]

    for i, response in enumerate(test_responses, start=1):
        print(f"\nTest Case {i}:")
        result = parse_response_content(response)
        print(f"Final Parsed Result: {result}")

from gmail_service import GmailService
from openai_service import classify_email
from utils import log_info, log_error

def main():
    """
    Main function to authenticate Gmail, fetch emails, classify them using OpenAI,
    and log the results.
    """
    try:
        log_info("Starting the application...")

        # Step 1: Ask if the user wants to switch accounts
        switch_account = input("Do you want to log in with a different account? (yes/no): ").strip().lower()
        force_new_login = switch_account == "yes"

        # Step 2: Authenticate Gmail
        log_info("Authenticating Gmail API...")
        gmail_service = GmailService()
        service = gmail_service.authenticate(force_new_login=force_new_login)
        log_info("Gmail authentication successful.")

        # Step 3: Fetch emails
        log_info("Fetching emails...")
        emails = gmail_service.fetch_emails(service)
        log_info(f"Fetched {len(emails)} emails.")

        # Step 4: Classify emails using OpenAI
        log_info("Classifying emails...")
        results = []
        for email in emails:
            classification = classify_email(email['content'])
            results.append({
                "subject": email['subject'],
                "classification": classification
            })

        # Step 5: Log and display results
        log_info("Email classification complete.")
        log_info("Classified Emails:")
        for result in results:
            log_info(f"Subject: {result['subject']}, Classification: {result['classification']}")

        print("\n--- Results ---")
        for result in results:
            print(f"Subject: {result['subject']}, Classification: {result['classification']}")

    except Exception as e:
        log_error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()


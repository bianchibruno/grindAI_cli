import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from utils import log_info, log_error
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailService:
    """
    Handles Gmail API authentication and email fetching.
    """

    def fetch_emails(self, service, max_results=50):
        """
        Fetch emails and their full content from the Primary Inbox.

        Args:
            service (googleapiclient.discovery.Resource): The Gmail API service instance.
            max_results (int): Maximum number of emails to fetch.

        Returns:
            list: A list of dictionaries with email metadata (id, subject, full content).
        """
        try:
            log_info(f"Fetching up to {max_results} emails from the Primary Inbox...")
            
            # Use Gmail's query language to search only in the Primary Inbox
            query = "category:primary"

            # Fetch email metadata
            results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
            messages = results.get('messages', [])
            email_data = []

            for message in messages:
                # Get the full message content
                msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                payload = msg.get('payload', {})
                headers = payload.get('headers', [])

                # Extract the subject
                subject = next(
                    (header['value'] for header in headers if header['name'] == 'Subject'), "No Subject"
                )

                # Extract the email body
                body = self.get_email_body(payload)

                email_data.append({
                    "id": message['id'],
                    "subject": subject,
                    "content": body
                })

            log_info(f"Successfully fetched {len(email_data)} emails.")
            return email_data
        except Exception as e:
            log_error(f"Failed to fetch emails: {str(e)}")
            raise

    def get_email_body(self, payload):
        """
        Extract the plain text or HTML body from the email payload.

        Args:
            payload (dict): The email payload from the Gmail API.

        Returns:
            str: The decoded email body as plain text.
        """
        import base64
        import quopri

        body = ""
        parts = payload.get('parts', [])
        if not parts:
            # If no parts, try the main body
            body = payload.get('body', {}).get('data', "")
        else:
            for part in parts:
                mime_type = part.get("mimeType", "")
                if mime_type == "text/plain":  # Prioritize plain text content
                    body = part.get("body", {}).get("data", "")
                    break
                elif mime_type == "text/html":  # Fallback to HTML
                    body = part.get("body", {}).get("data", "")

        if body:
            try:
                # Decode base64 content
                body = base64.urlsafe_b64decode(body).decode('utf-8', errors="replace")
            except Exception as e:
                log_error(f"Error decoding email body: {e}")
                body = "[Error decoding email body]"

        return body

    def authenticate(self, force_new_login=False):
        """
        Authenticate with Gmail API and return the service object.

        Args:
            force_new_login (bool): If True, forces a new login and ignores saved credentials.

        Returns:
            googleapiclient.discovery.Resource: The Gmail API service instance.
        """
        try:
            log_info("Starting Gmail API authentication...")
            creds = None

            # Check if user wants to force a new login
            if not force_new_login and os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token and not force_new_login:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next session
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            log_info("Gmail API authentication successful.")
            return build('gmail', 'v1', credentials=creds)
        except Exception as e:
            log_error(f"Failed to authenticate Gmail API: {str(e)}")
            raise


import os
import email
import base64
import pickle
from .validator import Validator
from .yesbank_parser import YesBankParser
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_service():
    """
    Create a gmail service using credential provided by the google developer
    to fetch the mail messages.
    :return: service
    """
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service


def get_all_messages(service, query: str):
    """
    Get all the messages based on the query searched.
    :return: List of messages
    """
    # Call the Gmail API only using IMPORTANT label
    response = service.users().messages().list(userId='me', includeSpamTrash=False, labelIds=['IMPORTANT'],
                                               q=query).execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])

    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(userId='me', q=query,
                                                   pageToken=page_token).execute()
        if 'messages' in response:
            messages.extend(response['messages'])

    return messages


def fetch_raw_message(service, message):
    """
    Fetch raw message from encoded message.
    :return: raw_message
    """
    msg = service.users().messages().get(
        userId='me', id=message['id'], format="raw").execute()

    msg_raw = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
    msg_str = email.message_from_bytes(msg_raw)
    return msg_str


def main():
    output_list = []
    service = get_service()
    query = 'credit card e-statement'
    messages = get_all_messages(service, query)
    for message in messages:
        # Store all the content
        output = dict()
        msg = fetch_raw_message(message)
        sender, receiver, subject, date = msg['from'], msg['to'], msg['Subject'], msg['Date']
        sender_domain = sender.split('@')[1]
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() in ('text/plain', 'text/html'):
                    output = Validator.get_parser_obj(sender_domain).extract_information(msg, part.get_content_type())
                    break
        else:
            output = Validator.get_parser_obj(sender_domain).extract_information(msg, msg.get_content_type())

        output['From'] = msg['from']
        output['To'] = msg['to']
        output['Subject'] = msg['Subject']
        output['Date'] = msg['Date']
        output_list.append(output)

    print(output_list)


if __name__ == '__main__':
    main()
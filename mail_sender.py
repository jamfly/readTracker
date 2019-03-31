import pickle
import os.path
import mimetypes

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from base64 import urlsafe_b64encode
from apiclient import errors

SCOPES = ['https://mail.google.com/']


class MailSender:
    def __init__(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens
        # and is created automatically when the authorization flow completes
        # for the first time.
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
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self._service = build('gmail', 'v1', credentials=creds)

    @property
    def service(self):
        return self._service

    def create_message(self, sender, to, subject, message_text):
        """Create a message for an email.

        Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

        Returns:
        An object containing a base64url encoded email object.
        """
        body = '<p>' + message_text + \
            '<img src="http://1x1px.me/FFFFFF-0.png"/></p>'
        message = MIMEText(body, 'html')
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

    def create_message_with_attachment(
            self, sender, to, subject, message_text, file):
        """Create a message for an email.

        Args:
            sender: Email address of the sender.
            to: Email address of the receiver.
            subject: The subject of the email message.
            message_text: The text of the email message.
            file: The path to the file to be attached.

        Returns:
            An object containing a base64url encoded email object.
        """
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject

        body = '<p>' + message_text + \
            '<img src="http://1x1px.me/FFFFFF-0.png"/></p>'
        msg = MIMEText(body, 'html')
        message.attach(msg)
        content_type, encoding = mimetypes.guess_type(file)

        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        if main_type == 'text':
            fp = open(file, 'rb')
            msg = MIMEText(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'image':
            fp = open(file, 'rb')
            msg = MIMEImage(fp.read(), _subtype=sub_type)
            fp.close()
        elif main_type == 'audio':
            fp = open(file, 'rb')
            msg = MIMEAudio(fp.read(), _subtype=sub_type)
            fp.close()
        else:
            fp = open(file, 'rb')
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
            fp.close()
        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)

        return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

    def send_message(self, user_id, message):
        """Send an email message.
        Args:
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

        Returns:
        Sent Message.
        """
        try:
            message = (self._service.users().messages().send(
                userId=user_id, body=message).execute())
            print('Message Id: %s' % message['id'])
            return message
        except errors.HttpError as error:
            print(f'An error occurred: {error}')
            return None


if __name__ == '__main__':
    mailSender = MailSender()
    myMailAddress = 'cocoredju222@gmail.com'
    reciverAddress = 'cocoredju000@yahoo.com.tw'
    filePath = os.path.relpath('test_image.jpg')
    message = mailSender.create_message(sender=myMailAddress,
                                        to=reciverAddress,
                                        subject='cool it is work',
                                        message_text='this is sooooooooo cool')

    attactedMessage = mailSender.create_message_with_attachment(
        sender=myMailAddress, to=reciverAddress, subject='attatch yo~~~',
        message_text='hahaha', file=filePath)

    mailSender.send_message(user_id='me', message=attactedMessage)

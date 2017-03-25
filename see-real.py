import serial
import httplib2
import os
import oauth2client
from oauth2client import client, tools
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apiclient import errors, discovery

# Some code from Google API site and a StackOverflow post which was then tweaked by me
# https://developers.google.com/gmail/api/quickstart/python
# https://developers.google.com/gmail/api/guides/sending
SCOPES = 'https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'See-real Box'

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-email-send.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print 'Storing credentials to ' + credential_path
    return credentials

def send_message(sender, to, subject, msgHtml):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    message1 = create_message(sender, to, subject, msgHtml)
    send_message_internal(service, "me", message1)

def send_message_internal(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print 'Message Id: %s' % message['id']
        return message
    except errors.HttpError, error:
        print 'An error occurred: %s' % error

def create_message(sender, to, subject, msgHtml):
	msg = MIMEMultipart('alternative')
	msg['Subject'] = subject
	msg['From'] = sender
	msg['To'] = to

	message = MIMEText(msgHtml, 'html')
	msg.attach(message)

	return {'raw': base64.urlsafe_b64encode(msg.as_string())}

def send_email():
	to = "psy226@nyu.edu"
	sender = "psy226@nyu.edu"
	subject = "Intrusion Detected from See-real Box"
	msgHtml = "Intrusion detected!<br/>Connect the USB to camera SD card and check video files in E:/VIDEO/DVREC/"
	print "Sending email..."
	send_message(sender, to, subject, msgHtml)

def main():
	ser = serial.Serial('COM4', 9600, timeout=0.2)
	ser.flush()

	while True:
		line = ser.readline().rstrip()
		if line:
			print line
		if line == "Motion detected!":
			send_email()
			print "Recording video..."
		if line == "Motion ended!":
			print "-------------------"

main()
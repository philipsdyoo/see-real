import serial
import httplib2
import os
import oauth2client
from oauth2client import client, tools
import base64
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from apiclient import errors, discovery

# Some code from Google API site and a StackOverflow post which was then tweaked by me
# https://developers.google.com/gmail/api/quickstart/python
# https://developers.google.com/gmail/api/guides/sending
# http://stackoverflow.com/questions/37201250/sending-email-via-gmail-python
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

def SendMessage(sender, to, subject, msgHtml, file):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    message1 = CreateMessage(sender, to, subject, msgHtml, file)
    SendMessageInternal(service, "me", message1)

def SendMessageInternal(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print 'Message Id: %s' % message['id']
        return message
    except errors.HttpError, error:
        print 'An error occurred: %s' % error

def CreateMessage(sender, to, subject, msgHtml, file):
	msg = MIMEMultipart('alternative')
	msg['Subject'] = subject
	msg['From'] = sender
	msg['To'] = to

	message = MIMEText(msgHtml, 'html')
	msg.attach(message)

	content_type, encoding = mimetypes.guess_type(file)

	if content_type is None or encoding is not None:
		content_type = 'application/octet-stream'
	main_type, sub_type = content_type.split('/', 1)
	if main_type == 'text':
		fp = open(file, 'rb')
		message = MIMEText(fp.read(), _subtype=sub_type)
		fp.close()
	elif main_type == 'image':
		fp = open(file, 'rb')
		message = MIMEImage(fp.read(), _subtype=sub_type)
		fp.close()
	elif main_type == 'audio':
		fp = open(file, 'rb')
		message = MIMEAudio(fp.read(), _subtype=sub_type)
		fp.close()
	else:
		fp = open(file, 'rb')
		message = MIMEBase(main_type, sub_type)
		message.set_payload(fp.read())
		fp.close()

	print file
	message.add_header('Content-Disposition', 'attachment', filename=file)
	msg.attach(message)

	return {'raw': base64.urlsafe_b64encode(msg.as_string())}

def send_email(file):
	to = "psy226@nyu.edu"
	sender = "psy226@nyu.edu"
	subject = "Intrusion Detected from See-real Box"
	msgHtml = "Intrusion detected!<br/>Please check attachment."
	print "Sending email..."
	SendMessage(sender, to, subject, msgHtml, file)

def check_dir(old_dir, new_dir):
	for f in new_dir:
		if f not in old_dir:
			return f
	return False

# Main
ser = serial.Serial('COM4', 9600, timeout=0.2)
ser.flush()

sd_dir = os.listdir("E:/")

while True:
	line = ser.readline()
	if line:
		print line
		new_file = check_dir(sd_dir, os.listdir("E:/"))
		if new_file:
			print "Attaching" + new_file + " to email"
			send_email("E:/"+new_file)
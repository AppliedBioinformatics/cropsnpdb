# Email alert for new CropSNPdb submissions (added 2026-10-18).
# Reads SMTP settings from snpdb/mail.cfg (kept out of git). If the file is missing, alerts are skipped.
import os, ssl, smtplib, threading, configparser, traceback, sys
from email.message import EmailMessage

CFG = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'mail.cfg'))

def _settings():
	if not os.path.isfile(CFG):
		return None
	cp = configparser.ConfigParser()
	cp.read(CFG)
	return cp['smtp'] if cp.has_section('smtp') else None

def _send(s, subject, body):
	try:
		msg = EmailMessage()
		msg['Subject'] = subject
		msg['From'] = s.get('from')
		msg['To'] = s.get('to')
		msg.set_content(body)
		host, port = s.get('host'), s.getint('port', 587)
		if port == 465:
			server = smtplib.SMTP_SSL(host, port, context=ssl.create_default_context(), timeout=30)
		else:
			server = smtplib.SMTP(host, port, timeout=30)
			if s.getboolean('starttls', True):
				server.starttls(context=ssl.create_default_context())
		if s.get('username'):
			server.login(s.get('username'), s.get('password', ''))
		server.send_message(msg)
		server.quit()
	except Exception:
		print('CropSNPdb notify failed:\n' + traceback.format_exc(), file=sys.stderr)

def notify_submission(subject, body):
	"""Send an alert in the background; never raises. Returns True if an attempt was started."""
	s = _settings()
	if s is None or not s.get('host') or not s.get('to'):
		return False
	threading.Thread(target=_send, args=(s, subject, body), daemon=True).start()
	return True

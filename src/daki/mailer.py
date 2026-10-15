from email.message import EmailMessage
from smtplib import SMTP
from dataclasses import dataclass

@dataclass
class Mailer:
	acco: str
	pw: str

	def send(self, subj: str, cont, **kwargs) -> None: # #
		msg = EmailMessage()
		msg['from'], msg['to'] = self.acco, self.acco
		msg['subject'] = subj
		msg.set_content(cont, **kwargs)
		with SMTP('smtp.gmail.com', 587) as smtp:
			smtp.ehlo()
			smtp.starttls()
			smtp.login(self.acco, self.pw)
			failures = smtp.send_message(msg)
		return failures
			

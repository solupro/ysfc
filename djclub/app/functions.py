# coding: utf-8
import time, datetime

import smtplib
from email.mime.text import MIMEText
from sgmllib import SGMLParser

from django.contrib.auth.models import User as U, check_password as cp
from django.conf import settings

from djclub.app.models import User

def set_password(raw_password):
	user = U()
	user.set_password(raw_password)
	password = user.password
	del user
	return password

def check_password(raw_password, enc_password):
	return cp(raw_password, enc_password)

def liketopic(a,b):
	import difflib
	return len(filter(lambda i: i.startswith('+'), difflib.ndiff(a,b)))

def mention(text):
	usernames = []
	if text.find('@') == -1:
		begin = -1
		usernames = usernames
	elif text.find(' ') != -1:
		begin = text.find('@') + 1
		if text.find('\n') != -1:
			end = text.find(' ') < text.find('\n') and text.find(' ') or text.find('\n')
		else:
			end = len(text)
	elif text.find('\n') != -1:
		begin = text.find('@') + 1
		end = text.find('\n')
	else:
		begin = text.find('@') +1
		end = len(text)
	if begin != -1:
		value = text[begin:end]
		n = len(value)
		for i in range(0,n):
			#print 'name:', value
			rv = None
			try:
				rv = User.objects.get(name=value)
			except Exception, e:
				print e
			if not rv:
				value = list(value)
				value.pop()
				value = ''.join(value)
			else:
				text = text[text.find('@') + len(value):]
				usernames = usernames + [value]
				break
	return usernames

def mentions(text):
	usernames = []
	if text.find('@') == -1:
		begin = -1
		usernames = usernames
	elif text.find(' ') != -1:
		begin = text.find('@') + 1
		if text.find('\n') != -1:
			end = text.find(' ') < text.find('\n') and text.find(' ') or text.find('\n')
		else:
			end = len(text)
	elif text.find('\n') != -1:
		begin = text.find('@') + 1
		end = text.find('\n')
	else:
		begin = text.find('@') +1
		end = len(text)
	if begin != -1:
		value = text[begin:end]
		n = len(value)
		for i in range(0,n):
			#print 'name:', value
			rv = None
			try:
				rv = User.objects.get(name=value)
			except Exception, e:
				print e
			if not rv:
				value = list(value)
				value.pop()
				value = ''.join(value)
			else:
				text = text[text.find('@') + len(value):]
				usernames = usernames + [value]
				while True:
					if mention(text) == []:
						break
					usernames = usernames + mention(text)
					text = text[text.find('@') + len(value):]
				break
	#print 'usernames:', usernames
	return usernames

def getTimeZone(today):
	firstDday = datetime.date(day=1, month=today.month, year=today.year)
	lastMonth = firstDday - datetime.timedelta(days=1)
	year = 0
	month = 0

	if today.month == 12:
		nextMonth = datetime.date(year=today.year+1, month=1, day=1)
	else:
		nextMonth = datetime.date(year=today.year, month=today.month+1, day=1)

	if today.day <= 26:
		st = datetime.datetime(year=lastMonth.year, month=lastMonth.month, day=27)
		et = datetime.datetime(year=today.year, month=today.month, day=26, hour=23,\
								minute=23, second=23)
		year = today.year
		month = today.month
	else:
		st = datetime.datetime(year=today.year, month=today.month, day=27)
		et = datetime.datetime(year=nextMonth.year, month=nextMonth.month, day=26, hour=23,\
								minute=23, second=23)
		year = nextMonth.year
		month = nextMonth.month
	startTime = int(time.mktime(st.timetuple()))
	endTime = int(time.mktime(et.timetuple()))

	return {'st':startTime, 'et':endTime, 'year':year, 'month':month}


def send_mail(title, message, to):
	if settings.IS_SAE:
		from sae.mail import EmailMessage
		m = EmailMessage()
		m.to = to
		m.subject = title
		m.html = '<b>%s</b>' % message
		m.smtp = (settings.MY_EMAIL_HOST, 25, settings.MY_EMAIL_HOST_USER, settings.MY_EMAIL_HOST_PASSWORD, False)
		m.send()

	else:	
		msg = MIMEText(message)
		msg['Subject'] = title
		msg['From'] = settings.MY_EMAIL_HOST_USER
		msg['To'] = to

		s = smtplib.SMTP(settings.MY_EMAIL_HOST)
		status = s.login(settings.MY_EMAIL_HOST_USER, settings.MY_EMAIL_HOST_PASSWORD)

		if status[0] == 235:
			s.sendmail(settings.MY_EMAIL_HOST_USER, [to], msg.as_string())

		s.quit()

class AnimeParser(SGMLParser):
	def reset(self):
		self.links=[]
		SGMLParser.reset(self)

	def parse(self,data):
		self.feed(data)
		self.close()
		
	def start_a(self,attr):
		l = [v for k, v in attr if k == 'href']
		if l:
			self.links.extend(l)

	def end_a(self):
		pass

class VoteParser(SGMLParser):
	def reset(self):
		self.title = ''
		self.votes = []
		self.istitle = False
		self.isdiv = False
		SGMLParser.reset(self)

	def parse(self,data):
		self.feed(data)
		self.close()
		
	def start_title(self,attr):
		self.istitle = True

	def end_title(self):
		self.istitle = False

	def start_div(self, attr):
		for k, v in attr:
			if k.lower() == 'align' and v.lower() == 'center':
				self.isdiv = True

	def end_div(self):
		self.isdiv = False

	def handle_data(self, text):
		if self.istitle:
			self.title = text.decode('gbk').encode('utf-8').replace(' 投票', '')

		if self.isdiv:
			v = int(text.decode('gbk').encode('utf-8').replace('票', ''))
			self.votes.append(v)

def mycmp(x, y):
	return y[1][0] - x[1][0]

# coding: utf-8

import os, time, re

from django import template
from django.conf import settings

from djclub.app.models import User, Topic, Notify, Reply, Thanks

register = template.Library()

@register.filter
def get_notify_count(user_id):
	count = 0
	try:
		user = User.objects.get(id=user_id)
		count = user.notify_set.filter(status=0).count()
	except Exception, e:
		print e
	return count

@register.filter
def gravatar(email, size=128):
	from hashlib import md5
	return 'http://ruby-china.org/avatar/%s?d=identicon&s=%d' % \
			(md5(email.strip().lower().encode('utf-8')).hexdigest(), int(size))

@register.filter
def format_datetime(timestamp):
	FORY = '%Y-%m-%d @ %H:%M'
	FORM = '%m-%d @ %H:%M'
	FORH = '%H:%M'
	os.environ["TZ"] = settings.TIME_ZONE
	time.tzset()
	rtime = time.strftime(FORM, time.localtime(timestamp))
	htime = time.strftime(FORH, time.localtime(timestamp))
	now = int(time.time())
	t = now - timestamp
	if t < 60:
		str = '刚刚'
	elif t < 60 * 60:
		min = t / 60
		str = '%d 分钟前' % min
	elif t < 60 * 60 * 24:
		h = t / (60 * 60)
		str = '%d 小时前 %s' % (h,htime)
	elif t < 60 * 60 * 24 * 3:
		d = t / (60 * 60 * 24)
		if d == 1:
			str = '昨天' + rtime
		else:
			str = '前天' + rtime
	else:
		str = time.strftime(FORY, time.localtime(timestamp))
	return str

@register.filter
def format_datetime2(timestamp):
	FORY = '%Y-%m-%d @ %H:%M'
	os.environ["TZ"] = settings.TIME_ZONE
	time.tzset()
	str = time.strftime(FORY, time.localtime(timestamp))
	return str

@register.filter
def email_to_base64(email):
	import base64
	return base64.encodestring(email)

@register.filter
def at_to_sharp(email):
	return email.replace('@', '(#)')


@register.filter
def get_user_info(user_id, field):
	rt = ''
	try:
		user = User.objects.get(id=user_id)
		rt = getattr(user, field)
	except Exception, e:
		print 'get_user_email:', e
	return rt

@register.filter
def get_user_hour(user_id):
	t = get_user_info(user_id, 'time')
	hour = t / 60
	return '%02d' % hour

@register.filter
def get_user_minute(user_id):
	t = get_user_info(user_id, 'time')
	minute = t % 60
	return '%02d' % minute

@register.filter
def get_balance_hour(balance):
	hour = balance/60
	return '%02d' % hour

@register.filter
def get_balance_minute(balance):
	minute = balance%60
	return '%02d' % minute

@register.filter
def get_bank_time(time):
	try:
		time = int(time)
	except Exception, e:
		print e
		time = 0
	
	hours = time/60
	minute = time%60
	day = hours/24
	hour = hours%24
	return '%d天%02d时%02d分' % (day,hour,minute)

@register.filter
def mentionfilter(text):
	text = text.replace('\n','<br />')
	text = re.sub(ur'(\A|\s|[\u4e00-\u9fa5])@(\w+)', ur'\1@<a href="/member/\2">\2</a>', text)
	return text

@register.filter
def get_topic_last_reply(topic_id):
	rv = Topic.objects.get(id=topic_id).replys.order_by('date')
	return rv[-1] if rv.count() else None

@register.filter
def get_topic_last_reply_id(topic_id):
	last_id = 0
	try:
		topic = Topic.objects.get(id=topic_id)
		replys = topic.reply_set.all().order_by('-date')
		last_id = replys[0].id
	except Exception, e:
		print e
	return last_id

@register.filter
def get_reply_author_id(reply_id):
	rv = Reply.objects.get(id=reply_id)
	return rv.author_id

@register.filter
def get_reply_date(reply_id):
	rv = Reply.objects.get(id=reply_id)
	return rv.date

@register.filter
def get_topic_reply_count(topic_id):
	return Topic.objects.get(id=topic_id).reply_set.count()

@register.filter
def get_reply_thankers_count(reply_id):
	return Reply.objects.get(id=reply_id).thanks_set.all().count()

@register.filter
def toadd(x, y):
	#print 'toadd::x:%s,y:%s' % (x, y)
	z = 0
	try:
		z = int(x) + int(y)
	except Exception, e:
		print e
	return z

@register.filter
def tosub(x, y):
	#print 'tosub::x:%s,y:%s' % (x, y)
	z = 0
	try:
		z = int(x) - int(y)
	except Exception, e:
		print e
	return z

@register.filter
def myrange(x, y):
	#print 'myrange::x:%s,y:%s' % (x, y)
	return [i for i in range(x, y)]
	
@register.filter
def topercent(x, y):
	return str(round(float(x) / y, 4) * 100) + '%'
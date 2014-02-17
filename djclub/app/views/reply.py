# coding: utf-8
import time

from django.shortcuts import render_to_response, redirect
from django.contrib import messages
from django.template import RequestContext
from django.conf import settings

from djclub.app.models import Topic, Reply, Notify, Bill, User, Thanks
from djclub.app.forms import ReplyForm
from djclub.app.functions import mention, mentions

def reply_add(request, topic_id=0):
	topic = None
	user = None
	try:
		topic = Topic.objects.get(id=topic_id)
	except Exception, e:
		print e
		messages.info(request, '主题不存在！')
		return redirect(view, topic.id)
	if not request.session.get('user'):
		messages.info(request, '登录后进行操作!')
		return redirect('login')
	if request.method == 'POST':
		form = ReplyForm(request.POST)
		if not form.is_valid():
			for field in form.errors:
				messages.info(request, form[field].errors.as_text())
		else:
			user = request.session.get('user')
			cd = form.cleaned_data
			reply = Reply(topic=topic, author=user, text=cd['content'], date=int(time.time()))
			reply.save()
			user.time -= settings.TOPIC_REPLY
			user.save()
			topic.author.time += settings.TOPIC_REPLY
			topic.author.save()
			topic.last_reply_date = int(time.time())
			topic.save()
			#for reader in topic.readers:
			#	topic.readers.remove(reader)

			t = int(time.time())
			if user.id != topic.author.id:
				reply_bill = Bill(author=user,time=settings.TOPIC_REPLY,type=3,date=t,reply=reply,user_id=topic.author.id,balance=user.time)
				reply_bill.save()
				author_bill = Bill(author=topic.author,time=settings.TOPIC_REPLY,type=5,date=t,reply=reply,user_id=user.id,balance=topic.author.time)
				author_bill.save()
				author_notify = Notify(author=topic.author, topic=topic, reply=reply, type=1, date=t)
				author_notify.save()
			for username in mentions(cd['content']):
				if username:
					if username != topic.author.name:
						print 'username:', username 
						author = User.objects.get(name=username)
						reply_notify = Notify(author=author, topic=topic, reply=reply, type=2, date=t)
						reply_notify.save()
	return redirect('topicview', topic.id)

def reply_del(request, reply_id):
	reply = None
	try:
		reply = Reply.objects.get(id=reply_id)
	except Exception, e:
		print e
	if not request.session.get('user') or not reply:
		messages.info(request, '非法操作！')
		return redirect('/')

	reply.delete()
	messages.info(request, '评论删除成功！')
	return redirect('topicview', reply.topic.id)

def reply_edit(request, reply_id):
	reply = None
	try:
		reply = Reply.objects.get(id=reply_id)
	except Exception, e:
		print e
	if not reply:
		messages.info(request, '非法操作！')
		return redirect('/')

	if getattr(request.session.get('user'), 'id', 0) != reply.author.id \
		and getattr(request.session.get('user'), 'id', 0) != 1:
		messages.info(request, '非法操作！')
		return redirect('topicview', reply.topic.id)
	form = ReplyForm(initial={
			'content': getattr(reply, 'text', '')
		})
	if request.method == 'POST':
		form = ReplyForm(request.POST)
		if not form.is_valid():
			for field in form.errors:
				messages.info(request, form[field].errors.as_text())
		else:
			cd = form.cleaned_data
			reply.text = cd['content']
			reply.save()
			messages.info(request, '评论更新成功！')
			return redirect('topicview', reply.topic.id)
	return render_to_response('reply_edit.html', locals(), context_instance=RequestContext(request))

def thanks(request, reply_id=0):
	if not request.session.get('user'):
		messages.info(request, '登录后进行操作!')
		return redirect('login')
	reply = None
	try:
		reply = Reply.objects.get(id=reply_id)
	except Exception, e:
		raise e
	user = request.session.get('user')
	if reply.id not in user.thanks:
		author = reply.author
		user.thanks.append(int(reply.id))
		user.time -= settings.TOPIC_THANKS
		author.time += settings.TOPIC_THANKS
		user.save()
		author.save()
		t = int(time.time())
		user_bill = Bill(author=user,time=settings.TOPIC_THANKS,type=4,date=t,reply=reply,user_id=author.id,balance=user.time)
		author_bill = Bill(author=author,time=settings.TOPIC_THANKS,type=6,date=t,reply=reply,user_id=user.id,balance=author.time)
		user_bill.save()
		author_bill.save()
		thanks = Thanks(user=user, reply=reply)
		thanks.save()
	return redirect('topicview', reply.topic.id)
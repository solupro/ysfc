# coding: utf-8
import time

from django.shortcuts import render_to_response, redirect
from django.contrib import messages
from django.template import RequestContext
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from djclub.app.models import Node, Nodeclass, Topic, User, Reply, Favorites, Bank, Bill, Votes
from djclub.app.forms import TopicForm, ReplyForm
from djclub.app.functions import liketopic

def index(request):
	nodeClasses = Nodeclass.objects.filter()
	usercount = User.objects.all().count()
	topiccount = Topic.objects.all().count()
	replycount = Reply.objects.all().count()
	topics = Topic.objects.all().order_by('-date')
	page = request.GET.get('page', 1)
	paginator = Paginator(topics, settings.PER_PAGE)
	page_obj = None
	try:
		page_obj = paginator.page(page)
	except PageNotAnInteger:
		page_obj = paginator.page(1)
	except EmptyPage:
		page_obj = paginator.page(paginator.num_pages)
	return render_to_response('index.html', locals(), context_instance=RequestContext(request))


def add(request):
	post = {}

	if not request.session.get('user'):
		messages.info(request, '登录后创建主题!')
		return redirect('login')

	if request.method == 'POST':
		post = request.POST.copy()
		form = TopicForm(post)
		if not form.is_valid():
			for field in form.errors:
				messages.info(request, form[field].errors.as_text())
		else:
			cd = form.cleaned_data
			if getattr(request.session['user'], 'time', 0) < settings.TOPIC_CREATE:
				messages.info(request, '时间不足%s分钟！' % settings.TOPIC_CREATE)
				return redirect('/')
			bank = Bank.objects.get(id=1)
			bank.time += settings.TOPIC_CREATE
			bank.save()
			request.session['user'].time -=settings.TOPIC_CREATE
			request.session['user'].save()

			topic = Topic()
			topic.author_id = getattr(request.session['user'], 'id', 0)
			topic.title = cd['title']
			topic.text = cd['text']
			topic.node_id = cd['nodename']
			topic.date = int(time.time())
			topic.save()

			bill = Bill(author=request.session['user'], time=settings.TOPIC_CREATE, type=2, date=int(time.time()),\
			topic=topic,balance=getattr(request.session['user'], 'time', 0))
			bill.save()
			messages.info(request, '主题创建成功！')
			return redirect('/')
	form = TopicForm(initial={
		'title' : request.POST.get('title', ''),
		'text' : request.POST.get('text', ''),
		'nodename': request.POST.get('nodename', '0'),
	})
	return render_to_response('topic_add.html', locals(), context_instance=RequestContext(request))

def delete(request, topic_id=0):
	topic = None
	try:
		topic = Topic.objects.get(id=topic_id)
	except Exception, e:
		print e
		messages.info(request, '主题不存在！')
		return redirect('/')
	for r in Reply.objects.filter(topic=topic):
		r.delete()
	topic.delete()
	messages.info(request, '主题删除成功！')
	return redirect('/')

def view(request, topic_id=0):
	topic = None
	try:
		topic = Topic.objects.get(id=topic_id)
	except Exception, e:
		print e
		messages.info(request, '主题不存在！')
		return redirect('/')
	liketopics = []
	i = 0
	for n in Topic.objects.all().order_by('-date'):
		if i == 6:
			break
		if liketopic(topic.title,n.title) == 0:
			liketopics += [n]
			i += 1
			continue
		elif liketopic(topic.title,n.title) == 1:
			liketopics += [n]
			i += 1
			continue
		elif liketopic(topic.title,n.title) == 2:
			liketopics += [n]
			i += 1
			continue
	#if request.session.get('user') and topic.id not in request.session['user'].reads:
	#	user = request.session['user']
	#	r = Reads(user=user, topic=topic)
	#	r.save()
	#	request.session['user'].reads.append(int(r.topic_id))
	form = ReplyForm()
	replys = topic.reply_set.all().order_by('-date')
	page = request.GET.get('page', 1)
	paginator = Paginator(replys, settings.RE_PER_PAGE)
	page_obj = None
	try:
		page_obj = paginator.page(page)
	except PageNotAnInteger:
		page_obj = paginator.page(1)
	except EmptyPage:
		page_obj = paginator.page(paginator.num_pages)
	return render_to_response('topic_view.html', locals(), context_instance=RequestContext(request))


def edit(request, topic_id=0):
	topic = None
	try:
		topic = Topic.objects.get(id=topic_id)
	except Exception, e:
		print e
		messages.info(request, '主题不存在！')
		return redirect(view, topic.id)

	#print 'userid:',int(getattr(request.session['user'], 'id', 0))
	#if getattr(request.session['user'], 'id', 0) != topic.author_id or \
	#		getattr(request.session['user'], 'id', 0) != 1:
	#	messages.info(request, '没有权限进行编辑操作！')
	#	return redirect(view, topic.id)

	if request.method == 'POST':
		post = request.POST.copy()
		form = TopicForm(post)
		if not form.is_valid():
			for field in form.errors:
				messages.info(request, form[field].errors.as_text())
		else:
			cd = form.cleaned_data

			topic.title = cd['title']
			topic.text = cd['text']
			topic.nodename = cd['nodename']
			topic.save()
			messages.info(request, '主题更新成功！')
			return redirect(view, topic.id)

	form = TopicForm(initial={
		'title' : getattr(topic, 'title', ''),
		'text' : getattr(topic, 'text', ''),
		'nodename': getattr(topic, 'node_id', '0'),
	})

	return render_to_response('topic_edit.html', locals(), context_instance=RequestContext(request))

def fav(request, topic_id=0):
	topic = None
	try:
		topic = Topic.objects.get(id=topic_id)
	except Exception, e:
		print e
		messages.info(request, '主题不存在！')
		return redirect(view, topic.id)

	if not request.session.get('user'):
		messages.info(request, '登录后进行操作!')
		return redirect('login')
	if request.session.get('user') and topic.id not in request.session['user'].favorites:
		user = request.session['user']
		f = Favorites(user=user, topic=topic)
		f.save()
		request.session['user'].favorites.append(int(f.topic_id))
	return redirect(view, topic.id)


def vote(request, topic_id=0):
	topic = None
	try:
		topic = Topic.objects.get(id=topic_id)
	except Exception, e:
		print e
		messages.info(request, '主题不存在！')
		return redirect(view, topic.id)

	if not request.session.get('user'):
		messages.info(request, '登录后进行操作!')
		return redirect('login')

	if request.session.get('user') and topic.id not in request.session['user'].votes:
		user = request.session['user']
		v = Votes(user=user, topic=topic)
		v.save()
		request.session['user'].votes.append(int(v.topic_id))
		topic.vote += 1
		if topic.vote >= 10:
			topic.report = 1
		topic.save()
		messages.info(request, '已举报，谢谢参与社区建设。')
	return redirect(view, topic.id)